"""
DB 연결 테스트 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv()

from backend.db.connect import DatabaseConnection
from backend.utils.logger import setup_logger

logger = setup_logger()

def test_db_connection():
    """DB 연결 및 스키마 테스트"""
    try:
        logger.info("=" * 60)
        logger.info("DB 연결 테스트 시작")
        logger.info("=" * 60)
        
        # DB 연결
        db = DatabaseConnection()
        logger.info("✅ DB 커넥션 풀 생성 완료")
        
        # 스키마 체크
        schema_ok = db.check_schema()
        if schema_ok:
            logger.info("✅ pgvector 확장 및 테이블 확인 완료")
        else:
            logger.warning("⚠️  스키마 확인 실패")
        
        # 간단한 쿼리 테스트
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM tourism_data")
                count = cur.fetchone()[0]
                logger.info(f"✅ tourism_data 테이블 레코드 수: {count}")
                
                cur.execute("SELECT COUNT(*) FROM langchain_pg_embedding")
                count = cur.fetchone()[0]
                logger.info(f"✅ langchain_pg_embedding 테이블 레코드 수: {count}")
        
        db.close()
        logger.info("=" * 60)
        logger.info("✅ 모든 DB 연결 테스트 통과!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ DB 연결 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_db_connection()
