from typing import TYPE_CHECKING
from datetime import datetime, timedelta, UTC, timezone

from src.core.config import settings

if TYPE_CHECKING:
    from src.database.models.schedules import Schedules


def round_to_multiple(value: int, multiple: int = 15) -> int:
    if value % multiple == 0:
        return value

    remainder = value % multiple
    if remainder < multiple / 2:
        return value - remainder
    else:
        return value + (multiple - remainder)


def round_to_multiple_dt(value: datetime | None, multiple: int = 15) -> datetime | None:
    if value is None:
        value = datetime.now()

    result = value.replace(second=0, microsecond=0)

    total_minutes = result.minute

    if total_minutes % multiple == 0:
        return result

    remainder = total_minutes % multiple
    if remainder < multiple / 2:
        new_minutes = total_minutes - remainder
    else:
        new_minutes = total_minutes + (multiple - remainder)

    if new_minutes >= 60:
        new_hour = result.hour + 1
        new_day = result.day
        new_month = result.month
        new_year = result.year

        if new_hour >= 24:
            new_hour = 0
            next_day = result.replace(hour=0, minute=0) + timedelta(days=1)
            new_day = next_day.day
            new_month = next_day.month
            new_year = next_day.year

        return datetime(
            year=new_year, month=new_month, day=new_day, hour=new_hour, minute=0, tzinfo=UTC
        )

    return result.replace(minute=new_minutes)


def find_next_takings(
    schedules: list["Schedules"], next_taking_interval: timedelta, current_time: datetime | None = None
) -> list[dict[str, "Schedules"]]:
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    taking_end_time: datetime = current_time + next_taking_interval

    if not (settings.MORNING_HOUR <= current_time.hour + 1 <= settings.EVENING_HOUR):
        return []

    next_takings: list[dict[str, "Schedules"]] = []

    for schedule in schedules:
        if schedule.end_date and schedule.end_date < current_time:
            continue

        if schedule.start_date > current_time:
            if schedule.start_date <= taking_end_time:
                if settings.MORNING_HOUR <= schedule.start_date.hour <= settings.EVENING_HOUR:
                    next_takings.append(
                        {"schedule": schedule, "next_taking_time": schedule.start_date}
                    )
            continue

        elapsed_time: float = (current_time - schedule.start_date).total_seconds() / 60
        intervals_passed: int = int(elapsed_time / schedule.frequency)
        last_taking_time: datetime = schedule.start_date + timedelta(
            minutes=intervals_passed * schedule.frequency
        )

        next_taking_time = last_taking_time + timedelta(minutes=schedule.frequency)
        while next_taking_time <= taking_end_time:
            if schedule.end_date and next_taking_time > schedule.end_date:
                break

            if settings.MORNING_HOUR <= next_taking_time.hour <= settings.EVENING_HOUR:
                next_takings.append({"schedule": schedule, "next_taking_time": next_taking_time})

            next_taking_time += timedelta(minutes=schedule.frequency)

    return next_takings
