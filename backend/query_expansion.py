"""
Query Expansion 설정 및 변형 생성 헬퍼
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Sequence

DEFAULT_PUNCTUATION = "、。！？「」『』（）［］【】〈〉《》,.!?;:'\"()[]{}…"
DEFAULT_SUFFIXES = ["おすすめ", "観光", "人気スポット"]
DEFAULT_MAX_VARIATIONS = 6

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "query_expansion.json"
CONFIG_ENV_KEY = "QUERY_EXPANSION_CONFIG_PATH"


def _load_config_from_path(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_config(data: dict) -> dict:
    return {
        "punctuation_chars": data.get("punctuation_chars", DEFAULT_PUNCTUATION),
        "suffixes": [s for s in data.get("suffixes", DEFAULT_SUFFIXES) if isinstance(s, str)],
        "max_variations": max(1, int(data.get("max_variations", DEFAULT_MAX_VARIATIONS))),
    }


def _get_config_path() -> Path:
    custom = os.getenv(CONFIG_ENV_KEY)
    if custom:
        return Path(custom).expanduser()
    return DEFAULT_CONFIG_PATH


@lru_cache(maxsize=1)
def load_query_expansion_config() -> dict:
    """설정 파일을 로드하고 캐시"""
    path = _get_config_path()
    try:
        data = _load_config_from_path(path)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Query expansion config 파싱 실패: {path}") from exc
    config = _normalize_config(data)
    return config


def reset_query_expansion_config_cache() -> None:
    """테스트에서 캐시 초기화용"""
    load_query_expansion_config.cache_clear()  # type: ignore[attr-defined]


def _remove_punctuation(text: str, punctuation_chars: str) -> str:
    table = str.maketrans("", "", punctuation_chars)
    return text.translate(table)


def _deduplicate(values: Sequence[str]) -> List[str]:
    seen = set()
    deduped: List[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def _apply_suffixes(base: str, suffixes: Sequence[str]) -> List[str]:
    variants = []
    for suffix in suffixes:
        suffix = suffix.strip()
        if not suffix:
            continue
        if suffix.startswith((" ", "　")):
            variants.append(f"{base}{suffix}")
        else:
            variants.append(f"{base} {suffix}")
    return variants


def generate_variations(
    query: str,
    user_variations: Optional[Sequence[str]] = None,
) -> List[str]:
    """
    설정 기반으로 Query Expansion 변형을 생성

    Args:
        query: 사용자 원본 쿼리
        user_variations: API 요청에서 전달한 변형 리스트

    Returns:
        고유한 변형 문자열 리스트 (max_variations 제한 적용)
    """
    if not query or not query.strip():
        raise ValueError("쿼리는 비어있을 수 없습니다.")

    config = load_query_expansion_config()
    max_variations = config["max_variations"]
    base = query.strip()

    candidates: List[str] = [base]

    stripped = _remove_punctuation(base, config["punctuation_chars"]).strip()
    if stripped and stripped != base:
        candidates.append(stripped)

    candidates.extend(_apply_suffixes(base, config["suffixes"]))

    if user_variations:
        for uv in user_variations:
            text = (uv or "").strip()
            if text:
                candidates.append(text)

    deduped = _deduplicate(candidates)
    return deduped[:max_variations]
