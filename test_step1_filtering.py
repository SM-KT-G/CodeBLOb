"""
Step 1: Metadata Filtering 테스트
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.retriever import Retriever


def test_metadata_filtering():
    """Metadata Filtering 품질 테스트"""
    
    print("="*60)
    print("Step 1: Metadata Filtering 테스트")
    print("="*60)
    
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    retriever = Retriever(db_url=db_url)
    
    print("\n✅ Retriever 초기화 완료\n")
    
    # 테스트 케이스
    test_cases = [
        {
            "name": "테스트 1: 도메인 필터링 (음식점)",
            "query": "美味しいラーメン",
            "domain": "food",
            "area": None,
            "expected": "food 도메인만 검색"
        },
        {
            "name": "테스트 2: 지역 필터링 (서울)",
            "query": "観光スポット",
            "domain": None,
            "area": "서울",
            "expected": "서울 지역 결과만"
        },
        {
            "name": "테스트 3: 도메인 + 지역 필터링",
            "query": "温泉",
            "domain": "stay",
            "area": "부산",
            "expected": "부산 지역 숙박시설만"
        },
        {
            "name": "테스트 4: 필터 없음 (기본 검색)",
            "query": "歴史",
            "domain": None,
            "area": None,
            "expected": "모든 도메인에서 검색"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"{test['name']}")
        print(f"쿼리: {test['query']}")
        print(f"도메인: {test['domain']}, 지역: {test['area']}")
        print(f"기대: {test['expected']}")
        print('='*60)
        
        try:
            results = retriever.search(
                query=test['query'],
                top_k=3,
                domain=test['domain'],
                area=test['area']
            )
            
            print(f"\n📄 검색 결과: {len(results)}개\n")
            
            for j, doc in enumerate(results, 1):
                print(f"[{j}] Domain: {doc.metadata['domain']}")
                print(f"    Title: {doc.metadata['title'][:40]}...")
                print(f"    Area: {doc.metadata['area'] or '(없음)'}")
                print(f"    Place: {doc.metadata['place_name'][:30]}..." if doc.metadata['place_name'] else "    Place: (없음)")
                print(f"    Similarity: {doc.metadata['similarity']:.4f}")
                
                # 필터 검증
                if test['domain']:
                    assert doc.metadata['domain'] == test['domain'], f"❌ 도메인 필터 실패!"
                if test['area']:
                    area_found = test['area'] in (doc.metadata.get('area', '') or '') or \
                                 test['area'] in (doc.metadata.get('place_name', '') or '') or \
                                 test['area'] in (doc.metadata.get('title', '') or '')
                    if not area_found:
                        print(f"    ⚠️  지역 '{test['area']}'가 메타데이터에서 발견되지 않음")
                
                print()
            
            print(f"✅ 테스트 {i} 통과!")
            
        except Exception as e:
            print(f"❌ 테스트 {i} 실패: {e}")
    
    print("\n" + "="*60)
    print("✅ Step 1: Metadata Filtering 테스트 완료!")
    print("="*60)


if __name__ == "__main__":
    test_metadata_filtering()
