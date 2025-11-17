-- chat_history 테이블 초기화
-- MariaDB 10.2.7+ (JSON 타입 지원)

-- 기존 테이블 삭제 (초기화용)
DROP TABLE IF EXISTS chat_history;

-- chat_history 테이블 생성
CREATE TABLE chat_history (
    chat_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    response_type VARCHAR(50) NOT NULL,
    assistant_response LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 인덱스
    INDEX idx_session (session_id),
    INDEX idx_created (created_at),
    INDEX idx_session_created (session_id, created_at),
    
    -- JSON 검증 제약
    CONSTRAINT chk_json_valid CHECK (JSON_VALID(assistant_response))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 테이블 생성 확인
SELECT 'chat_history 테이블 생성 완료' AS status;
