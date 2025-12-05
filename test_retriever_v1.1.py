"""
v1.1 Retriever 테스트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

from backend.retriever import Retriever


def test_retriever():
    """Retriever 기본 동작 테스트"""
    
    print("🔍 Retriever 테스트 시작\n")
    
    # DB URL 구성
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    print(f"DB URL: {db_url}\n")
    
    # Retriever 초기화
    print("📦 Retriever 초기화 중...")
    retriever = Retriever(
        db_url=db_url,
        embedding_model="intfloat/multilingual-e5-small"
    )
    print("✅ Retriever 초기화 완료\n")
    
    # 테스트 쿼리
    test_queries = [
        "東京で美味しいラーメン店を教えてください",
        "温泉旅館のおすすめはありますか",
        "歴史的な観光地を知りたい"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"테스트 {i}: {query}")
        print('='*60)
        
        try:
            # 검색 실행
            results = retriever.search(query=query, top_k=3)
            
            print(f"\n📄 검색 결과: {len(results)}개\n")
            
            for j, doc in enumerate(results, 1):
                print(f"[{j}] Content: {doc.page_content[:100]}...")
                print(f"    Metadata: {doc.metadata}")
                print()
        
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
    
    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    test_retriever()
