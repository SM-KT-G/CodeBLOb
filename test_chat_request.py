"""Chat API 요청 스키마 테스트 (session_id 제거 후)"""
from backend.schemas import ChatRequest
import pytest


def test_chat_request_basic():
    """필수 필드는 text 하나만"""
    req = ChatRequest(text="서울 맛집 추천해줘")
    assert req.text == "서울 맛집 추천해줘"
    # session_id 필드가 제거되었음을 확인
    assert not hasattr(req, "session_id")


def test_chat_request_strips_whitespace():
    """text는 앞뒤 공백을 잘라서 저장"""
    req = ChatRequest(text="   부산 여행 추천   ")
    assert req.text == "부산 여행 추천"


def test_chat_request_empty_text():
    """빈 text는 거부되어야 함"""
    with pytest.raises(ValueError):
        ChatRequest(text="   ")


if __name__ == "__main__":
    test_chat_request_basic()
    test_chat_request_strips_whitespace()
    test_chat_request_empty_text()
    print("\n✅ 모든 테스트 통과!")
