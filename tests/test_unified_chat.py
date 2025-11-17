"""
UnifiedChatHandler 테스트
Function Calling 통합 처리
"""
import os
import pytest
from backend.unified_chat import UnifiedChatHandler
from backend.schemas import ChatRequest
from backend.chat_history import ChatHistoryManager
from backend.retriever import Retriever


@pytest.fixture
async def chat_handler():
    """테스트용 UnifiedChatHandler"""
    # MariaDB 채팅 기록
    chat_history = ChatHistoryManager(
        host=os.getenv("MARIADB_HOST", "127.0.0.1"),
        user=os.getenv("MARIADB_USER", "tourism_user"),
        password=os.getenv("MARIADB_PASSWORD", "tourism_pass"),
        database=os.getenv("MARIADB_DATABASE", "tourism_db")
    )
    
    # RAG Retriever (DB 연결 필요)
    retriever = Retriever(
        db_url=os.getenv("DATABASE_URL", "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db")
    )
    
    handler = UnifiedChatHandler(
        chat_history=chat_history,
        retriever=retriever
    )
    await handler.initialize()
    yield handler
    await handler.close()


@pytest.mark.asyncio
async def test_general_chat_no_function_call(chat_handler):
    """일반 대화 - Function Calling 없음"""
    request = ChatRequest(
        text="こんにちは",
        session_id="test-general"
    )
    
    response = await chat_handler.handle_chat(request)
    
    assert response["response_type"] == "chat"
    assert "message" in response
    assert isinstance(response["message"], str)


@pytest.mark.asyncio
async def test_search_places_function_call(chat_handler):
    """장소 검색 - search_places 호출"""
    request = ChatRequest(
        text="ソウルでおすすめのカフェを教えて",
        session_id="test-search"
    )
    
    response = await chat_handler.handle_chat(request)
    
    assert response["response_type"] == "search"
    assert "message" in response
    assert "places" in response
    assert isinstance(response["places"], list)


@pytest.mark.asyncio
async def test_create_itinerary_function_call(chat_handler):
    """여행 일정 생성 - create_itinerary 호출"""
    request = ChatRequest(
        text="ソウル 2泊3日のプラン作って",
        session_id="test-itinerary"
    )
    
    response = await chat_handler.handle_chat(request)
    
    assert response["response_type"] == "itinerary"
    assert "message" in response
    assert "itinerary" in response
    
    # Structured 응답 검증
    itinerary = response["itinerary"]
    assert itinerary["title"]
    assert itinerary["days"]
    assert len(itinerary["days"]) >= 1


@pytest.mark.asyncio
async def test_chat_history_saved_to_db(chat_handler):
    """대화 기록이 DB에 저장됨"""
    session_id = "test-history-save"
    
    request = ChatRequest(
        text="こんにちは",
        session_id=session_id
    )
    
    await chat_handler.handle_chat(request)
    
    # DB에서 조회
    history = chat_handler.chat_history.get_history(session_id)
    
    assert len(history) >= 1
    assert history[-1]["user_message"] == "こんにちは"
    
    # 정리
    chat_handler.chat_history.delete_session(session_id)


@pytest.mark.asyncio
async def test_context_included_in_follow_up(chat_handler):
    """후속 질문에 이전 컨텍스트 포함"""
    session_id = "test-context-follow"
    
    # 첫 질문
    request1 = ChatRequest(
        text="ソウルでおすすめのカフェ教えて",
        session_id=session_id
    )
    await chat_handler.handle_chat(request1)
    
    # 후속 질문 (컨텍스트 필요)
    request2 = ChatRequest(
        text="その中で一番近い場所は？",
        session_id=session_id
    )
    response2 = await chat_handler.handle_chat(request2)
    
    # 응답이 이전 컨텍스트를 이해했어야 함
    assert response2["response_type"] in ["chat", "search"]
    assert response2["message"]
    
    # 정리
    chat_handler.chat_history.delete_session(session_id)
