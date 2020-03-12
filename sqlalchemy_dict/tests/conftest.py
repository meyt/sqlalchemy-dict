import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .db import DeclarativeBase


class DatabaseWrapper(object):
    db_url = "sqlite:///:memory:"
    connect_args = {}

    def __init__(self):
        self.engine = create_engine(
            self.db_url, connect_args=self.connect_args
        )
        self.session = Session(self.engine)

    def __enter__(self):
        DeclarativeBase.metadata.drop_all(self.engine)
        DeclarativeBase.metadata.create_all(self.engine)
        return self

    def __exit__(self, *args):
        self.session.close()
        self.session.get_bind().dispose()


class PostgresDatabaseWrapper(DatabaseWrapper):  # pragma: nocover
    db_name = "sqlalchemy_dict"
    db_url = "postgresql://postgres:postgres@localhost/%s" % db_name
    admin_db_url = "postgresql://postgres:postgres@localhost/postgres"
    connect_args = {"options": "-c timezone=Asia/Tehran"}

    def __init__(self):
        self.admin_engine = create_engine(self.admin_db_url)
        self.admin_connection = self.admin_engine.connect()
        self.admin_connection.execute("commit")
        if not self.database_exists():
            self.create_database()
        self.close_admin_database()
        super().__init__()

    def database_exists(self):
        r = self.admin_connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = '%s'" % self.db_name
        )
        try:
            ret = r.cursor.fetchall()
            return ret
        finally:
            r.cursor.close()

    def create_database(self):
        self.admin_connection.execute("CREATE DATABASE %s" % self.db_name)
        self.admin_connection.execute("commit")

    def drop_database(self):
        self.admin_connection.execute(
            "DROP DATABASE IF EXISTS %s" % self.db_name
        )
        self.admin_connection.execute("commit")

    def close_admin_database(self):
        self.admin_connection.close()
        self.admin_engine.dispose()


@pytest.fixture(scope="function")
def db():
    with DatabaseWrapper() as wrapper:
        yield wrapper


@pytest.fixture(scope="function")
def pgdb():
    with PostgresDatabaseWrapper() as wrapper:
        yield wrapper
