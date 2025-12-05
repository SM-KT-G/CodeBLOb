"""
Pydantic 스키마 정의
요청/응답 모델 및 데이터 검증
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum


class DomainEnum(str, Enum):
    """관광 도메인 타입"""
    FOOD = "food"
    STAY = "stay"
    NAT = "nat"
    HIS = "his"
    SHOP = "shop"
    LEI = "lei"


class RAGQueryRequest(BaseModel):
    """RAG 질의 요청 모델"""
    question: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="사용자 질문 (일본어)"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="검색할 문서 개수"
    )
    domain: Optional[DomainEnum] = Field(
        default=None,
        description="특정 도메인으로 필터링 (선택사항)"
    )
    area: Optional[str] = Field(
        default=None,
        description="지역 필터 (예: 서울, 부산)"
    )
    expansion: bool = Field(
        default=False,
        description="쿼리 확장 사용 여부 (search_with_expansion 사용)"
    )
    expansion_variations: Optional[List[str]] = Field(
        default=None,
        description="사용자 정의 쿼리 변형 리스트 (선택)"
    )
    parent_context: bool = Field(
        default=True,
        description="검색 결과에 parent summary(문서 요약)를 포함할지 여부"
    )
    
    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """질문 검증"""
        if not v or not v.strip():
            raise ValueError("질문은 비어있을 수 없습니다.")
        return v.strip()


class RAGQueryResponse(BaseModel):
    """RAG 질의 응답 모델"""
    answer: str = Field(
        ...,
        min_length=1,
        description="생성된 답변 (일본어)"
    )
    sources: List[str] = Field(
        default_factory=list,
        description="참조한 문서 출처 목록"
    )
    latency: float = Field(
        ...,
        ge=0,
        description="응답 생성 시간 (초)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="추가 메타데이터"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "ソウルの明洞は韓国料理とショッピングで有名な観光地です。",
                "sources": ["J_FOOD_000001", "J_SHOP_000023"],
                "latency": 1.23,
                "metadata": {"model": "gpt-4-turbo", "tokens": 150}
            }
        }


class HealthCheckResponse(BaseModel):
    """헬스 체크 응답"""
    status: str = Field(default="healthy")
    timestamp: str
    version: str = Field(default="0.1.0")
    checks: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(default=None, description="상세 정보")
    timestamp: str


class ItinerarySegment(BaseModel):
    """추천 일정 내 세부 방문 정보"""
    time: Optional[str] = Field(default=None, description="예: 오전, 오후, 10:00 등")
    place_name: str = Field(..., description="장소 이름")
    description: str = Field(..., description="장소 설명 또는 액티비티")
    document_id: Optional[str] = Field(default=None, description="참조 원본 document_id")
    source_url: Optional[str] = Field(default=None, description="원본 출처 URL")
    area: Optional[str] = Field(default=None, description="장소 지역")
    notes: Optional[str] = Field(default=None, description="추가 메모")


class DayPlan(BaseModel):
    """일차별 세부 일정"""
    day: int = Field(..., ge=1, description="Day 번호 (1부터 시작)")
    segments: List[ItinerarySegment] = Field(default_factory=list, description="방문/활동 목록")


class ItineraryPlan(BaseModel):
    """추천 일정 한 건"""
    title: str
    summary: str
    days: List[DayPlan]
    highlights: List[str] = Field(default_factory=list)
    estimated_budget: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ItineraryRecommendationRequest(BaseModel):
    """여행 추천 요청"""
    region: str = Field(..., min_length=1, description="선호 지역 (예: 서울, 부산)")
    domains: List[DomainEnum] = Field(
        ...,
        min_length=1,
        description="관심 도메인 목록 (예: food, stay)",
    )
    duration_days: int = Field(
        ...,
        ge=1,
        le=7,
        description="여행 일수 (1~7)",
    )
    themes: List[str] = Field(
        default_factory=list,
        description="여행 테마 태그 (예: 힐링, 인스타)",
    )
    transport_mode: Optional[str] = Field(
        default=None,
        description="이동 수단 (예: public, car, walk)",
    )
    budget_level: Optional[str] = Field(
        default=None,
        description="예산 수준 (economy/standard/premium 등)",
    )
    preferred_places: List[str] = Field(
        default_factory=list,
        description="반드시 포함하고 싶은 document_id 목록",
    )
    avoid_places: List[str] = Field(
        default_factory=list,
        description="제외할 document_id 목록",
    )
    expansion: bool = Field(
        default=True,
        description="Query Expansion 사용 여부",
    )

    @field_validator("region")
    @classmethod
    def validate_region(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("region은 비어있을 수 없습니다.")
        return v.strip()


class ItineraryRecommendationResponse(BaseModel):
    """여행 추천 응답"""
    itineraries: List[ItineraryPlan] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Structured Outputs용 스키마
class ItineraryDay(BaseModel):
    """Structured Outputs용 일차별 일정"""
    day: int = Field(..., ge=1, description="Day 번호")
    segments: List[ItinerarySegment] = Field(..., description="세부 일정")


class ItineraryData(BaseModel):
    """Structured Outputs용 일정 데이터"""
    title: str = Field(..., description="일정 제목")
    summary: str = Field(..., description="일정 요약")
    days: List[ItineraryDay] = Field(..., description="일차별 일정")
    highlights: List[str] = Field(default_factory=list, description="하이라이트")


class ItineraryStructuredResponse(BaseModel):
    """Structured Outputs 응답 (100% JSON 보장)"""
    message: str = Field(..., description="친절한 인사 메시지")
    itinerary: ItineraryData = Field(..., description="일정 데이터")


# 통합 채팅용 스키마
class ChatRequest(BaseModel):
    """통합 채팅 요청"""
    text: str = Field(..., min_length=1, description="사용자 메시지")
    
    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("text는 비어있을 수 없습니다.")
        return v.strip()
