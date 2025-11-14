"""
Itinerary recommendation API 테스트
"""
from typing import Any, Dict

from fastapi.testclient import TestClient

import backend.main as main_module
from backend.main import app


def test_itinerary_endpoint_returns_plans(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    class DummyRetriever:
        def __init__(self, db_url: str, **_):
            self.db_url = db_url

        def close(self):
            return None

    class DummyPlanner:
        def __init__(self, retriever):
            self.retriever = retriever

        def recommend(self, request):
            return {
                "itineraries": [
                    {
                        "title": "서울 2일 추천 #1",
                        "summary": "샘플",
                        "days": [
                            {
                                "day": 1,
                                "segments": [
                                    {
                                        "place_name": "명동",
                                        "description": "쇼핑",
                                    }
                                ],
                            }
                        ],
                        "highlights": ["명동"],
                        "metadata": {"region": "서울"},
                    }
                ],
                "metadata": {"generated_count": 1, "region": "서울"},
            }

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "ItineraryPlanner", lambda retriever: DummyPlanner(retriever))
    monkeypatch.setattr(main_module, "init_cache_from_env", lambda: None)

    with TestClient(app) as client:
        response = client.post(
            "/recommend/itinerary",
            json={
                "region": "서울",
                "domains": ["food", "stay"],
                "duration_days": 2,
                "themes": ["인스타"],
                "transport_mode": "public",
            },
        )

    assert response.status_code == 200
    data: Dict[str, Any] = response.json()
    assert len(data["itineraries"]) == 1
    assert data["itineraries"][0]["days"][0]["segments"][0]["place_name"] == "명동"
