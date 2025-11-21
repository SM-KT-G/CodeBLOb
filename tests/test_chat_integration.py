"""통합 채팅 API 테스트 (세션/저장 제거 후 간단 검증)"""
import pytest
from fastapi.testclient import TestClient

import backend.main as main_module
from backend.main import app


@pytest.fixture(autouse=True)
def _patch_dependencies(monkeypatch):
    """lifespan 초기화 시 필요한 의존성을 더미로 대체"""
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    class DummyRetriever:
        def __init__(self, db_url: str, **_):
            self.db_url = db_url

        def close(self):
            return None

    class DummyPlanner:
        def __init__(self, retriever, **_):
            self.retriever = retriever

    class DummyHandler:
        def __init__(self):
            self.response = {"chat_completion_id": "default", "message": "default"}

        async def initialize(self):
            return None

        async def close(self):
            return None

        async def handle_chat(self, request):
            return self.response

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "ItineraryPlanner", lambda retriever, **_: DummyPlanner(retriever))
    monkeypatch.setattr(main_module, "UnifiedChatHandler", lambda **_: DummyHandler())


def test_chat_endpoint_general_conversation():
    """일반 대화: message와 chat_completion_id만 확인"""
    with TestClient(app) as client:
        app.state.unified_chat_handler.response = {
            "chat_completion_id": "chatcmpl-test1",
            "message": "안녕하세요",
        }
        resp = client.post("/chat", json={"text": "こんにちは"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["chat_completion_id"] == "chatcmpl-test1"
        assert data["message"] == "안녕하세요"


def test_chat_endpoint_search_places():
    """검색: places 포함 가능하지만 response_type 없음"""
    with TestClient(app) as client:
        app.state.unified_chat_handler.response = {
            "chat_completion_id": "chatcmpl-search",
            "message": "1件の場所が見つかりました。",
            "places": [{"name": "명동 교자", "description": "칼국수", "area": "서울", "document_id": "DOC1"}],
        }
        resp = client.post("/chat", json={"text": "서울 맛집"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["chat_completion_id"] == "chatcmpl-search"
        assert data["places"][0]["name"] == "명동 교자"


def test_chat_endpoint_invalid_request():
    """잘못된 요청: text 없으면 422"""
    with TestClient(app) as client:
        resp = client.post("/chat", json={})
        assert resp.status_code == 422
