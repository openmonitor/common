import pytest

import psycopg2
from pytest_mock import mocker

try:
    import common.database.connection as connection
    import common.database.factory as factory
    import common.database.operations as ops
    import common.model as model
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed')
import monitor.config.factory as fac


def test_db_conn():
    fac = factory.DatabaseConnectionFactory()
    conn = fac.make_connection()


def test_db_conn_fail():
    with pytest.raises(psycopg2.OperationalError):
        fac = factory.DatabaseConnectionFactory(
            database=None,
            user=None,
            password=None,
            host=None,
            port=None,
        )
        conn = fac.make_connection()


def test_db_conn_kill():
    fac = factory.DatabaseConnectionFactory()
    conn = fac.make_connection()
    conn.kill()
