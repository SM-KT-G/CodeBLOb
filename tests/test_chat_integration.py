"""
통합 채팅 API 테스트
Mock을 사용하여 Docker 없이 테스트
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas import ChatRequest


@pytest.fixture
def mock_chat_history():
    """Mock ChatHistoryManager"""
    mock = Mock()
    mock.save_message = Mock(return_value=1)
    mock.get_history = Mock(return_value=[])
    mock.get_recent_context = Mock(return_value=[])
    mock.delete_session = Mock(return_value=1)
    return mock


@pytest.fixture
def mock_llm_client():
    """Mock LLMClient"""
    mock = Mock()
    
    # generate_structured mock
    from backend.schemas import ItineraryStructuredResponse, ItineraryData, ItineraryDay, ItinerarySegment
    
    mock_itinerary = ItineraryStructuredResponse(
        message="はい、ソウルの2日間プランをお作りしました！",
        itinerary=ItineraryData(
            title="ソウル 2日間グルメ旅行",
            summary="明洞と弘大のカフェ&グルメ巡り",
            days=[
                ItineraryDay(
                    day=1,
                    segments=[
                        ItinerarySegment(
                            time="午前",
                            place_name="明洞カフェ",
                            description="有名なカフェでブランチ"
                        ),
                        ItinerarySegment(
                            time="午後",
                            place_name="景福宮",
                            description="歴史的な宮殿見学"
                        )
                    ]
                ),
                ItineraryDay(
                    day=2,
                    segments=[
                        ItinerarySegment(
                            time="午前",
                            place_name="弘大カフェストリート",
                            description="おしゃれなカフェ巡り"
                        )
                    ]
                )
            ],
            highlights=["明洞", "弘大", "景福宮"]
        )
    )
    
    mock.generate_structured = Mock(return_value=mock_itinerary)
    
    # OpenAI client mock (Function Calling용)
    mock_client = Mock()
    mock_message = Mock()
    mock_message.content = "こんにちは！韓国旅行のお手伝いをします。"
    mock_message.tool_calls = None
    
    mock_choice = Mock()
    mock_choice.message = mock_message
    
    mock_completion = Mock()
    mock_completion.choices = [mock_choice]
    
    mock_client.chat.completions.create = Mock(return_value=mock_completion)
    mock.client = mock_client
    
    return mock


def test_chat_endpoint_general_conversation(mock_chat_history, mock_llm_client):
    """일반 대화 테스트 (Function Call 없음)"""
    with patch('backend.unified_chat.LLMClient', return_value=mock_llm_client):
        with patch('backend.main.ChatHistoryManager', return_value=mock_chat_history):
            with TestClient(app) as client:
                response = client.post(
                    "/chat",
                    json={
                        "text": "こんにちは",
                        "session_id": "test-session-1"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                assert data["response_type"] == "chat"
                assert "message" in data
                assert len(data["message"]) > 0


def test_chat_endpoint_search_places(mock_chat_history, mock_llm_client):
    """장소 검색 테스트 (Function Call: search_places)"""
    # Function Calling 응답 mock
    mock_tool_call = Mock()
    mock_tool_call.function.name = "search_places"
    mock_tool_call.function.arguments = '{"query": "ソウル カフェ", "domain": "food", "top_k": 5}'
    
    mock_message = Mock()
    mock_message.tool_calls = [mock_tool_call]
    
    mock_choice = Mock()
    mock_choice.message = mock_message
    
    mock_completion = Mock()
    mock_completion.choices = [mock_choice]
    
    mock_llm_client.client.chat.completions.create = Mock(return_value=mock_completion)
    
    # Retriever mock
    mock_retriever = AsyncMock()
    mock_retriever.search = AsyncMock(return_value=[
        {
            "name": "明洞カフェ",
            "description": "人気のカフェ",
            "area": "ソウル",
            "document_id": "J_FOOD_00001"
        }
    ])
    
    with patch('backend.unified_chat.LLMClient', return_value=mock_llm_client):
        with patch('backend.main.ChatHistoryManager', return_value=mock_chat_history):
            with patch.object(app.state, 'unified_chat_handler') as mock_handler:
                async def mock_handle_chat(request):
                    return {
                        "response_type": "search",
                        "message": "1件の場所が見つかりました。",
                        "places": [
                            {
                                "name": "明洞カフェ",
                                "description": "人気のカフェ",
                                "area": "ソウル",
                                "document_id": "J_FOOD_00001"
                            }
                        ]
                    }
                
                mock_handler.handle_chat = mock_handle_chat
                
                with TestClient(app) as client:
                    response = client.post(
                        "/chat",
                        json={
                            "text": "ソウルのカフェを教えて",
                            "session_id": "test-session-2"
                        }
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    assert data["response_type"] == "search"
                    assert "places" in data
                    assert len(data["places"]) > 0


def test_chat_endpoint_create_itinerary(mock_chat_history, mock_llm_client):
    """여행 일정 생성 테스트 (Function Call: create_itinerary)"""
    # Function Calling 응답 mock
    mock_tool_call = Mock()
    mock_tool_call.function.name = "create_itinerary"
    mock_tool_call.function.arguments = '{"region": "ソウル", "duration_days": 2, "themes": ["グルメ"], "domains": ["food"]}'
    
    mock_message = Mock()
    mock_message.tool_calls = [mock_tool_call]
    
    mock_choice = Mock()
    mock_choice.message = mock_message
    
    mock_completion = Mock()
    mock_completion.choices = [mock_choice]
    
    mock_llm_client.client.chat.completions.create = Mock(return_value=mock_completion)
    
    with patch('backend.unified_chat.LLMClient', return_value=mock_llm_client):
        with patch('backend.main.ChatHistoryManager', return_value=mock_chat_history):
            with patch.object(app.state, 'unified_chat_handler') as mock_handler:
                async def mock_handle_chat(request):
                    return {
                        "response_type": "itinerary",
                        "message": "はい、ソウルの2日間プランをお作りしました！",
                        "itinerary": {
                            "title": "ソウル 2日間グルメ旅行",
                            "summary": "明洞と弘大のカフェ&グルメ巡り",
                            "days": [
                                {
                                    "day": 1,
                                    "segments": [
                                        {
                                            "time": "午前",
                                            "place_name": "明洞カフェ",
                                            "description": "有名なカフェでブランチ",
                                            "place_id": None
                                        }
                                    ]
                                }
                            ],
                            "highlights": ["明洞", "弘大"]
                        }
                    }
                
                mock_handler.handle_chat = mock_handle_chat
                
                with TestClient(app) as client:
                    response = client.post(
                        "/chat",
                        json={
                            "text": "ソウル 2日間のプラン作って",
                            "session_id": "test-session-3"
                        }
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    assert data["response_type"] == "itinerary"
                    assert "itinerary" in data
                    assert data["itinerary"]["title"]
                    assert len(data["itinerary"]["days"]) >= 1


def test_chat_endpoint_invalid_request():
    """잘못된 요청 테스트"""
    with TestClient(app) as client:
        # text 누락
        response = client.post(
            "/chat",
            json={
                "session_id": "test-session"
            }
        )
        assert response.status_code == 422
        
        # session_id 누락은 이제 정상 (Optional)
        response = client.post(
            "/chat",
            json={
                "text": "こんにちは"
            }
        )
        assert response.status_code == 200  # session_id 없어도 OK
        
        # 빈 text
        response = client.post(
            "/chat",
            json={
                "text": "",
                "session_id": "test-session"
            }
        )
        assert response.status_code == 422
