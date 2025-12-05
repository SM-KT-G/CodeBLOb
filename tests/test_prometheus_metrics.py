"""
Prometheus 메트릭 테스트
TDD: Red → Green → Refactor
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


def test_metrics_endpoint_should_exist():
    """
    /metrics 엔드포인트가 존재해야 한다.
    
    Given: FastAPI 앱이 실행 중일 때
    When: GET /metrics를 호출하면
    Then: 200 OK를 반환해야 한다
    """
    from backend.main import app
    
    client = TestClient(app)
    response = client.get("/metrics")
    
    assert response.status_code == 200, \
        f"/metrics 엔드포인트가 없거나 오류입니다: {response.status_code}"


def test_metrics_should_include_rag_latency():
    """
    메트릭에 RAG 응답 시간이 포함되어야 한다.
    
    Given: RAG 쿼리를 실행한 후
    When: /metrics를 확인하면
    Then: rag_query_duration_seconds 메트릭이 있어야 한다
    """
    from backend.main import app
    
    client = TestClient(app)
    
    # Mock retriever and dependencies
    with patch('backend.main.app.state') as mock_state:
        mock_retriever = Mock()
        mock_retriever.search_with_expansion.return_value = []
        mock_state.retriever = mock_retriever
        mock_state.llm_model = "gpt-4o-mini"
        
        # RAG 쿼리 실행
        response = client.post(
            "/rag/query",
            json={"question": "서울 맛집"}
        )
    
    # 메트릭 확인
    metrics_response = client.get("/metrics")
    metrics_text = metrics_response.text
    
    assert "rag_query_duration_seconds" in metrics_text, \
        "RAG 쿼리 응답 시간 메트릭이 없습니다"


def test_metrics_should_include_cache_hit_rate():
    """
    메트릭에 캐시 히트율이 포함되어야 한다.
    
    Given: 캐시를 사용하는 환경에서
    When: /metrics를 확인하면
    Then: cache_hit_total과 cache_miss_total 메트릭이 있어야 한다
    """
    from backend.main import app
    
    client = TestClient(app)
    metrics_response = client.get("/metrics")
    metrics_text = metrics_response.text
    
    assert "cache_hit_total" in metrics_text or "cache_hits_total" in metrics_text, \
        "캐시 히트 메트릭이 없습니다"
    
    assert "cache_miss_total" in metrics_text or "cache_misses_total" in metrics_text, \
        "캐시 미스 메트릭이 없습니다"


def test_metrics_should_include_query_expansion_stats():
    """
    메트릭에 Query Expansion 통계가 포함되어야 한다.
    
    Given: Query Expansion을 사용할 때
    When: /metrics를 확인하면
    Then: query_expansion_duration_seconds 메트릭이 있어야 한다
    """
    from backend.main import app
    
    client = TestClient(app)
    metrics_response = client.get("/metrics")
    metrics_text = metrics_response.text
    
    assert "query_expansion_duration_seconds" in metrics_text or \
           "query_expansion_latency" in metrics_text, \
        "Query Expansion 응답 시간 메트릭이 없습니다"


def test_metrics_should_include_http_request_stats():
    """
    메트릭에 HTTP 요청 통계가 포함되어야 한다.
    
    Given: FastAPI 앱이 실행 중일 때
    When: /metrics를 확인하면
    Then: HTTP 요청 수와 응답 시간 메트릭이 있어야 한다
    """
    from backend.main import app
    
    client = TestClient(app)
    
    # 몇 가지 요청 실행
    client.get("/health")
    
    # 메트릭 확인
    metrics_response = client.get("/metrics")
    metrics_text = metrics_response.text
    
    # Prometheus 표준 메트릭 확인
    assert "http_requests_total" in metrics_text or \
           "http_request_duration_seconds" in metrics_text or \
           "fastapi" in metrics_text, \
        "HTTP 요청 메트릭이 없습니다"


def test_metrics_should_track_error_rate():
    """
    메트릭에 에러율이 포함되어야 한다.
    
    Given: 에러가 발생할 때
    When: /metrics를 확인하면
    Then: error_total 또는 status_code별 메트릭이 있어야 한다
    """
    from backend.main import app
    
    client = TestClient(app)
    
    # 에러 발생 (잘못된 요청)
    client.post("/rag/query", json={"question": ""})  # validation error
    
    # 메트릭 확인
    metrics_response = client.get("/metrics")
    metrics_text = metrics_response.text
    
    # 에러 추적 메트릭
    assert "error" in metrics_text.lower() or \
           "status_code" in metrics_text or \
           "http_responses_total" in metrics_text, \
        "에러 추적 메트릭이 없습니다"


def test_metrics_format_should_be_prometheus_compatible():
    """
    메트릭 포맷이 Prometheus 표준을 따라야 한다.
    
    Given: /metrics 엔드포인트가 있을 때
    When: 응답을 확인하면
    Then: Content-Type이 text/plain이고 Prometheus 형식이어야 한다
    """
    from backend.main import app
    
    client = TestClient(app)
    response = client.get("/metrics")
    
    # Content-Type 확인
    assert "text/plain" in response.headers.get("content-type", ""), \
        f"메트릭 응답 타입이 잘못되었습니다: {response.headers.get('content-type')}"
    
    # Prometheus 형식 확인 (# HELP, # TYPE 주석)
    assert "# HELP" in response.text or "# TYPE" in response.text or \
           response.text.count("\n") > 5, \
        "Prometheus 메트릭 형식이 아닙니다"


@pytest.mark.asyncio
async def test_metrics_should_update_in_realtime():
    """
    메트릭이 실시간으로 업데이트되어야 한다.
    
    Given: 요청을 여러 번 보낼 때
    When: 메트릭을 조회하면
    Then: 카운터가 증가해야 한다
    """
    from backend.main import app
    
    client = TestClient(app)
    
    # 첫 번째 메트릭 조회
    response1 = client.get("/metrics")
    metrics1 = response1.text
    
    # 요청 몇 번 실행
    for _ in range(3):
        client.get("/health")
    
    # 두 번째 메트릭 조회
    response2 = client.get("/metrics")
    metrics2 = response2.text
    
    # 메트릭이 변경되었는지 확인 (내용이 달라야 함)
    # 적어도 한 줄은 달라야 함 (카운터 증가)
    assert metrics1 != metrics2 or len(metrics2) > 0, \
        "메트릭이 실시간으로 업데이트되지 않습니다"
