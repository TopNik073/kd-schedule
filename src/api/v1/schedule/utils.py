from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from src.core.config import Settings
from src.core.logger import get_logger

if TYPE_CHECKING:
    from src.database.models.schedules import Schedules

logger = get_logger(__name__)


def round_to_multiple(value: int, multiple: int = 15) -> int:
    if value <= multiple:
        return multiple

    if value % multiple == 0:
        return value

    remainder = value % multiple
    if remainder < multiple / 2:
        return value - remainder

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
    schedules: list["Schedules"],
    next_taking_interval: timedelta,
    config: Settings,
    current_time: datetime | None = None,
) -> list[dict[str, Any]]:
    if current_time is None:
        current_time = datetime.now(UTC)

    taking_end_time: datetime = current_time + next_taking_interval

    evening_time_today = datetime.combine(taking_end_time.date(), config.EVENING_TIME, tzinfo=UTC)
    taking_end_time = min(taking_end_time, evening_time_today)

    next_takings: list[dict[str, Any]] = []

    for schedule in schedules:
        logger.debug(f"Checking schedule {schedule.id}")
        if schedule.end_date and schedule.end_date < current_time:
            logger.debug(f"Schedule {schedule.id} has ended")
            continue

        if schedule.start_date > taking_end_time:
            logger.debug(f"Schedule {schedule.id} has not started yet")
            continue

        if schedule.start_date >= current_time and schedule.start_date <= taking_end_time:
            logger.debug(f"Schedule starts at {schedule.start_date} within search interval")
            schedule_time = schedule.start_date.time()
            if config.MORNING_TIME <= schedule_time <= config.EVENING_TIME:
                next_takings.append({"schedule": schedule, "next_taking_time": schedule.start_date})
                logger.debug(f"Added first taking at schedule start: {schedule.start_date}")
            next_taking_time = schedule.start_date + timedelta(minutes=schedule.frequency)
        else:
            elapsed_time: float = (current_time - schedule.start_date).total_seconds() / 60
            intervals_passed: int = int(elapsed_time / schedule.frequency)

            last_taking_time: datetime = schedule.start_date + timedelta(
                minutes=intervals_passed * schedule.frequency
            )

            if last_taking_time >= current_time:
                last_taking_time -= timedelta(minutes=schedule.frequency)

            next_taking_time = last_taking_time + timedelta(minutes=schedule.frequency)
            logger.debug(f"Schedule already started, next taking time: {next_taking_time}")

        while next_taking_time <= taking_end_time:
            if schedule.end_date and next_taking_time > schedule.end_date:
                logger.debug(
                    f"Next taking time {next_taking_time} is after end date {schedule.end_date}"
                )
                break

            next_taking_time_of_day = next_taking_time.time()
            if not (config.MORNING_TIME <= next_taking_time_of_day <= config.EVENING_TIME):
                logger.debug(
                    f"Next taking time {next_taking_time} is not in the allowed hours, searching for next taking"
                )
                next_taking_time += timedelta(minutes=schedule.frequency)
                continue

            logger.debug(
                f"Next taking time {next_taking_time} is in the allowed hours, adding to next takings"
            )
            next_takings.append({"schedule": schedule, "next_taking_time": next_taking_time})

            next_taking_time += timedelta(minutes=schedule.frequency)
            logger.debug(f"Next taking time is {next_taking_time}")

    return sorted(next_takings, key=lambda x: x["next_taking_time"])
