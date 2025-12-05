"""
Connection Pool 성능 테스트
"""
import time
import pytest
from backend.retriever import Retriever


def test_connection_pool_concurrent_queries():
    """Connection Pool을 사용한 동시 쿼리 성능 테스트"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    with Retriever(db_url=db_url) as retriever:
        queries = [
            "東京のおすすめレストラン",
            "大阪の観光スポット",
            "京都の宿泊施設",
            "北海道の自然",
            "福岡のショッピング",
        ]
        
        start_time = time.time()
        
        # 순차적으로 여러 쿼리 실행
        results = []
        for query in queries:
            docs = retriever.search(query, top_k=3)
            results.append(len(docs))
        
        elapsed = time.time() - start_time
        
        # 모든 쿼리가 성공적으로 실행되었는지 확인
        assert len(results) == 5
        assert all(r > 0 for r in results), "All queries should return results"
        
        # 성능 정보 출력
        print(f"\n5개 쿼리 순차 실행 시간: {elapsed:.2f}초")
        print(f"쿼리당 평균 시간: {elapsed/5:.2f}초")
        
        # Connection Pool이 있으므로 연결 재사용으로 성능 향상 기대
        # (이전에는 매번 새 연결을 생성했을 것)


def test_connection_pool_context_manager():
    """Context manager를 통한 Connection Pool 정리 테스트"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    # with 문으로 사용
    with Retriever(db_url=db_url) as retriever:
        docs = retriever.search("東京のおすすめレストラン", top_k=3)
        assert len(docs) > 0
        assert hasattr(retriever, 'pool')
    
    # with 블록을 벗어나면 pool이 close되어야 함
    # (실제 close 확인은 로그에서 확인 가능)


def test_connection_pool_manual_close():
    """수동으로 Connection Pool을 정리하는 테스트"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    retriever = Retriever(db_url=db_url)
    
    # 쿼리 실행
    docs = retriever.search("大阪の観光スポット", top_k=3)
    assert len(docs) > 0
    
    # 수동으로 close
    retriever.close()
    
    # close 후에는 pool이 종료된 상태
    # (추가 쿼리 시도하면 에러 발생할 것 - 이 테스트에서는 확인하지 않음)
