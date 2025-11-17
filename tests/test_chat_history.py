"""
ChatHistoryManager 테스트
MariaDB에 대화 저장/조회 기능
"""
import pytest
import json
import os
from backend.chat_history import ChatHistoryManager


@pytest.fixture
def chat_manager():
    """테스트용 ChatHistoryManager"""
    return ChatHistoryManager(
        host=os.getenv("MARIADB_HOST", "localhost"),
        user=os.getenv("MARIADB_USER", "test_user"),
        password=os.getenv("MARIADB_PASSWORD", "test_pass"),
        database=os.getenv("MARIADB_DATABASE", "test_tourism_db")
    )


def test_save_simple_chat_message(chat_manager):
    """일반 대화 메시지 저장"""
    session_id = "test-simple-chat"
    
    chat_id = chat_manager.save_message(
        session_id=session_id,
        user_message="こんにちは",
        response_type="chat",
        assistant_response={"response_type": "chat", "message": "こんにちは！"}
    )
    
    assert chat_id is not None
    assert isinstance(chat_id, int)
    
    # 정리
    chat_manager.delete_session(session_id)


def test_save_and_retrieve_json_response(chat_manager):
    """JSON 응답을 저장하고 정확히 복원"""
    session_id = "test-json-response"
    
    # 복잡한 JSON 응답
    itinerary_response = {
        "response_type": "itinerary",
        "message": "はい、プランをお作りしました",
        "itinerary": {
            "title": "ソウル 2泊3日",
            "summary": "グルメとカフェ",
            "days": [
                {
                    "day": 1,
                    "segments": [
                        {
                            "time": "午前",
                            "place_name": "明洞",
                            "description": "ショッピング",
                            "place_id": "J_SHOP_001"
                        }
                    ]
                }
            ],
            "highlights": ["明洞", "カフェ"]
        }
    }
    
    # 저장
    chat_id = chat_manager.save_message(
        session_id=session_id,
        user_message="プラン作って",
        response_type="itinerary",
        assistant_response=itinerary_response
    )
    
    assert chat_id is not None
    
    # 조회
    history = chat_manager.get_history(session_id)
    assert len(history) == 1
    
    retrieved = history[0]["assistant_response"]
    
    # JSON 구조가 정확히 보존되는지 확인
    assert retrieved["response_type"] == "itinerary"
    assert retrieved["message"] == "はい、プランをお作りしました"
    assert retrieved["itinerary"]["title"] == "ソウル 2泊3日"
    assert retrieved["itinerary"]["days"][0]["segments"][0]["place_name"] == "明洞"
    
    # 정리
    chat_manager.delete_session(session_id)


def test_get_recent_context(chat_manager):
    """최근 N개 컨텍스트 조회"""
    session_id = "test-context"
    
    # 여러 메시지 저장
    for i in range(5):
        chat_manager.save_message(
            session_id=session_id,
            user_message=f"メッセージ {i}",
            response_type="chat",
            assistant_response={"response_type": "chat", "message": f"応答 {i}"}
        )
    
    # 최근 3개만 조회
    recent = chat_manager.get_recent_context(session_id, limit=3)
    
    assert len(recent) == 3
    # 오래된 순서대로 (LLM 컨텍스트용)
    assert recent[0]["user_message"] == "メッセージ 2"
    assert recent[2]["user_message"] == "メッセージ 4"
    
    # 정리
    chat_manager.delete_session(session_id)
