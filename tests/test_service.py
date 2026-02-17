import pytest
import fakeredis
from app import create_app
from app.extensions import redis_client


@pytest.fixture
def app(monkeypatch):
    app = create_app()
    fake_redis = fakeredis.FakeStrictRedis(decode_responses=True)

    monkeypatch.setattr("app.extensions.redis_client", fake_redis)

    with app.app_context():
        yield app
