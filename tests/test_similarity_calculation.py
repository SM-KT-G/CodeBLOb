"""
Similarity와 Distance 계산 검증 테스트
"""
import pytest
from backend.retriever import Retriever


def test_similarity_and_distance_in_metadata():
    """검색 결과의 metadata에 distance와 similarity가 모두 포함되는지 확인"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    with Retriever(db_url=db_url) as retriever:
        docs = retriever.search("東京のおすすめレストラン", top_k=3)
        
        assert len(docs) > 0, "검색 결과가 있어야 함"
        
        for doc in docs:
            # distance와 similarity가 모두 metadata에 포함되어야 함
            assert "distance" in doc.metadata, "distance가 metadata에 없음"
            assert "similarity" in doc.metadata, "similarity가 metadata에 없음"
            
            distance = doc.metadata["distance"]
            similarity = doc.metadata["similarity"]
            
            # 타입 검증
            assert isinstance(distance, float), f"distance는 float여야 함, 현재: {type(distance)}"
            assert isinstance(similarity, float), f"similarity는 float여야 함, 현재: {type(similarity)}"
            
            # 값 범위 검증
            assert 0 <= distance <= 2, f"distance는 0~2 범위여야 함, 현재: {distance}"
            assert -1 <= similarity <= 1, f"similarity는 -1~1 범위여야 함, 현재: {similarity}"
            
            # distance와 similarity의 관계 검증 (similarity = 1 - distance)
            expected_similarity = 1 - distance
            assert abs(similarity - expected_similarity) < 0.0001, \
                f"similarity({similarity})는 1 - distance({distance}) = {expected_similarity}와 같아야 함"


def test_results_sorted_by_similarity():
    """검색 결과가 similarity 내림차순으로 정렬되는지 확인"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    with Retriever(db_url=db_url) as retriever:
        docs = retriever.search("大阪の観光スポット", top_k=5)
        
        assert len(docs) > 1, "비교를 위해 최소 2개 이상의 결과 필요"
        
        # 연속된 문서의 similarity를 비교
        for i in range(len(docs) - 1):
            current_sim = docs[i].metadata["similarity"]
            next_sim = docs[i + 1].metadata["similarity"]
            
            # 현재 문서의 similarity가 다음 문서보다 크거나 같아야 함
            assert current_sim >= next_sim, \
                f"결과가 similarity 순으로 정렬되지 않음: {current_sim} < {next_sim}"


def test_results_sorted_by_distance_ascending():
    """검색 결과가 distance 오름차순으로 정렬되는지 확인 (distance가 작을수록 유사)"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    with Retriever(db_url=db_url) as retriever:
        docs = retriever.search("京都の宿泊施設", top_k=5)
        
        assert len(docs) > 1, "비교를 위해 최소 2개 이상의 결과 필요"
        
        # 연속된 문서의 distance를 비교
        for i in range(len(docs) - 1):
            current_dist = docs[i].metadata["distance"]
            next_dist = docs[i + 1].metadata["distance"]
            
            # 현재 문서의 distance가 다음 문서보다 작거나 같아야 함
            assert current_dist <= next_dist, \
                f"결과가 distance 순으로 정렬되지 않음: {current_dist} > {next_dist}"


def test_similarity_consistency_with_expansion():
    """Query expansion 사용 시에도 distance/similarity가 일관되게 계산되는지 확인"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    with Retriever(db_url=db_url) as retriever:
        docs = retriever.search_with_expansion(
            query="東京のレストラン",
            top_k=3,
            variations=["東京のおすすめレストラン"]
        )
        
        assert len(docs) > 0, "검색 결과가 있어야 함"
        
        for doc in docs:
            # distance와 similarity가 모두 존재
            assert "distance" in doc.metadata
            assert "similarity" in doc.metadata
            
            distance = doc.metadata["distance"]
            similarity = doc.metadata["similarity"]
            
            # 관계 검증
            expected_similarity = 1 - distance
            assert abs(similarity - expected_similarity) < 0.0001, \
                f"Expansion에서도 similarity = 1 - distance 관계가 유지되어야 함"


def test_top_document_has_highest_similarity():
    """첫 번째 문서가 가장 높은 similarity를 가지는지 확인"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    with Retriever(db_url=db_url) as retriever:
        docs = retriever.search("北海道の自然", top_k=5)
        
        assert len(docs) > 0, "검색 결과가 있어야 함"
        
        if len(docs) > 1:
            top_similarity = docs[0].metadata["similarity"]
            
            # 첫 번째 문서의 similarity가 가장 높아야 함
            for doc in docs[1:]:
                assert top_similarity >= doc.metadata["similarity"], \
                    f"첫 번째 문서가 가장 높은 similarity를 가져야 함"


def test_distance_and_similarity_numerical_precision():
    """Distance와 similarity의 수치 정확도 검증"""
    db_url = "postgresql://tourism_user:tourism_pass@localhost:5432/tourism_db"
    
    with Retriever(db_url=db_url) as retriever:
        docs = retriever.search("福岡のショッピング", top_k=3)
        
        for doc in docs:
            distance = doc.metadata["distance"]
            similarity = doc.metadata["similarity"]
            
            # 정밀도 검증: similarity = 1 - distance
            calculated_similarity = 1.0 - distance
            diff = abs(similarity - calculated_similarity)
            
            # 부동소수점 오차 허용 범위: 0.0001 이내
            assert diff < 0.0001, \
                f"수치 정밀도 문제: similarity({similarity}) != 1 - distance({distance}), diff={diff}"
