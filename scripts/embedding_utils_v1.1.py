"""
v1.1 임베딩 유틸 - Parent-Child 아키텍처
- Parent: 문서 요약 (임베딩 없음)
- Child: QA 청크별 임베딩
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


def extract_document_id(filepath: Path) -> str:
    """
    파일명에서 document_id 추출
    예: /path/to/J_FOOD_000001.json -> J_FOOD_000001
    """
    return filepath.stem


def extract_domain(document_id: str) -> str:
    """
    document_id에서 도메인 추출
    J_FOOD_000001 -> food
    """
    domain_map = {
        'FOOD': 'food',
        'STAY': 'stay',
        'NAT': 'nat',
        'HIS': 'his',
        'SHOP': 'shop',
        'LEI': 'lei'
    }
    
    for key, value in domain_map.items():
        if key in document_id.upper():
            return value
    
    return 'other'


def parse_qa_pairs(qa_data: List[Dict]) -> List[Dict]:
    """
    QA 데이터를 청크로 분리
    
    Args:
        qa_data: [{"question": "...", "answer": "..."}] 형식
        
    Returns:
        [{"question": "...", "answer": "..."}] 형식
    """
    qa_chunks = []
    
    for item in qa_data:
        question = item.get('question', '').strip()
        answer = item.get('answer', '').strip()
        
        # 빈 QA 제외
        if not question or not answer:
            continue
            
        qa_chunks.append({
            'question': question,
            'answer': answer
        })
    
    return qa_chunks


def create_parent_data(data: Dict, document_id: str) -> Dict:
    """
    Parent 레코드 생성 (문서 요약)
    
    Args:
        data: JSON 원본 데이터
        document_id: J_FOOD_000001
        
    Returns:
        Parent 레코드 dict
    """
    # 실제 필드명 사용
    metadata = data.get('data_info', {})
    
    # 도메인 추출
    domain = extract_domain(document_id)
    
    # 장소명 추출 (title 사용)
    place_name = metadata.get('title', '')
    
    # 지역 정보 (없으면 빈 문자열)
    area = metadata.get('area', '') or metadata.get('region', '')
    
    # 출처 정보
    source_url = metadata.get('source_url', '')
    source_type = classify_source_type(source_url)
    
    # 날짜 파싱
    collected_date = parse_date(metadata.get('collectedDate', ''))
    published_date = parse_date(metadata.get('publishedDate', ''))
    
    return {
        'document_id': document_id,
        'domain': domain,
        'title': metadata.get('title', ''),
        'summary_text': data.get('text', ''),
        'place_name': place_name,
        'area': area,
        'lang': 'ja',  # 모두 일본어
        'source_type': source_type,
        'source_url': source_url,
        'collected_date': collected_date,
        'published_date': published_date
    }


def create_child_chunks(
    data: Dict,
    document_id: str,
    parent_db_id: int
) -> List[Dict]:
    """
    Child 청크 생성 (QA별 임베딩)
    
    Args:
        data: JSON 원본 데이터
        document_id: J_FOOD_000001
        parent_db_id: Parent 테이블 PK
        
    Returns:
        Child 레코드 리스트
    """
    qa_data = data.get('QA', [])
    qa_chunks = parse_qa_pairs(qa_data)
    
    # 메타데이터
    metadata = data.get('data_info', {})
    domain = extract_domain(document_id)
    title = metadata.get('title', '')
    place_name = metadata.get('title', '')  # title을 place_name으로 사용
    area = metadata.get('area', '') or metadata.get('region', '')
    
    child_records = []
    
    for idx, qa in enumerate(qa_chunks):
        qa_id = f"{document_id}#{idx}"
        
        # QA 텍스트 결합 (임베딩용)
        chunk_text = f"質問: {qa['question']}\n回答: {qa['answer']}"
        
        child_records.append({
            'qa_id': qa_id,
            'parent_id': parent_db_id,
            'document_id': document_id,
            'question': qa['question'],
            'answer': qa['answer'],
            'chunk_text': chunk_text,
            'domain': domain,
            'title': title,
            'place_name': place_name,
            'area': area,
            'lang': 'ja'
        })
    
    return child_records


def classify_source_type(url: str) -> str:
    """
    URL에서 출처 유형 분류
    """
    if not url:
        return 'other'
    
    url_lower = url.lower()
    
    if 'blog' in url_lower or 'note' in url_lower:
        return 'blog'
    elif 'review' in url_lower or 'tabelog' in url_lower:
        return 'review'
    elif 'news' in url_lower or 'article' in url_lower:
        return 'news'
    elif any(official in url_lower for official in ['.go.jp', 'city.', 'pref.', 'gov.']):
        return 'official'
    elif 'amazon' in url_lower or 'rakuten' in url_lower:
        return 'book'
    else:
        return 'other'


def parse_date(date_str: str) -> Optional[str]:
    """
    날짜 문자열을 PostgreSQL DATE 형식으로 변환
    
    Args:
        date_str: "2024-11-07" 또는 다양한 형식
        
    Returns:
        "YYYY-MM-DD" 또는 None
    """
    if not date_str:
        return None
    
    # 이미 YYYY-MM-DD 형식
    if len(date_str) == 10 and date_str.count('-') == 2:
        return date_str
    
    # 다른 형식 파싱 시도
    try:
        for fmt in ['%Y/%m/%d', '%Y.%m.%d', '%Y%m%d']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
    except:
        pass
    
    return None


def validate_json_structure(data: Dict, filepath: Path) -> bool:
    """
    JSON 구조 검증
    
    필수 필드:
    - text (Parent용)
    - QA (Child용)
    - data_info
    """
    required_fields = ['text', 'QA', 'data_info']
    
    for field in required_fields:
        if field not in data:
            print(f"⚠️  {filepath.name}: 필수 필드 누락 - {field}")
            return False
    
    # QA가 리스트인지
    if not isinstance(data['QA'], list):
        print(f"⚠️  {filepath.name}: QA 필드가 리스트가 아님")
        return False
    
    # 최소 1개 QA 있는지
    qa_chunks = parse_qa_pairs(data['QA'])
    if len(qa_chunks) == 0:
        print(f"⚠️  {filepath.name}: 유효한 QA가 없음")
        return False
    
    return True


def process_json_file(filepath: Path) -> Tuple[Optional[Dict], List[Dict]]:
    """
    JSON 파일 처리 (Parent + Child 분리)
    
    Args:
        filepath: JSON 파일 경로
        
    Returns:
        (parent_data, child_chunks_without_embedding)
        임베딩은 나중에 배치로 추가
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 검증
        if not validate_json_structure(data, filepath):
            return None, []
        
        # document_id 추출
        document_id = extract_document_id(filepath)
        
        # Parent 데이터 생성
        parent_data = create_parent_data(data, document_id)
        
        # Child 청크 생성 (임베딩 없이)
        # parent_db_id는 DB 삽입 후 채워짐
        child_chunks = create_child_chunks(data, document_id, parent_db_id=None)
        
        return parent_data, child_chunks
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {filepath.name} - {e}")
        return None, []
    except Exception as e:
        print(f"❌ 파일 처리 오류: {filepath.name} - {e}")
        return None, []


