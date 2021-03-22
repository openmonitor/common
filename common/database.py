import logging
import os

import psycopg2
import psycopg2.extras

import model


logger = logging.getLogger(__name__)


def get_connection(
    database=os.getenv('DB'),
    user=os.getenv('DBUSER'),
    password=os.getenv('DBPASSWD'),
    host=os.getenv('DBHOST'),
    port=int(os.getenv('DBPORT')),
):
    """
    Returns database connection, if not specified configuration is taken from environment.
    :param database:
    :param user:
    :param password:
    :param host:
    :param port:
    :return:
    """
    return psycopg2.connect(
        database=database,
        user=user,
        password=password,
        host=host,
        port=port,
    )


def kill_connection(
    conn,
):
    """
    Closes given connection.
    :param conn:
    :return:
    """
    try:
        conn.close()
    except psycopg2.Error:
        pass


def _execute(
    conn,
    statement: str,
    values: tuple,
    print_exception: bool = True,
):
    """
    Executes given prepared statement (with given values) on specified connection, therefore a cursor
    is created. In case of failure a rollback is executed and committed. Occurred error are printable,
    default is true.
    :param conn:
    :param statement:
    :param values:
    :param print_exception:
    :return:
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        logger.debug(f'{statement=}')
        logger.debug(f'{values=}')
        cur.execute(statement, values)
    except psycopg2.Error as e:
        if print_exception:
            print(e)
        cur.execute("rollback")
        conn.commit()
    return cur


def _set_timestamp(
    target,
):
    """
    Sets target's field "timestamp" to "now()" so if inserted to database the timestamp function
    from postgres is used.
    :param target:
    :return:
    """
    # necessary since we have to differentiate between timestamp on runtime and timestamp in database
    target.timestamp = 'now()'
    return target


def insert_component_frame(
    conn,
    component_frame: model.ComponentFrame,
):
    statement = "INSERT INTO ComponentFrame (component, timestamp, reachable, responseTime)" \
                "VALUES (%s, %s, %s, %s)"

    # exclude frame, it's incremented by database
    values = (
        component_frame.component,
        component_frame.timestamp,
        component_frame.reachable,
        component_frame.responseTime,
    )

    _execute(
        conn=conn,
        statement=statement,
        values=values,
        print_exception=True,
    )

    conn.commit()
