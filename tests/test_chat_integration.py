"""통합 채팅 API 테스트 (세션/저장 제거 후 간단 검증)"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app


def test_chat_endpoint_general_conversation():
    """일반 대화: message와 chat_completion_id만 확인"""
    async def mock_handle_chat(request):
        return {"chat_completion_id": "chatcmpl-test1", "message": "안녕하세요"}

    with patch.object(app.state, "unified_chat_handler") as mock_handler:
        mock_handler.handle_chat = mock_handle_chat
        with TestClient(app) as client:
            resp = client.post("/chat", json={"text": "こんにちは"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["chat_completion_id"] == "chatcmpl-test1"
            assert data["message"] == "안녕하세요"


def test_chat_endpoint_search_places():
    """검색: places 포함 가능하지만 response_type 없음"""
    async def mock_handle_chat(request):
        return {
            "chat_completion_id": "chatcmpl-search",
            "message": "1件の場所が見つかりました。",
            "places": [{"name": "명동 교자", "description": "칼국수", "area": "서울", "document_id": "DOC1"}],
        }

    with patch.object(app.state, "unified_chat_handler") as mock_handler:
        mock_handler.handle_chat = mock_handle_chat
        with TestClient(app) as client:
            resp = client.post("/chat", json={"text": "서울 맛집"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["chat_completion_id"] == "chatcmpl-search"
            assert data["places"][0]["name"] == "명동 교자"


def test_chat_endpoint_create_itinerary():
    """일정 생성: itinerary 구조 확인"""
    async def mock_handle_chat(request):
        return {
            "chat_completion_id": "chatcmpl-itin",
            "message": "일정을 준비했어요",
            "itinerary": {
                "title": "서울 2일 여행",
                "summary": "맛집과 문화",
                "days": [
                    {"day": 1, "segments": [{"time": "오전", "place_name": "경복궁", "description": "관람", "place_id": "DOC101"}]}
                ],
                "highlights": ["경복궁"],
            },
        }

    with patch.object(app.state, "unified_chat_handler") as mock_handler:
        mock_handler.handle_chat = mock_handle_chat
        with TestClient(app) as client:
            resp = client.post("/chat", json={"text": "서울 2일 플랜"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["chat_completion_id"] == "chatcmpl-itin"
            assert data["itinerary"]["title"] == "서울 2일 여행"


def test_chat_endpoint_invalid_request():
    """잘못된 요청: text 없으면 422"""
    with TestClient(app) as client:
        resp = client.post("/chat", json={})
        assert resp.status_code == 422