def create_embedding_text_for_child(chunk: Dict) -> str:
    """
    Child 청크의 임베딩용 텍스트 생성
    
    현재는 chunk_text 그대로 사용하지만,
    향후 프롬프트 엔지니어링 가능
    
    예: "질문: ... 답변: ..."
    """
    return chunk['chunk_text']


# ========================================
# 통계 함수
# ========================================

def calculate_statistics(parent_list: List[Dict], child_list: List[Dict]) -> Dict:
    """
    처리 통계 계산
    """
    domain_count = {}
    for parent in parent_list:
        domain = parent['domain']
        domain_count[domain] = domain_count.get(domain, 0) + 1
    
    total_parents = len(parent_list)
    total_children = len(child_list)
    avg_qa_per_doc = total_children / total_parents if total_parents > 0 else 0
    
    return {
        'total_documents': total_parents,
        'total_qa_chunks': total_children,
        'avg_qa_per_document': round(avg_qa_per_doc, 2),
        'domain_distribution': domain_count
    }


if __name__ == '__main__':
    # 테스트
    test_file = Path('/Users/ckdlsxor/Desktop/Training/labled_data/TL_FOOD/J_FOOD_000001.json')
    
    if test_file.exists():
        parent, children = process_json_file(test_file)
        
        if parent:
            print("✅ Parent 데이터:")
            print(f"  document_id: {parent['document_id']}")
            print(f"  domain: {parent['domain']}")
            print(f"  title: {parent['title'][:50]}...")
            print(f"  area: {parent['area']}")
            
            print(f"\n✅ Child 청크: {len(children)}개")
            for i, child in enumerate(children[:2]):  # 처음 2개만
                print(f"\n  [{i}] qa_id: {child['qa_id']}")
                print(f"      question: {child['question'][:50]}...")
                print(f"      answer: {child['answer'][:50]}...")
    else:
        print(f"❌ 테스트 파일 없음: {test_file}")
