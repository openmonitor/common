import dataclasses
import logging
import os
import typing

import psycopg2
import psycopg2.extras

try:
    import common.model as model
except ModuleNotFoundError:
    print('common package not in python path or dependencies not installed')


logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(
        self,
        connection,
    ):
        self.connection = connection
        return

    def kill(self):
        logger.info('killing database connection')
        self.connection.close()

    def _execute(
        self,
        statement: str,
        values: tuple,
        print_exception: bool = True,
    ):
        cur = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            logger.debug(f'{statement=}')
            logger.debug(f'{values=}')
            cur.execute(statement, values)
        except psycopg2.Error as e:
            if print_exception:
                logger.error(e)
            cur.execute("rollback")

        self.connection.commit()
        return cur

    def insert_system(
        self,
        system: model.System,
    ):
        statement = "INSERT INTO System " \
                    "VALUES (%s, %s, %s)"

        values = (dataclasses.astuple(system))

        self._execute(
            statement=statement,
            values=values,
        )

    def insert_metric(
        self,
        metric: model.Metric,
        component_id: str
    ):
        statement = "INSERT INTO Metric " \
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        values = (
            metric.id,
            component_id,
            metric.endpoint,
            metric.frequency.as_string(),
            metric.expectedTime.as_string(),
            metric.timeout.as_string(),
            metric.deleteAfter.as_string(),
            metric.authToken,
            metric.baseUrl,
        )

        self._execute(
            statement=statement,
            values=values,
        )

    def insert_component(
        self,
        component: model.Component,
    ):
        statement = "INSERT INTO Component " \
                    "VALUES (%s, %s, %s, %s, %s, %s)"

        values = (
            component.id,
            component.name,
            component.baseUrl,
            component.systemId,
            component.ref,
            component.authToken,
        )

        self._execute(
            statement=statement,
            values=values,
        )

    def select_system(
        self,
        system_id: str,
    ):
        statement = "SELECT * FROM system " \
                    "WHERE id = %s"
        values = (system_id,)

        cur = self._execute(
            statement=statement,
            values=values,
        )

        try:
            res = cur.fetchone()[0]
        except TypeError:
            return None
        return model.System(
            id=res[0],
            name=res[1],
            ref=res[2],
        )

    def select_component(
        self,
        component_id: str,
    ):
        statement = "SELECT * FROM component " \
                    "WHERE id = %s"
        values = (component_id,)

        cur = self._execute(
            statement=statement,
            values=values,
        )

        try:
            res = cur.fetchone()[0]
        except TypeError:
            return None

        model.Component(
            id=res[0],
            name=res[1],
            base=res[2],
            sys=res[3],
            ref=res[4],
            auth=res[5],
            metrics=self.select_metrics_from_component(component_id=component_id),
        )

    def select_component_from_system_id(
        self,
        system_id: str,
    ) -> typing.List[model.Component]:
        statement = "SELECT * FROM component " \
                    "WHERE system = %s"
        values = (system_id,)

        cur = self._execute(
            statement=statement,
            values=values,
        )

        try:
            res = cur.fetchall()
        except TypeError:
            return None

        if not res:
            return None

        components: typing.List[model.Component] = []
        for c in res:
            components.append(model.Component(
                id=c[0],
                name=c[1],
                baseUrl=c[2],
                systemId=c[3],
                ref=c[4],
                authToken=c[5],
                metrics=self.select_metrics_from_component(component_id=c[0]),
            ))
        return components

    def select_metrics_from_component(
        self,
        component_id: str,
    ) -> typing.List[model.Metric]:
        statement = "SELECT * FROM metric " \
                    "WHERE ComponentId = %s"

        values = (component_id,)

        cur = self._execute(
            statement=statement,
            values=values,
        )

        try:
            res = cur.fetchall()
        except TypeError:
            return None

        metrics: typing.List[model.Metrics] = []

        if not res:
            return None

        for m in res:
            metrics.append(model.Metric(
                id=m[0],
                endpoint=m[2],
                frequency=m[3],
                expectedTime=m[4],
                timeout=m[5],
                deleteAfter=m[6],
                authToken=m[7],
                baseUrl=m[8],
            ))

        return metrics

    def delete_system(
        self,
        system_id: str,
    ):
        statement = "DELETE FROM system " \
                    "WHERE id = %s"

        values = (system_id,)

        self._execute(
            statement=statement,
            values=values,
        )

    def delete_metric_by_component_id(
        self,
        component_id: str,
    ):
        statement = "DELETE FROM metric " \
                    "WHERE ComponentId = %s"

        values = (component_id,)

        self._execute(
            statement=statement,
            values=values,
        )

    def delete_component(
        self,
        component_id: str,
    ):
        statement = "DELETE FROM component " \
                    "WHERE Id = %s"

        values = (component_id,)

        self._execute(
            statement=statement,
            values=values,
        )

    def insert_result(
        self,
        res: model.Result,
    ):
        statement = "INSERT INTO Result " \
                    "VALUES (%s, %s, %s, %s, %s, %s)"

        values = (dataclasses.astuple(res))

        self._execute(
            statement=statement,
            values=values,
        )
