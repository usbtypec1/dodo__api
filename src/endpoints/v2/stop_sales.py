import uuid
from datetime import datetime

from fastapi import APIRouter, Query

import models
from services.api import private_dodo_api
from utils import time_utils

router = APIRouter(prefix='/v2/stop-sales', tags=['Stop sales'])


@router.get(
    path='/ingredients',
    response_model_by_alias=False,
    response_model=list[models.StopSalesByIngredients],
)
async def get_ingredient_stop_sales(
        token: str,
        unit_uuids: list[uuid.UUID] = Query(...),
        from_datetime: datetime | None = Query(None, description='Today unless specified'),
        to_datetime: datetime | None = Query(None, description='Current datetime unless specified'),
):
    period = time_utils.Period(from_datetime, to_datetime)
    return await private_dodo_api.get_ingredient_stop_sales(token, unit_uuids, period)


@router.get(
    path='/channels',
    response_model_by_alias=False,
    response_model=list[models.StopSalesBySalesChannels],
)
async def get_channels_stop_sales(
        token: str,
        unit_uuids: list[uuid.UUID] = Query(...),
        from_datetime: datetime | None = Query(None, description='Today unless specified'),
        to_datetime: datetime | None = Query(None, description='Current datetime unless specified'),
):
    period = time_utils.Period(from_datetime, to_datetime)
    return await private_dodo_api.get_channels_stop_sales(token, unit_uuids, period)


@router.get(
    path='/products',
    response_model_by_alias=False,
    response_model=list[models.StopSalesByProduct],
)
async def get_products_stop_sales(
        token: str,
        unit_uuids: list[uuid.UUID] = Query(...),
        from_datetime: datetime | None = Query(None, description='Today unless specified'),
        to_datetime: datetime | None = Query(None, description='Current datetime unless specified'),
):
    period = time_utils.Period(from_datetime, to_datetime)
    return await private_dodo_api.get_products_stop_sales(token, unit_uuids, period)
