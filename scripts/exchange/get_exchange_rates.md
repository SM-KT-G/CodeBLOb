# Exchange Rate API 명세서

## 개요
Open Exchange Rates API를 사용하여 최신 환율 정보를 조회하는 CLI 도구입니다. JSON 형식으로 환율 데이터를 출력하고 파일로 저장할 수 있습니다.

## 실행 방법

```bash
python get_exchange_rates.py [options]
```

## 파라미터

### CLI 옵션

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--config` | Path | config.json | 설정 파일 경로 |
| `--base` | string | None | 기본 통화 (config 값 덮어씀) |
| `--symbols` | string | None | 쉼표로 구분된 통화 목록 (예: KRW,JPY,EUR) |
| `--amount` | float | None | 환산 기준 금액 (config 값 덮어씀) |
| `--output` | Path | None | 결과 JSON 저장 경로 |

## 설정 파일

### config.json 구조

```json
{
  "base_currency": "USD",
  "symbols": ["KRW", "JPY", "EUR", "GBP", "CNY"],
  "amount": 1.0
}
```

또는 symbols를 쉼표 구분 문자열로:

```json
{
  "base_currency": "USD",
  "symbols": "KRW,JPY,EUR,GBP,CNY",
  "amount": 100.0
}
```

## 주요 클래스 및 함수

### ExchangeQuery

환율 조회 요청을 나타내는 데이터 클래스

#### 필드

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `base_currency` | string | 필수 | 기준 통화 코드 |
| `symbols` | Iterable[str] | 필수 | 조회할 통화 목록 |
| `amount` | float | 1.0 | 환산할 금액 |

#### 메서드

##### normalized_base()

```python
def normalized_base() -> str
```

기준 통화를 대문자로 정규화합니다.

**Returns:** 대문자로 변환된 통화 코드

##### normalized_symbols()

```python
def normalized_symbols() -> List[str]
```

통화 심볼 목록을 정규화(대문자, 공백 제거)합니다.

**Returns:** 정규화된 통화 코드 리스트

### ExchangeClient

Open Exchange Rates API 클라이언트

#### 생성자

```python
ExchangeClient(
    base_url: str = "https://open.er-api.com/v6/latest",
    session: Optional[requests.Session] = None,
    timeout: int = 10
)
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `base_url` | string | open.er-api.com | API 베이스 URL |
| `session` | requests.Session | None | 재사용할 HTTP 세션 |
| `timeout` | int | 10 | HTTP 타임아웃 (초) |

#### 메서드

##### fetch_rates()

```python
def fetch_rates(query: ExchangeQuery) -> Dict[str, object]
```

지정된 통화의 환율을 조회합니다.

**Parameters:**
- `query`: 환율 조회 쿼리

**Returns:** 정규화된 환율 데이터 딕셔너리

**응답 구조:**

```python
{
    "base_code": "USD",
    "amount": 100.0,
    "rates": {
        "KRW": 133500.0,  # amount를 곱한 값
        "JPY": 15000.0,
        "EUR": 92.5
    },
    "missing_symbols": ["XXX"],  # 찾을 수 없는 통화
    "meta": {
        "provider": "https://www.exchangerate-api.com",
        "time_last_update_unix": 1700380801,
        "time_last_update_utc": "Mon, 19 Nov 2025 00:00:01 +0000",
        "time_next_update_unix": 1700467201,
        "time_next_update_utc": "Tue, 20 Nov 2025 00:00:01 +0000"
    },
    "raw_count": 162  # API가 제공하는 전체 통화 수
}
```

**Raises:**
- `requests.HTTPError`: HTTP 요청 실패
- `ValueError`: API 에러 응답 또는 rates 필드 누락

## CLI 함수

### parse_args()

```python
def parse_args() -> argparse.Namespace
```

CLI 인자를 파싱합니다.

**Returns:** 파싱된 인자

### load_config()

```python
def load_config(path: Path) -> Dict[str, Any]
```

JSON 설정 파일을 로드합니다.

**Parameters:**
- `path`: 설정 파일 경로

**Returns:** 설정 딕셔너리

**Raises:**
- `FileNotFoundError`: 파일을 찾을 수 없음
- `json.JSONDecodeError`: JSON 파싱 실패

### main()

```python
def main() -> None
```

메인 실행 함수 - 설정 로드, API 호출, 결과 출력을 수행합니다.

