"""
Unit tests for Retriever helper methods.
Tests individual helper methods in isolation.
"""
import pytest
from unittest.mock import MagicMock, patch
from backend.retriever import Retriever
from langchain_core.documents import Document


class TestRetrieverHelpers:
    """Test suite for Retriever private helper methods."""
    
    @pytest.fixture
    def retriever(self):
        """Create a Retriever instance for testing."""
        db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
        return Retriever(db_url=db_url)
    
    def test_embed_query_returns_vector(self, retriever):
        """Test that _embed_query returns a vector of correct dimension."""
        query = "東京のおすすめレストラン"
        embedding = retriever._embed_query(query)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # multilingual-e5-small dimension
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embed_query_strips_whitespace(self, retriever):
        """Test that _embed_query strips leading/trailing whitespace."""
        query_with_spaces = "  東京のおすすめレストラン  "
        query_clean = "東京のおすすめレストラン"
        
        embedding_spaces = retriever._embed_query(query_with_spaces)
        embedding_clean = retriever._embed_query(query_clean)
        
        # Should produce same embedding (whitespace stripped)
        assert embedding_spaces == embedding_clean
    
    def test_build_sql_no_filters(self, retriever):
        """Test SQL building with no domain/area filters."""
        query_embedding = [0.1] * 384
        top_k = 5
        
        sql, params = retriever._build_sql_and_params(
            query_embedding, top_k, domain=None, area=None
        )
        
        # Should not have domain/area filters in WHERE clause
        assert "c.domain = %s" not in sql
        assert "c.area LIKE" not in sql
        # params should be: [query_embedding_str, query_embedding_str, top_k]
        assert isinstance(params, list)
        assert len(params) == 3
        assert params[2] == 5  # top_k
    
    def test_build_sql_with_domain_filter(self, retriever):
        """Test SQL building with domain filter only."""
        query_embedding = [0.1] * 384
        top_k = 5
        domain = "FOOD"
        
        sql, params = retriever._build_sql_and_params(
            query_embedding, top_k, domain=domain, area=None
        )
        
        # Should have domain filter
        assert "c.domain = %s" in sql
        assert "FOOD" in params
        assert params[-1] == 5  # top_k at end
        # Should not have area filter
        assert "c.area LIKE" not in sql
    
    def test_build_sql_with_area_filter(self, retriever):
        """Test SQL building with area filter only."""
        query_embedding = [0.1] * 384
        top_k = 10
        area = "東京都"
        
        sql, params = retriever._build_sql_and_params(
            query_embedding, top_k, domain=None, area=area
        )
        
        # Should have area filter with LIKE pattern
        assert "c.area LIKE %s" in sql
        assert "c.place_name LIKE %s" in sql
        assert "c.title LIKE %s" in sql
        # Area pattern should be in params with wildcards
        assert any("%東京都%" in str(p) for p in params)
        assert params[-1] == 10  # top_k at end
        # Should not have domain filter
        assert "c.domain = %s" not in sql
    
    def test_build_sql_with_both_filters(self, retriever):
        """Test SQL building with both domain and area filters."""
        query_embedding = [0.1] * 384
        top_k = 3
        domain = "STAY"
        area = "大阪府"
        
        sql, params = retriever._build_sql_and_params(
            query_embedding, top_k, domain=domain, area=area
        )
        
        # Should have both filters
        assert "c.domain = %s" in sql
        assert "c.area LIKE %s" in sql
        assert "STAY" in params
        assert any("%大阪府%" in str(p) for p in params)
        assert params[-1] == 3  # top_k at end
    
    def test_rows_to_documents_basic(self, retriever):
        """Test converting DB rows to Document objects."""
        # Mock DB rows matching actual query structure:
        # (chunk_text, question, answer, domain, title, place_name, area, 
        #  source_url, document_id, summary_text, distance, similarity)
        mock_rows = [
            (
                "子ドキュメント1のテキスト",  # chunk_text
                "質問1",  # question
                "回答1",  # answer
                "FOOD",  # domain
                "タイトル1",  # title
                "場所1",  # place_name
                "東京都",  # area
                "http://example.com/1",  # source_url
                101,  # document_id
                "親ドキュメント1の要約",  # summary_text
                0.15,  # distance
                0.85,  # similarity (1 - 0.15 distance)
            ),
            (
                "子ドキュメント2のテキスト",
                "質問2",
                "回答2",
                "STAY",
                "タイトル2",
                "場所2",
                "大阪府",
                "http://example.com/2",
                102,
                "親ドキュメント2の要約",
                0.25,  # distance
                0.75,  # similarity (1 - 0.25 distance)
            ),
        ]
        
        documents = retriever._rows_to_documents(mock_rows)
        
        assert len(documents) == 2
        
        # Check first document
        doc1 = documents[0]
        assert isinstance(doc1, Document)
        assert "親ドキュメント1の要約" in doc1.page_content
        assert "質問1" in doc1.page_content
        assert "回答1" in doc1.page_content
        assert doc1.metadata["document_id"] == 101
        assert doc1.metadata["parent_summary"] == "親ドキュメント1の要約"
        assert doc1.metadata["distance"] == 0.15
        assert doc1.metadata["similarity"] == 0.85
        assert doc1.metadata["domain"] == "FOOD"
        assert doc1.metadata["area"] == "東京都"
        
        # Check second document
        doc2 = documents[1]
        assert isinstance(doc2, Document)
        assert "親ドキュメント2の要約" in doc2.page_content
        assert doc2.metadata["document_id"] == 102
        assert doc2.metadata["distance"] == 0.25
        assert doc2.metadata["similarity"] == 0.75
        assert doc2.metadata["domain"] == "STAY"
    
    def test_rows_to_documents_empty(self, retriever):
        """Test converting empty row list returns empty document list."""
        documents = retriever._rows_to_documents([])
        assert documents == []
    
    def test_rows_to_documents_preserves_metadata(self, retriever):
        """Test that metadata from DB is preserved in Document."""
        mock_rows = [
            (
                "テキスト",  # chunk_text
                "質問",  # question
                "回答",  # answer
                "FOOD",  # domain
                "カスタムタイトル",  # title
                "カスタム場所",  # place_name
                "北海道",  # area
                "http://example.com/custom",  # source_url
                301,  # document_id
                "要約テキスト",  # summary_text
                0.1,  # distance
                0.9,  # similarity
            ),
        ]
        
        documents = retriever._rows_to_documents(mock_rows)
        
        assert len(documents) == 1
        doc = documents[0]
        # All metadata should be preserved
        assert doc.metadata["domain"] == "FOOD"
        assert doc.metadata["title"] == "カスタムタイトル"
        assert doc.metadata["place_name"] == "カスタム場所"
        assert doc.metadata["area"] == "北海道"
        assert doc.metadata["source_url"] == "http://example.com/custom"
        assert doc.metadata["document_id"] == 301
        assert doc.metadata["parent_summary"] == "要約テキスト"
        assert doc.metadata["distance"] == 0.1
        assert doc.metadata["similarity"] == 0.9
