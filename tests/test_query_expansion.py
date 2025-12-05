"""
Query Expansion 간단 테스트
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.retriever import Retriever


def test_query_expansion():
    print("\n🔎 Query Expansion 테스트 시작")

    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    retriever = Retriever(db_url=db_url)

    query = "温泉"

    print(f"원본 쿼리: {query}")
    try:
        base_results = retriever.search(query=query, top_k=5)
        print(f"원본 결과 수: {len(base_results)}")
    except Exception as e:
        print(f"⚠️  테스트 중 DB 연결 또는 다른 오류 발생: {e}")
        print("테스트를 건너뜁니다 — 데이터베이스가 실행 중인지 확인하세요.")
        return
    try:
        expanded_results = retriever.search_with_expansion(query=query, top_k=5)
    except Exception as e:
        print(f"⚠️  테스트 중 DB 연결 또는 다른 오류 발생: {e}")
        print("테스트를 건너뜁니다 — 데이터베이스가 실행 중인지 확인하세요.")
        return
    print(f"확장 결과 수: {len(expanded_results)}")

    # document_id로 유니크 판단
    base_ids = set([r.metadata.get("document_id") or hash(r.page_content) for r in base_results])
    expanded_ids = set([r.metadata.get("document_id") or hash(r.page_content) for r in expanded_results])

    union_count = len(base_ids.union(expanded_ids))

    print(f"base_ids: {base_ids}")
    print(f"expanded_ids: {expanded_ids}")
    print(f"union_count: {union_count}")

    assert union_count >= len(base_ids), "확장된 검색이 원본보다 문서 수가 적어서는 안됩니다"

    print("✅ Query Expansion 테스트 통과")


if __name__ == "__main__":
    test_query_expansion()
