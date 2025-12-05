"""UnifiedChatHandler 동작 테스트"""
import json
import pytest

from backend.unified_chat import UnifiedChatHandler
from backend.schemas import ChatRequest


class _FakeToolCall:
    def __init__(self, name: str):
        self.function = type("Function", (), {"name": name, "arguments": json.dumps({})})


class _FakeMessage:
    def __init__(self, tool_name: str):
        self.tool_calls = [_FakeToolCall(tool_name)]
        self.content = None


class _FakeChatCompletions:
    def __init__(self, message):
        self._message = message

    def create(self, *_, **__):
        return type("Completion", (), {"choices": [type("Choice", (), {"message": self._message})], "id": "dummy"})


class _FakeChat:
    def __init__(self, message):
        self.completions = _FakeChatCompletions(message)


class _FakeClient:
    def __init__(self, message):
        self.chat = _FakeChat(message)


class _FakeLLM:
    def __init__(self, message):
        self.model = "fake-model"
        self.client = _FakeClient(message)


@pytest.mark.asyncio
async def test_chat_handler_rejects_itinerary_tool():
    """create_itinerary 도구 호출 시 /chat은 거부하고 안내 메시지를 반환해야 한다."""
    message = _FakeMessage(tool_name="create_itinerary")
    handler = UnifiedChatHandler(llm_client=_FakeLLM(message))

    response = await handler.handle_chat(ChatRequest(text="서울 2일 일정 짜줘"))

    assert "itinerary" not in response
    assert "recommend/itinerary" in response["message"]


@pytest.mark.asyncio
async def test_handle_search_places_uses_region_as_area_and_maps_fields():
    """지역 정보를 query arguments에 전달하고 메타데이터를 name/area로 매핑한다."""
    from langchain.schema import Document

    class FakeRetriever:
        def __init__(self):
            self.last_args = None

        def search(self, *, query, top_k, domain, area):
            self.last_args = {"query": query, "top_k": top_k, "domain": domain, "area": area}
            return [
                Document(
                    page_content="상세 설명",
                    metadata={
                        "place_name": "명동 교자",
                        "area": "서울",
                        "document_id": "DOC1",
                    },
                )
            ]

    handler = UnifiedChatHandler(retriever=FakeRetriever())

    response = await handler._handle_search_places(
        {"query": "서울 맛집", "region": "서울", "domain": "food", "top_k": 3, "user_text": "서울 맛집"}
    )

    assert response["places"][0]["name"] == "명동 교자"
    assert response["places"][0]["area"] == "서울"
    assert handler.retriever.last_args == {
        "query": "서울 맛집",
        "top_k": 3,
        "domain": "food",
        "area": "서울",
    }


@pytest.mark.asyncio
async def test_handle_search_places_falls_back_to_user_text_and_region_when_missing():
    """query가 비어 있어도 user_text/region으로 보완하고 area는 region으로 채운다."""
    from langchain.schema import Document

    class FakeRetriever:
        def __init__(self):
            self.last_args = None

        def search(self, *, query, top_k, domain, area):
            self.last_args = {"query": query, "top_k": top_k, "domain": domain, "area": area}
            return [
                Document(
                    page_content="상세 설명",
                    metadata={
                        "place_name": "서울 식당",
                        "area": "",
                        "document_id": "DOC2",
                    },
                )
            ]

    handler = UnifiedChatHandler(retriever=FakeRetriever())

    response = await handler._handle_search_places(
        {"query": "", "region": "서울", "domain": "food", "top_k": 2, "user_text": "서울 맛집"}
    )

    assert response["places"][0]["name"] == "서울 식당"
    assert response["places"][0]["area"] == "서울"
    assert handler.retriever.last_args == {
        "query": "서울 맛집",
        "top_k": 2,
        "domain": "food",
        "area": "서울",
    }


@pytest.mark.asyncio
async def test_handle_search_places_infers_area_from_user_text():
    """region/area가 없을 때 텍스트에서 지역 키워드를 추론한다."""
    from langchain.schema import Document

    class FakeRetriever:
        def __init__(self):
            self.last_args = None

        def search(self, *, query, top_k, domain, area):
            self.last_args = {"query": query, "top_k": top_k, "domain": domain, "area": area}
            return [
                Document(
                    page_content="상세 설명",
                    metadata={
                        "place_name": "서울 식당",
                        "area": "",
                        "document_id": "DOC3",
                    },
                )
            ]

    handler = UnifiedChatHandler(retriever=FakeRetriever())

    response = await handler._handle_search_places(
        {"query": "ソウル ごはん", "region": None, "domain": "food", "top_k": 2, "user_text": "ソウル ごはん"}
    )

    assert response["places"][0]["name"] == "서울 식당"
    assert response["places"][0]["area"] == "서울"
    assert handler.retriever.last_args == {
        "query": "ソウル ごはん",
        "top_k": 2,
        "domain": "food",
        "area": "서울",
    }
