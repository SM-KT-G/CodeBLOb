"""
임베딩 데이터 처리 유틸리티

JSON 파일 로드, 도메인 매핑, 텍스트 추출 등 공통 기능 제공
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

# 도메인 한글 → ENUM 매핑
DOMAIN_MAPPING = {
    "음식점": "food",
    "숙박": "stay", 
    "자연": "nat",
    "역사": "his",
    "쇼핑": "shop",
    "레저": "lei"
}

# 폴더명 → ENUM 매핑
FOLDER_DOMAIN_MAPPING = {
    "TL_FOOD": "food",
    "TL_STAY": "stay",
    "TL_NAT": "nat",
    "TL_HIS": "his",
    "TL_SHOP": "shop",
    "TL_LEI": "lei"
}


def load_json_file(file_path: Path) -> Dict:
    """
    JSON 파일 로드
    
    Args:
        file_path: JSON 파일 경로
        
    Returns:
        파싱된 JSON 데이터
        
    Raises:
        ValueError: JSON 파싱 실패 시
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {file_path} - {e}")
    except Exception as e:
        raise ValueError(f"파일 읽기 실패: {file_path} - {e}")


def extract_embedding_text(data: Dict, include_qa: bool = False) -> str:
    """
    JSON 데이터에서 임베딩할 텍스트 추출
    
    옵션 C: 제목 + 도메인 + 본문 (+ 선택적 QA)
    
    Args:
        data: JSON 데이터
        include_qa: QA 포함 여부 (기본 False)
        
    Returns:
        임베딩할 텍스트
    """
    data_info = data.get("data_info", {})
    title = data_info.get("title", "")
    domain = data_info.get("domain", "")
    text = data.get("text", "").strip()
    
    # 기본: 제목 + 도메인 + 본문
    parts = []
    if title:
        parts.append(f"タイトル: {title}")
    if domain:
        parts.append(f"分野: {domain}")
    if text:
        parts.append(text)
    
    # QA 추가 (선택)
    if include_qa and "QA" in data:
        qa_texts = []
        for qa in data["QA"]:
            q = qa.get("question", "").strip()
            a = qa.get("answer", "").strip()
            if q and a:
                qa_texts.append(f"Q: {q}\nA: {a}")
        if qa_texts:
            parts.append("\n".join(qa_texts))
    
    return "\n\n".join(parts)


def map_domain(domain_kr: str, folder_name: str = None) -> str:
    """
    한글 도메인을 ENUM 값으로 변환
    
    Args:
        domain_kr: 한글 도메인 (예: "음식점")
        folder_name: 폴더명 (예: "TL_FOOD") - 백업용
        
    Returns:
        ENUM 도메인 (예: "food")
        
    Raises:
        ValueError: 매핑 실패 시
    """
    # 1차: 한글 도메인으로 매핑
    if domain_kr in DOMAIN_MAPPING:
        return DOMAIN_MAPPING[domain_kr]
    
    # 2차: 폴더명으로 매핑 (백업)
    if folder_name and folder_name in FOLDER_DOMAIN_MAPPING:
        logger.warning(f"한글 도메인 '{domain_kr}' 매핑 실패, 폴더명 '{folder_name}' 사용")
        return FOLDER_DOMAIN_MAPPING[folder_name]
    
    raise ValueError(f"알 수 없는 도메인: {domain_kr} (폴더: {folder_name})")


def find_json_files(data_dir: Path, domains: List[str] = None) -> List[Tuple[Path, str]]:
    """
    데이터 디렉토리에서 JSON 파일 탐색
    
    Args:
        data_dir: labled_data 디렉토리 경로
        domains: 특정 도메인만 처리 (예: ["food", "stay"])
        
    Returns:
        (파일경로, 폴더명) 튜플 리스트
    """
    json_files = []
    
    for folder in data_dir.iterdir():
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        
        folder_name = folder.name
        
        # 도메인 필터링
        if domains:
            folder_domain = FOLDER_DOMAIN_MAPPING.get(folder_name)
            if folder_domain not in domains:
                logger.info(f"스킵: {folder_name} (필터링됨)")
                continue
        
        # JSON 파일 수집
        for json_file in folder.glob("*.json"):
            json_files.append((json_file, folder_name))
    
    return sorted(json_files)


def validate_data(data: Dict) -> bool:
    """
    JSON 데이터 유효성 검증
    
    Args:
        data: JSON 데이터
        
    Returns:
        유효 여부
    """
    # 필수 필드 확인
    if "data_info" not in data:
        logger.error("data_info 필드 누락")
        return False
    
    data_info = data["data_info"]
    
    if "documentID" not in data_info:
        logger.error("documentID 누락")
        return False
    
    if "text" not in data or not data["text"].strip():
        logger.error(f"text 필드 누락 또는 비어있음: {data_info.get('documentID')}")
        return False
    
    return True


def extract_metadata(data: Dict) -> Dict:
    """
    DB 저장용 메타데이터 추출 (최소화)
    
    Args:
        data: JSON 데이터
        
    Returns:
        메타데이터 딕셔너리 (source_url, source만 포함)
    """
    data_info = data.get("data_info", {})
    
    metadata = {}
    
    # 출처 URL (RAG 응답 시 출처 표시용)
    source_url = data_info.get("source_url", "").strip()
    if source_url and source_url != "null":
        # URL 클린업 (앞뒤 따옴표 제거)
        source_url = source_url.strip("'\"")
        metadata["source_url"] = source_url
    
    # 출처 타입
    source = data_info.get("source", "").strip()
    if source and source != "null":
        metadata["source"] = source
    
    return metadata


def estimate_tokens(text: str) -> int:
    """
    텍스트 토큰 수 대략 추정
    
    일본어/한글 혼합: 평균 1 문자 = 1.5 토큰
    
    Args:
        text: 텍스트
        
    Returns:
        예상 토큰 수
    """
    return int(len(text) * 1.5)
