import logging
import os

import psycopg2
import psycopg2.extras

from . import connection


logger = logging.getLogger(__name__)


class DatabaseConnectionFactory:
    def __init__(
        self,
        database=os.getenv('DB'),
        user=os.getenv('DBUSER'),
        password=os.getenv('DBPASSWD'),
        host=os.getenv('DBHOST'),
        port=int(os.getenv('DBPORT')),
    ):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        return

    def make_connection(self):
        logger.debug('making database connection')
        return connection.DatabaseConnection(
            psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
        ))
