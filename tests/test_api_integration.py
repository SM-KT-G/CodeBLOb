"""
FastAPI 엔드포인트 통합 테스트
실제 FastAPI 애플리케이션을 통해 /rag/query 엔드포인트 테스트
"""
import sys
from pathlib import Path

# backend 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture(scope="module")
def client():
    """TestClient 생성 (lifespan 활성화)"""
    with TestClient(app) as test_client:
        yield test_client


class TestRAGQueryIntegration:
    """RAG Query 엔드포인트 통합 테스트"""
    
    def test_basic_query_integration(self, client):
        """기본 쿼리 통합 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "東京のおすすめレストランを教えてください",
                "top_k": 3
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 응답 구조 확인
        assert "answer" in data
        assert "sources" in data
        assert "latency" in data
        
        # 답변이 있어야 함
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        
        # Sources는 리스트여야 함
        assert isinstance(data["sources"], list)
        
        # Latency는 숫자여야 함
        assert isinstance(data["latency"], (int, float))
        assert data["latency"] > 0
    
    def test_query_with_domain_filter(self, client):
        """도메인 필터를 사용한 쿼리 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "おすすめの場所を教えてください",
                "top_k": 5,
                "domain": "food"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert isinstance(data["sources"], list)
    
    def test_query_with_area_filter(self, client):
        """지역 필터를 사용한 쿼리 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "観光スポットを教えてください",
                "top_k": 3,
                "area": "東京"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
    
    def test_query_with_expansion_enabled(self, client):
        """Query expansion을 활성화한 쿼리 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "レストランを探しています",
                "top_k": 5,
                "expansion": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert isinstance(data["sources"], list)
    
    def test_query_with_expansion_and_variations(self, client):
        """Query expansion + 커스텀 variations 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "東京のレストラン",
                "top_k": 3,
                "expansion": True,
                "expansion_variations": [
                    "東京のおすすめレストラン",
                    "東京の人気レストラン"
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
    
    def test_query_with_domain_and_area_filters(self, client):
        """도메인과 지역 필터를 동시에 사용하는 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "おすすめを教えてください",
                "top_k": 3,
                "domain": "stay",
                "area": "大阪"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
    
    def test_invalid_question_empty(self, client):
        """빈 질문으로 요청 시 에러 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "",
                "top_k": 3
            }
        )
        
        # 400 Bad Request 또는 422 Unprocessable Entity 예상
        assert response.status_code in [400, 422]
    
    def test_invalid_question_too_short(self, client):
        """너무 짧은 질문으로 요청 시 에러 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "あ",
                "top_k": 3
            }
        )
        
        # 422 Unprocessable Entity 예상 (Pydantic validation)
        assert response.status_code == 422
    
    def test_invalid_top_k_too_large(self, client):
        """top_k가 너무 큰 경우 에러 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "東京のおすすめレストラン",
                "top_k": 100
            }
        )
        
        # 422 Unprocessable Entity 예상 (Pydantic validation - top_k <= 10)
        assert response.status_code == 422
    
    def test_response_time_within_limit(self, client):
        """응답 시간이 합리적인 범위 내인지 확인"""
        response = client.post(
            "/rag/query",
            json={
                "question": "京都の観光スポット",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Latency가 10초 이내여야 함 (합리적인 범위)
        assert data["latency"] < 10.0
    
    def test_sources_format(self, client):
        """Sources의 형식이 올바른지 확인"""
        response = client.post(
            "/rag/query",
            json={
                "question": "大阪の美味しいレストラン",
                "top_k": 3
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Sources는 리스트여야 함
        assert isinstance(data["sources"], list)
        # Sources는 정수 또는 문자열이어야 함 (document_id)
        for source in data["sources"]:
            assert isinstance(source, (int, str))
    
    def test_all_domain_types(self, client):
        """모든 도메인 타입으로 쿼리 테스트"""
        domains = ["food", "stay", "nat", "his", "shop", "lei"]
        
        for domain in domains:
            response = client.post(
                "/rag/query",
                json={
                    "question": "おすすめを教えてください",
                    "top_k": 2,
                    "domain": domain
                }
            )
            
            assert response.status_code == 200, f"Failed for domain: {domain}"
            data = response.json()
            assert "answer" in data
            assert "sources" in data


class TestRAGQueryEdgeCases:
    """RAG Query 엣지 케이스 테스트"""
    
    def test_japanese_special_characters(self, client):
        """일본어 특수 문자 처리 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "「東京」の『人気』レストラン（おすすめ）",
                "top_k": 3
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
    
    def test_very_long_question(self, client):
        """매우 긴 질문 처리 테스트"""
        long_question = "東京のおすすめレストランを教えてください。" * 20
        
        response = client.post(
            "/rag/query",
            json={
                "question": long_question,
                "top_k": 3
            }
        )
        
        # 요청은 성공해야 함 (내부에서 적절히 처리)
        assert response.status_code in [200, 400, 422]
    
    def test_mixed_language_query(self, client):
        """여러 언어 혼합 쿼리 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "Tokyo 東京 restaurant レストラン",
                "top_k": 3
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
    
    def test_top_k_minimum(self, client):
        """top_k 최소값 테스트"""
        response = client.post(
            "/rag/query",
            json={
                "question": "東京のおすすめレストラン",
                "top_k": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        # 결과가 있다면 최대 1개
        if data["sources"]:
            assert len(data["sources"]) <= 1
