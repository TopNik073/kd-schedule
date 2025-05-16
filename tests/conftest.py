from contextlib import contextmanager
from datetime import datetime, timedelta
import os
import dotenv

import psycopg2
import pytest

from alembic import command
from alembic.config import Config
from tests.models import MedicineTest, UserTest

alembic_cfg = Config("alembic.ini")

dotenv.load_dotenv()
DB_ORIGINAL_NAME = os.getenv("DB_NAME")


@contextmanager
def get_db_connection(dbname: str = "postgres"):
    """Get a database connection with specified database name."""
    conn = psycopg2.connect(
        dbname=dbname,
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
    )
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_db_cursor(dbname: str = "postgres"):
    """Get a database cursor with specified database name."""
    with get_db_connection(dbname) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            yield cur


def pytest_configure(config):
    """Configure test environment before any imports."""
    dotenv.set_key(dotenv.find_dotenv(), "DB_NAME", "kd-schedule-test")
    dotenv.load_dotenv(override=True)

    with get_db_cursor() as cur:
        cur.execute('DROP DATABASE IF EXISTS "kd-schedule-test"')
        cur.execute('CREATE DATABASE "kd-schedule-test"')

    command.upgrade(alembic_cfg, "head")


def pytest_unconfigure(config):
    """Clean up after tests."""
    dotenv.set_key(dotenv.find_dotenv(), "DB_NAME", DB_ORIGINAL_NAME)
    dotenv.load_dotenv(override=True)


@pytest.fixture(scope="module")
def get_test_user():
    return UserTest(name="E2ETest User", medicine_policy=12345)


@pytest.fixture(scope="module")
def get_test_medicine():
    return MedicineTest(
        medicine_name="E2E Test Medicine",
        frequency=30,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7),
        duration=timedelta(days=7),
    )
