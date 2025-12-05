"""
v1.1 임베딩 파이프라인 - Parent-Child 아키텍처
- e5-small (384차원) + 배치 최적화
- Parent/Child 분리 저장
- 체크포인트 복구
"""
import os
import sys
import json
import asyncio
import psycopg
import torch
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# embedding_utils_v1.1.py에서 함수 임포트
import importlib.util
spec = importlib.util.spec_from_file_location(
    "embedding_utils_v11",
    project_root / "scripts" / "embedding_utils_v1.1.py"
)
embedding_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(embedding_utils)

process_json_file = embedding_utils.process_json_file
create_embedding_text_for_child = embedding_utils.create_embedding_text_for_child
calculate_statistics = embedding_utils.calculate_statistics


# ========================================
# 설정
# ========================================
DATA_DIR = project_root / 'labled_data'
CHECKPOINT_FILE = project_root / 'scripts' / 'embedding_checkpoint_v1.1.json'

# PostgreSQL 연결 정보
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'tourism_db',
    'user': 'tourism_user',
    'password': 'tourism_pass'
}

# 임베딩 설정
MODEL_NAME = 'intfloat/multilingual-e5-small'  # 384 dims
BATCH_SIZE = 32  # 작게 시작 (테스트)
DEVICE = 'mps' if torch.backends.mps.is_available() else 'cpu'

print(f"🔧 임베딩 설정:")
print(f"   모델: {MODEL_NAME} (384 dims)")
print(f"   배치: {BATCH_SIZE}")
print(f"   디바이스: {DEVICE}")


# ========================================
# 모델 로드
# ========================================
print(f"\n📦 모델 로딩 중...")
model = SentenceTransformer(MODEL_NAME, device=DEVICE)
model.eval()
print(f"✅ 모델 준비 완료")


# ========================================
# DB 연결
# ========================================
def get_db_connection():
    """PostgreSQL 연결"""
    return psycopg.connect(**DB_CONFIG)


def init_database():
    """
    DB 초기화 (v1.1 스키마 실행)
    """
    print(f"ℹ️  스키마 초기화 건너뜀 (이미 실행됨)")
    return True


# ========================================
# Parent 저장
# ========================================
def save_parent_batch(parents: List[Dict]) -> Dict[str, int]:
    """
    Parent 레코드 배치 저장
    
    Returns:
        {document_id: parent_db_id} 매핑
    """
    if not parents:
        return {}
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # INSERT 쿼리
            insert_sql = """
                INSERT INTO tourism_parent (
                    document_id, domain, title, summary_text,
                    place_name, area, lang, source_type, source_url,
                    collected_date, published_date
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (document_id) DO NOTHING
                RETURNING id, document_id;
            """
            
            id_map = {}
            
            for parent in parents:
                cur.execute(insert_sql, (
                    parent['document_id'],
                    parent['domain'],
                    parent['title'],
                    parent['summary_text'],
                    parent['place_name'],
                    parent['area'],
                    parent['lang'],
                    parent['source_type'],
                    parent['source_url'],
                    parent['collected_date'],
                    parent['published_date']
                ))
                
                result = cur.fetchone()
                if result:
                    parent_id, doc_id = result
                    id_map[doc_id] = parent_id
            
            conn.commit()
    
    return id_map


# ========================================
# Child 저장 (임베딩 포함)
# ========================================
def save_child_batch(children: List[Dict], embeddings: List[List[float]]):
    """
    Child 청크 배치 저장 (임베딩 포함)
    """
    if not children or not embeddings:
        return
    
    if len(children) != len(embeddings):
        raise ValueError(f"청크({len(children)})와 임베딩({len(embeddings)}) 수 불일치")
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            insert_sql = """
                INSERT INTO tourism_child (
                    qa_id, parent_id, document_id,
                    question, answer, chunk_text,
                    domain, title, place_name, area, lang,
                    embedding
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (qa_id) DO NOTHING;
            """
            
            for child, emb in zip(children, embeddings):
                cur.execute(insert_sql, (
                    child['qa_id'],
                    child['parent_id'],
                    child['document_id'],
                    child['question'],
                    child['answer'],
                    child['chunk_text'],
                    child['domain'],
                    child['title'],
                    child['place_name'],
                    child['area'],
                    child['lang'],
                    emb
                ))
            
            conn.commit()


# ========================================
# 파일 수집
# ========================================
def collect_json_files() -> List[Path]:
    """모든 JSON 파일 수집"""
    json_files = []
    
    for domain_dir in DATA_DIR.iterdir():
        if domain_dir.is_dir() and domain_dir.name.startswith('TL_'):
            json_files.extend(domain_dir.glob('*.json'))
    
    return sorted(json_files)


