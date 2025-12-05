-- PostgreSQL + pgvector 초기화 스크립트
-- FastAPI RAG 백엔드용 데이터베이스 스키마

-- 사용자 생성 (이미 존재하면 무시)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'tourism_user') THEN
        CREATE USER tourism_user WITH PASSWORD 'tourism_pass';
    END IF;
END$$;

-- 데이터베이스 권한 부여
GRANT ALL PRIVILEGES ON DATABASE tourism_db TO tourism_user;

-- pgvector 확장 설치 (없으면 생성)
CREATE EXTENSION IF NOT EXISTS vector;

-- 도메인 ENUM 타입 정의
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'domain_type') THEN
        CREATE TYPE domain_type AS ENUM (
            'food',   -- 음식
            'stay',   -- 숙박
            'nat',    -- 자연
            'his',    -- 역사
            'shop',   -- 쇼핑
            'lei'     -- 레저
        );
    END IF;
END$$;

-- LangChain PGVector 테이블 (자동 생성되지만 스키마 명시)
-- 테이블명: langchain_pg_embedding (LangChain 기본값)
CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID,
    embedding vector(1024),  -- multilingual-e5-large dimension
    document TEXT NOT NULL,
    cmetadata JSONB,
    custom_id TEXT
);

-- 관광 데이터 전용 테이블 (선택사항)
CREATE TABLE IF NOT EXISTS tourism_data (
    id SERIAL PRIMARY KEY,
    document_id TEXT UNIQUE NOT NULL,  -- 예: J_FOOD_000001
    domain domain_type NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL,
    embedding vector(1024),  -- multilingual-e5-large dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (벡터 검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_langchain_embedding 
    ON langchain_pg_embedding 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_tourism_embedding 
    ON tourism_data 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- 메타데이터 인덱스
CREATE INDEX IF NOT EXISTS idx_langchain_metadata 
    ON langchain_pg_embedding 
    USING gin (cmetadata);

CREATE INDEX IF NOT EXISTS idx_tourism_metadata 
    ON tourism_data 
    USING gin (metadata);

-- 도메인 필터링 인덱스
CREATE INDEX IF NOT EXISTS idx_tourism_domain 
    ON tourism_data (domain);

-- 컬렉션 인덱스
CREATE INDEX IF NOT EXISTS idx_langchain_collection 
    ON langchain_pg_embedding (collection_id);

-- 메타데이터 검증 함수 (NULL/빈 문자열 방지)
CREATE OR REPLACE FUNCTION validate_metadata()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.metadata IS NULL THEN
        RAISE EXCEPTION 'metadata는 NULL일 수 없습니다.';
    END IF;
    
    IF NEW.content IS NULL OR trim(NEW.content) = '' THEN
        RAISE EXCEPTION 'content는 비어있을 수 없습니다.';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 설정
DROP TRIGGER IF EXISTS check_tourism_metadata ON tourism_data;
CREATE TRIGGER check_tourism_metadata
    BEFORE INSERT OR UPDATE ON tourism_data
    FOR EACH ROW
    EXECUTE FUNCTION validate_metadata();

-- 샘플 데이터 (테스트용)
INSERT INTO tourism_data (doc_id, domain, title, content, metadata, embedding)
VALUES (
    'SAMPLE_001',
    'food',
    'テストデータ',
    'これはテストデータです。',
    '{"source": "test", "language": "ja"}'::jsonb,
    array_fill(0.0, ARRAY[1536])::vector
) ON CONFLICT (doc_id) DO NOTHING;

-- 스키마 버전 정보
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version) 
VALUES ('0.1.0') 
ON CONFLICT (version) DO NOTHING;

-- 완료 메시지
DO $$
BEGIN
    RAISE NOTICE 'pgvector 스키마 초기화 완료';
END$$;
