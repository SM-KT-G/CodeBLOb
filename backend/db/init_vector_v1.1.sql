-- PostgreSQL + pgvector v1.1 스키마
-- Parent-Child 아키텍처

-- pgvector 확장
CREATE EXTENSION IF NOT EXISTS vector;

-- 도메인 ENUM
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'domain_type') THEN
        CREATE TYPE domain_type AS ENUM ('food', 'stay', 'nat', 'his', 'shop', 'lei');
    END IF;
END$$;

-- 출처 타입 ENUM
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'source_type') THEN
        CREATE TYPE source_type AS ENUM ('book', 'blog', 'official', 'review', 'news', 'other');
    END IF;
END$$;

-- ========================================
-- Parent 테이블 (문서 요약 - 임베딩 없음)
-- ========================================
CREATE TABLE IF NOT EXISTS tourism_parent (
    id SERIAL PRIMARY KEY,
    document_id TEXT UNIQUE NOT NULL,           -- J_FOOD_000001
    domain domain_type NOT NULL,
    title TEXT NOT NULL,
    summary_text TEXT NOT NULL,                 -- 원본 text 필드
    
    -- 메타데이터 (복원)
    place_name TEXT,                            -- 장소명
    area TEXT,                                  -- 지역
    lang TEXT DEFAULT 'ja',                     -- 언어
    source_type source_type,                    -- 출처 유형
    source_url TEXT,
    collected_date DATE,
    published_date DATE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- Child 테이블 (QA 청크 - 임베딩 있음)
-- ========================================
CREATE TABLE IF NOT EXISTS tourism_child (
    id SERIAL PRIMARY KEY,
    qa_id TEXT UNIQUE NOT NULL,                 -- J_FOOD_000001#0, J_FOOD_000001#1
    parent_id INTEGER NOT NULL REFERENCES tourism_parent(id) ON DELETE CASCADE,
    document_id TEXT NOT NULL,                  -- 역추적용
    
    -- QA 내용
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    chunk_text TEXT NOT NULL,                   -- question + answer 결합
    
    -- 메타데이터 (부모에서 상속)
    domain domain_type NOT NULL,
    title TEXT,
    place_name TEXT,
    area TEXT,
    lang TEXT DEFAULT 'ja',
    
    -- 벡터 임베딩 (384차원 - e5-small)
    embedding vector(384),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- 인덱스 (최적화)
-- ========================================

-- Parent 인덱스
CREATE INDEX IF NOT EXISTS idx_parent_document_id ON tourism_parent(document_id);
CREATE INDEX IF NOT EXISTS idx_parent_domain ON tourism_parent(domain);
CREATE INDEX IF NOT EXISTS idx_parent_area ON tourism_parent(area);
CREATE INDEX IF NOT EXISTS idx_parent_collected_date ON tourism_parent(collected_date);

-- Child 벡터 인덱스 (IVFFlat - lists 조정 필요)
-- 초기값: lists = 예상 청크 수 / 1000
-- 예상: 377K 문서 × 평균 4 QA = 1.5M 청크 → lists ≈ 1500
CREATE INDEX IF NOT EXISTS idx_child_embedding 
    ON tourism_child 
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 1500);

-- Child 필터 인덱스
CREATE INDEX IF NOT EXISTS idx_child_domain ON tourism_child(domain);
CREATE INDEX IF NOT EXISTS idx_child_area ON tourism_child(area);
CREATE INDEX IF NOT EXISTS idx_child_parent_id ON tourism_child(parent_id);
CREATE INDEX IF NOT EXISTS idx_child_qa_id ON tourism_child(qa_id);

-- ========================================
-- 검색 성능 최적화
-- ========================================

-- 도메인별 파티셔닝 준비 (향후)
-- CREATE TABLE tourism_child_food PARTITION OF tourism_child FOR VALUES IN ('food');

-- ANALYZE 자동화
CREATE OR REPLACE FUNCTION update_parent_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_parent_updated_at
    BEFORE UPDATE ON tourism_parent
    FOR EACH ROW
    EXECUTE FUNCTION update_parent_timestamp();

-- ========================================
-- 뷰: Parent + Child 조인 (검색 편의)
-- ========================================
CREATE OR REPLACE VIEW v_tourism_search AS
SELECT 
    c.id AS child_id,
    c.qa_id,
    c.question,
    c.answer,
    c.chunk_text,
    c.embedding,
    c.domain,
    c.area,
    p.document_id,
    p.title,
    p.place_name,
    p.summary_text,
    p.source_url,
    p.source_type
FROM tourism_child c
JOIN tourism_parent p ON c.parent_id = p.id;

-- ========================================
-- 스키마 버전
-- ========================================
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO schema_version (version) 
VALUES ('1.1.0') 
ON CONFLICT (version) DO NOTHING;

-- 완료 메시지
DO $$
BEGIN
    RAISE NOTICE 'Parent-Child 스키마 v1.1 초기화 완료';
    RAISE NOTICE 'lists=1500으로 설정됨 (조정 필요)';
END$$;