# ========================================
# 체크포인트 관리
# ========================================
def load_checkpoint() -> Dict:
    """체크포인트 로드"""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'processed_files': [],
        'total_parents': 0,
        'total_children': 0,
        'last_updated': None
    }


def save_checkpoint(checkpoint: Dict):
    """체크포인트 저장"""
    checkpoint['last_updated'] = datetime.now().isoformat()
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


# ========================================
# 메인 임베딩 파이프라인
# ========================================
async def embed_all_files():
    """
    전체 파일 임베딩 파이프라인
    
    1. Parent 배치 저장
    2. Child 텍스트 수집
    3. 배치 임베딩
    4. Child + 임베딩 저장
    """
    # 1. 파일 수집
    print(f"\n📂 JSON 파일 수집 중...")
    all_files = collect_json_files()
    print(f"✅ 총 {len(all_files):,}개 파일 발견")
    
    # 2. 체크포인트 로드
    checkpoint = load_checkpoint()
    processed_set = set(checkpoint['processed_files'])
    remaining_files = [f for f in all_files if str(f) not in processed_set]
    
    print(f"📊 진행 상황:")
    print(f"   완료: {len(processed_set):,}개")
    print(f"   남음: {len(remaining_files):,}개")
    
    if not remaining_files:
        print(f"\n✅ 모든 파일 처리 완료!")
        return
    
    # 3. 배치 처리
    parent_batch = []
    child_batch = []
    all_child_chunks = []  # 모든 child 저장
    processed_count = len(processed_set)
    
    for filepath in tqdm(remaining_files, desc="임베딩 진행"):
        # JSON 파싱
        parent_data, child_chunks = process_json_file(filepath)
        
        if not parent_data:
            continue
        
        parent_batch.append(parent_data)
        all_child_chunks.extend(child_chunks)  # child 누적
        
        # 배치 크기 도달 시 저장
        if len(parent_batch) >= BATCH_SIZE:
            # Parent 저장 및 ID 매핑
            id_map = save_parent_batch(parent_batch)
            
            # Child에 parent_id 매핑
            for child in all_child_chunks:
                doc_id = child['document_id']
                parent_db_id = id_map.get(doc_id)
                
                if parent_db_id:
                    child['parent_id'] = parent_db_id
                    child_batch.append(child)
            
            # Child 임베딩 + 저장
            if child_batch:
                # 임베딩 텍스트 추출
                texts = [create_embedding_text_for_child(c) for c in child_batch]
                
                # 배치 임베딩
                with torch.no_grad():
                    embeddings = model.encode(
                        texts,
                        batch_size=min(BATCH_SIZE, len(texts)),
                        show_progress_bar=False,
                        convert_to_numpy=True
                    )
                
                # 저장
                save_child_batch(child_batch, embeddings.tolist())
                
                # 체크포인트 업데이트
                checkpoint['total_parents'] += len(parent_batch)
                checkpoint['total_children'] += len(child_batch)
            
            # 배치 초기화
            for parent in parent_batch:
                checkpoint['processed_files'].append(str(filepath))
            
            processed_count += len(parent_batch)
            parent_batch = []
            child_batch = []
            all_child_chunks = []
            
            # 체크포인트 저장 (1000개마다)
            if processed_count % 1000 == 0:
                save_checkpoint(checkpoint)
    
    # 4. 마지막 배치 처리
    if parent_batch:
        id_map = save_parent_batch(parent_batch)
        
        for child in all_child_chunks:
            doc_id = child['document_id']
            parent_db_id = id_map.get(doc_id)
            
            if parent_db_id:
                child['parent_id'] = parent_db_id
                child_batch.append(child)
        
        if child_batch:
            texts = [create_embedding_text_for_child(c) for c in child_batch]
            
            with torch.no_grad():
                embeddings = model.encode(
                    texts,
                    batch_size=min(BATCH_SIZE, len(texts)),
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
            
            save_child_batch(child_batch, embeddings.tolist())
            
            checkpoint['total_parents'] += len(parent_batch)
            checkpoint['total_children'] += len(child_batch)
        
        for parent in parent_batch:
            checkpoint['processed_files'].append(str(filepath))
    
    # 5. 최종 저장
    save_checkpoint(checkpoint)
    
    print(f"\n✅ 임베딩 완료!")
    print(f"   Parents: {checkpoint['total_parents']:,}개")
    print(f"   Children: {checkpoint['total_children']:,}개")


# ========================================
# 실행
# ========================================
if __name__ == '__main__':
    print(f"🚀 v1.1 임베딩 파이프라인 시작\n")
    
    # DB 초기화
    if not init_database():
        sys.exit(1)
    
    # 임베딩 실행
    asyncio.run(embed_all_files())
    
    print(f"\n🎉 모든 작업 완료!")
