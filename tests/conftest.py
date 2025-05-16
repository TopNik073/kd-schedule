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

dotenv_path = dotenv.find_dotenv()
if dotenv_path:
    dotenv.load_dotenv(dotenv_path)

DB_ORIGINAL_NAME = os.environ["DB_NAME"]


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
    os.environ["DB_NAME"] = "kd-schedule-test"

    if dotenv_path:
        dotenv.set_key(dotenv_path, "DB_NAME", "kd-schedule-test")
        dotenv.load_dotenv(dotenv_path, override=True)

    with get_db_cursor() as cur:
        cur.execute('DROP DATABASE IF EXISTS "kd-schedule-test"')
        cur.execute('CREATE DATABASE "kd-schedule-test"')

    command.upgrade(alembic_cfg, "head")


def pytest_unconfigure(config):
    """Clean up after tests."""
    if DB_ORIGINAL_NAME:
        os.environ["DB_NAME"] = DB_ORIGINAL_NAME
    else:
        os.environ.pop("DB_NAME", None)

    if dotenv_path and DB_ORIGINAL_NAME:
        dotenv.set_key(dotenv_path, "DB_NAME", DB_ORIGINAL_NAME)
        dotenv.load_dotenv(dotenv_path, override=True)


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
