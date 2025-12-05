# Itinerary Recommendation API Spec

여행 계획 추천 기능은 기존 RAG 인프라(Parent/Child QA + Query Expansion + Redis 캐시)를 활용하여 **여러 개의 일정안을 생성**하고, 프론트엔드 별도 화면에서 사용자가 선택할 수 있도록 설계한다.

---

## 1. 목표
- 사용자의 기본 조건(지역, 도메인, 기간 등)을 입력받아 2~4개의 추천 일정을 생성.
- 각 일정은 **Day 별 루트, 장소 요약, 참조 문서 ID**를 포함.
- 기존 `tourism_parent`/`tourism_child` 데이터의 `domain`, `area`, `place_name`, `summary_text`를 활용.

---

## 2. 엔드포인트 제안
- `POST /recommend/itinerary`
- FastAPI 라우터를 `/rag/query`와 분리하여 비동기 처리 및 추후 rate-limit을 독립 적용.

---

## 3. 입력 스키마 (`ItineraryRecommendationRequest`)
| 필드 | 타입 | 필수 | 설명 | 데이터 매핑 |
| --- | --- | --- | --- | --- |
| `region` | `string` | ✅ | 선호 지역 (예: `서울`, `부산`). 부분 일치로 `tourism_child.area` / `place_name` 필터링 | `area`, `place_name`, `title` |
| `domains` | `array[DomainEnum]` | ✅ | 관심 도메인 목록 (`food`, `stay`, `nat`, `his`, `shop`, `lei`) | `c.domain` |
| `duration_days` | `int` | ✅ | 일정 길이 (1~5일 권장). Day 구분 시 활용 | LLM 프롬프트 변수 |
| `themes` | `array[string]` | ❌ | “힐링”, “인스타”, “가족” 등 텍스트 태그. LLM 프롬프트 참고 | 없음(LLM 참고) |
| `transport_mode` | `string` | ❌ | `public`, `car`, `walk` 등. 이동 동선 설명 시 사용 | 없음(LLM 참고) |
| `budget_level` | `string` | ❌ | `economy`, `standard`, `premium`. 장소 추천 우선순위 힌트 | 없음(LLM 참고) |
| `preferred_places` | `array[string]` | ❌ | 반드시 포함하고 싶은 장소 ID/이름. `document_id` 직접 전달 가능 | `tourism_parent.document_id` |
| `avoid_places` | `array[string]` | ❌ | 제외하고 싶은 장소 ID/이름 | 동일 |
| `expansion` | `bool` | ❌ | Query Expansion 사용 여부 (기본 true). 짧은 입력 시 recall 향상 | `Retriever.search_with_expansion` |

> `themes`, `transport_mode`, `budget_level` 등 데이터 필드에 없는 항목은 LLM 프롬프트에서 가중치로만 사용한다.

### 예시 요청
```json
{
  "region": "서울",
  "domains": ["food", "lei"],
  "duration_days": 3,
  "themes": ["야경", "인스타"],
  "transport_mode": "public",
  "budget_level": "standard",
  "preferred_places": ["J_FOOD_010203"],
  "avoid_places": [],
  "expansion": true
}
```

---

## 4. 응답 스키마 (`ItineraryRecommendationResponse`)
| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `itineraries` | `array[ItineraryPlan]` | 추천 일정 목록 (기본 3개) |
| `metadata` | `object` | LLM 모델, Query Expansion 지표, 캐시 여부 등 |

`ItineraryPlan` 구조:
```json
{
  "title": "서울 3일 힐링 플랜",
  "summary": "맛집과 야경 중심 3일 일정...",
  "days": [
    {
      "day": 1,
      "segments": [
        {
          "time": "오전",
          "place_name": "북촌 한옥마을",
          "description": "전통 거리 산책과 포토 스팟",
          "document_id": "J_HIS_012345",
          "source_url": "https://example.com",
          "notes": "대중교통 이용 권장"
        },
        ...
      ]
    }
  ],
  "highlights": ["한강 야경", "전통 시장"],
  "estimated_budget": "약 30만원",
  "metadata": {
    "domains": ["food", "lei"],
    "region": "서울",
    "parent_context": true
  }
}
```

### 메타데이터
- `model`: 사용한 LLM (예: `gpt-4-turbo`).
- `expansion_metrics`: `/rag/query`와 동일한 변형 지표.
- `cache_hit`: Redis 캐시 사용 여부.
- `generated_at`: ISO8601 타임스탬프.

---

## 5. 처리 플로우
1. 입력 검증 (region/domain/duration 범위 확인).
2. Query Expansion + Redis 캐시 활용으로 후보 장소 조회.
3. Parent summary 포함 문서에서 Day별 후보 리스트 구성.
4. LLM Prompt:
   - 사용자 입력(지역/도메인/테마/이동수단/예산) + 후보 장소 요약.
   - “N개의 일정안을 JSON 형식으로 생성” 지시.
5. 응답 파싱 & 반환, metadata에 지표 기록.

---

## 6. 향후 TODO
- [`docs/API_INTEGRATION_FOR_NODE.md`](./API_INTEGRATION_FOR_NODE.md)에 추천 API 추가.
- Redis TTL/키 전략을 운영 문서에 상세 기재.
- 추천 결과를 저장/재조회할 수 있는 `/recommend/itinerary/{id}` API 검토.
- 프론트엔드 요구에 따라 `themes`, `transport_mode`, `budget_level`의 Enum 값을 확정.

---

문의/수정 사항은 `docs/PROJECT_PLAN.md`의 우선순위 로드맵에 반영해 주세요.
