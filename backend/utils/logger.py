"""
로깅 및 예외 처리 유틸리티
"""
import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
import json


def setup_logger(name: str = "fastapi-rag", level: str = "INFO") -> logging.Logger:
    """
    구조화된 로거 설정
    
    Args:
        name: 로거 이름
        level: 로깅 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        설정된 Logger 인스턴스
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 핸들러가 이미 있으면 재설정 방지
    if logger.handlers:
        return logger
    
    # 콘솔 핸들러 설정
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # 포맷터 설정 (JSON 구조화 로그)
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "message": "%(message)s"}'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def log_exception(
    e: Exception,
    context: Optional[Dict[str, Any]] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    예외 정보를 구조화하여 로깅
    
    Args:
        e: 발생한 예외
        context: 추가 컨텍스트 정보 (딕셔너리)
        logger: 사용할 Logger 인스턴스 (없으면 기본 로거 사용)
    """
    if logger is None:
        logger = setup_logger()
    
    error_info = {
        "exception_type": type(e).__name__,
        "exception_message": str(e),
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if context:
        error_info["context"] = context
    
    logger.error(json.dumps(error_info, ensure_ascii=False))


# 기본 로거 인스턴스
default_logger = setup_logger()
