import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from datetime import datetime, timedelta

from google.protobuf.timestamp_pb2 import Timestamp

import grpc
from src.grpc_server.schedule_pb2 import CreateScheduleRequest
from src.grpc_server.schedule_pb2_grpc import ScheduleServiceStub


async def create_schedule():
    channel = grpc.aio.insecure_channel("localhost:50051")
    stub = ScheduleServiceStub(channel)

    try:
        request = CreateScheduleRequest(
            name="Test User", medicine_policy=12345, medicine_name="Test Medicine", frequency=60
        )

        start_time = Timestamp()
        now = datetime.now()
        start_time.FromDatetime(now)
        request.start_date.CopyFrom(start_time)

        end_time = Timestamp()
        end_time.FromDatetime(now + timedelta(days=7))
        request.end_date.CopyFrom(end_time)

        # duration = Duration()
        # duration.FromTimedelta(timedelta(days=7))
        # request.duration.CopyFrom(duration)

        print("Sending request to create schedule...")
        print(
            f"Data: name={request.name}, "
            f"medicine={request.medicine_name}, "
            f"frequency={request.frequency} mins"
        )

        response = await stub.CreateSchedule(request)

        print("Schedule created successfully")
        print(f"schedule UUID: {response.id}")
        try:
            uuid.UUID(response.id)
            print("UUID is valid")
        except ValueError:
            print("UUID is NOT valid")

        return response.id

    except grpc.RpcError as e:
        print(f"RPC error: {e.code()}: {e.details()}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await channel.close()
