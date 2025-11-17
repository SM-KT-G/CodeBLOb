"""
ChatHistoryManager - MariaDB 대화 기록 관리
JSON을 LONGTEXT로 저장/조회
"""
import mariadb
import json
from typing import List, Dict, Any, Optional
from datetime import datetime


class ChatHistoryManager:
    """MariaDB를 사용한 채팅 기록 관리"""
    
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        """
        Args:
            host: MariaDB 호스트
            user: 사용자명
            password: 비밀번호
            database: 데이터베이스 이름
            port: 포트 (기본 3306)
        """
        self.conn_params = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port,
            "autocommit": False
        }
        self._ensure_table()
    
    def _get_connection(self):
        """새로운 연결 생성"""
        return mariadb.connect(**self.conn_params)
    
    def _ensure_table(self):
        """chat_history 테이블 생성 (없으면)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            chat_id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            user_message TEXT NOT NULL,
            response_type VARCHAR(50) NOT NULL,
            assistant_response LONGTEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_session (session_id),
            INDEX idx_created (created_at),
            CONSTRAINT chk_json_valid CHECK (JSON_VALID(assistant_response))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def save_message(
        self,
        session_id: str,
        user_message: str,
        response_type: str,
        assistant_response: Dict[str, Any]
    ) -> int:
        """
        대화 메시지 저장
        
        Args:
            session_id: 세션 ID
            user_message: 사용자 메시지
            response_type: 응답 타입 (chat/search/itinerary)
            assistant_response: 어시스턴트 응답 (dict)
        
        Returns:
            chat_id: 저장된 레코드 ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # dict → JSON 문자열
        response_json = json.dumps(assistant_response, ensure_ascii=False)
        
        cursor.execute("""
        INSERT INTO chat_history 
        (session_id, user_message, response_type, assistant_response)
        VALUES (?, ?, ?, ?)
        """, (session_id, user_message, response_type, response_json))
        
        chat_id = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return chat_id
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        세션의 전체 대화 기록 조회
        
        Args:
            session_id: 세션 ID
        
        Returns:
            대화 기록 리스트 (오래된 순)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT 
            chat_id,
            user_message,
            response_type,
            assistant_response,
            created_at
        FROM chat_history
        WHERE session_id = ?
        ORDER BY created_at ASC
        """, (session_id,))
        
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            chat_id, user_msg, resp_type, resp_json, created = row
            
            # JSON 문자열 → dict
            assistant_resp = json.loads(resp_json)
            
            history.append({
                "chat_id": chat_id,
                "user_message": user_msg,
                "response_type": resp_type,
                "assistant_response": assistant_resp,
                "created_at": created.isoformat() if created else None
            })
        
        cursor.close()
        conn.close()
        
        return history
    
    def get_recent_context(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        최근 N개 대화 컨텍스트 조회 (LLM 프롬프트용)
        
        Args:
            session_id: 세션 ID
            limit: 최대 개수
        
        Returns:
            최근 대화 리스트 (오래된 순으로 정렬)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT 
            user_message,
            response_type,
            assistant_response
        FROM chat_history
        WHERE session_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """, (session_id, limit))
        
        rows = cursor.fetchall()
        
        # 역순 정렬 (오래된 것부터)
        context = []
        for row in reversed(rows):
            user_msg, resp_type, resp_json = row
            assistant_resp = json.loads(resp_json)
            
            context.append({
                "user_message": user_msg,
                "response_type": resp_type,
                "assistant_response": assistant_resp
            })
        
        cursor.close()
        conn.close()
        
        return context
    
    def delete_session(self, session_id: str) -> int:
        """
        세션의 모든 대화 삭제
        
        Args:
            session_id: 세션 ID
        
        Returns:
            삭제된 레코드 개수
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        DELETE FROM chat_history
        WHERE session_id = ?
        """, (session_id,))
        
        deleted = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return deleted
