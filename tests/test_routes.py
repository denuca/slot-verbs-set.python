from app.redis_repo import SlotRepository
from app.extensions import redis_client


def test_spin_route(client, app):
    redis_client.hset(
        SlotRepository.KEY,
        "test",
        "A,A,A|Word1,Word2|easy"
    )

    response = client.post("/api/spin", json={"slots": 3})
    assert response.status_code == 200
