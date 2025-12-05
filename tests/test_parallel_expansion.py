"""
Query Expansion 병렬 처리 테스트
TDD: Red → Green → Refactor
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from langchain.schema import Document


@pytest.mark.asyncio
async def test_search_with_expansion_async_should_run_in_parallel():
    """
    Query Expansion이 병렬로 실행되어야 한다.
    
    Given: 3개의 쿼리 변형이 있을 때
    When: search_with_expansion_async를 호출하면
    Then: 3개의 검색이 동시에 실행되어야 한다 (순차 실행보다 빠름)
    """
    from backend.retriever import Retriever
    
    # Mock embeddings client
    mock_embeddings = Mock()
    mock_embeddings.embed_query = Mock(return_value=[0.1] * 384)
    
    # Mock DB connection pool
    with patch('backend.retriever.ConnectionPool') as mock_pool:
        mock_pool.return_value = Mock()
        
        retriever = Retriever(
            db_url="postgresql://test",
            embeddings_client=mock_embeddings
        )
        
        # Mock search method to simulate delay
        async def mock_search_async(query, top_k=5, domain=None, area=None):
            await asyncio.sleep(0.1)  # 각 검색이 100ms 걸린다고 가정
            return [
                Document(
                    page_content=f"Result for {query}",
                    metadata={"document_id": f"doc_{query}", "similarity": 0.9}
                )
            ]
        
        # Async method should exist
        assert hasattr(retriever, 'search_with_expansion_async'), \
            "search_with_expansion_async 메서드가 존재해야 합니다"
        
        # Patch search to be async
        with patch.object(retriever, 'search_async', side_effect=mock_search_async):
            start_time = asyncio.get_event_loop().time()
            
            # 3개 변형 → 병렬 실행 시 ~100ms, 순차 실행 시 ~300ms
            results = await retriever.search_with_expansion_async(
                query="서울 맛집",
                top_k=5
            )
            
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            # 병렬 실행이므로 200ms 이내에 완료되어야 함 (순차는 300ms+)
            assert duration < 0.2, \
                f"병렬 실행이 아닙니다. 걸린 시간: {duration:.2f}초 (기대: <0.2초)"
            
            assert len(results) > 0, "결과가 반환되어야 합니다"


@pytest.mark.asyncio
async def test_search_with_expansion_async_should_merge_and_deduplicate():
    """
    병렬 검색 결과가 올바르게 병합되고 중복 제거되어야 한다.
    
    Given: 여러 변형에서 동일한 문서가 검색될 때
    When: search_with_expansion_async를 호출하면
    Then: 중복이 제거되고 가장 높은 유사도만 유지되어야 한다
    """
    from backend.retriever import Retriever
    
    mock_embeddings = Mock()
    mock_embeddings.embed_query = Mock(return_value=[0.1] * 384)
    
    with patch('backend.retriever.ConnectionPool') as mock_pool:
        mock_pool.return_value = Mock()
        
        retriever = Retriever(
            db_url="postgresql://test",
            embeddings_client=mock_embeddings
        )
        
        # Mock search_async to return overlapping results
        async def mock_search_async(query, top_k=5, domain=None, area=None):
            if "맛집" in query:
                return [
                    Document(
                        page_content="명동 교자",
                        metadata={"document_id": "doc_001", "similarity": 0.95}
                    ),
                    Document(
                        page_content="광장시장",
                        metadata={"document_id": "doc_002", "similarity": 0.90}
                    )
                ]
            else:
                # 다른 변형에서 동일 문서 + 낮은 유사도
                return [
                    Document(
                        page_content="명동 교자",
                        metadata={"document_id": "doc_001", "similarity": 0.85}
                    ),
                    Document(
                        page_content="북촌 한옥마을",
                        metadata={"document_id": "doc_003", "similarity": 0.88}
                    )
                ]
        
        with patch.object(retriever, 'search_async', side_effect=mock_search_async):
            results = await retriever.search_with_expansion_async(
                query="서울 맛집",
                top_k=5
            )
            
            # doc_001은 한 번만 나타나야 하고, 더 높은 유사도(0.95)를 가져야 함
            doc_ids = [doc.metadata["document_id"] for doc in results]
            assert len(doc_ids) == len(set(doc_ids)), "중복 문서가 제거되어야 합니다"
            
            doc_001 = next(doc for doc in results if doc.metadata["document_id"] == "doc_001")
            assert doc_001.metadata["similarity"] == 0.95, \
                "가장 높은 유사도가 유지되어야 합니다"


@pytest.mark.asyncio
async def test_search_with_expansion_async_should_handle_failures_gracefully():
    """
    일부 변형 검색이 실패해도 전체 검색은 계속되어야 한다.
    
    Given: 3개 변형 중 1개가 실패할 때
    When: search_with_expansion_async를 호출하면
    Then: 나머지 2개 결과는 정상 반환되어야 한다
    """
    from backend.retriever import Retriever
    
    mock_embeddings = Mock()
    mock_embeddings.embed_query = Mock(return_value=[0.1] * 384)
    
    with patch('backend.retriever.ConnectionPool') as mock_pool:
        mock_pool.return_value = Mock()
        
        retriever = Retriever(
            db_url="postgresql://test",
            embeddings_client=mock_embeddings
        )
        
        call_count = 0
        
        async def mock_search_async(query, top_k=5, domain=None, area=None):
            nonlocal call_count
            call_count += 1
            
            # 두 번째 호출만 실패
            if call_count == 2:
                raise Exception("DB connection error")
            
            return [
                Document(
                    page_content=f"Result {call_count}",
                    metadata={"document_id": f"doc_{call_count}", "similarity": 0.9}
                )
            ]
        
        with patch.object(retriever, 'search_async', side_effect=mock_search_async):
            results = await retriever.search_with_expansion_async(
                query="서울 맛집",
                top_k=5
            )
            
            # 실패한 1개를 제외하고 2개 결과는 반환되어야 함
            assert len(results) >= 2, "실패한 변형을 제외한 결과가 반환되어야 합니다"
            
            # metrics에 실패 카운트가 기록되어야 함
            assert retriever.last_expansion_metrics is not None
            assert retriever.last_expansion_metrics.get("failure_count", 0) > 0


@pytest.mark.asyncio
async def test_search_async_should_exist():
    """
    search_async 메서드가 존재하고 비동기로 동작해야 한다.
    
    Given: Retriever 인스턴스가 있을 때
    When: search_async를 호출하면
    Then: 비동기로 검색 결과를 반환해야 한다
    """
    from backend.retriever import Retriever
    
    mock_embeddings = Mock()
    mock_embeddings.embed_query = Mock(return_value=[0.1] * 384)
    
    with patch('backend.retriever.ConnectionPool') as mock_pool:
        # Mock connection and cursor properly
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (
                "서울 명동 교자 맛집",  # chunk_text
                "명동 교자는 어떤 곳인가요?",  # question
                "칼국수와 만두로 유명한 맛집입니다.",  # answer
                "food",  # domain_val
                "서울 맛집 가이드",  # title
                "명동 교자",  # place_name
                "서울",  # area
                "http://example.com/doc1",  # source_url
                "child_001",  # document_id
                "서울 명동 교자 요약",  # summary_text
                0.05,  # distance
                0.95  # similarity
            )
        ]
        
        mock_conn = Mock()
        mock_conn.cursor.return_value = Mock(__enter__=Mock(return_value=mock_cursor), __exit__=Mock())
        
        mock_pool_instance = Mock()
        mock_pool_instance.connection.return_value = Mock(
            __enter__=Mock(return_value=mock_conn),
            __exit__=Mock()
        )
        mock_pool.return_value = mock_pool_instance
        
        retriever = Retriever(
            db_url="postgresql://test",
            embeddings_client=mock_embeddings
        )
        
        # search_async should exist
        assert hasattr(retriever, 'search_async'), \
            "search_async 메서드가 존재해야 합니다"
        
        # Should be async
        result = retriever.search_async(query="서울 맛집", top_k=5)
        assert asyncio.iscoroutine(result), "search_async는 코루틴을 반환해야 합니다"
        
        # Await and check result
        docs = await result
        assert len(docs) > 0, "검색 결과가 반환되어야 합니다"
        assert docs[0].metadata["similarity"] == 0.95
