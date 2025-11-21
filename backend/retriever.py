"""
벡터 검색 모듈 (v1.1)
tourism_child 테이블 직접 검색
"""
import asyncio
import os
import time
from typing import Any, Dict, List, Optional
import psycopg
from psycopg_pool import ConnectionPool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from backend.utils.logger import setup_logger, log_exception
from backend.query_expansion import generate_variations


logger = setup_logger()


class Retriever:
    """
    tourism_child 테이블 직접 검색 클래스
    """
    
    def __init__(
        self,
        db_url: str,
        embedding_model: str = "intfloat/multilingual-e5-small",
        embeddings_client = None,
    ):
        """
        초기화
        
        Args:
            db_url: PostgreSQL 연결 URL
            embedding_model: HuggingFace 임베딩 모델명
            embeddings_client: Optional embeddings client (테스트 시 mock 주입용)
        """
        try:
            logger.info(f"Retriever 초기화 중... (모델: {embedding_model})")
            
            self.db_url = db_url
            self.last_expansion_metrics: Optional[Dict[str, Any]] = None
            
            # Connection Pool 초기화 (min 2, max 10 connections)
            self.pool = ConnectionPool(
                conninfo=db_url,
                min_size=2,
                max_size=10,
                timeout=30.0,
            )
            logger.info("DB Connection Pool 생성 완료 (min=2, max=10)")
            
            # Embeddings client 설정 (주입 또는 기본값 생성)
            if embeddings_client is not None:
                self.embeddings = embeddings_client
                logger.info("외부 Embeddings Client 주입됨")
            else:
                # HuggingFace 임베딩 모델 로드
                # Docker 컨테이너에서는 'cpu', M1/M2/M3/M4 Mac에서는 'mps' 사용
                device = os.getenv("EMBEDDING_DEVICE", "cpu")
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=embedding_model,
                    model_kwargs={'device': device},
                    encode_kwargs={'normalize_embeddings': True}
                )
                logger.info(f"HuggingFace Embeddings 모델 로드 완료: {embedding_model}, device={device}")
            
            logger.info("Retriever 초기화 완료")
        
        except Exception as e:
            log_exception(
                e,
                context={
                    "db_url": db_url[:30] + "...",
                    "model": embedding_model,
                },
                logger=logger,
            )
            raise
    
    def close(self):
        """Connection Pool 정리"""
        if hasattr(self, 'pool'):
            self.pool.close()
            logger.info("DB Connection Pool 종료 완료")
    
    def __enter__(self):
        """Context manager 지원"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료 시 pool 정리"""
        self.close()
    
    def _embed_query(self, query: str) -> List[float]:
        """쿼리를 벡터로 임베딩"""
        return self.embeddings.embed_query(query.strip())
    
    def _build_sql_and_params(
        self,
        query_embedding: List[float],
        top_k: int,
        domain: Optional[str] = None,
        area: Optional[str] = None,
    ) -> tuple[str, list]:
        """SQL 쿼리와 파라미터 생성"""
        sql = """
            SELECT 
                c.chunk_text,
                c.question,
                c.answer,
                c.domain,
                c.title,
                c.place_name,
                c.area,
                p.source_url,
                p.document_id,
                p.summary_text,
                (c.embedding <=> %s::vector) AS distance,
                (1 - (c.embedding <=> %s::vector)) AS similarity
            FROM tourism_child c
            JOIN tourism_parent p ON c.parent_id = p.id
            WHERE 1=1
        """
        
        # Distance와 similarity 모두 계산하기 위해 쿼리 임베딩을 두 번 전달
        params = [str(query_embedding), str(query_embedding)]
        
        # 도메인 필터 추가
        if domain:
            sql += " AND c.domain = %s"
            params.append(domain)
        
        # 지역 필터 추가 (부분 일치)
        if area:
            sql += " AND (c.area LIKE %s OR c.place_name LIKE %s OR c.title LIKE %s)"
            area_pattern = f"%{area}%"
            params.extend([area_pattern, area_pattern, area_pattern])
        
        # ORDER BY에서는 이미 계산된 distance 사용
        sql += " ORDER BY distance LIMIT %s"
        params.append(top_k)
        
        return sql, params
    
    def _execute_search(self, sql: str, params: list) -> list:
        """SQL 쿼리 실행하여 결과 반환 (Connection Pool 사용)"""
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
    
    def _rows_to_documents(self, rows: list) -> List[Document]:
        """DB row를 Document 객체 리스트로 변환"""
        documents = []
        for row in rows:
            # SQL SELECT 순서: chunk_text, question, answer, domain, title, place_name, area, 
            # source_url, document_id, summary_text, distance, similarity
            chunk_text, question, answer, domain_val, title, place_name, area, source_url, document_id, summary_text, distance, similarity = row

            # Include parent summary in page_content to provide context
            page = """
親ドキュメント要約:
{summary}

質問:
{question}

回答:
{answer}
""".format(summary=summary_text or "(要約なし)", question=question or "", answer=answer or "")

            doc = Document(
                page_content=page,
                metadata={
                    "domain": domain_val,
                    "title": title or "",
                    "place_name": place_name or "",
                    "area": area or "",
                    "source_url": source_url or "",
                    "document_id": document_id,
                    "distance": float(distance),
                    "similarity": float(similarity),
                    "parent_summary": summary_text or "",
                }
            )
            documents.append(doc)
        
        return documents

    def search(
        self,
        query: str,
        top_k: int = 5,
        domain: Optional[str] = None,
        area: Optional[str] = None,
    ) -> List[Document]:
        """
        유사도 기반 문서 검색 (Metadata Filtering 강화)
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수
            domain: 도메인 필터 (food, stay, nat, his, shop, lei)
            area: 지역 필터 (예: 서울, 부산)
        
        Returns:
            검색된 Document 리스트
        """
        # 입력 검증
        if not query or len(query.strip()) < 2:
            raise ValueError("쿼리는 최소 2자 이상이어야 합니다.")
        
        if not isinstance(top_k, int) or top_k < 1 or top_k > 10:
            raise ValueError("top_k는 1~10 사이의 정수여야 합니다.")
        
        try:
            self.last_expansion_metrics = None
            logger.info(f"문서 검색 시작: query='{query[:50]}...', top_k={top_k}, domain={domain}, area={area}")

            # 쿼리 임베딩 생성
            query_embedding = self._embed_query(query)
            
            # SQL 쿼리 구성
            sql, params = self._build_sql_and_params(query_embedding, top_k, domain, area)
            
            # 검색 실행
            rows = self._execute_search(sql, params)
            
            # Document 객체로 변환
            documents = self._rows_to_documents(rows)
            
            logger.info(f"검색 완료: {len(documents)}개 문서 반환")
            
            return documents
        
        except Exception as e:
            log_exception(
                e,
                context={
                    "query": query[:100],
                    "top_k": top_k,
                    "domain": domain,
                    "area": area,
                },
                logger=logger,
            )
            raise

    def _get_document_id(self, doc: Document) -> Any:
        """Document에서 고유 ID 추출 (중복 제거용)"""
        doc_id = doc.metadata.get("document_id") or doc.metadata.get("documentId")
        if not doc_id:
            doc_id = hash(doc.page_content)
        return doc_id
    
    def _merge_documents_by_similarity(self, all_results: List[List[Document]]) -> Dict[Any, Document]:
        """
        여러 검색 결과를 document_id 기준으로 병합하고 가장 높은 유사도만 유지
        
        Args:
            all_results: 검색 결과 리스트의 리스트
        
        Returns:
            document_id를 키로 하는 Document 딕셔너리
        """
        merged = {}
        for results in all_results:
            for doc in results:
                doc_id = self._get_document_id(doc)
                prev = merged.get(doc_id)
                sim = float(doc.metadata.get("similarity", 0.0))
                if not prev or sim > prev.metadata.get("similarity", 0.0):
                    merged[doc_id] = doc
        return merged
    
    def _sort_and_limit_by_similarity(self, documents: Dict[Any, Document], top_k: int) -> List[Document]:
        """유사도 기준 정렬 및 top_k 제한"""
        docs = sorted(
            documents.values(),
            key=lambda d: d.metadata.get("similarity", 0.0),
            reverse=True
        )
        return docs[:top_k]

    async def search_async(
        self,
        query: str,
        top_k: int = 5,
        domain: Optional[str] = None,
        area: Optional[str] = None,
    ) -> List[Document]:
        """
        비동기 문서 검색 (병렬 처리용)
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수
            domain: 도메인 필터
            area: 지역 필터
        
        Returns:
            검색된 Document 리스트
        """
        # 동기 search를 asyncio에서 실행
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.search(query, top_k, domain, area)
        )

    def search_with_expansion(
        self,
        query: str,
        top_k: int = 5,
        domain: Optional[str] = None,
        area: Optional[str] = None,
        variations: Optional[List[str]] = None,
    ) -> List[Document]:
        """
        간단한 Query Expansion을 적용한 검색

        전략(간단 버전):
        - 기본 쿼리
        - 구두점 제거 버전
        - 추천어 추가(예: 'おすすめ')
        - 사용자 제공 variations 병합

        반환: 중복 Document는 document_id 기준으로 제거하고 similarity가 높은 순으로 정렬하여 top_k 반환
        """
        if not query or len(query.strip()) < 2:
            raise ValueError("쿼리는 최소 2자 이상이어야 합니다.")

        vars_to_try = generate_variations(query, user_variations=variations)
        metrics: Dict[str, Optional[int | List[str]]] = {
            "variants": vars_to_try,
            "success_count": 0,
            "failure_count": 0,
        }

        # 결과 수집: key by document_id (metadata.document_id)
        all_results = []
        start_time = time.perf_counter()

        for qv in vars_to_try:
            try:
                results = self.search(query=qv, top_k=top_k, domain=domain, area=area)
                all_results.append(results)
                metrics["success_count"] = int(metrics["success_count"] or 0) + 1
            except Exception:
                # 한 변형이 실패해도 계속 진행
                metrics["failure_count"] = int(metrics["failure_count"] or 0) + 1
                continue

        # 중복 제거 및 병합
        merged = self._merge_documents_by_similarity(all_results)
        
        # 정렬 및 top_k 선택
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        docs = self._sort_and_limit_by_similarity(merged, top_k)
        
        metrics["retrieved"] = len(docs)
        metrics["duration_ms"] = duration_ms
        logger.info(f"Query Expansion metrics: {metrics}")
        self.last_expansion_metrics = metrics
        return docs

    async def search_with_expansion_async(
        self,
        query: str,
        top_k: int = 5,
        domain: Optional[str] = None,
        area: Optional[str] = None,
        variations: Optional[List[str]] = None,
    ) -> List[Document]:
        """
        비동기 Query Expansion 검색 (병렬 처리)
        
        전략:
        - 모든 쿼리 변형을 asyncio.gather로 병렬 실행
        - 중복 제거 및 유사도 기준 정렬
        - 실패한 변형은 무시하고 계속 진행
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 문서 개수
            domain: 도메인 필터
            area: 지역 필터
            variations: 사용자 정의 쿼리 변형
        
        Returns:
            검색된 Document 리스트
        """
        if not query or len(query.strip()) < 2:
            raise ValueError("쿼리는 최소 2자 이상이어야 합니다.")

        vars_to_try = generate_variations(query, user_variations=variations)
        metrics: Dict[str, Optional[int | List[str]]] = {
            "variants": vars_to_try,
            "success_count": 0,
            "failure_count": 0,
        }

        # 병렬 검색 실행
        start_time = time.perf_counter()
        
        # 모든 변형에 대해 비동기 검색 태스크 생성
        tasks = [
            self.search_async(query=qv, top_k=top_k, domain=domain, area=area)
            for qv in vars_to_try
        ]
        
        # 병렬 실행 (return_exceptions=True로 일부 실패 허용)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 성공한 결과만 수집
        all_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 실패한 변형
                metrics["failure_count"] = int(metrics["failure_count"] or 0) + 1
                logger.warning(f"Query variation failed: {vars_to_try[i]}, error: {result}")
            else:
                # 성공한 변형
                metrics["success_count"] = int(metrics["success_count"] or 0) + 1
                all_results.append(result)

        # 중복 제거 및 병합
        merged = self._merge_documents_by_similarity(all_results)

        # 정렬 및 top_k 선택
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        docs = self._sort_and_limit_by_similarity(merged, top_k)
        
        metrics["retrieved"] = len(docs)
        metrics["duration_ms"] = duration_ms
        logger.info(f"Query Expansion async metrics: {metrics}")
        
        self.last_expansion_metrics = metrics
        return docs
