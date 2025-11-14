# 프로젝트 문서 목록

## 📚 문서 구조

### 1. 프로젝트 계획
- **[프로젝트_계획서.md](./프로젝트_계획서.md)**: 초기 프로젝트 개요 및 목표
- **[PROJECT_PLAN.md](./PROJECT_PLAN.md)**: 상세 프로젝트 계획서 (영문)
- **[IMPLEMENTATION_TRACKER.md](./IMPLEMENTATION_TRACKER.md)**: 구현 진행 상황 추적

### 2. 기술 문서
- **[RAG_PIPELINE_ARCHITECTURE.md](./RAG_PIPELINE_ARCHITECTURE.md)**: RAG 파이프라인 아키텍처 설계 (v1.1)
- **[EMBEDDING_PLAN.md](./EMBEDDING_PLAN.md)**: 임베딩 전략 및 계획
- **[ITINERARY_RECOMMENDATION.md](./ITINERARY_RECOMMENDATION.md)**: 여행 추천 API 사양 (입력/응답 스키마, 흐름)
- **[REDIS_CACHE_GUIDE.md](./REDIS_CACHE_GUIDE.md)**: Redis TTL, 키 구조, 장애 대응, 모니터링 지표 정리

---

## 🔄 버전 히스토리

### v1.1 (2025-11-07~12) - Parent-Child Architecture ✅ COMPLETE
- **주요 변경사항**:
  - Document-level → Parent-Child QA chunking
  - 메타데이터 확장 (2개 → 9+개 필드)
  - multilingual-e5-large (1024d) → multilingual-e5-small (384d)
  - 직접 SQL 쿼리 방식 (PGVector <=> 연산자)
  - Metadata Filtering 구현 (area, domain)
  - Query Expansion + Parent Context 옵션 + Redis 캐시 도입
- **완료 상태**:
  - ✅ 377,263개 Parents 임베딩 완료
  - ✅ 2,202,565개 Children 임베딩 완료
  - ✅ Retriever 구현 및 테스트 (90%+ 유사도)
  - ✅ Metadata Filtering / Query Expansion / Parent Context / Redis 캐시 동작 확인
- **다음 단계**:
  - Query Expansion latency 분석 및 cutoff 전략
  - Redis 캐시 운영 가이드 및 장애 대응 시나리오 문서화

### v1.0 (2025-11-05~06) - Initial Implementation (Deprecated)
- 기본 RAG 파이프라인 구축
- Document-level 임베딩 (66% 완료 후 중단)
- 단순 벡터 유사도 검색
- 아키텍처 결함으로 v1.1로 재설계

---

## 📊 프로젝트 현황

**데이터**: 377,265개 일본어 관광 문서 (6개 도메인)
- 음식점 (FOOD): 113,383개
- 역사 (HIS): 116,387개  
- 레저 (LEI): 15,373개
- 자연 (NAT): 37,408개
- 쇼핑 (SHOP): 29,005개
- 숙박 (STAY): 67,709개

**임베딩 현황**: 
- ✅ v1.1 100% 완료 (2025-11-07)
- Parents: 377,263개 (문서 요약)
- Children: 2,202,565개 (QA 청크, 평균 5.8개/문서)
- 처리 시간: 2시간 54분
- 속도: 35.97 files/sec

**검색 성능**:
- 평균 유사도: 90%+ (0.90~0.92)
- Metadata Filtering: 복합 조건 검색 시 0.91 달성
- M4 GPU (MPS) 가속 사용

---

## 🛠️ 기술 스택

- **Backend**: FastAPI + Python 3.10
- **Database**: PostgreSQL + pgvector
- **LLM**: OpenAI GPT-4
- **Embedding**: intfloat/multilingual-e5-small (384d)
- **Hardware**: M4 GPU (MPS acceleration)
- **Cache**: Redis
- **Deployment**: Docker Compose

## 📈 품질 개선 현황

### ✅ Step 1: Metadata Filtering (완료)
- 지역/도메인별 타겟팅 검색
- 복합 필터 지원 (area + domain)
- 검색 정확도 향상 (최고 유사도 0.91)

### ✅ Step 2: Query Expansion (완료)
- JSON 설정 기반 변형 생성(접미어, 구두점, 사용자 변형)
- 변형별 성공/실패/latency/cached 지표 로깅 및 `/rag/query` metadata로 노출
- Redis TTL 캐시로 반복 쿼리 응답 속도 향상

### ✅ Step 3: Parent Context (완료)
- `parent_context` 플래그로 parent summary 포함 여부 제어
- fallback 경로에서도 요약 제거 처리

### 🔄 Step 4: 캐시/운영 가시성 (진행 중)
- Redis TTL 전략 운영 가이드 및 fallback 시나리오 문서화
- Query Expansion/검색 지표를 모니터링 대시보드에 노출

---

## 📖 참고 링크

프로젝트 루트의 [README.md](../README.md)를 참조하세요.
