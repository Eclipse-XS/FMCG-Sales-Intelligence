import pytest
from psycopg.conninfo import conninfo_to_dict

from fmcg_sales_intelligence.pipelines.persistence import connection
from fmcg_sales_intelligence.product.analytics.publish_scientific_results import create_engine_from_env


def test_database_requires_explicit_credentials(monkeypatch):
    monkeypatch.setattr(connection, "load_env", lambda: None)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="POSTGRES_PASSWORD"):
        connection.dsn()
    with pytest.raises(ValueError, match="POSTGRES_PASSWORD"):
        create_engine_from_env()


def test_credentials_are_escaped_and_connection_wait_is_bounded(monkeypatch):
    monkeypatch.setattr(connection, "load_env", lambda: None)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    password = "test password'@/value"
    monkeypatch.setenv("POSTGRES_PASSWORD", password)
    assert conninfo_to_dict(connection.dsn())["password"] == password
    assert create_engine_from_env().url.password == password
    called = {}
    def fake_connect(dsn, **kwargs):
        called.update(kwargs)
    monkeypatch.setattr(connection.psycopg, "connect", fake_connect)
    connection.connect()
    assert called["connect_timeout"] == 5
