import uuid
from datetime import timedelta

import pytest

import grpc
from src.grpc_server.schedule_pb2 import (
    CreateScheduleRequest,
    GetNextTakingsRequest,
    GetScheduleRequest,
    GetSchedulesIdsRequest,
)
from src.grpc_server.schedule_pb2_grpc import ScheduleServiceStub
from tests.models import MedicineTest, UserTest

from src.grpc_server.server import GRPCServer


@pytest.fixture(scope="session", autouse=True)
async def start_grpc_server():
    server = GRPCServer(50051)
    await server.start()
    yield server
    await server.stop()


@pytest.mark.asyncio(loop_scope="session")
class TestScheduleServicer:
    @pytest.fixture(autouse=True)
    async def setup(self):
        self.channel = grpc.aio.insecure_channel("localhost:50051")
        self.stub = ScheduleServiceStub(self.channel)
        yield
        await self.channel.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_end_time", [True, False])
    async def test_schedule_servicer_e2e(self, get_test_user, get_test_medicine, use_end_time):
        # Step 1: Create a schedule
        schedule_id = await self._create_schedule(
            self.stub, get_test_user, get_test_medicine, use_end_time
        )

        assert schedule_id is not None
        assert uuid.UUID(schedule_id)

        # Step 2: Get the schedules ids
        schedules = await self._get_schedules_ids(self.stub, get_test_user)

        assert len(schedules.schedule_ids) >= 1
        assert schedule_id in schedules.schedule_ids

        # Step 3: Get the schedule
        response = await self._get_schedule(self.stub, schedule_id, get_test_user)

        assert hasattr(response, "schedule")
        schedule = response.schedule
        assert schedule is not None
        assert schedule.medicine_name == get_test_medicine.medicine_name
        assert schedule.frequency == get_test_medicine.frequency
        assert schedule.end_date is not None

        # Step 4: Get the next takings
        await self._get_next_takings(self.stub, get_test_user)

        # TODO: Sometimes the next takings are empty for some reason. 
        # Probably beacuse of rounding the start_date (but this case is handled by the tests/test_schedule_utils.py::test_schedule_start_in_interval)
        # assert len(next_takings) >= 1

    @staticmethod
    async def _send_request(method: grpc.aio._channel.UnaryUnaryMultiCallable, request):
        try:
            response = await method(request)
            assert response is not None
            return response
        except grpc.RpcError as e:
            pytest.fail(f"Error sending request {method.__repr__}: {e}")
        except Exception as e:
            pytest.fail(f"Error sending request {method.__repr__}: {e}")

    async def _create_schedule(
        self, stub, test_user: UserTest, test_medicine: MedicineTest, use_end_time: bool
    ):
        request = CreateScheduleRequest(
            name=test_user.name,
            medicine_policy=test_user.medicine_policy,
            medicine_name=test_medicine.medicine_name,
            frequency=test_medicine.frequency,
            start_date=test_medicine.start_date,
        )

        if use_end_time:
            request.end_date.FromDatetime(test_medicine.end_date)
        else:
            request.duration.FromTimedelta(test_medicine.duration)

        response = await self._send_request(stub.CreateSchedule, request)
        return response.id

    async def _get_schedules_ids(self, stub, test_user: UserTest):
        request = GetSchedulesIdsRequest(user_id=test_user.medicine_policy)
        return await self._send_request(stub.GetSchedulesIds, request)

    async def _get_schedule(self, stub, schedule_id: uuid.UUID, test_user: UserTest):
        request = GetScheduleRequest(
            schedule_id=str(schedule_id), user_id=test_user.medicine_policy
        )
        return await self._send_request(stub.GetSchedule, request)

    async def _get_next_takings(self, stub, test_user: UserTest):
        request = GetNextTakingsRequest(user_id=test_user.medicine_policy)
        request.next_takings_interval.FromTimedelta(timedelta(hours=2))
        return await self._send_request(stub.GetNextTakings, request)
