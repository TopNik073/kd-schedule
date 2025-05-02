from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.api.v1.schedule.utils import find_next_takings
from src.database.models.schedules import Schedules


@pytest.fixture
def test_schedule() -> Schedules:
    return Schedules(
        id=uuid4(),
        user_id=uuid4(),
        medicine_name="Test Medicine",
        frequency=15,
        start_date=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
        end_date=datetime(2025, 1, 1, 11, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def test_schedule_no_end() -> Schedules:
    return Schedules(
        id=uuid4(),
        user_id=uuid4(),
        medicine_name="Test Medicine No End",
        frequency=30,
        start_date=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
        end_date=None,
    )


class TestFindNextTakings:
    def test_multiple_takings_in_interval(self, test_schedule: Schedules) -> None:
        # Test interval: 1 hour, should get 4 takings (every 15 minutes)
        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        interval = timedelta(hours=1)

        takings = find_next_takings([test_schedule], interval, current_time)

        assert len(takings) == 4
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 10, 15, tzinfo=timezone.utc)
        assert takings[1]["next_taking_time"] == datetime(2025, 1, 1, 10, 30, tzinfo=timezone.utc)
        assert takings[2]["next_taking_time"] == datetime(2025, 1, 1, 10, 45, tzinfo=timezone.utc)
        assert takings[3]["next_taking_time"] == datetime(2025, 1, 1, 11, 0, tzinfo=timezone.utc)

    def test_takings_outside_allowed_hours(self) -> None:
        # Create schedule with takings outside allowed hours
        schedule = Schedules(
            id=uuid4(),
            user_id=uuid4(),
            medicine_name="Night Medicine",
            frequency=60,
            start_date=datetime(2025, 1, 1, 3, 0, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 1, 5, 0, tzinfo=timezone.utc),
        )

        current_time = datetime(2025, 1, 1, 3, 0, tzinfo=timezone.utc)
        interval = timedelta(hours=2)
        takings = find_next_takings([schedule], interval, current_time)
        assert len(takings) == 0

    def test_takings_after_end_date(self) -> None:
        # Create schedule that has already ended
        schedule = Schedules(
            id=uuid4(),
            user_id=uuid4(),
            medicine_name="Ended Medicine",
            frequency=30,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 1, 11, 0, tzinfo=timezone.utc),
        )

        current_time = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)  # After end_date
        interval = timedelta(hours=1)
        takings = find_next_takings([schedule], interval, current_time)
        assert len(takings) == 0

    def test_schedule_without_end_date(self, test_schedule_no_end: Schedules) -> None:
        # Test schedule without end_date
        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        interval = timedelta(hours=2)  # 2 hours interval

        takings = find_next_takings([test_schedule_no_end], interval, current_time)

        assert len(takings) == 4  # Every 30 minutes for 2 hours
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 10, 30, tzinfo=timezone.utc)
        assert takings[1]["next_taking_time"] == datetime(2025, 1, 1, 11, 0, tzinfo=timezone.utc)
        assert takings[2]["next_taking_time"] == datetime(2025, 1, 1, 11, 30, tzinfo=timezone.utc)
        assert takings[3]["next_taking_time"] == datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)

    def test_multiple_schedules(self, test_schedule: Schedules, test_schedule_no_end: Schedules):
        # Test multiple schedules
        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        interval = timedelta(hours=1)

        takings = find_next_takings([test_schedule, test_schedule_no_end], interval, current_time)

        # test_schedule: 4 takings (every 15 minutes)
        # test_schedule_no_end: 2 takings (every 30 minutes)
        assert len(takings) == 6

    def test_schedule_starting_in_future(self) -> None:
        # Test schedule that starts in the future
        future_schedule = Schedules(
            id=uuid4(),
            user_id=uuid4(),
            medicine_name="Future Medicine",
            frequency=30,
            start_date=datetime(2025, 1, 1, 11, 0, tzinfo=timezone.utc),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        interval = timedelta(hours=1)
        takings = find_next_takings([future_schedule], interval, current_time)

        # Should only include the first taking at 11:00
        assert len(takings) == 1
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 11, 0, tzinfo=timezone.utc)

    def test_schedule_starting_in_one_day_after_current_time(self) -> None:
        # Test schedule that starts in one day after current time
        future_schedule = Schedules(
            id=uuid4(),
            user_id=uuid4(),
            medicine_name="Future Medicine",
            frequency=30,
            start_date=datetime(2025, 1, 2, 10, 0, tzinfo=timezone.utc),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
        interval = timedelta(hours=1)
        takings = find_next_takings([future_schedule], interval, current_time)

        # Should not include any takings because the schedule starts in one day after current time
        assert len(takings) == 0
