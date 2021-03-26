import dataclasses
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


def _build_delete_outdated_component_frames_interval(
    delete_after: str,
) -> str:
    interval_translation = {
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
    }
    interval = delete_after[:-1] + ' ' + delete_after[-1]
    for k, v in interval_translation.items():
        interval = interval.replace(k, v)
    return interval


def delete_outdated_component_frames(
    cc: model.ComponentConfig,
    conn,
):
    interval = _build_delete_outdated_component_frames_interval(
        delete_after=cc.deleteAfter,
    )
    stmt = 'DELETE FROM componentframe WHERE timestamp < NOW() - INTERVAL %s'

    _execute(
        conn=conn,
        statement=stmt,
        values=(interval, ),
    )

    conn.commit()


def insert_component(
    conn,
    component: model.Component,
):
    statement = "INSERT INTO Component " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

    values = (dataclasses.astuple(component))

    _execute(
        conn=conn,
        statement=statement,
        values=values,
        print_exception=True,
    )

    conn.commit()


def insert_system(
    conn,
    system: model.System,
):
    statement = "INSERT INTO System " \
                "VALUES (%s, %s, %s)"

    values = (dataclasses.astuple(system))

    _execute(
        conn=conn,
        statement=statement,
        values=values,
        print_exception=True,
    )

    conn.commit()


def select_component(
    conn,
    component: str,
) -> model.Component:

    statement = "SELECT * FROM component " \
                "WHERE component = %s"
    values = (component,)

    cur = _execute(
        conn=conn,
        statement=statement,
        values=values,
    )

    conn.commit()
    res = cur.fetchone()[0]
    return model.Component(
        component=res[0],
        name=res[1],
        baseUrl=res[2],
        statusEndpoint=res[3],
        system=res[4],
        ref=res[5],
        expectedTime=res[6],
        timeout=res[7],
    )


def update_component(
    conn,
    component: model.Component,
):
    statement = "UPDATE component SET name = %s, baseUrl = %s, statusEndpoint = %s, system = %s, " \
                "ref = %s, expectedTime = %s, timeout = %s WHERE component = %s"

    values = (component.name, component.baseUrl, component.baseUrl, component.system, component.ref,
              component.expectedTime, component.timeout, component.component)

    _execute(
        conn=conn,
        statement=statement,
        values=values,
        print_exception=True,
    )

    conn.commit()


def select_system(
    conn,
    system: str,
) -> model.System:

    statement = "SELECT * FROM system " \
                "WHERE system = %s"
    values = (system,)

    cur = _execute(
        conn=conn,
        statement=statement,
        values=values,
    )

    conn.commit()
    res = cur.fetchone()[0]
    return model.System(
        system=res[0],
        name=res[1],
        ref=res[2],
    )


def update_system(
    conn,
    system: model.System,
):
    statement = "UPDATE system SET name = %s, ref = %s WHERE system = %s"

    values = (system.name, system.ref, system.system)

    _execute(
        conn=conn,
        statement=statement,
        values=values,
        print_exception=True,
    )

    conn.commit()


def select_components(
    conn,
):
    statement = "SELECT * FROM component"

    cur = _execute(
        conn=conn,
        statement=statement,
        values=(),
    )

    conn.commit()
    return cur.fetchall()


def select_systems(
    conn,
):
    statement = "SELECT * FROM system"

    cur = _execute(
        conn=conn,
        statement=statement,
        values=(),
    )

    conn.commit()
    return cur.fetchall()


def select_component_frames(
    conn,
):
    statement = "SELECT * FROM componentframe"

    cur = _execute(
        conn=conn,
        statement=statement,
        values=(),
    )

    conn.commit()
    return cur.fetchall()
