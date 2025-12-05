"""
Query Expansion 설정 기반 변형 생성 테스트
"""
import json
from importlib import reload

import pytest

import backend.query_expansion as qe


def write_config(tmp_path, data):
    path = tmp_path / "qe_config.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def reload_with_config(monkeypatch, tmp_path, data):
    path = write_config(tmp_path, data)
    monkeypatch.setenv("QUERY_EXPANSION_CONFIG_PATH", str(path))
    qe.reset_query_expansion_config_cache()
    reload(qe)


def test_generate_variations_applies_suffixes(monkeypatch, tmp_path):
    reload_with_config(
        monkeypatch,
        tmp_path,
        {"suffixes": ["おすすめ", "旅行"], "max_variations": 5, "punctuation_chars": ""},
    )

    variations = qe.generate_variations("東京", [])

    assert variations[0] == "東京"
    assert "東京 おすすめ" in variations
    assert "東京 旅行" in variations


def test_generate_variations_removes_punctuation(monkeypatch, tmp_path):
    reload_with_config(
        monkeypatch,
        tmp_path,
        {"punctuation_chars": "!", "suffixes": [], "max_variations": 3},
    )

    variations = qe.generate_variations("京都!", [])

    assert "京都" in variations
    assert "京都!" not in variations[1:]


def test_generate_variations_enforces_max(monkeypatch, tmp_path):
    reload_with_config(
        monkeypatch,
        tmp_path,
        {
            "punctuation_chars": "",
            "suffixes": ["おすすめ", "人気", "旅行"],
            "max_variations": 3,
        },
    )

    variations = qe.generate_variations("大阪", ["서울", "부산"])

    assert len(variations) == 3
    assert variations[0] == "大阪"
