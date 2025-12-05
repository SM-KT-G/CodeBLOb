"""
API 응답 fixtures를 생성하고 검증하는 테스트
Node.js로 전달할 실제 응답 형식을 저장
"""
import json
import os
from pathlib import Path
from typing import Any, Dict

from fastapi.testclient import TestClient
import pytest

import backend.main as main_module
from backend.main import app


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def save_fixture(filename: str, data: Dict[str, Any]) -> None:
    """fixture를 JSON 파일로 저장"""
    filepath = FIXTURES_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def test_save_rag_query_response_fixture(monkeypatch):
    """RAG 쿼리 응답을 fixture로 저장"""
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    class DummyRetriever:
        def __init__(self, db_url: str, **_):
            self.db_url = db_url

        def close(self):
            return None

    class DummyRAGChain:
        def __call__(self, inputs):
            return {
                "result": "明洞は韓国ソウルの中心部に位置する繁華街です。ショッピングとグルメで有名です。",
                "source_documents": [],
            }

    def mock_create_rag_chain(*args, **kwargs):
        return DummyRAGChain()

    def mock_execute_retriever_query(*args, **kwargs):
        from langchain.schema import Document
        return [
            Document(
                page_content="明洞でショッピング",
                metadata={
                    "document_id": "J_SHOP_001",
                    "place_name": "明洞",
                    "source_url": "https://example.com/myeongdong",
                }
            ),
            Document(
                page_content="明洞で韓国料理",
                metadata={
                    "document_id": "J_FOOD_001",
                    "place_name": "明洞グルメ",
                    "source_url": "https://example.com/myeongdong-food",
                }
            ),
        ]

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "create_rag_chain", mock_create_rag_chain)
    monkeypatch.setattr(main_module, "execute_retriever_query", mock_execute_retriever_query)
    monkeypatch.setattr(main_module, "init_cache_from_env", lambda: None)

    with TestClient(app) as client:
        response = client.post(
            "/rag/query",
            json={
                "question": "明洞について教えてください",
                "top_k": 5,
                "expansion": False,
            },
        )

    assert response.status_code == 200
    data = response.json()
    
    # fixture로 저장
    save_fixture("rag_query_response.json", data)
    
    # 저장된 파일 확인
    fixture_path = FIXTURES_DIR / "rag_query_response.json"
    assert fixture_path.exists()
    
    # 필수 필드 검증
    assert "answer" in data
    assert "sources" in data
    assert "latency" in data


def test_save_itinerary_response_fixture(monkeypatch):
    """여행 일정 추천 응답을 fixture로 저장"""
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    class DummyRetriever:
        def __init__(self, db_url: str, **_):
            self.db_url = db_url

        def search_with_expansion(self, query, **kwargs):
            from langchain.schema import Document
            return [
                Document(
                    page_content="明洞でショッピング",
                    metadata={
                        "document_id": "J_SHOP_001",
                        "place_name": "明洞",
                        "domain": "shop",
                        "area": "ソウル",
                    }
                ),
                Document(
                    page_content="景福宮の歴史",
                    metadata={
                        "document_id": "J_HIS_001",
                        "place_name": "景福宮",
                        "domain": "his",
                        "area": "ソウル",
                    }
                ),
            ]

        def close(self):
            return None

    class DummyPlanner:
        def __init__(self, retriever):
            self.retriever = retriever

        def recommend(self, request):
            return {
                "itineraries": [
                    {
                        "title": "ソウル 2日おすすめ #1",
                        "summary": "ソウルでショッピングと歴史探訪を楽しむ2日間のプラン",
                        "days": [
                            {
                                "day": 1,
                                "segments": [
                                    {
                                        "time": "午前",
                                        "place_name": "明洞",
                                        "description": "ショッピングとグルメを楽しむ",
                                        "document_id": "J_SHOP_001",
                                        "source_url": "https://example.com/myeongdong",
                                        "area": "ソウル",
                                        "notes": "domain=shop",
                                    },
                                    {
                                        "time": "午後",
                                        "place_name": "景福宮",
                                        "description": "朝鮮王朝の歴史を探訪",
                                        "document_id": "J_HIS_001",
                                        "source_url": "https://example.com/gyeongbokgung",
                                        "area": "ソウル",
                                        "notes": "domain=his",
                                    },
                                ],
                            },
                            {
                                "day": 2,
                                "segments": [
                                    {
                                        "time": "午前",
                                        "place_name": "南大門市場",
                                        "description": "伝統市場でショッピング",
                                        "document_id": "J_SHOP_002",
                                        "area": "ソウル",
                                    },
                                ],
                            },
                        ],
                        "highlights": ["明洞", "景福宮", "南大門市場"],
                        "estimated_budget": "standard",
                        "metadata": {"region": "ソウル", "domains": ["shop", "his"]},
                    }
                ],
                "metadata": {
                    "generated_count": 1,
                    "duration_days": 2,
                    "region": "ソウル",
                    "domains": ["shop", "his"],
                    "themes": ["インスタ映え"],
                    "generator": "llm",
                },
            }

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "ItineraryPlanner", lambda retriever, **_: DummyPlanner(retriever))
    monkeypatch.setattr(main_module, "init_cache_from_env", lambda: None)

    with TestClient(app) as client:
        response = client.post(
            "/recommend/itinerary",
            json={
                "region": "ソウル",
                "domains": ["shop", "his"],
                "duration_days": 2,
                "themes": ["インスタ映え"],
                "transport_mode": "public",
                "budget_level": "standard",
            },
        )

    assert response.status_code == 200
    data = response.json()
    
    # fixture로 저장
    save_fixture("itinerary_response.json", data)
    
    # 저장된 파일 확인
    fixture_path = FIXTURES_DIR / "itinerary_response.json"
    assert fixture_path.exists()
    
    # 필수 필드 검증
    assert "itineraries" in data
    assert "metadata" in data
    assert len(data["itineraries"]) > 0
    assert len(data["itineraries"][0]["days"]) == 2


def test_save_health_response_fixture(monkeypatch):
    """헬스 체크 응답을 fixture로 저장"""
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    class DummyRetriever:
        def __init__(self, db_url: str, **_):
            self.db_url = db_url

        def close(self):
            return None

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "init_cache_from_env", lambda: None)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    
    # fixture로 저장
    save_fixture("health_response.json", data)
    
    # 저장된 파일 확인
    fixture_path = FIXTURES_DIR / "health_response.json"
    assert fixture_path.exists()
    
    # 필수 필드 검증
    assert "status" in data
    assert "timestamp" in data
    assert "checks" in data


def test_all_fixtures_are_valid_json():
    """저장된 모든 fixture가 유효한 JSON인지 검증"""
    fixture_files = [
        "rag_query_response.json",
        "itinerary_response.json",
        "health_response.json",
    ]
    
    for filename in fixture_files:
        filepath = FIXTURES_DIR / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert isinstance(data, dict)
                # Node.js로 전달 가능한 JSON인지 재확인
                json_str = json.dumps(data, ensure_ascii=False)
                assert len(json_str) > 0
