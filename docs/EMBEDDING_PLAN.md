# 임베딩 데이터 처리 계획

## 📊 데이터 현황

### 데이터 위치
```
labled_data/
├── TL_FOOD/    # 음식점 데이터
├── TL_STAY/    # 숙박 데이터
├── TL_NAT/     # 자연 관광지 데이터
├── TL_HIS/     # 역사 관광지 데이터
├── TL_SHOP/    # 쇼핑 데이터
└── TL_LEI/     # 레저 데이터
```

### 데이터 구조 (JSON)
```json
{
    "data_info": {
        "documentID": "J_FOOD_000001",
        "domain": "음식점",
        "title": "지코바치킨 문경모전점",
        "source": "도서",
        "publishedDate": "2017-03-10"
    },
    "text": "일본어 본문 텍스트...",
    "QA": [
        {
            "question": "질문",
            "answer": "답변"
        }
    ],
    "word_Count": {
        "text": 122,
        "QA": 177
    }
}
```

---

## 🎯 임베딩 전략

### 1. 임베딩 모델
- **모델**: `text-embedding-3-small` (OpenAI)
- **차원**: 1536
- **이유**: readme.md 명세 준수, 비용 효율적, 한국어/일본어 지원 우수

### 2. 임베딩 대상 텍스트
각 JSON 파일에서 **3가지 방식**으로 임베딩:

#### 옵션 A: 본문 전체 임베딩 (권장)
```python
# text 필드만 임베딩
embedding_text = data["text"]
```
- **장점**: 간단, 빠름
- **단점**: QA 정보 활용 안 함

#### 옵션 B: 본문 + QA 결합 임베딩
```python
# text + 모든 QA 결합
qa_text = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in data["QA"]])
embedding_text = f"{data['text']}\n\n{qa_text}"
```
- **장점**: 검색 정확도 향상
- **단점**: 토큰 비용 증가

#### 옵션 C: 본문 + 메타데이터 결합 (최종 권장)
```python
# 제목 + 도메인 + 본문
metadata = f"제목: {data['data_info']['title']}\n도메인: {data['data_info']['domain']}\n"
embedding_text = f"{metadata}{data['text']}"
```

---

## 📅 임베딩 시점

### Phase 1: 초기 데이터 로드 (지금 진행)
```bash
# 스크립트 실행으로 일회성 임베딩
python scripts/embed_initial_data.py
```
- **시점**: 개발 환경 DB 셋업 직후 (Step 2 완료 후)
- **대상**: `labled_data/` 전체 JSON 파일
- **목적**: RAG 시스템 테스트 가능하도록 초기 데이터 준비

### Phase 2: 증분 업데이트 (향후)
```bash
# 새로운 데이터만 추가
python scripts/embed_incremental.py --new-files-only
```
- **시점**: 새 JSON 파일 추가 시
- **트리거**: 수동 실행 또는 CI/CD 파이프라인
- **목적**: 데이터 갱신

### Phase 3: 재임베딩 (필요 시)
```bash
# 전체 데이터 재임베딩 (모델 변경, 스키마 변경 시)
python scripts/embed_initial_data.py --force-reembed
```

---

## 🛠️ 구현 계획

### 스크립트 구조
```
scripts/
├── embed_initial_data.py      # 초기 임베딩 스크립트
├── embed_incremental.py        # 증분 임베딩 스크립트
└── embedding_utils.py          # 공통 유틸리티
```

### embed_initial_data.py 주요 기능
1. **JSON 파일 로드**: `labled_data/` 재귀 탐색
2. **텍스트 추출**: 옵션 C 방식 (본문 + 메타데이터)
3. **임베딩 생성**: OpenAI API 호출 (배치 처리, 에러 핸들링)
4. **DB 저장**: `tourism_data` 테이블에 INSERT
5. **진행 상황 로깅**: 처리된 파일 수, 실패 파일 기록
6. **중복 방지**: `documentID`로 이미 임베딩된 데이터 스킵

