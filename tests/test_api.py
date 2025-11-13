"""
FastAPI API 통합 테스트 (TDD용)
"""
from dataclasses import dataclass
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import backend.main as main_module
from backend.main import app


@dataclass
class StubDocument:
    """RAG 테스트용 문서 스텁"""
    page_content: str
    metadata: Dict[str, Any]


def test_rag_query_returns_chain_answer(monkeypatch):
    """
    `/rag/query`가 RAG 체인 결과를 그대로 응답에 반영하는지 검증.
    chain.invoke()가 반환한 `result`와 `source_documents`를 사용해야 한다.
    """
    # 환경 변수 세팅 (lifespan에서 검증)
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test_user:test_pass@localhost:5432/test_db")

    stub_docs = [
        StubDocument(
            page_content="stub content",
            metadata={"document_id": "DOC_123"},
        )
    ]

    class DummyRetriever:
        """실제 DB 의존성을 제거한 더미 Retriever"""

        def __init__(self, db_url: str):
            self.db_url = db_url
            self.search_call_count = 0
            self.search_with_expansion_call_count = 0

        def search(self, *_, **__):
            self.search_call_count += 1
            return stub_docs

        def search_with_expansion(self, *_, **__):
            self.search_with_expansion_call_count += 1
            return stub_docs

        def close(self):
            """lifespan 종료 시 호출되는 메서드"""
            return None

    fake_chain = MagicMock()
    fake_chain.invoke.return_value = {
        "result": "LLM 기반 응답",
        "source_documents": stub_docs,
    }

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "init_cache_from_env", lambda: None)
    monkeypatch.setattr(main_module, "create_rag_chain", lambda **kwargs: fake_chain, raising=False)

    with TestClient(app) as client:
        response = client.post(
            "/rag/query",
            json={
                "question": "東京のおすすめレストランを教えて",
                "top_k": 2,
                "expansion": False,
                "parent_context": True,
            },
        )

    assert response.status_code == 200
    data = response.json()

    assert data["answer"] == "LLM 기반 응답"
    assert data["sources"] == ["DOC_123"]
    assert isinstance(data["latency"], float)

    fake_chain.invoke.assert_called_once()


def test_rag_query_parent_context_false_strips_parent_summary(monkeypatch):
    """
    parent_context=False일 때 fallback 경로에서도 parent summary가 제거되는지 검증.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test_user:test_pass@localhost:5432/test_db")

    page = (
        "親ドキュメント要約:\n서울 소개\n\n質問:\nおすすめ?\n\n回答:\n楽しいです\n"
    )

    stub_docs = [
        StubDocument(
            page_content=page,
            metadata={"document_id": "DOC_PARENT"},
        )
    ]

    class DummyRetriever:
        def __init__(self, db_url: str):
            self.db_url = db_url

        def search(self, *_, **__):
            return stub_docs

        def search_with_expansion(self, *_, **__):
            return stub_docs

        def close(self):
            return None

    def raise_chain(**kwargs):
        raise RuntimeError("chain failure")

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "create_rag_chain", raise_chain, raising=False)
    monkeypatch.setattr(main_module, "init_cache_from_env", lambda: None)

    with TestClient(app) as client:
        response = client.post(
            "/rag/query",
            json={
                "question": "서울?",
                "top_k": 1,
                "parent_context": False,
            },
        )

    assert response.status_code == 200
    data = response.json()

    assert "親ドキュメント要約" not in data["answer"]
    assert "質問:" in data["answer"]


def test_health_check_reports_db_and_llm_status(monkeypatch):
    """
    /health가 DB와 LLM 상태를 체크 항목으로 노출하는지 검증.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")

    class DummyRetriever:
        def __init__(self, db_url: str):
            self.db_url = db_url

        def close(self):
            return None

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "execute_retriever_query", lambda **kwargs: [])
    monkeypatch.setattr(main_module, "init_cache_from_env", lambda: None)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "db" in data["checks"]
    assert "llm" in data["checks"]
    assert "cache" in data["checks"]


def test_rag_query_returns_expansion_metrics_in_metadata(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test_user:test_pass@localhost:5432/test_db")

    stub_docs = [
        StubDocument(
            page_content="stub content",
            metadata={"document_id": "DOC_EXP"},
        )
    ]

    class DummyRetriever:
        def __init__(self, db_url: str):
            self.db_url = db_url
            self.last_expansion_metrics = None

        def search(self, *_, **__):
            return stub_docs

        def search_with_expansion(self, *_, **__):
            self.last_expansion_metrics = {
                "variants": ["원본", "추천"],
                "success_count": 2,
                "failure_count": 0,
                "retrieved": 1,
                "cache_hit": False,
            }
            return stub_docs

        def close(self):
            return None

    def raise_chain(**kwargs):
        raise RuntimeError("chain failure")

    monkeypatch.setattr(main_module, "Retriever", lambda db_url, **_: DummyRetriever(db_url))
    monkeypatch.setattr(main_module, "init_cache_from_env", lambda: None)
    monkeypatch.setattr(main_module, "create_rag_chain", raise_chain, raising=False)

    with TestClient(app) as client:
        response = client.post(
            "/rag/query",
            json={
                "question": "大阪 グルメ",
                "top_k": 2,
                "expansion": True,
                "parent_context": True,
            },
        )

    data = response.json()
    assert data["metadata"]["expansion_metrics"]["variants"] == ["원본", "추천"]
    assert data["metadata"]["expansion_metrics"]["success_count"] == 2
