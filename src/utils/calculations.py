import models

__all__ = (
    'calculate_revenue_delta_in_percents',
    'calculate_delivery_with_courier_app_percent',
    'calculate_orders_for_courier_count_per_hour',
    'calculate_orders_with_phone_number_percent',
    'calculate_couriers_workload',
    'calculate_revenue_metadata',
    'calculate_orders_count_delta',
)

SECONDS_IN_HOUR = 3600


def calculate_revenue_delta_in_percents(revenue_today: int | float,
                                        revenue_week_before: int | float) -> int:
    """Calculate how revenue has changed since week before.
    If either *revenue_today* or *revenue_week_before* equals to zero, zero will be returned.

    Args:
        revenue_today: Today's revenue.
        revenue_week_before: Revenue week before.

    Returns: Difference of revenue between today and week before in percents.
    """
    if revenue_week_before == 0:
        return 0
    return round(revenue_today / revenue_week_before * 100) - 100


def calculate_orders_for_courier_count_per_hour(
        delivery_orders_count: int,
        couriers_shift_duration: int,
) -> float:
    if couriers_shift_duration == 0:
        return 0
    return round(delivery_orders_count / (couriers_shift_duration / SECONDS_IN_HOUR), 2)


def calculate_delivery_with_courier_app_percent(
        orders_with_courier_app_count: int,
        delivery_orders_count: int,
) -> float:
    if delivery_orders_count == 0:
        return 0
    return round(orders_with_courier_app_count / delivery_orders_count * 100, 2)


def calculate_couriers_workload(trips_duration: int, couriers_shifts_duration: int) -> float:
    if couriers_shifts_duration == 0:
        return 0
    return round(trips_duration / couriers_shifts_duration * 100, 2)


def calculate_revenue_metadata(
        revenue_statistics: list[models.RevenueForTodayAndWeekBeforeStatistics],
) -> models.UnitsRevenueMetadata:
    total_revenue_today = 0
    total_revenue_week_before = 0
    for unit_revenue_statistics in revenue_statistics:
        total_revenue_today += unit_revenue_statistics.today
        total_revenue_week_before += unit_revenue_statistics.week_before
    delta_from_week_before = calculate_revenue_delta_in_percents(total_revenue_today, total_revenue_week_before)
    return models.UnitsRevenueMetadata(
        delta_from_week_before=delta_from_week_before,
        total_revenue_week_before=total_revenue_week_before,
        total_revenue_today=total_revenue_today,
    )


def calculate_orders_count_delta(today: float, week_before: float) -> float:
    if week_before == 0:
        return 0
    return round(today * 100 / week_before - 100, 2)


def calculate_orders_with_phone_number_percent(with_phone_numbers: int, total: int) -> float:
    if total == 0:
        return 0
    return round(with_phone_numbers / total * 100, 2)
