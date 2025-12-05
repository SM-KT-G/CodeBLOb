"""
Query Expansion 병렬 처리 성능 측정 테스트
TDD: Red → Green → Refactor
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from langchain.schema import Document


@pytest.mark.asyncio
async def test_parallel_expansion_should_be_faster_than_sequential():
    """
    병렬 처리가 순차 처리보다 빨라야 한다.
    
    Given: 3개의 쿼리 변형이 있고 각각 100ms 걸릴 때
    When: 병렬과 순차로 실행하면
    Then: 병렬이 최소 2배 이상 빨라야 한다
    """
    from backend.retriever import Retriever
    
    # Mock embeddings
    mock_embeddings = Mock()
    mock_embeddings.embed_query = Mock(return_value=[0.1] * 384)
    
    with patch('backend.retriever.ConnectionPool') as mock_pool:
        mock_pool.return_value = Mock()
        
        retriever = Retriever(
            db_url="postgresql://test",
            embeddings_client=mock_embeddings
        )
        
        # Mock search with 100ms delay
        search_count = 0
        
        def mock_search_sync(query, top_k=5, domain=None, area=None):
            nonlocal search_count
            search_count += 1
            time.sleep(0.1)  # 100ms delay
            return [
                Document(
                    page_content=f"Result {search_count}",
                    metadata={"document_id": f"doc_{search_count}", "similarity": 0.9}
                )
            ]
        
        async def mock_search_async(query, top_k=5, domain=None, area=None):
            await asyncio.sleep(0.1)  # 100ms delay
            return [
                Document(
                    page_content=f"Result for {query}",
                    metadata={"document_id": f"doc_{query}", "similarity": 0.9}
                )
            ]
        
        # 순차 실행 측정
        with patch.object(retriever, 'search', side_effect=mock_search_sync):
            start_time = time.perf_counter()
            seq_results = retriever.search_with_expansion(
                query="서울 맛집",
                top_k=5
            )
            seq_duration = time.perf_counter() - start_time
        
        # 병렬 실행 측정
        with patch.object(retriever, 'search_async', side_effect=mock_search_async):
            start_time = time.perf_counter()
            par_results = await retriever.search_with_expansion_async(
                query="서울 맛집",
                top_k=5
            )
            par_duration = time.perf_counter() - start_time
        
        # 성능 검증
        speedup = seq_duration / par_duration
        
        print(f"\n성능 측정 결과:")
        print(f"  순차 실행: {seq_duration:.3f}초")
        print(f"  병렬 실행: {par_duration:.3f}초")
        print(f"  속도 향상: {speedup:.2f}배")
        
        # 병렬이 최소 2배 이상 빨라야 함
        assert speedup >= 2.0, \
            f"병렬 처리가 충분히 빠르지 않습니다. 속도 향상: {speedup:.2f}배 (기대: 2.0배 이상)"
        
        # 결과는 동일해야 함
        assert len(seq_results) > 0
        assert len(par_results) > 0


@pytest.mark.asyncio
async def test_parallel_expansion_metrics_should_show_performance_gain():
    """
    병렬 처리 메트릭이 성능 향상을 보여줘야 한다.
    
    Given: Query Expansion을 병렬로 실행할 때
    When: last_expansion_metrics를 확인하면
    Then: duration_ms가 순차 실행보다 짧아야 한다
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
        
        async def mock_search_async(query, top_k=5, domain=None, area=None):
            await asyncio.sleep(0.05)  # 50ms delay
            return [
                Document(
                    page_content=f"Result for {query}",
                    metadata={"document_id": f"doc_{query}", "similarity": 0.9}
                )
            ]
        
        with patch.object(retriever, 'search_async', side_effect=mock_search_async):
            results = await retriever.search_with_expansion_async(
                query="서울 맛집",
                top_k=5
            )
        
        # 메트릭 검증
        metrics = retriever.last_expansion_metrics
        assert metrics is not None, "메트릭이 기록되어야 합니다"
        
        # 3개 변형 × 50ms = 150ms (순차)
        # 병렬로는 ~50-70ms 정도 예상
        assert metrics["duration_ms"] < 100, \
            f"병렬 실행 시간이 너무 깁니다: {metrics['duration_ms']}ms (기대: <100ms)"
        
        assert metrics["success_count"] >= 2, "최소 2개 이상 성공해야 합니다"
        
        print(f"\n메트릭 결과:")
        print(f"  실행 시간: {metrics['duration_ms']}ms")
        print(f"  성공: {metrics['success_count']}개")
        print(f"  실패: {metrics['failure_count']}개")
        print(f"  검색된 문서: {metrics['retrieved']}개")


@pytest.mark.asyncio
async def test_performance_should_scale_with_variations():
    """
    쿼리 변형 개수가 늘어나도 병렬 처리는 시간이 선형 증가하지 않아야 한다.
    
    Given: 쿼리 변형이 3개 → 6개로 늘어날 때
    When: 병렬 실행 시간을 측정하면
    Then: 2배보다 훨씬 작게 증가해야 한다 (1.5배 이하)
    """
    from backend.retriever import Retriever
    from backend.query_expansion import generate_variations
    
    mock_embeddings = Mock()
    mock_embeddings.embed_query = Mock(return_value=[0.1] * 384)
    
    with patch('backend.retriever.ConnectionPool') as mock_pool:
        mock_pool.return_value = Mock()
        
        retriever = Retriever(
            db_url="postgresql://test",
            embeddings_client=mock_embeddings
        )
        
        async def mock_search_async(query, top_k=5, domain=None, area=None):
            await asyncio.sleep(0.05)  # 50ms delay
            return [
                Document(
                    page_content=f"Result for {query}",
                    metadata={"document_id": f"doc_{query}", "similarity": 0.9}
                )
            ]
        
        # 3개 변형 테스트
        with patch('backend.query_expansion.generate_variations') as mock_gen:
            mock_gen.return_value = ["query1", "query2", "query3"]
            
            with patch.object(retriever, 'search_async', side_effect=mock_search_async):
                start = time.perf_counter()
                await retriever.search_with_expansion_async(query="test", top_k=5)
                duration_3 = time.perf_counter() - start
        
        # 6개 변형 테스트
        with patch('backend.query_expansion.generate_variations') as mock_gen:
            mock_gen.return_value = ["q1", "q2", "q3", "q4", "q5", "q6"]
            
            with patch.object(retriever, 'search_async', side_effect=mock_search_async):
                start = time.perf_counter()
                await retriever.search_with_expansion_async(query="test", top_k=5)
                duration_6 = time.perf_counter() - start
        
        ratio = duration_6 / duration_3
        
        print(f"\n확장성 테스트:")
        print(f"  3개 변형: {duration_3:.3f}초")
        print(f"  6개 변형: {duration_6:.3f}초")
        print(f"  증가율: {ratio:.2f}배")
        
        # 병렬 처리이므로 2배가 아닌 1.5배 이하여야 함
        assert ratio < 1.5, \
            f"병렬 처리 확장성이 좋지 않습니다: {ratio:.2f}배 (기대: <1.5배)"
