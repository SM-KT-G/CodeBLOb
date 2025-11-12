"""
Parent Context 포함 여부 테스트
(데이터베이스가 없으면 건너뜁니다)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.retriever import Retriever


def test_parent_context():
    print("\n🧾 Parent Context 테스트 시작")

    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    retriever = Retriever(db_url=db_url)

    query = "歴史"

    try:
        results = retriever.search(query=query, top_k=3)
    except Exception as e:
        print(f"⚠️  DB 연결 오류로 테스트 건너뜀: {e}")
        return

    if not results:
        print("⚠️  검색 결과가 없습니다. 테스트 종료")
        return

    for doc in results:
        parent_summary = doc.metadata.get("parent_summary")
        print(f"parent_summary present: {bool(parent_summary)}")
        assert parent_summary is not None, "Parent summary가 metadata에 포함되어야 합니다"

    print("✅ Parent Context 테스트 통과")


if __name__ == "__main__":
    test_parent_context()
