from datetime import datetime, timedelta

import pytest

from src.grpc.server import GRPCServer
from tests.models import MedicineTest, UserTest


@pytest.fixture(scope="session", autouse=True)
async def start_grpc_server():
    server = GRPCServer(50051)
    await server.start()
    yield server
    await server.stop()


@pytest.fixture(scope="module")
def get_test_user():
    return UserTest(name=" E2ETest User", medicine_policy=12345)


@pytest.fixture(scope="module")
def get_test_medicine():
    return MedicineTest(
        medicine_name="E2E Test Medicine",
        frequency=60,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7),
        duration=timedelta(days=7),
    )
