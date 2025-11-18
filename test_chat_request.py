"""
Chat API 수정 사항 간단 테스트
session_id가 Optional인지 확인
"""
from backend.schemas import ChatRequest


def test_chat_request_with_session_id():
    """session_id가 있는 경우"""
    req = ChatRequest(
        text="서울 맛집 추천해줘",
        session_id="user123"
    )
    assert req.text == "서울 맛집 추천해줘"
    assert req.session_id == "user123"
    print("✅ session_id 있는 요청: OK")


def test_chat_request_without_session_id():
    """session_id가 없는 경우 (수정 후)"""
    req = ChatRequest(
        text="부산 여행 추천"
    )
    assert req.text == "부산 여행 추천"
    assert req.session_id is None
    print("✅ session_id 없는 요청: OK")


def test_chat_request_empty_text():
    """빈 text는 거부되어야 함"""
    try:
        ChatRequest(text="   ")
        print("❌ 빈 text 거부 실패")
        assert False
    except ValueError as e:
        print(f"✅ 빈 text 거부: {e}")


if __name__ == "__main__":
    test_chat_request_with_session_id()
    test_chat_request_without_session_id()
    test_chat_request_empty_text()
    print("\n✅ 모든 테스트 통과!")
