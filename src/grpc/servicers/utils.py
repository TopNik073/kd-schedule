from datetime import datetime, timedelta, timezone
from google.protobuf.timestamp_pb2 import Timestamp

def convert_from_timestamp(request, target: str) -> datetime:
    """Convert Protobuf Timestamp to datetime"""
    if hasattr(request, target):
        timestamp = getattr(request, target)
        return datetime.fromtimestamp(timestamp.seconds, tz=timezone.utc)
    return None


def convert_from_duration(request, target: str) -> timedelta:
    """Convert Protobuf Duration to timedelta"""
    if hasattr(request, target):
        duration = getattr(request, target)
        return timedelta(seconds=duration.seconds)

    return None

def convert_to_timestamp(datetime: datetime) -> Timestamp:
    timestamp = Timestamp()
    timestamp.FromDatetime(datetime)
    return timestamp
