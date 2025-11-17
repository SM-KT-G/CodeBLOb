"""
Structured Outputs 테스트
100% JSON 보장 여부 확인
"""
import pytest
from backend.llm_base import LLMClient
from backend.schemas import ItineraryStructuredResponse


def test_generate_structured_returns_pydantic_model():
    """generate_structured가 Pydantic 모델을 반환"""
    client = LLMClient()
    
    result = client.generate_structured(
        prompt="東京 1日グルメプラン",
        response_format=ItineraryStructuredResponse,
        system_prompt="あなたは旅行プランナーです"
    )
    
    # Pydantic 모델이어야 함
    assert isinstance(result, ItineraryStructuredResponse)
    
    # 필수 필드 존재
    assert hasattr(result, "message")
    assert hasattr(result, "itinerary")
    
    # message는 문자열
    assert isinstance(result.message, str)
    
    # itinerary는 ItineraryData
    assert result.itinerary.title
    assert result.itinerary.days


def test_structured_response_always_valid_json():
    """Structured Outputs는 항상 유효한 JSON 스키마"""
    client = LLMClient()
    
    # 10번 실행해도 항상 성공
    for i in range(10):
        result = client.generate_structured(
            prompt=f"大阪 {i+1}日プラン",
            response_format=ItineraryStructuredResponse,
            system_prompt="あなたは旅行プランナーです"
        )
        
        # 스키마 검증 (Pydantic이 자동으로 함)
        assert result.itinerary.title
        assert len(result.itinerary.days) >= 1
        
        # 각 day는 segments를 가짐
        for day in result.itinerary.days:
            assert day.segments
            assert len(day.segments) > 0
            
            # 각 segment는 필수 필드를 가짐
            for seg in day.segments:
                assert seg.time
                assert seg.place_name
                assert seg.description


def test_structured_output_has_greeting_message():
    """친절한 인사 메시지가 포함됨"""
    client = LLMClient()
    
    result = client.generate_structured(
        prompt="京都 2日カフェ巡り",
        response_format=ItineraryStructuredResponse,
        system_prompt="""あなたは親切な旅行プランナーです。
プランの前に必ず挨拶と簡単な説明をしてください。"""
    )
    
    # message 필드가 비어있지 않아야 함
    assert result.message
    assert len(result.message) > 10  # 최소한의 인사말
