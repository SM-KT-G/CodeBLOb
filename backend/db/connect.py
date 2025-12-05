"""
PostgreSQL 연결 관리
커넥션 풀 및 재시도 로직
"""
import os
import time
from typing import Optional
from contextlib import contextmanager

try:
    from psycopg_pool import ConnectionPool
    import psycopg
except ImportError:
    # 패키지 미설치 시 임시 처리
    ConnectionPool = None
    psycopg = None

from backend.utils.logger import setup_logger, log_exception


logger = setup_logger()


class DatabaseConnection:
    """
    PostgreSQL 연결 관리 클래스
    """
    
    def __init__(
        self,
        db_url: Optional[str] = None,
        min_size: int = 5,
        max_size: int = 20,
        max_retries: int = 5,
        retry_delay: int = 2,
    ):
        """
        초기화
        
        Args:
            db_url: 데이터베이스 연결 URL
            min_size: 최소 커넥션 수
            max_size: 최대 커넥션 수
            max_retries: 최대 재시도 횟수
            retry_delay: 재시도 대기 시간 (초)
        """
        self.db_url = db_url or os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL이 설정되지 않았습니다.")
        
        self.min_size = min_size
        self.max_size = max_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.pool: Optional[ConnectionPool] = None
        
        # 연결 초기화
        self._initialize_connection()
    
    def _initialize_connection(self) -> None:
        """
        커넥션 풀 초기화 (재시도 로직 포함)
        """
        if ConnectionPool is None:
            logger.warning("psycopg_pool이 설치되지 않았습니다. 연결을 건너뜁니다.")
            return
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"DB 연결 시도 {attempt}/{self.max_retries}... "
                    f"(min_size={self.min_size}, max_size={self.max_size})"
                )
                
                self.pool = ConnectionPool(
                    conninfo=self.db_url,
                    min_size=self.min_size,
                    max_size=self.max_size,
                    timeout=10,
                )
                
                # 연결 테스트
                with self.pool.connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                        result = cur.fetchone()
                        assert result[0] == 1
                
                logger.info("DB 연결 성공")
                return
            
            except Exception as e:
                log_exception(
                    e,
                    context={
                        "attempt": attempt,
                        "max_retries": self.max_retries,
                    },
                    logger=logger,
                )
                
                if attempt == self.max_retries:
                    error_msg = f"DB 연결 실패 ({self.max_retries}회 시도)"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg) from e
                
                logger.info(f"{self.retry_delay}초 후 재시도...")
                time.sleep(self.retry_delay)
    
    @contextmanager
    def get_connection(self):
        """
        컨텍스트 매니저로 연결 제공
        
        Yields:
            psycopg.Connection
        """
        if self.pool is None:
            raise RuntimeError("커넥션 풀이 초기화되지 않았습니다.")
        
        with self.pool.connection() as conn:
            try:
                yield conn
            except Exception as e:
                log_exception(e, logger=logger)
                raise
    
    def execute_script(self, script_path: str) -> None:
        """
        SQL 스크립트 파일 실행
        
        Args:
            script_path: SQL 파일 경로
        """
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"SQL 스크립트를 찾을 수 없습니다: {script_path}")
        
        logger.info(f"SQL 스크립트 실행: {script_path}")
        
        with open(script_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_script)
            conn.commit()
        
        logger.info("SQL 스크립트 실행 완료")
    
    def check_schema(self) -> bool:
        """
        스키마 상태 확인
        
        Returns:
            pgvector 확장 및 테이블 존재 여부
        """
        if self.pool is None:
            return False
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # pgvector 확장 확인
                    cur.execute(
                        "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                    )
                    vector_exists = cur.fetchone()[0]
                    
                    # 테이블 확인 (예: tourism_embeddings)
                    cur.execute(
                        "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                        "WHERE table_name = 'langchain_pg_embedding')"
                    )
                    table_exists = cur.fetchone()[0]
                    
                    logger.info(
                        f"스키마 상태: pgvector={vector_exists}, table={table_exists}"
                    )
                    
                    return vector_exists and table_exists
        
        except Exception as e:
            log_exception(e, logger=logger)
            return False
    
    def close(self) -> None:
        """커넥션 풀 종료"""
        if self.pool:
            self.pool.close()
            logger.info("DB 커넥션 풀 종료")


# 전역 DB 연결 인스턴스 (싱글톤)
_db_instance: Optional[DatabaseConnection] = None


def get_db() -> DatabaseConnection:
    """
    전역 DB 연결 인스턴스 반환
    
    Returns:
        DatabaseConnection 인스턴스
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseConnection()
    
    return _db_instance
