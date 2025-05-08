from datetime import UTC, datetime, time, timedelta
from typing import Callable
from uuid import uuid4

import pytest

from src.api.v1.schedule.utils import find_next_takings
from src.core.config import Settings
from src.database.models.schedules import Schedules


@pytest.fixture
def test_config() -> Settings:
    return Settings(
        MORNING_TIME=time(8, 0),
        EVENING_TIME=time(22, 0),
        DB_USER="",
        DB_PASS="",
        DB_HOST="",
        DB_PORT="",
        DB_NAME="",
    )


@pytest.fixture
def schedule_factory() -> Callable[..., Schedules]:
    """Factory function to create a schedule with the given parameters"""

    def create_schedule(
        medicine_name: str = "Factory Test Medicine",
        frequency: int = 15,
        start_date: datetime | None = datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
        end_date: datetime | None = None,
    ) -> Schedules:
        return Schedules(
            id=uuid4(),
            user_id=uuid4(),
            medicine_name=medicine_name,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
        )

    return create_schedule


class TestFindNextTakings:
    def test_multiple_takings_in_interval(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test interval: 1 hour, should get 4 takings (every 15 minutes)
        schedule = schedule_factory(
            medicine_name="Test Multiple Takings In Interval",
            frequency=15,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=datetime(2025, 1, 1, 11, 0, tzinfo=UTC),
        )

        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
        interval = timedelta(hours=1)

        takings = find_next_takings([schedule], interval, test_config, current_time)

        assert len(takings) == 5  # Should get 5 takings
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
        assert takings[1]["next_taking_time"] == datetime(2025, 1, 1, 10, 15, tzinfo=UTC)
        assert takings[2]["next_taking_time"] == datetime(2025, 1, 1, 10, 30, tzinfo=UTC)
        assert takings[3]["next_taking_time"] == datetime(2025, 1, 1, 10, 45, tzinfo=UTC)
        assert takings[4]["next_taking_time"] == datetime(2025, 1, 1, 11, 0, tzinfo=UTC)

    def test_takings_outside_allowed_hours(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Create schedule with takings outside allowed hours
        schedule = schedule_factory(
            medicine_name="Test Takings Outside Allowed Hours",
            frequency=15,
            start_date=datetime(2025, 1, 1, 21, 15, tzinfo=UTC),
            end_date=datetime(2025, 1, 1, 22, 45, tzinfo=UTC),
        )

        current_time = datetime(2025, 1, 1, 21, 0, tzinfo=UTC)
        interval = timedelta(hours=2)
        takings = find_next_takings([schedule], interval, test_config, current_time)
        assert len(takings) == 4  # Should only get 4 takings
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 21, 15, tzinfo=UTC)
        assert takings[1]["next_taking_time"] == datetime(2025, 1, 1, 21, 30, tzinfo=UTC)
        assert takings[2]["next_taking_time"] == datetime(2025, 1, 1, 21, 45, tzinfo=UTC)
        assert takings[3]["next_taking_time"] == datetime(2025, 1, 1, 22, 0, tzinfo=UTC)

        # Test schedule that starts after allowed hours
        schedule.start_date = datetime(2025, 1, 1, 22, 15, tzinfo=UTC)
        schedule.end_date = datetime(2025, 1, 1, 23, 45, tzinfo=UTC)

        takings = find_next_takings([schedule], interval, test_config, current_time)
        assert len(takings) == 0  # Shouldn't get any schedules

    def test_takings_after_end_date(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Create schedule that has already ended
        schedule = schedule_factory(
            medicine_name="Test Takings After End Date",
            frequency=30,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=datetime(2025, 1, 1, 11, 0, tzinfo=UTC),
        )

        current_time = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
        interval = timedelta(hours=1)
        takings = find_next_takings([schedule], interval, test_config, current_time)
        assert len(takings) == 0

    def test_schedule_without_end_date(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test schedule without end_date
        schedule = schedule_factory(
            medicine_name="Test Schedule Without End Date",
            frequency=30,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
        interval = timedelta(hours=2)

        takings = find_next_takings([schedule], interval, test_config, current_time)

        assert len(takings) == 5  # Every 30 minutes for 2 hours
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
        assert takings[1]["next_taking_time"] == datetime(2025, 1, 1, 10, 30, tzinfo=UTC)
        assert takings[2]["next_taking_time"] == datetime(2025, 1, 1, 11, 0, tzinfo=UTC)
        assert takings[3]["next_taking_time"] == datetime(2025, 1, 1, 11, 30, tzinfo=UTC)
        assert takings[4]["next_taking_time"] == datetime(2025, 1, 1, 12, 0, tzinfo=UTC)

    def test_multiple_schedules(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ):
        # Test multiple schedules
        schedule1 = schedule_factory(
            medicine_name="Test Multiple Schedules (With End Date)",
            frequency=15,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=datetime(2025, 1, 1, 11, 0, tzinfo=UTC),
        )

        schedule2 = schedule_factory(
            medicine_name="Test Multiple Schedules (No End Date)",
            frequency=30,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
        interval = timedelta(hours=1)

        takings = find_next_takings([schedule1, schedule2], interval, test_config, current_time)

        # schedule1: 5 takings (every 15 minutes)
        # schedule2: 3 takings (every 30 minutes)
        assert len(takings) == 8

    def test_schedule_starting_in_future(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test schedule that starts in the future
        schedule = schedule_factory(
            medicine_name="Test Schedule Starting In Future",
            frequency=30,
            start_date=datetime(2025, 1, 1, 11, 0, tzinfo=UTC),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
        interval = timedelta(hours=1)
        takings = find_next_takings([schedule], interval, test_config, current_time)

        # Should only include the first taking at 11:00
        assert len(takings) == 1
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 11, 0, tzinfo=UTC)

    def test_schedule_starting_in_one_day_after_current_time(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test schedule that starts in one day after current time
        schedule = schedule_factory(
            medicine_name="Test Schedule Starting In One Day After Current Time",
            frequency=30,
            start_date=datetime(2025, 1, 2, 10, 0, tzinfo=UTC),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
        interval = timedelta(hours=1)
        takings = find_next_takings([schedule], interval, test_config, current_time)

        # Should not include any takings because the schedule starts in one day after current time
        assert len(takings) == 0

    def test_sorted_multiple_schedules(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test multiple schedules with different frequencies
        schedule1 = schedule_factory(
            medicine_name="Test Sorted Multiple Schedules (Medicine 1)",
            frequency=15,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=None,
        )
        schedule2 = schedule_factory(
            medicine_name="Test Sorted Multiple Schedules (Medicine 2)",
            frequency=30,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
        interval = timedelta(hours=1)
        takings = find_next_takings([schedule1, schedule2], interval, test_config, current_time)

        # Should have 8 takings in total, sorted by time
        assert len(takings) == 8
        # Verify that schedules are sorted
        for i in range(len(takings) - 1):
            assert takings[i]["next_taking_time"] <= takings[i + 1]["next_taking_time"]

    def test_edge_case_exactly_at_start_time(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test case 1: Check exactly at start time
        schedule = schedule_factory(
            medicine_name="Test Edge Case Exactly At Start Time",
            frequency=60,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
        interval = timedelta(minutes=30)
        takings = find_next_takings([schedule], interval, test_config, current_time)
        assert len(takings) == 1  # Should get one taking at 10:00
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 10, 0, tzinfo=UTC)

    def test_edge_case_frequency_greater_than_interval(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test case 2: Check with frequency greater than interval
        schedule = schedule_factory(
            medicine_name="Test Edge Case Frequency Greater Than Interval",
            frequency=60,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 10, 30, tzinfo=UTC)
        interval = timedelta(minutes=30)
        takings = find_next_takings([schedule], interval, test_config, current_time)
        assert len(takings) == 1  # Should get one taking at 11:00
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 11, 0, tzinfo=UTC)

    def test_edge_case_end_time_outside_interval(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test case 3: Check with exact end time outside the interval
        schedule = schedule_factory(
            medicine_name="Test Edge Case End Time Outside Interval",
            frequency=30,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=datetime(2025, 1, 1, 11, 0, tzinfo=UTC),
        )

        current_time = datetime(2025, 1, 1, 10, 50, tzinfo=UTC)
        interval = timedelta(hours=1)
        takings = find_next_takings([schedule], interval, test_config, current_time)
        assert len(takings) == 1  # Only one taking at 11:00
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 11, 0, tzinfo=UTC)

    def test_edge_case_end_time_inside_interval(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test case 4: Check with exact end time inside the interval
        schedule = schedule_factory(
            medicine_name="Test Edge Case End Time Inside Interval",
            frequency=30,
            start_date=datetime(2025, 1, 1, 10, 0, tzinfo=UTC),
            end_date=datetime(2025, 1, 1, 11, 0, tzinfo=UTC),
        )

        current_time = datetime(2025, 1, 1, 10, 30, tzinfo=UTC)
        interval = timedelta(hours=1)
        takings = find_next_takings([schedule], interval, test_config, current_time)
        assert len(takings) == 2  # Two takings at 10:30 and 11:00
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 10, 30, tzinfo=UTC)
        assert takings[1]["next_taking_time"] == datetime(2025, 1, 1, 11, 0, tzinfo=UTC)

    def test_without_schedules(self, test_config: Settings) -> None:
        current_time = datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
        interval = timedelta(hours=1)
        takings = find_next_takings([], interval, test_config, current_time)
        assert len(takings) == 0

    def test_schedule_at_night_time(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test schedule that takes place at night
        schedule = schedule_factory(
            medicine_name="Test Schedule At Night Time",
            frequency=15,
            start_date=datetime(2025, 1, 1, 23, 0, tzinfo=UTC),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 22, 30, tzinfo=UTC)
        interval = timedelta(hours=3)
        takings = find_next_takings([schedule], interval, test_config, current_time)
        assert len(takings) == 0

        schedule.end_date = datetime(2025, 1, 1, 5, 0, tzinfo=UTC)
        takings = find_next_takings([schedule], interval, test_config, current_time)
        assert len(takings) == 0

    def test_checking_before_night_time(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test checking takings before night
        schedule = schedule_factory(
            medicine_name="Test Checking Before Night Time",
            frequency=15,
            start_date=datetime(2025, 1, 1, 21, 0, tzinfo=UTC),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 21, 30, tzinfo=UTC)
        interval = timedelta(hours=1)
        takings = find_next_takings([schedule], interval, test_config, current_time)

        # Should include takings at 21:30, 21:45, 22:00
        assert len(takings) == 3
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 21, 30, tzinfo=UTC)
        assert takings[1]["next_taking_time"] == datetime(2025, 1, 1, 21, 45, tzinfo=UTC)
        assert takings[2]["next_taking_time"] == datetime(2025, 1, 1, 22, 0, tzinfo=UTC)

    def test_checking_before_morning_time(
        self, schedule_factory: Callable[..., Schedules], test_config: Settings
    ) -> None:
        # Test checking takings before morning time
        schedule = schedule_factory(
            medicine_name="Test Checking Before Morning Time",
            frequency=15,
            start_date=datetime(2025, 1, 1, 7, 0, tzinfo=UTC),
            end_date=None,
        )

        current_time = datetime(2025, 1, 1, 7, 30, tzinfo=UTC)  # 7:30
        interval = timedelta(hours=1)
        takings = find_next_takings([schedule], interval, test_config, current_time)

        # Should include takings at 8:00, 8:15, 8:30
        assert len(takings) == 3
        assert takings[0]["next_taking_time"] == datetime(2025, 1, 1, 8, 0, tzinfo=UTC)
        assert takings[1]["next_taking_time"] == datetime(2025, 1, 1, 8, 15, tzinfo=UTC)
        assert takings[2]["next_taking_time"] == datetime(2025, 1, 1, 8, 30, tzinfo=UTC)