**동작:**
1. CLI 인자 파싱
2. 설정 파일 로드
3. `ExchangeQuery` 생성 (CLI 인자가 우선)
4. API 호출
5. JSON 출력 및 파일 저장 (선택)

## 사용 예시

### 기본 사용 (config.json 사용)

```bash
python get_exchange_rates.py
```

**출력:**
```json
{
  "base_code": "USD",
  "amount": 1.0,
  "rates": {
    "KRW": 1335.0,
    "JPY": 150.0,
    "EUR": 0.925
  },
  "missing_symbols": [],
  "meta": {
    "provider": "https://www.exchangerate-api.com",
    "time_last_update_utc": "Mon, 19 Nov 2025 00:00:01 +0000"
  },
  "raw_count": 162
}
```

### 기본 통화 변경

```bash
# EUR를 기준으로 환율 조회
python get_exchange_rates.py --base EUR
```

### 특정 통화만 조회

```bash
# USD 기준으로 KRW, JPY만 조회
python get_exchange_rates.py --symbols KRW,JPY
```

### 금액 지정

```bash
# 100 USD를 각 통화로 환산
python get_exchange_rates.py --amount 100
```

### 결과 파일 저장

```bash
# stdout과 파일 모두에 저장
python get_exchange_rates.py --output ./rates.json
```

### 조합 사용

```bash
python get_exchange_rates.py \
  --base EUR \
  --symbols KRW,JPY,USD,GBP \
  --amount 50 \
  --output ./eur_rates.json
```

### 커스텀 설정 파일

```bash
python get_exchange_rates.py --config ./custom_config.json
```

## 에러 처리

### 설정 파일 오류

```bash
$ python get_exchange_rates.py --config missing.json
[config] config file not found: missing.json
# Exit code: 1
```

### 필수 필드 누락

```bash
[config] missing required field: 'base_currency'
# Exit code: 1
```

### 잘못된 값

```bash
[config] invalid value: symbols must be a string or iterable
# Exit code: 1
```

### API 요청 실패

```bash
[exchange] API 요청에 실패했습니다: HTTPSConnectionPool(host='open.er-api.com', port=443)
# Exit code: 1
```

### API 에러 응답

```python
# ExchangeClient 내부에서 발생
ValueError: API returned error: unsupported-code
```

## 응답 필드 상세

### rates
요청한 각 통화의 환율 (amount 값을 곱한 결과)

```python
"rates": {
    "KRW": 1335.0,  # 1 USD = 1335 KRW
    "JPY": 150.0    # 1 USD = 150 JPY
}
```

### missing_symbols
API에서 제공하지 않는 통화 목록

```python
"missing_symbols": ["XXX", "YYY"]
```

### meta
API 메타데이터 (업데이트 시간 등)

```python
"meta": {
    "provider": "https://www.exchangerate-api.com",
    "time_last_update_unix": 1700380801,
    "time_last_update_utc": "Mon, 19 Nov 2025 00:00:01 +0000",
    "time_next_update_unix": 1700467201,
    "time_next_update_utc": "Tue, 20 Nov 2025 00:00:01 +0000"
}
```

### raw_count
API가 제공하는 전체 통화 개수

```python
"raw_count": 162
```

## 지원 통화

API는 160개 이상의 통화를 지원합니다. 주요 통화 코드:

- `USD`: 미국 달러
- `EUR`: 유로
- `KRW`: 대한민국 원
- `JPY`: 일본 엔
- `GBP`: 영국 파운드
- `CNY`: 중국 위안
- `AUD`: 호주 달러
- `CAD`: 캐나다 달러

전체 목록은 [Exchange Rate API](https://www.exchangerate-api.com/docs/supported-currencies) 참조

## 의존성

### 외부 라이브러리
- `requests`: HTTP 클라이언트

### 표준 라이브러리
- `argparse`: CLI 파싱
- `json`: JSON 처리
- `pathlib`: 파일 경로
- `typing`: 타입 힌트
- `dataclasses`: 데이터 클래스

## 참고사항

- Open Exchange Rates API는 무료 티어를 제공합니다
- 통화 코드는 자동으로 대문자로 정규화됩니다
- 응답의 `rates` 값은 이미 `amount`가 곱해진 값입니다
- API는 하루 한 번 업데이트됩니다
- 기본 API URL은 인증키가 필요 없는 무료 서비스입니다
