"""
FastAPI 메인 애플리케이션
엔트리포인트 및 라우터 정의
"""
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from backend.schemas import (
    RAGQueryRequest,
    RAGQueryResponse,
    HealthCheckResponse,
    ErrorResponse,
)
from backend.retriever import Retriever
from backend.utils.logger import setup_logger, log_exception

# 환경 변수 로드
load_dotenv()

# 로거 설정
logger = setup_logger(level=os.getenv("LOG_LEVEL", "INFO"))


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
    except Exception as e:
        log_exception(e, {"db_url": db_url[:50] if db_url else None}, logger)
        raise
    
    yield
    
    # 종료 시
    logger.info("FastAPI 애플리케이션 종료")
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


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """응답 시간 측정 미들웨어"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.2f}"
    return response


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
    checks = {
        "api": "ok",
        # TODO: DB 연결 상태 체크
        # TODO: LLM 연결 상태 체크
    }
    
    return HealthCheckResponse(
        status="healthy",
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
        
        # Retriever 실행 (expansion 옵션에 따라 분기)
        retriever: Retriever = app.state.retriever

        if request.expansion:
            docs = retriever.search_with_expansion(
                query=request.question,
                top_k=request.top_k,
                domain=(request.domain.value if request.domain else None),
                area=request.area,
                variations=request.expansion_variations,
            )
        else:
            docs = retriever.search(
                query=request.question,
                top_k=request.top_k,
                domain=(request.domain.value if request.domain else None),
                area=request.area,
            )

        # Parent context 포함 여부에 따라 응답 구성
        sources = [d.metadata.get("document_id") for d in docs if d.metadata.get("document_id")]

        # 간단한 답변: 상위 문서의 요약(또는 첫 문서의 내용 일부)을 반환
        if docs:
            # limit answer length
            answer = docs[0].page_content[:200]
        else:
            answer = "該当する情報が見つかりませんでした。"
        
        latency = round(time.time() - start_time, 2)
        
        # 응답 시간 제약 체크 (3초)
        if latency > 3.0:
            logger.warning(f"응답 시간 초과: {latency}초")
        
        return RAGQueryResponse(
            answer=answer,
            sources=sources,
            latency=latency,
        )
    
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
            detail="RAG 처리 중 오류 발생",
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
