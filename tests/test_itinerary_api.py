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
    monkeypatch.setattr(main_module, "ItineraryPlanner", lambda retriever, **_: DummyPlanner(retriever))

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


def test_itinerary_accepts_japanese_input(monkeypatch):
    """일본어 입력도 받아들이고 처리하는지 테스트"""
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    class DummyRetriever:
        def __init__(self, db_url: str, **_):
            self.db_url = db_url

        def search_with_expansion(self, query, **kwargs):
            # 일본어 쿼리가 들어와도 정상 처리
            return []

        def search(self, query, **kwargs):
            return []

        def close(self):
            return None

    class DummyPlanner:
        def __init__(self, retriever):
            self.retriever = retriever

        def recommend(self, request):
            # 일본어 region을 받아서 일본어로 응답
            return {
                "itineraries": [
                    {
                        "title": f"{request.region} 2日おすすめ #1",
                        "summary": "サンプル",
                        "days": [
                            {
                                "day": 1,
                                "segments": [
                                    {
                                        "place_name": "明洞",
                                        "description": "ショッピング",
                                    }
                                ],
                            }
                        ],
                        "highlights": ["明洞"],
                        "metadata": {"region": request.region},
                    }
                ],
                "metadata": {"generated_count": 1, "region": request.region},
            }

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "ItineraryPlanner", lambda retriever, **_: DummyPlanner(retriever))

    with TestClient(app) as client:
        response = client.post(
            "/recommend/itinerary",
            json={
                "region": "ソウル",  # 일본어로 "서울"
                "domains": ["food", "stay"],
                "duration_days": 2,
                "themes": ["インスタ映え"],  # 일본어 테마
                "transport_mode": "public",
            },
        )

    assert response.status_code == 200
    data: Dict[str, Any] = response.json()
    assert len(data["itineraries"]) == 1
    assert "ソウル" in data["itineraries"][0]["title"]
    assert data["metadata"]["region"] == "ソウル"


def test_llm_prompt_should_be_in_japanese(monkeypatch):
    """LLM 프롬프트가 일본어로 작성되어야 함"""
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    from backend.itinerary import ItineraryPlanner
    from backend.schemas import ItineraryRecommendationRequest, DomainEnum

    class DummyRetriever:
        def search_with_expansion(self, **kwargs):
            from langchain.schema import Document
            return [
                Document(
                    page_content="明洞でショッピング",
                    metadata={
                        "document_id": "J_SHOP_001",
                        "place_name": "明洞",
                        "domain": "shop",
                    }
                )
            ]

    planner = ItineraryPlanner(DummyRetriever())
    
    request = ItineraryRecommendationRequest(
        region="ソウル",
        domains=[DomainEnum.FOOD],
        duration_days=2,
        themes=["グルメ"],
    )
    
    # _build_prompt 메서드가 일본어 프롬프트를 생성하는지 확인
    from langchain.schema import Document
    candidates = planner._format_candidates([
        Document(
            page_content="明洞でショッピング",
            metadata={"document_id": "J_SHOP_001", "place_name": "明洞", "domain": "shop"}
        )
    ])
    prompt = planner._build_prompt(request, candidates)
    
    # 프롬프트에 일본어 키워드가 포함되어야 함
    assert "地域" in prompt or "ドメイン" in prompt or "日程" in prompt
    assert "ソウル" in prompt
    assert "グルメ" in prompt


def test_recommend_alias_returns_plans(monkeypatch):
    """신규 /recommend 엔드포인트가 기존 일정 응답을 반환한다."""
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
                        "title": "서울 1일 추천",
                        "summary": "샘플",
                        "days": [{"day": 1, "segments": []}],
                        "highlights": [],
                        "metadata": {"region": "서울"},
                    }
                ],
                "metadata": {"generated_count": 1, "region": "서울"},
            }

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "ItineraryPlanner", lambda retriever, **_: DummyPlanner(retriever))

    with TestClient(app) as client:
        resp = client.post(
            "/recommend",
            json={
                "region": "서울",
                "domains": ["food"],
                "duration_days": 1,
            },
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["metadata"]["region"] == "서울"
    assert data["itineraries"][0]["title"] == "서울 1일 추천"
