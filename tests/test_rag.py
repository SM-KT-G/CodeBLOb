"""
RAG 체인 후처리 테스트
"""
from langchain.schema import Document

from backend.rag_chain import process_rag_response


class TestProcessRAGResponse:
    """process_rag_response 동작 검증"""

    def test_deduplicates_sources_and_reports_metadata(self):
        """중복 출처를 제거하고 metadata.retrieved_count를 채운다."""
        mock_result = {
            "result": "テスト回答입니다。",
            "source_documents": [
                Document(page_content="doc1", metadata={"document_id": "DOC_001"}),
                Document(page_content="doc2", metadata={"document_id": "DOC_001"}),
                Document(page_content="doc3", metadata={"id": "DOC_002"}),
                Document(page_content="doc4", metadata={"source": "DOC_003"}),
            ],
        }

        processed = process_rag_response(mock_result)

        assert processed["answer"] == "テスト回答입니다。"
        assert processed["sources"] == ["DOC_001", "DOC_002", "DOC_003"]
        assert processed["metadata"]["retrieved_count"] == 4

    def test_handles_missing_ids(self):
        """id/source/document_id가 모두 없으면 Unknown으로 대체한다."""
        mock_result = {
            "result": "답변",
            "source_documents": [
                Document(page_content="doc-no-id", metadata={}),
            ],
        }

        processed = process_rag_response(mock_result)

        assert processed["sources"] == ["Unknown"]
        assert processed["metadata"]["retrieved_count"] == 1
