"""
FastAPI 메인 애플리케이션
엔트리포인트 및 라우터 정의
"""
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    from prometheus_fastapi_instrumentator import Instrumentator
except ImportError:  # pragma: no cover - 옵셔널 의존성 미설치 시 대체
    class _NoOpMetric:
        def __init__(self, *_, **__):
            pass

        def labels(self, *_, **__):
            return self

        def observe(self, *_, **__):
            return None

        def inc(self, *_, **__):
            return None

        def dec(self, *_, **__):
            return None

    class _NoOpInstrumentator:
        def instrument(self, app):
            return self

        def expose(self, app, endpoint="/metrics"):
            return self

    Counter = Histogram = Gauge = _NoOpMetric
    generate_latest = lambda *_, **__: b""  # type: ignore[var-annotated]
    CONTENT_TYPE_LATEST = "text/plain"
    Instrumentator = _NoOpInstrumentator  # type: ignore[assignment]

from fastapi.responses import Response

from backend.schemas import (
    RAGQueryRequest,
    RAGQueryResponse,
    HealthCheckResponse,
    ErrorResponse,
    ItineraryRecommendationRequest,
    ItineraryRecommendationResponse,
    ChatRequest,
)
from backend.retriever import Retriever
from backend.rag_chain import (
    RetrieverAdapter,
    create_rag_chain,
    execute_retriever_query,
    process_rag_response,
    remove_parent_summary,
)
from backend.itinerary import ItineraryPlanner
from backend.unified_chat import UnifiedChatHandler
from backend.utils.logger import setup_logger, log_exception

# 환경 변수 로드
load_dotenv()

# 로거 설정
logger = setup_logger(level=os.getenv("LOG_LEVEL", "INFO"))


def init_cache_from_env():
    """캐시 초기화 플레이스홀더 (테스트 호환용)"""
    return None

# Prometheus 메트릭 정의
rag_query_duration = Histogram(
    'rag_query_duration_seconds',
    'RAG 쿼리 응답 시간 (초)',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

query_expansion_duration = Histogram(
    'query_expansion_duration_seconds', 
    'Query Expansion 실행 시간 (초)',
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0]
)

rag_errors = Counter('rag_errors_total', 'RAG 쿼리 에러 수', ['error_type'])

active_requests = Gauge('active_requests', '현재 처리 중인 요청 수')


