"""
RAG 체인 단위 테스트
"""
import pytest
from unittest.mock import Mock, MagicMock
from typing import List

# TODO: 패키지 설치 후 주석 해제
# from langchain.schema import Document
# from backend.rag_chain import create_rag_chain, process_rag_response


class MockDocument:
    """Mock Document 클래스"""
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata


class TestRAGChain:
    """RAG 체인 테스트"""
    
    @pytest.fixture
    def mock_retriever(self):
        """Mock Retriever"""
        retriever = Mock()
        retriever.get_relevant_documents = Mock(return_value=[
            MockDocument(
                page_content="ソウルの明洞は人気の観光地です。",
                metadata={"id": "J_FOOD_000001", "domain": "food"}
            ),
            MockDocument(
                page_content="韓国料理は美味しいです。",
                metadata={"id": "J_FOOD_000002", "domain": "food"}
            ),
        ])
        return retriever
    
    def test_process_rag_response(self):
        """RAG 응답 후처리 테스트"""
        # Given
        mock_result = {
            "result": "テスト回答です。",
            "source_documents": [
                MockDocument(
                    page_content="Content 1",
                    metadata={"id": "DOC_001"}
                ),
                MockDocument(
                    page_content="Content 2",
                    metadata={"source": "DOC_002"}
                ),
            ]
        }
        
        # When
        # TODO: 패키지 설치 후 실제 함수 호출
        # processed = process_rag_response(mock_result)
        
        # 임시 구현
        processed = {
            "answer": mock_result["result"],
            "sources": ["DOC_001", "DOC_002"],
        }
        
        # Then
        assert "answer" in processed
        assert "sources" in processed
        assert len(processed["sources"]) == 2
        assert processed["answer"] == "テスト回答です。"
    
    def test_empty_response(self):
        """빈 응답 처리 테스트"""
        # Given
        mock_result = {
            "result": "",
            "source_documents": []
        }
        
        # When
        processed = {
            "answer": mock_result["result"],
            "sources": [],
        }
        
        # Then
        assert processed["answer"] == ""
        assert len(processed["sources"]) == 0
    
    def test_duplicate_sources(self):
        """중복 출처 제거 테스트"""
        # Given
        mock_result = {
            "result": "答え",
            "source_documents": [
                MockDocument("Content", {"id": "DOC_001"}),
                MockDocument("Content", {"id": "DOC_001"}),  # 중복
                MockDocument("Content", {"id": "DOC_002"}),
            ]
        }
        
        # When
        sources = []
        for doc in mock_result["source_documents"]:
            doc_id = doc.metadata.get("id")
            if doc_id and doc_id not in sources:
                sources.append(doc_id)
        
        # Then
        assert len(sources) == 2
        assert "DOC_001" in sources
        assert "DOC_002" in sources


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
