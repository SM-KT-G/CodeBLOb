"""
초기 임베딩 데이터 처리 스크립트

labled_data/ 폴더의 JSON 파일들을 읽어서 HuggingFace 로컬 모델로 임베딩 생성 후 DB에 저장
"""
import os
import sys
import time
import json
import argparse
from pathlib import Path
from typing import List, Dict
import logging

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from scripts.embedding_utils import (
    find_json_files,
    load_json_file,
    extract_embedding_text,
    extract_metadata,
    map_domain,
    validate_data,
    estimate_tokens,
)
from backend.db.connect import DatabaseConnection
from backend.utils.logger import setup_logger, log_exception

# 로거 설정
logger = setup_logger(__name__)


class EmbeddingProcessor:
    """임베딩 처리 클래스"""
    
    def __init__(self, dry_run: bool = False, include_qa: bool = False, model_name: str = "intfloat/multilingual-e5-large"):
        """
        Args:
            dry_run: True면 실제 DB 저장 없이 테스트만
            include_qa: QA 데이터도 임베딩에 포함할지 여부
            model_name: HuggingFace 모델 이름
        """
        self.dry_run = dry_run
        self.include_qa = include_qa
        self.model_name = model_name
        
        # HuggingFace 모델 로드 (GPU 사용)
        import torch
        device = 'mps' if torch.backends.mps.is_available() else 'cpu'
        logger.info(f"🤗 HuggingFace 모델 로드 중: {model_name} (device: {device})")
        self.model = SentenceTransformer(model_name, device=device)
        logger.info(f"✅ 모델 로드 완료 (차원: {self.model.get_sentence_embedding_dimension()}, device: {device})")
        
        # DB 연결 (dry_run이 아닐 때만)
        self.db = None if dry_run else DatabaseConnection()
        
        # 통계
        self.stats = {
            "total": 0,
            "success": 0,
            "skipped": 0,
            "failed": 0,
            "total_tokens": 0,
        }
    
    def create_embedding(self, text: str) -> List[float]:
        """
        HuggingFace 모델로 임베딩 생성
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터 (dimension 1024)
        """
        try:
            # E5 모델은 쿼리에 "query: " 접두사 필요 (문서는 필요 없음)
            # 우리는 문서 임베딩이므로 그대로 사용
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # 토큰 수 추정 (통계용)
            tokens_used = estimate_tokens(text)
            self.stats["total_tokens"] += tokens_used
            
            # 차원 검증
            expected_dim = self.model.get_sentence_embedding_dimension()
            if len(embedding) != expected_dim:
                raise ValueError(f"잘못된 임베딩 차원: {len(embedding)}, 예상: {expected_dim}")
            
            return embedding.tolist()
            
        except Exception as e:
            log_exception(e, {"text_length": len(text)}, logger)
            raise
    
    def check_document_exists(self, document_id: str) -> bool:
        """
        DB에 이미 존재하는 document인지 확인
        
        Args:
            document_id: 문서 ID
            
        Returns:
            존재 여부
        """
        if self.dry_run or not self.db:
            return False
        
        try:
            with self.db.pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM tourism_data WHERE document_id = %s",
                        (document_id,)
                    )
                    return cur.fetchone() is not None
        except Exception as e:
            log_exception(e, {"document_id": document_id}, logger)
            return False
    
    def insert_document(
        self, 
        document_id: str, 
        domain: str, 
        title: str, 
        content: str, 
        embedding: List[float],
        metadata: Dict
    ):
        """
        DB에 문서 삽입
        
        Args:
            document_id: 문서 ID
            domain: 도메인 (ENUM)
            title: 제목
            content: 본문
            embedding: 임베딩 벡터
            metadata: 메타데이터 JSON
        """
        if self.dry_run:
            logger.info(f"[DRY-RUN] INSERT: {document_id} (domain={domain})")
            return
        
        try:
            with self.db.pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO tourism_data 
                        (document_id, domain, title, content, embedding, metadata, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                        """,
                        (
                            document_id,
                            domain,
                            title,
                            content,
                            embedding,
                            json.dumps(metadata, ensure_ascii=False)  # dict → JSON 문자열 변환
                        )
                    )
                    conn.commit()
            logger.info(f"✅ 저장 완료: {document_id}")
            
        except Exception as e:
            log_exception(e, {
                "document_id": document_id,
                "domain": domain,
                "title": title
            }, logger)
            raise
    
    def process_file(self, file_path: Path, folder_name: str) -> bool:
        """
        단일 JSON 파일 처리
        
        Args:
            file_path: JSON 파일 경로
            folder_name: 폴더명 (TL_FOOD 등)
            
        Returns:
            성공 여부
        """
        try:
            # 1. JSON 로드
            data = load_json_file(file_path)
            
            # 2. 유효성 검증
            if not validate_data(data):
                logger.warning(f"⚠️  유효하지 않은 데이터: {file_path.name}")
                return False
            
            data_info = data["data_info"]
            document_id = data_info["documentID"]
            
            # 3. 중복 체크
            if self.check_document_exists(document_id):
                logger.info(f"⏭️  이미 존재: {document_id}")
                self.stats["skipped"] += 1
                return True
            
            # 4. 도메인 매핑
            domain_kr = data_info.get("domain", "")
            domain = map_domain(domain_kr, folder_name)
            
            # 5. 임베딩 텍스트 추출
            embedding_text = extract_embedding_text(data, include_qa=self.include_qa)
            
            if not embedding_text.strip():
                logger.warning(f"⚠️  빈 텍스트: {document_id}")
                return False
            
            # 6. 임베딩 생성
            embedding = self.create_embedding(embedding_text)
            
            # 7. 메타데이터 추출 (최소화: source_url, source만)
            metadata = extract_metadata(data)
            
            # 8. DB 저장
            self.insert_document(
                document_id=document_id,
                domain=domain,
                title=data_info.get("title", ""),
                content=data.get("text", ""),
                embedding=embedding,
                metadata=metadata
            )
            
            return True
            
        except Exception as e:
            log_exception(e, {"file": str(file_path)}, logger)
            return False
    
    def process_batch(self, files: List[tuple], batch_size: int = 1000):
        """
        파일 배치 처리
        
        Args:
            files: (파일경로, 폴더명) 튜플 리스트
            batch_size: 배치 크기 (로컬 모델이므로 1000개로 증가)
        """
        total = len(files)
        
        for i, (file_path, folder_name) in enumerate(files, 1):
            logger.info(f"[{i}/{total}] 처리 중: {file_path.name}")
            
            success = self.process_file(file_path, folder_name)
            
            if success:
                self.stats["success"] += 1
            else:
                self.stats["failed"] += 1
            
            # 배치 단위로 잠시 대기 (API rate limit 방지)
            if i % batch_size == 0:
                logger.info(f"배치 {i//batch_size} 완료, 1초 대기...")
                time.sleep(1)
    
    def print_summary(self, elapsed_time: float):
        """실행 결과 요약 출력"""
        logger.info("=" * 60)
        logger.info("📊 임베딩 처리 완료")
        logger.info("=" * 60)
        logger.info(f"모델: {self.model_name}")
        logger.info(f"총 파일 수: {self.stats['total']}")
        logger.info(f"✅ 성공: {self.stats['success']}")
        logger.info(f"⏭️  스킵: {self.stats['skipped']}")
        logger.info(f"❌ 실패: {self.stats['failed']}")
        logger.info(f"🔢 총 토큰 (추정): {self.stats['total_tokens']:,}")
        logger.info(f"💰 비용: $0 (로컬 모델)")
        logger.info(f"⏱️  소요 시간: {elapsed_time:.1f}초")
        logger.info("=" * 60)
    
    def close(self):
        """리소스 정리"""
        if self.db:
            self.db.close()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="초기 임베딩 데이터 처리")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=project_root / "labled_data",
        help="데이터 디렉토리 (기본: labled_data/)"
    )
    parser.add_argument(
        "--domains",
        type=str,
        help="처리할 도메인 (쉼표 구분, 예: food,stay)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 DB 저장 없이 테스트만 실행"
    )
    parser.add_argument(
        "--include-qa",
        action="store_true",
        help="QA 데이터도 임베딩에 포함"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="intfloat/multilingual-e5-large",
        help="HuggingFace 모델 이름 (기본: intfloat/multilingual-e5-large)"
    )
    
    args = parser.parse_args()
    
    # 환경 변수 로드
    load_dotenv()
    
    logger.info("🚀 초기 임베딩 처리 시작 (HuggingFace 로컬 모델)")
    logger.info(f"데이터 디렉토리: {args.data_dir}")
    logger.info(f"모델: {args.model}")
    logger.info(f"드라이런 모드: {args.dry_run}")
    logger.info(f"QA 포함: {args.include_qa}")
    
    # 데이터 디렉토리 확인
    if not args.data_dir.exists():
        logger.error(f"❌ 데이터 디렉토리 없음: {args.data_dir}")
        sys.exit(1)
    
    # 도메인 파싱
    domains = None
    if args.domains:
        domains = [d.strip() for d in args.domains.split(",")]
        logger.info(f"필터링 도메인: {domains}")
    
    try:
        # 1. JSON 파일 탐색
        logger.info("📂 JSON 파일 탐색 중...")
        files = find_json_files(args.data_dir, domains)
        logger.info(f"총 {len(files)}개 파일 발견")
        
        if not files:
            logger.warning("⚠️  처리할 파일 없음")
            return
        
        # 2. 임베딩 처리
        start_time = time.time()
        
        processor = EmbeddingProcessor(
            dry_run=args.dry_run,
            include_qa=args.include_qa,
            model_name=args.model
        )
        processor.stats["total"] = len(files)
        
        processor.process_batch(files)
        
        # 3. 결과 출력
        elapsed_time = time.time() - start_time
        processor.print_summary(elapsed_time)
        
        # 4. 리소스 정리
        processor.close()
        
        # 5. 종료 코드
        if processor.stats["failed"] > 0:
            logger.warning(f"⚠️  {processor.stats['failed']}개 파일 처리 실패")
            sys.exit(1)
        
        logger.info("✅ 모든 파일 처리 완료!")
        
    except KeyboardInterrupt:
        logger.warning("⚠️  사용자에 의해 중단됨")
        sys.exit(1)
    except Exception as e:
        log_exception(e, {}, logger)
        sys.exit(1)


if __name__ == "__main__":
    main()