### 데이터베이스 매핑
```sql
INSERT INTO tourism_data (
    document_id,     -- data_info.documentID
    domain,          -- data_info.domain → ENUM 변환
    title,           -- data_info.title
    content,         -- text 필드
    embedding,       -- OpenAI embedding vector
    metadata         -- data_info 전체 JSON
) VALUES (...);
```

### 도메인 매핑
```python
DOMAIN_MAPPING = {
    "음식점": "food",
    "숙박": "stay",
    "자연": "nat",
    "역사": "his",
    "쇼핑": "shop",
    "레저": "lei"
}
```

---

## 💰 비용 예측

### OpenAI 임베딩 비용
- **모델**: `text-embedding-3-small`
- **가격**: $0.02 / 1M tokens
- **예상 평균 텍스트**: 200 tokens/문서
- **총 파일 수**: 약 500개 (추정)
- **총 비용**: (500 × 200) / 1,000,000 × $0.02 = **$0.002** (약 3원)

→ **매우 저렴하므로 재임베딩도 부담 없음**

---

## ⚙️ 실행 예시

### 1. 초기 임베딩 (개발 환경)
```bash
# .env 파일에 OPENAI_API_KEY 설정 필요
source .venv/bin/activate
python scripts/embed_initial_data.py

# 출력 예시:
# [INFO] 총 523개 JSON 파일 발견
# [INFO] TL_FOOD: 89개 처리 중...
# [INFO] TL_STAY: 102개 처리 중...
# [INFO] 임베딩 완료: 523개 성공, 0개 실패
# [INFO] 소요 시간: 2분 34초
```

### 2. 특정 도메인만 임베딩
```bash
python scripts/embed_initial_data.py --domains food,stay
```

### 3. 드라이런 (실제 DB 저장 없이 테스트)
```bash
python scripts/embed_initial_data.py --dry-run
```

---

## 🔍 품질 검증

### 임베딩 후 확인 사항
1. **DB 레코드 수 확인**
```sql
SELECT domain, COUNT(*) FROM tourism_data GROUP BY domain;
```

2. **벡터 차원 확인**
```sql
SELECT document_id, vector_dims(embedding) FROM tourism_data LIMIT 5;
```

3. **검색 테스트**
```python
from backend.retriever import Retriever
retriever = Retriever()
results = retriever.search("韓国の美味しいチキン料理", top_k=3)
print(results)
```

---

## 📋 체크리스트

### Step 2.5: 임베딩 데이터 준비 (DB 셋업 직후)
- [ ] `scripts/` 디렉토리 생성
- [ ] `embedding_utils.py` 작성 (JSON 로드, 도메인 매핑 함수)
- [ ] `embed_initial_data.py` 작성
  - [ ] JSON 파일 재귀 탐색
  - [ ] 텍스트 추출 (옵션 C)
  - [ ] OpenAI 임베딩 API 호출 (배치 처리)
  - [ ] DB INSERT with error handling
  - [ ] 진행 상황 로깅
  - [ ] 중복 방지 로직
- [ ] 개발 환경에서 임베딩 실행
- [ ] DB 데이터 검증 (레코드 수, 벡터 차원)
- [ ] Retriever로 검색 테스트
- [ ] IMPLEMENTATION_TRACKER.md에 완료 기록

---

## 🚀 다음 단계

1. **지금 바로**: `scripts/embed_initial_data.py` 작성
2. **DB 셋업 완료 후**: 초기 임베딩 실행
3. **RAG 구현 후**: 실제 검색 품질 확인
4. **프로덕션 배포 전**: 전체 데이터 재임베딩

---

> 이 계획은 PROJECT_PLAN.md Step 2와 Step 3 사이에 위치하며, RAG 시스템이 실제 데이터를 검색할 수 있도록 준비하는 핵심 단계입니다.
