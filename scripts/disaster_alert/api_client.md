# Disaster API Client API 명세서

## 개요
data.go.kr의 재난 문자 API를 호출하고 정규화된 메시지를 반환하는 클라이언트입니다. HTTP 재시도, 타임아웃, 중복 검사 등의 기능을 제공합니다.

## 클래스

### DisasterMessage

재난 메시지 데이터 클래스 (불변)

#### 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `message_id` | string | 메시지 고유 ID |
| `content` | string | 메시지 내용 |
| `location` | string | 발생 지역 |
| `raw` | Dict[str, Any] | 원본 API 응답 데이터 |

### DisasterApiClient

재난 API 래퍼 클래스

#### 생성자

```python
DisasterApiClient(
    api_config: ApiConfig,
    parsing: ParsingConfig,
    timeout: int = 10,
    retries: int = 3,
    backoff_factor: float = 0.5,
    session: Optional[requests.Session] = None
)
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `api_config` | ApiConfig | 필수 | API 설정 (URL, 파라미터, 서비스 키) |
| `parsing` | ParsingConfig | 필수 | 응답 파싱 설정 |
| `timeout` | int | 10 | HTTP 요청 타임아웃 (초) |
| `retries` | int | 3 | 재시도 횟수 |
| `backoff_factor` | float | 0.5 | 재시도 간격 계산용 백오프 팩터 |
| `session` | requests.Session | None | 재사용할 HTTP 세션 (선택사항) |

## 메서드

### fetch_messages()

```python
def fetch_messages(debug: bool = False) -> Tuple[List[DisasterMessage], Dict[str, Any]]
```

API를 호출하여 정규화된 메시지 목록과 원본 페이로드를 반환합니다.

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `debug` | boolean | False | 디버그 로깅 활성화 여부 |

**Returns:**
- `Tuple[List[DisasterMessage], Dict[str, Any]]`: (메시지 목록, 원본 JSON)

**Raises:**
- `RuntimeError`: API 연결 실패 시
- `requests.HTTPError`: HTTP 에러 발생 시
- `ValueError`: 응답 데이터 파싱 실패 또는 중복 ID 검출 시

**동작:**
1. API 파라미터 구성 (`pageNo`, `numOfRows`, `returnType`, `serviceKey`)
2. HTTP GET 요청 실행
3. 응답 JSON 파싱
4. 설정된 `items_path`를 따라 메시지 항목 추출
5. 각 항목을 `DisasterMessage` 객체로 변환
6. 중복 `message_id` 검사
7. 디버그 모드일 경우 요청/응답 로깅

### close()

```python
def close() -> None
```

세션을 소유하고 있는 경우 HTTP 세션을 종료합니다.

**Parameters:** 없음

**Returns:** None

## 내부 메서드

### _extract_items()

```python
def _extract_items(data: Dict[str, Any]) -> Iterable[Dict[str, Any]]
```

JSON 응답에서 `items_path`를 따라 항목 리스트를 추출합니다.

**Parameters:**
- `data`: API 응답 JSON

**Returns:** 메시지 항목 리스트

**Raises:**
- `ValueError`: 경로가 잘못되었거나 예상 구조가 아닐 때

### _to_message()

```python
def _to_message(item: Dict[str, Any]) -> DisasterMessage
```

API 항목을 `DisasterMessage` 객체로 변환합니다.

**Parameters:**
- `item`: API 응답의 개별 항목

**Returns:** `DisasterMessage` 인스턴스

**Raises:**
- `ValueError`: 필수 필드가 없거나 비어있을 때

### _require_text_field()

```python
def _require_text_field(
    item: Dict[str, Any], 
    field_name: str, 
    label: str
) -> str
```

필수 텍스트 필드를 추출하고 검증합니다.

**Parameters:**
- `item`: 데이터 딕셔너리
- `field_name`: 추출할 필드 이름
- `label`: 에러 메시지용 레이블

**Returns:** 추출된 텍스트 (공백 제거됨)

**Raises:**
- `ValueError`: 필드가 없거나 비어있을 때

### _configure_retries()

```python
def _configure_retries(retries: int, backoff_factor: float) -> None
```

HTTP 어댑터에 재시도 정책을 설정합니다.

**Parameters:**
- `retries`: 최대 재시도 횟수
- `backoff_factor`: 백오프 팩터

**재시도 조건:**
- HTTP 상태 코드: 429, 500, 502, 503, 504
- GET 메서드만 재시도
- 연결, 읽기, 상태 에러에 대해 재시도

## 사용 예시

### 기본 사용

```python
from config_loader import load_app_config
from api_client import DisasterApiClient

# 설정 로드
config = load_app_config()

# 클라이언트 생성
client = DisasterApiClient(
    api_config=config.api,
    parsing=config.parsing
)

# 메시지 조회
messages, raw_data = client.fetch_messages()

for msg in messages:
    print(f"[{msg.location}] {msg.content}")

# 세션 종료
client.close()
```

### 디버그 모드

```python
# 디버그 로깅 활성화
messages, raw_data = client.fetch_messages(debug=True)
```

### 커스텀 재시도 설정

```python
# 재시도 없음
client = DisasterApiClient(
    api_config=config.api,
    parsing=config.parsing,
    retries=0
)

# 긴 타임아웃, 많은 재시도
client = DisasterApiClient(
    api_config=config.api,
    parsing=config.parsing,
    timeout=30,
    retries=5,
    backoff_factor=1.0
)
```

### 세션 재사용

```python
import requests

# 공유 세션 생성
shared_session = requests.Session()

client1 = DisasterApiClient(
    api_config=config.api,
    parsing=config.parsing,
    session=shared_session
)

client2 = DisasterApiClient(
    api_config=config.api,
    parsing=config.parsing,
    session=shared_session
)

# 세션을 직접 관리
shared_session.close()
```

## 에러 처리

### RuntimeError
```python
try:
    messages, data = client.fetch_messages()
except RuntimeError as e:
    print(f"API 연결 실패: {e}")
```

### ValueError (중복 ID)
```python
try:
    messages, data = client.fetch_messages()
except ValueError as e:
    if "Duplicate message_id" in str(e):
        print("중복된 메시지 ID가 감지되었습니다")
```

### ValueError (파싱 실패)
```python
try:
    messages, data = client.fetch_messages()
except ValueError as e:
    print(f"응답 파싱 오류: {e}")
```

## 의존성

### 외부 라이브러리
- `requests`: HTTP 클라이언트
- `urllib3`: HTTP 재시도 정책

### 내부 모듈
- `config_loader.ApiConfig`: API 설정
- `config_loader.ParsingConfig`: 파싱 설정

### 표준 라이브러리
- `json`: JSON 처리
- `time`: 타임스탬프
- `logging`: 로깅
- `dataclasses`: 데이터 클래스
- `typing`: 타입 힌트

## 참고사항

- 기본 파라미터로 `pageNo=1`, `numOfRows=10`, `returnType=json`이 설정됩니다
- 서비스 키는 `ApiConfig`에서 제공받아 자동으로 추가됩니다
- 중복 메시지 ID 검출 시 즉시 예외가 발생합니다
- 재시도는 GET 요청에 대해서만 적용됩니다
- 디버그 모드에서는 서비스 키가 `***REDACTED***`로 마스킹됩니다
