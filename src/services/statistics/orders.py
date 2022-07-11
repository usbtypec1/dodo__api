import asyncio
from typing import Iterable, Sequence, TypeAlias

import pandas as pd

import models
from db.cache import set_in_cache, get_from_cache
from services.api import dodo_is_api
from utils import exceptions, time_utils

GroupedByUnitName: TypeAlias = Sequence[tuple[str, pd.DataFrame]]


async def get_restaurant_orders(
        cookies: dict,
        units: Iterable[models.UnitIdAndName],
        datetime_config: time_utils.Period,
) -> list[GroupedByUnitName]:
    unit_name_to_unit_id = {unit.unit_name: unit.unit_id for unit in units}
    units_restaurant_orders: list[GroupedByUnitName] = []
    unit_ids_to_get_from_api = []
    for unit in units:
        key = f'restaurant_orders@{unit.unit_id}'
        try:
            grouped_by_unit_name_df: GroupedByUnitName = await get_from_cache(key)
        except exceptions.DoesNotExistInCache:
            unit_ids_to_get_from_api.append(unit.unit_id)
        else:
            units_restaurant_orders.append(grouped_by_unit_name_df)

    if unit_ids_to_get_from_api:
        responses = await dodo_is_api.get_restaurant_orders(cookies, unit_ids_to_get_from_api, datetime_config)

        for grouped_by_unit_name_df in responses:
            unit_id = unit_name_to_unit_id[grouped_by_unit_name_df[0]]
            key = f'restaurant_orders@{unit_id}'
            await set_in_cache(key, grouped_by_unit_name_df)
        units_restaurant_orders += responses

    return units_restaurant_orders


def zip_certificates_today_and_week_before(
        units: Iterable[models.UnitIdAndName],
        certificates_today: Iterable[models.UnitBeingLateCertificates],
        certificates_week_before: Iterable[models.UnitBeingLateCertificates],
) -> list[models.UnitBeingLateCertificatesTodayAndWeekBefore]:
    certificates_today_unit_id_to_count = {report.unit_id: report.being_late_certificates_count
                                           for report in certificates_today}
    certificates_week_before_unit_id_to_count = {report.unit_id: report.being_late_certificates_count
                                                 for report in certificates_week_before}
    result = []
    for unit in units:
        certificates_today_count = certificates_today_unit_id_to_count.get(unit.unit_id, 0)
        certificates_week_before_count = certificates_week_before_unit_id_to_count.get(unit.unit_id, 0)
        result.append(models.UnitBeingLateCertificatesTodayAndWeekBefore(
            unit_id=unit.unit_id,
            unit_name=unit.unit_name,
            certificates_today_count=certificates_today_count,
            certificates_week_before_count=certificates_week_before_count,
        ))
    return result


async def get_being_late_certificates_statistics(
        cookies: dict,
        units: Iterable[models.UnitIdAndName],
) -> list[models.UnitBeingLateCertificatesTodayAndWeekBefore]:
    period_today = time_utils.Period.new_today()
    period_week_before = time_utils.Period.new_week_ago()

    units_to_get_from_api: list[models.UnitIdAndName] = []
    all_certificates_for_today_and_week_before: list[models.UnitBeingLateCertificatesTodayAndWeekBefore] = []

    for unit in units:
        key = f'being_late_certificates@{unit.unit_id}'
        try:
            unit_being_late_certificates = await get_from_cache(key)
        except exceptions.DoesNotExistInCache:
            units_to_get_from_api.append(unit)
        else:
            all_certificates_for_today_and_week_before.append(unit_being_late_certificates)

    if units_to_get_from_api:
        task_today = dodo_is_api.get_being_late_certificates(cookies, units, period_today)
        task_week_before = dodo_is_api.get_being_late_certificates(cookies, units, period_week_before)
        responses: tuple[models.UnitBeingLateCertificates, models.UnitBeingLateCertificates] = await asyncio.gather(
            task_today, task_week_before)
        certificates_today, certificates_week_before = responses
        certificates_for_today_and_week_before = zip_certificates_today_and_week_before(
            units, certificates_today, certificates_week_before)
        for unit_certificates in certificates_for_today_and_week_before:
            key = f'being_late_certificates@{unit_certificates.unit_id}'
            await set_in_cache(key, unit_certificates)
        all_certificates_for_today_and_week_before += certificates_for_today_and_week_before
    return all_certificates_for_today_and_week_before
