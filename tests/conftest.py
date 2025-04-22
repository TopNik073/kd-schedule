import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

# from src.grpc.server import GRPCServer

from tests.models import UserTest, MedicineTest

# TODO: fix clossing connections for db after tests (appears when grpc server is started with this fixture)
# @pytest.fixture(scope="function", autouse=True)
# async def start_grpc_server():
#     server = GRPCServer(50051)
#     await server.start()
#     print("GRPC Server started")
#     yield server
#     print("GRPC Server stopped")
#     await server.stop()


@pytest.fixture(scope="session")
def grpc_context():
    return AsyncMock()


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
