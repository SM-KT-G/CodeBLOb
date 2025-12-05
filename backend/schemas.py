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
