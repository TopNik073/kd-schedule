from datetime import UTC, datetime, timedelta
from typing import Any

from google.protobuf.timestamp_pb2 import Timestamp


def convert_from_timestamp(request: Any, target: str) -> datetime | None:
    """Convert Protobuf Timestamp to datetime"""
    if hasattr(request, target):
        timestamp = getattr(request, target)
        return datetime.fromtimestamp(timestamp.seconds, tz=UTC)
    return None


def convert_from_duration(request: Any, target: str) -> timedelta | None:
    """Convert Protobuf Duration to timedelta"""
    if hasattr(request, target):
        duration = getattr(request, target)
        return timedelta(seconds=duration.seconds)

    return None


def convert_to_timestamp(datetime: datetime) -> Timestamp:
    timestamp = Timestamp()
    timestamp.FromDatetime(datetime)
    return timestamp
