import dataclasses
import logging
import os
import typing

import psycopg2
import psycopg2.extras

try:
    import common.model as model
    import common.util as commonutil
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

    def select_all_systems(self) -> typing.List[model.System]:
        statement = "SELECT * FROM system"

        cur = self._execute(
            statement=statement,
            values=(),
        )

        try:
            res = cur.fetchall()
        except TypeError:
            return None

        if not res:
            return None

        systems: typing.List[model.System] = []
        for s in res:
            systems.append(model.System(
                id=s[0],
                name=s[1],
                ref=s[2],
            ))
        return systems

    def select_all_components(self) -> typing.List[model.Component]:
        statement = "SELECT * FROM component"

        cur = self._execute(
            statement=statement,
            values=(),
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

    def select_all_results(self) -> typing.List[model.Result]:
        statement = "SELECT * FROM result"

        cur = self._execute(
            statement=statement,
            values=(),
        )

        try:
            res = cur.fetchall()
        except TypeError:
            return None

        if not res:
            return None

        results: typing.List[model.Result] = []
        for r in res:
            results.append(model.Result(
                metricId=r[0],
                componentId=r[1],
                value=r[2],
                timeout=r[3],
                timestamp=str(r[4]),
                responseTime=r[5],
            ))
        return results

    def select_all_comments(self) -> typing.List[model.Comment]:
        statement = "SELECT * FROM comment"

        cur = self._execute(
            statement=statement,
            values=(),
        )

        try:
            res = cur.fetchall()
        except TypeError:
            return None

        if not res:
            return None

        comments: typing.List[model.Comment] = []
        for c in res:
            comments.append(model.Comment(
                metricId=c[0],
                componentId=c[1],
                comment=c[2],
                timestamp=str(c[3]),
                startTimestamp=str(c[4]),
                endTimestamp=str(c[5]),
            ))

        return comments

    def select_comment(
        self,
        component_id: str,
        metric_id: str,
        timestamp: str,
    ) -> typing.Union[None, model.Comment]:
        statement = "SELECT * FROM comment " \
                    "WHERE metricId = %s AND componentId = %s AND timestamp = %s"
        values = (metric_id, component_id, timestamp)

        cur = self._execute(
            statement=statement,
            values=values,
        )

        if not (res := cur.fetchone()):
            return None

        return model.Comment(
            metricId=res[0],
            componentId=res[1],
            comment=res[2],
            timestamp=res[3],
            startTimestamp=res[4],
            endTimestamp=res[5],
        )

    def select_metric(
        self,
        component_id: str,
        metric_id: str,
    ) -> typing.Union[None, model.Metric]:
        statement = "SELECT * FROM metric " \
                    "WHERE id = %s AND componentId = %s"
        values = (metric_id, component_id)

        cur = self._execute(
            statement=statement,
            values=values,
        )

        if not (res := cur.fetchone()):
            return None

        return model.Metric(
            id=res[0],
            endpoint=res[2],
            frequency=commonutil.parse_time_str_to_timedetail(time_str=res[3]),
            expectedTime=commonutil.parse_time_str_to_timedetail(time_str=res[4]),
            timeout=commonutil.parse_time_str_to_timedetail(time_str=res[5]),
            deleteAfter=commonutil.parse_time_str_to_timedetail(time_str=res[6]),
            authToken=res[7],
            baseUrl=res[8],
        )

    def select_component(
        self,
        component_id: str,
    ) -> typing.Union[None, model.Component]:
        statement = "SELECT * FROM component " \
                    "WHERE id = %s"
        values = (component_id,)

        cur = self._execute(
            statement=statement,
            values=values,
        )

        if not (res := cur.fetchone()):
            return None

        return model.Component(
            id=res[0],
            name=res[1],
            baseUrl=res[2],
            systemId=res[3],
            ref=res[4],
            authToken=res[5],
            metrics=self.select_metrics_from_component(component_id=res[0]),
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
                frequency=commonutil.parse_time_str_to_timedetail(time_str=m[3]),
                expectedTime=commonutil.parse_time_str_to_timedetail(time_str=m[4]),
                timeout=commonutil.parse_time_str_to_timedetail(time_str=m[5]),
                deleteAfter=commonutil.parse_time_str_to_timedetail(time_str=m[6]),
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

    def delete_result_from_component_id(
        self,
        component_id: str,
    ):
        statement = "DELETE FROM result " \
                    "WHERE componentId = %s"

        values = (component_id,)

        self._execute(
            statement=statement,
            values=values,
        )

    def delete_comment_from_component_id(
        self,
        component_id: str,
    ):
        statement = "DELETE FROM comment " \
                    "WHERE componentId = %s"

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

    def delete_comment(
        self,
        component_id: str,
        metric_id: str,
        timestamp: str,
    ):
        statement = "DELETE FROM comment " \
                    "WHERE metricId = %s AND componentId = %s AND timestamp = %s"

        values = (metric_id, component_id, timestamp)

        self._execute(
            statement=statement,
            values=values,
        )

    def insert_result(
        self,
        res: model.Result,
    ):
        statement = "INSERT INTO result " \
                    "VALUES (%s, %s, %s, %s, %s, %s)"

        values = (dataclasses.astuple(res))

        self._execute(
            statement=statement,
            values=values,
        )

    def insert_comment(
        self,
        comment: model.Comment,
    ):
        statement = "INSERT INTO comment " \
                    "VALUES (%s, %s, %s, %s, %s, %s)"

        values = (dataclasses.astuple(comment))

        self._execute(
            statement=statement,
            values=values,
        )

    def delete_outdated_results(
        self,
        interval: str,
    ):
        stmt = 'DELETE FROM result WHERE timestamp < NOW() - INTERVAL %s'

        values = (interval,)

        self._execute(
            statement=stmt,
            values=values,
        )
