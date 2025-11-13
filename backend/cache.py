"""
Redis 캐시 유틸리티
"""
from __future__ import annotations

import json
import os
from typing import Any, Optional, Sequence

import redis

from backend.utils.logger import setup_logger


logger = setup_logger()


class RedisCache:
    """
    Redis 기반 JSON 캐시
    """

    def __init__(self, client: redis.Redis, ttl: int = 300, prefix: str = "rag"):
        self.client = client
        self.ttl = ttl
        self.prefix = prefix

    def make_key(self, namespace: str, parts: Sequence[str]) -> str:
        serialized = "|".join(parts)
        return f"{self.prefix}:{namespace}:{serialized}"

    def get_json(self, key: str) -> Optional[Any]:
        value = self.client.get(key)
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return json.loads(value)

    def set_json(self, key: str, value: Any) -> None:
        payload = json.dumps(value, ensure_ascii=False)
        self.client.setex(key, self.ttl, payload)


def init_cache_from_env() -> Optional[RedisCache]:
    """
    환경 변수 기반 Redis 캐시 초기화
    """
    url = os.getenv("REDIS_URL")
    if not url:
        return None

    ttl = int(os.getenv("REDIS_TTL", "300"))
    prefix = os.getenv("CACHE_PREFIX", "rag")

    try:
        client = redis.from_url(url)
        client.ping()
    except Exception as exc:
        logger.warning(f"Redis 캐시 초기화 실패: {exc}")
        return None

    logger.info(f"Redis 캐시 활성화 (ttl={ttl}, prefix={prefix})")
    return RedisCache(client=client, ttl=ttl, prefix=prefix)