def validate_env_variables() -> None:
    """필수 환경 변수 검증"""
    required_vars = [
        "OPENAI_API_KEY",
        "DATABASE_URL",
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        error_msg = f"필수 환경 변수 누락: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    logger.info("환경 변수 검증 완료")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시
    logger.info("FastAPI 애플리케이션 시작")
    validate_env_variables()
    
    # DB 연결 및 Retriever 초기화
    db_url = os.getenv("DATABASE_URL")

    try:
        app.state.retriever = Retriever(db_url=db_url)
        logger.info("Retriever 인스턴스 생성 및 앱 상태에 등록됨")
        app.state.llm_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        app.state.itinerary_planner = ItineraryPlanner(
            app.state.retriever,
            llm_model=app.state.llm_model,
        )
        
        # UnifiedChatHandler 초기화
        app.state.unified_chat_handler = UnifiedChatHandler(
            retriever=app.state.retriever,
            itinerary_recommender=app.state.itinerary_planner
        )
        await app.state.unified_chat_handler.initialize()
        logger.info("UnifiedChatHandler 초기화 완료")
        
    except Exception as e:
        log_exception(e, {"db_url": db_url[:50] if db_url else None}, logger)
        raise
    
    yield
    
    # 종료 시
    logger.info("FastAPI 애플리케이션 종료")
    
    # UnifiedChatHandler 정리
    if hasattr(app.state, 'unified_chat_handler'):
        await app.state.unified_chat_handler.close()
        logger.info("UnifiedChatHandler 정리 완료")
    
    # Connection Pool 정리
    if hasattr(app.state, 'retriever'):
        app.state.retriever.close()
        logger.info("Retriever Connection Pool 정리 완료")


# FastAPI 앱 생성
app = FastAPI(
    title="FastAPI RAG Backend",
    description="한국 관광 가이드 챗봇 백엔드 API",
    version="0.1.0",
    lifespan=lifespan,
)

# Prometheus Instrumentator 설정
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """응답 시간 측정 미들웨어"""
    active_requests.inc()
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.2f}"
        return response
    finally:
        active_requests.dec()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 핸들러"""
    log_exception(
        exc,
        context={
            "path": request.url.path,
            "method": request.method,
        },
        logger=logger,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="내부 서버 오류",
            detail=str(exc),
            timestamp=datetime.utcnow().isoformat(),
        ).model_dump(),
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """헬스 체크 엔드포인트"""
    checks: dict[str, str] = {
        "api": "ok",
    }

    retriever: Optional[Retriever] = getattr(app.state, "retriever", None)
    db_status = "ok"
    if retriever is None:
        db_status = "missing"
    else:
        try:
            # 연결을 실제로 열고 간단한 쿼리로 확인한 뒤 풀에 반환
            with retriever.pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
        except Exception as exc:
            logger.warning("DB health check failed: %s", exc)
            db_status = "error"
    checks["db"] = db_status

    llm_status = "ok" if os.getenv("OPENAI_API_KEY") else "missing"
    checks["llm"] = llm_status

    # 캐시 상태는 현재 비활성화 (placeholder)
    checks["cache"] = "missing"

    overall_status = "healthy" if db_status == "ok" and llm_status == "ok" else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        checks=checks,
    )


@app.post("/rag/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """
    RAG 기반 질의응답 엔드포인트
    
    Args:
        request: RAG 질의 요청
    
    Returns:
        RAG 응답 (답변, 출처, 지연시간)
    """
    start_time = time.time()
    
    try:
        logger.info(f"RAG 질의 수신: {request.question[:50]}...")

        retriever: Retriever = app.state.retriever
        llm_model = getattr(app.state, "llm_model", os.getenv("OPENAI_MODEL", "gpt-4-turbo"))

        adapter = RetrieverAdapter(
            retriever=retriever,
            top_k=request.top_k,
            domain=(request.domain.value if request.domain else None),
            area=request.area,
            expansion=request.expansion,
            variations=request.expansion_variations or [],
            include_parent_summary=request.parent_context,
        )

        metadata: dict[str, Any] = {
            "model": llm_model,
            "top_k": request.top_k,
            "expansion": request.expansion,
            "parent_context": request.parent_context,
        }

        try:
            chain = create_rag_chain(
                llm_model=llm_model,
                retriever=adapter,
            )
            chain_result = chain.invoke({"query": request.question})
            rag_result = process_rag_response(chain_result)

            answer = rag_result["answer"] or "該当する情報が見つかりませんでした。"
            sources = rag_result["sources"]
            metadata.update(rag_result.get("metadata") or {})
            if request.expansion:
                expansion_metrics = getattr(retriever, "last_expansion_metrics", None)
                metadata["expansion_metrics"] = expansion_metrics
                
                # Query Expansion 메트릭 기록
                if expansion_metrics and expansion_metrics.get("duration_ms"):
                    query_expansion_duration.observe(expansion_metrics["duration_ms"] / 1000.0)
        except Exception as e:
            rag_errors.labels(error_type="rag_chain").inc()
            log_exception(
                e,
                {
                    "phase": "rag_chain",
                    "question": request.question[:100],
                },
                logger,
            )
            docs = execute_retriever_query(
                retriever=retriever,
                query=request.question,
                top_k=request.top_k,
                domain=(request.domain.value if request.domain else None),
                area=request.area,
                expansion=request.expansion,
                variations=request.expansion_variations or [],
            )
            if not request.parent_context:
                docs = remove_parent_summary(docs)
            sources = [
                d.metadata.get("document_id")
                for d in docs
                if d.metadata.get("document_id")
            ]
            answer = docs[0].page_content[:200] if docs else "該当する情報が見つかりませんでした。"
            metadata["fallback"] = True
            metadata["retrieved_count"] = len(docs)
            if request.expansion:
                expansion_metrics = getattr(retriever, "last_expansion_metrics", None)
                metadata["expansion_metrics"] = expansion_metrics
                if expansion_metrics and expansion_metrics.get("duration_ms"):
                    query_expansion_duration.observe(expansion_metrics["duration_ms"] / 1000.0)

        latency = round(time.time() - start_time, 2)
        
        # RAG 쿼리 응답 시간 메트릭 기록
        rag_query_duration.observe(latency)
        
        # 응답 시간 제약 체크 (3초)
        if latency > 3.0:
            logger.warning(f"응답 시간 초과: {latency}초")
        
        # Similarity 통계 계산
        similarities = [d.metadata.get("similarity", 0.0) for d in docs]
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        max_similarity = max(similarities) if similarities else 0.0
        
        return RAGQueryResponse(
            answer=answer,
            sources=sources,
            latency=latency,
            metadata=metadata,
        )
    
    except ValueError as e:
        rag_errors.labels(error_type="validation").inc()
        log_exception(e, {"request": request.model_dump()}, logger)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        rag_errors.labels(error_type="internal").inc()
        log_exception(e, {"request": request.model_dump()}, logger)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RAG 처리 중 오류 발생",
        )


@app.post("/recommend/itinerary", response_model=ItineraryRecommendationResponse)
async def recommend_itinerary(request: ItineraryRecommendationRequest):
    """여행 추천 일정 생성"""
    start_time = time.time()
    try:
        planner: ItineraryPlanner = getattr(app.state, "itinerary_planner", None)
        if planner is None:
            planner = ItineraryPlanner(app.state.retriever)
        result = planner.recommend(request)
        result["metadata"]["latency"] = round(time.time() - start_time, 2)
        return ItineraryRecommendationResponse(**result)
    except ValueError as e:
        log_exception(e, {"request": request.model_dump()}, logger)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        log_exception(e, {"request": request.model_dump()}, logger)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Itinerary 추천 중 오류 발생",
        )


@app.post("/recommend", response_model=ItineraryRecommendationResponse)
async def recommend_itinerary_alias(request: ItineraryRecommendationRequest):
    """
    여행 추천 일정 생성 (경로: /recommend)
    기존 /recommend/itinerary와 동일한 응답을 반환한다.
    """
    return await recommend_itinerary(request)


@app.post("/chat")
async def unified_chat(request: ChatRequest):
    """
    통합 채팅 엔드포인트
    Function Calling으로 일반 대화, RAG 검색, 여행 일정을 하나로 처리
    
    Args:
        request: 채팅 요청 (text)
    
    Returns:
        응답
    """
    try:
        handler: UnifiedChatHandler = app.state.unified_chat_handler
        response = await handler.handle_chat(request)
        return JSONResponse(content=response)
    
    except ValueError as e:
        log_exception(e, {"request": request.model_dump()}, logger)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        log_exception(e, {"request": request.model_dump()}, logger)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="채팅 처리 중 오류 발생",
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=int(os.getenv("MAX_WORKERS", 2)),
        reload=os.getenv("APP_ENV") == "development",
    )
