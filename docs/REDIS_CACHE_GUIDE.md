# Redis Cache Guide

RAG 백엔드는 Redis를 이용해 검색/Query Expansion 결과를 TTL 기반으로 캐싱합니다. 이 문서는 운영자가 캐시를 설정·모니터링·문제 처리하는 방법을 정리합니다.

---

## 1. 환경 변수

| 변수 | 설명 | 기본값 |
| --- | --- | --- |
| `REDIS_URL` | Redis 접속 URL (`redis://user:pass@host:port/db`) | 미설정 시 캐시 비활성화 |
| `REDIS_TTL` | 캐시 TTL(초) | `300` |
| `CACHE_PREFIX` | 키 네임스페이스 (환경 구분) | `rag` |

`.env.local` 예시
```
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=300
CACHE_PREFIX=rag
```

---

## 2. 캐시 구조

### Search Cache
- 키 형식: `rag:search:{query}|{top_k}|{domain}|{area}`
- 값: `Document` 리스트를 JSON으로 직렬화 (page_content, metadata)
- 히트 시 검색/임베딩 과정을 건너뛰고 즉시 반환

### Query Expansion Cache
- 키 형식: `rag:search_expansion:{json_variants}|{top_k}|{domain}|{area}`
- 값: Query Expansion 병합 결과 문서 리스트(JSON)
- `metadata.expansion_metrics.cache_hit=true`로 응답에 반영

---

## 3. 모니터링 지표

FastAPI `/rag/query` 응답의 `metadata.expansion_metrics`에 아래 값을 포함합니다.
- `variants`: 실행된 변형 문자열
- `success_count` / `failure_count`
- `retrieved`: 최종 문서 수
- `duration_ms`: 변형 전체 실행 시간
- `cache_hit`: 캐시 적중 여부

로그 예시:
```
Query Expansion metrics: {
  "variants": ["温泉", "温泉 おすすめ"],
  "success_count": 2,
  "failure_count": 0,
  "retrieved": 5,
  "duration_ms": 450.3,
  "cache_hit": false
}
```

---

## 4. 운영 시나리오

### TTL 조정
- 트래픽이 많아 캐시 효과를 높이고 싶을 때 `REDIS_TTL`을 늘리거나, 실시간성이 중요하면 줄입니다.
- TTL 변경 후 서버 재시작 또는 환경 변수 reload 필요.

### 장애 대응
- `/health`에서 `cache=missing`/`error`가 표시되면 Redis 접속 오류.
- 로그에 `Redis 캐시 초기화 실패`가 찍힌 경우 Redis를 재기동 후 FastAPI를 재시작.
- 캐시가 비활성화된 상태에서도 서비스는 정상 동작하지만, 응답 지연이 증가할 수 있음.

### 키 정리
- 운영 환경에서 TTL이 자동으로 만료되므로 수동 삭제는 드물다.
- 필요 시 `redis-cli --scan | grep "rag:" | xargs redis-cli del` 등의 스크립트로 정리.

---

## 5. TODO / 개선 방향
- 캐시 히트율을 Prometheus 등으로 수집해서 대시보드화.
- Query Expansion 메트릭을 central logging 시스템(Kibana 등)에서 모니터링.
- 추천 API (`/recommend/itinerary`)에도 캐시 전략 적용 검토.
