"""
Mock embeddings를 사용한 Retriever 의존성 주입 테스트
"""
import pytest
from unittest.mock import MagicMock
from backend.retriever import Retriever


class MockEmbeddings:
    """테스트용 Mock Embeddings 클래스"""
    
    def __init__(self, dimension=384):
        self.dimension = dimension
        self.call_count = 0
    
    def embed_query(self, text: str):
        """고정된 벡터 반환 (테스트용)"""
        self.call_count += 1
        # 간단한 벡터 생성 (실제 임베딩 대신)
        return [0.1] * self.dimension


def test_embeddings_dependency_injection():
    """Embeddings client 의존성 주입 테스트"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    # Mock embeddings 생성
    mock_embeddings = MockEmbeddings(dimension=384)
    
    # Mock을 주입하여 Retriever 생성
    retriever = Retriever(
        db_url=db_url,
        embeddings_client=mock_embeddings
    )
    
    try:
        # embeddings가 주입된 mock인지 확인
        assert retriever.embeddings is mock_embeddings
        
        # 검색 실행 (mock 벡터로는 실제 결과가 없을 수 있음)
        docs = retriever.search("東京のおすすめレストラン", top_k=3)
        
        # Mock이 호출되었는지 확인 (중요!)
        assert mock_embeddings.call_count == 1
        
        # 결과는 리스트여야 함 (빈 리스트일 수도 있음)
        assert isinstance(docs, list)
        
        # 만약 결과가 있다면, Document 구조를 갖춰야 함
        if len(docs) > 0:
            assert all(hasattr(doc, 'page_content') for doc in docs)
            assert all(hasattr(doc, 'metadata') for doc in docs)
    
    finally:
        retriever.close()


def test_default_embeddings_without_injection():
    """의존성 주입 없이 기본 HuggingFace embeddings 사용 테스트"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    # embeddings_client를 주입하지 않음 (기본값 사용)
    retriever = Retriever(db_url=db_url)
    
    try:
        # HuggingFaceEmbeddings가 생성되었는지 확인
        assert retriever.embeddings is not None
        assert hasattr(retriever.embeddings, 'embed_query')
        
        # 실제 임베딩으로 검색 가능한지 확인
        docs = retriever.search("大阪の観光スポット", top_k=2)
        
        assert len(docs) > 0
    
    finally:
        retriever.close()


def test_mock_embeddings_with_search_expansion():
    """Query expansion에서도 mock embeddings 동작 확인"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    # Mock embeddings 생성
    mock_embeddings = MockEmbeddings(dimension=384)
    
    # Retriever에 주입
    with Retriever(db_url=db_url, embeddings_client=mock_embeddings) as retriever:
        # Expansion으로 검색
        docs = retriever.search_with_expansion(
            query="東京のレストラン",
            top_k=3,
            variations=["東京のおすすめレストラン"]
        )
        
        # Mock이 여러 번 호출되었는지 확인 (원본 + variations)
        assert mock_embeddings.call_count >= 2
        
        # 결과 확인
        assert isinstance(docs, list)


def test_embeddings_interface_compatibility():
    """Mock embeddings가 필수 인터페이스를 구현하는지 확인"""
    mock = MockEmbeddings()
    
    # embed_query 메서드 존재 확인
    assert hasattr(mock, 'embed_query')
    assert callable(mock.embed_query)
    
    # 반환 타입 확인
    result = mock.embed_query("test query")
    assert isinstance(result, list)
    assert len(result) == 384
    assert all(isinstance(x, float) for x in result)
