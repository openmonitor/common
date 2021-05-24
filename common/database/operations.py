import logging

from . import connection
import common.model as model


class DatabaseOperations:
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
                        self.connection.delete_metric_by_component_id(component_id=c.id)
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
