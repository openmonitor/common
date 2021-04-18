import dataclasses
import logging
import os
import typing

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
    statement = "INSERT INTO ComponentFrame (component, timestamp, reachable, responseTime, cpu)" \
                "VALUES (%s, %s, %s, %s, %s)"

    # exclude frame, it's incremented by database
    values = (
        component_frame.component,
        component_frame.timestamp,
        component_frame.reachable,
        component_frame.responseTime,
        component_frame.cpu,
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
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

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
) -> typing.Union[model.Component, None]:

    statement = "SELECT * FROM component " \
                "WHERE component = %s"
    values = (component,)

    cur = _execute(
        conn=conn,
        statement=statement,
        values=values,
    )

    conn.commit()
    res = cur.fetchone()
    logger.debug(f'{type(res)}')
    if isinstance(res, type(None)):
        return None
    else:
        return model.Component(
            component=res[0],
            name=res[1],
            baseUrl=res[2],
            statusEndpoint=res[3],
            system=res[4],
            ref=res[5],
            expectedTime=res[6],
            timeout=res[7],
            frequency=res[8],
            authToken=res[9],
        )


def update_component(
    conn,
    component: model.Component,
):
    statement = "UPDATE component SET name = %s, baseUrl = %s, statusEndpoint = %s, system = %s, " \
                "ref = %s, expectedTime = %s, timeout = %s, frequency = %s, authtoken = %s WHERE component = %s"

    values = (
        component.name,
        component.baseUrl,
        component.baseUrl,
        component.system,
        component.ref,
        component.expectedTime,
        component.timeout,
        component.frequency,
        component.authToken,
        component.component,
    )

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
) -> typing.Union[model.System, None]:

    statement = "SELECT * FROM system " \
                "WHERE system = %s"
    values = (system,)

    cur = _execute(
        conn=conn,
        statement=statement,
        values=values,
    )

    conn.commit()
    try:
        res = cur.fetchone()[0]
    except TypeError:
        return None
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
) -> typing.List[model.Component]:
    statement = "SELECT * FROM component"

    cur = _execute(
        conn=conn,
        statement=statement,
        values=(),
    )

    conn.commit()
    comps = cur.fetchall()
    comp_l: typing.List[model.Component] = []
    for c in comps:
        comp_l.append(model.Component(
            component=c[0],
            name=c[1],
            baseUrl=c[2],
            statusEndpoint=c[3],
            system=c[4],
            ref=c[5],
            expectedTime=c[6],
            timeout=c[7],
            frequency=c[8],
            authToken=c[9],
        ))
    return comp_l


def select_systems(
    conn,
) -> typing.List[model.System]:
    statement = "SELECT * FROM system"

    cur = _execute(
        conn=conn,
        statement=statement,
        values=(),
    )

    conn.commit()
    sys = cur.fetchall()
    sys_l: typing.List[model.System] = []
    for s in sys:
        sys_l.append(model.System(
            system=s[0],
            name=s[1],
            ref=s[2],
        ))
    return sys_l


def select_component_frames_with_component(
    conn,
    comp: model.Component,
) -> typing.List[model.ComponentFrame]:
    statement = "SELECT * FROM componentframe WHERE component = %s"

    cur = _execute(
        conn=conn,
        statement=statement,
        values=(comp.component,),
    )

    conn.commit()
    cfs = cur.fetchall()
    cf_l: typing.List[model.ComponentFrame] = []
    for cf in cfs:
        cf_l.append(model.ComponentFrame(
            component=cf[0],
            frame=cf[1],
            timestamp=str(cf[2]),
            reachable=cf[3],
            responseTime=cf[4],
            cpu=cf[5],
        ))
    return cf_l


def insert_framecomment(
    conn,
    fc: model.FrameComment,
):
    statement = "INSERT INTO FrameComment (component, startframe, endframe, commenttext) " \
                "VALUES (%s, %s, %s, %s)"

    logger.debug(f'{fc=}')
    values = (fc.component.component, fc.startFrame, fc.endFrame, fc.commentText)

    _execute(
        conn=conn,
        statement=statement,
        values=values,
        print_exception=True,
    )

    conn.commit()


def select_framecomments_for_component(
    conn,
    comp: model.Component,
) -> typing.List[model.FrameComment]:
    statement = "SELECT * FROM framecomment WHERE component = %s"

    cur = _execute(
        conn=conn,
        statement=statement,
        values=(comp.component,),
    )

    conn.commit()
    fcs = cur.fetchall()
    if not fcs:
        return None
    fc_l: typing.List[model.FrameComment] = []
    for fc in fcs:
        logger.debug(f'{fc=}')
        fc_l.append(model.FrameComment(
            component=comp,
            comment=fc[1],
            startFrame=fc[2],
            endFrame=fc[3],
            commentText=fc[4],
        ))
    return fc_l


def select_framecomment_for_component_and_comment(
    conn,
    comp: model.Component,
    comment: int
) -> typing.Union[model.FrameComment, None]:
    statement = "SELECT * FROM framecomment WHERE component = %s AND comment = %s"

    cur = _execute(
        conn=conn,
        statement=statement,
        values=(comp.component, comment),
    )

    conn.commit()
    fc = cur.fetchone()
    if not fc:
        return None
    return model.FrameComment(
        component=comp,
        comment=fc[1],
        startFrame=fc[2],
        endFrame=fc[3],
        commentText=fc[4],
    )


def update_framecomment(
    conn,
    comp: model.Component,
    comment: int,
    text: str,
):
    statement = "UPDATE framecomment SET commenttext = %s WHERE component = %s AND comment = %s"

    _execute(
        conn=conn,
        statement=statement,
        values=(text, comp.component, comment),
    )

    conn.commit()


def delete_framecomment(
    conn,
    comp: model.Component,
    comment: int,
):
    statement = "DELETE FROM framecomment WHERE component = %s AND comment = %s"

    _execute(
        conn=conn,
        statement=statement,
        values=(comp.component, comment),
    )

    conn.commit()
