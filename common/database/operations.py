import logging

from . import connection
import common.model as model


class DatabaseOperator:
    def __init__(
        self,
        connection: connection.DatabaseConnection,
    ):
        self.connection = connection
        self.logger = logging.getLogger(__name__)
        return

    def insert_config(
        self,
        cfg: model.Config,
    ):
        # insert systems
        for system in cfg.systems:
            # delete system and relating entities
            if self.connection.select_system(system_id=system.id):
                self.logger.debug(f'{system.id=} present, deleting')
                # find all components refering to system
                if components := self.connection.select_component_from_system_id(system_id=system.id):
                    # delete each component and its metrics
                    for c in components:
                        self.logger.debug(f'deleting comments with {c.id=}')
                        self.connection.delete_comment_from_component_id(component_id=c.id)

                        self.logger.debug(f'deleting results with {c.id=}')
                        self.connection.delete_result_from_component_id(component_id=c.id)

                        self.logger.debug(f'deleting metrics with {c.id=}')
                        self.connection.delete_metric_by_component_id(component_id=c.id)

                        self.logger.debug(f'{c.id=} present, deleting')
                        self.connection.delete_component(component_id=c.id)

                # finally delete system
                self.connection.delete_system(system_id=system.id)

            self.connection.insert_system(system=system)

        # insert components
        for c in cfg.components:
            # delete component and metricsif id taken
            if self.connection.select_component(component_id=c.id):
                self.connection.delete_metric_by_component_id(component_id=c.id)
                self.connection.delete_component(component_id=c.id)
            # insert component
            self.connection.insert_component(component=c)

            # insert metrics
            for m in c.metrics:
                self.connection.insert_metric(metric=m, component_id=c.id,)

    def insert_result(
        self,
        res: model.Result,
    ):
        self.connection.insert_result(res=res)

    def insert_comment(
        self,
        comment: model.Comment,
    ):
        self.connection.insert_comment(comment=comment)


    def select_all_components(
        self,
    ):
        return self.connection.select_all_components()

    def select_all_systems(
        self,
    ):
        return self.connection.select_all_systems()

    def select_all_results(
        self,
    ):
        return self.connection.select_all_results()

    def select_all_comments(
        self,
    ):
        return self.connection.select_all_comments()

    def delete_outdated_results(
        self,
        component_id: str,
        metric_id: str,
        delete_after: model.TimeDetail,
    ):
        self.connection.delete_outdated_results(delete_after.as_interval())

    def update_comment(
        self,
        old: model.Comment,
        new: model.Comment,
    ):
        self.connection.delete_comment(
            metric_id=old.metricId,
            component_id=old.componentId,
            timestamp=old.timestamp,
        )
        self.connection.insert_comment(comment=new)

    def delete_comment(
        self,
        component_id: str,
        metric_id: str,
        timestamp: str,
    ):
        self.connection.delete_comment(
            metric_id=metric_id,
            component_id=component_id,
            timestamp=timestamp,
        )

    def select_comment(
        self,
        component_id: str,
        metric_id: str,
        timestamp: str,
    ):
        return self.connection.select_comment(
            component_id=component_id,
            metric_id=metric_id,
            timestamp=timestamp,
        )

    def select_metric(
        self,
        component_id: str,
        metric_id: str,
    ) -> model.Metric:
        return self.connection.select_metric(
            component_id=component_id,
            metric_id=metric_id,
        )

    def select_component(
        self,
        component_id: str,
    ):
        return self.connection.select_component(component_id=component_id)

    def select_metric(
        self,
        component_id: str,
        metric_id: str,
    ) -> model.Metric:
        return self.connection.select_metric(
            component_id=component_id,
            metric_id=metric_id,
        )
