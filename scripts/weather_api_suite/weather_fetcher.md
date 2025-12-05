# Weather API Suite 명세서

## 개요
대한민국 기상청 및 환경부 공공 API를 사용하여 날씨 예보, 경보, 대기질 데이터를 조회하고 MongoDB에 저장하는 CLI 도구입니다.

## 실행 방법

```bash
python weather_fetcher.py SERVICE [options]
```

## 서비스 종류

| 서비스 | 설명 | API 제공처 |
|--------|------|------------|
| `short-term` | 단기예보 (초단기/동네예보) | 기상청 |
| `mid-term` | 중기예보 (육상/기온) | 기상청 |
| `warnings` | 기상특보 | 기상청 |
| `air` | 대기질 정보 | 환경부 |

## 공통 파라미터

### 필수 옵션

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `service` | string | 필수 | 서비스 종류 (위 표 참조) |
| `--api-key` | string | 환경변수 | API 서비스 키 |

### 선택 옵션

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--debug` | boolean | False | 디버그 로깅 활성화 |
| `--upload` | boolean | False | MongoDB 업로드 활성화 |
| `--mongo-uri` | string | None | MongoDB 연결 URI (--upload 필수) |
| `--mongo-db` | string | weather_data | MongoDB 데이터베이스 이름 |
| `--mongo-prefix` | string | weather | 컬렉션 접두사 |

## 환경 변수

```bash
export WEATHER_API_KEY="your-api-key-here"
```

또는 `--api-key` 옵션으로 직접 전달

## 서비스별 파라미터

### short-term (단기예보)

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--nx` | integer | 60 | 격자 X 좌표 (서울) |
| `--ny` | integer | 127 | 격자 Y 좌표 (서울) |
| `--base-date` | string | auto | 발표일시 (YYYYMMDD) |
| `--base-time` | string | auto | 발표시각 (HHMM) |

### mid-term (중기예보)

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--mid-region` | string | 11B10101 | 지역 코드 (서울) |
| `--mid-tmfc` | string | auto | 발표시각 (YYYYMMDDHHMM) |

### warnings (기상특보)

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--warning-region` | string | 108 | 관측소 ID (전국) |

### air (대기질)

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--sido` | string | 서울 | 시도 이름 |

## 주요 클래스

### WeatherAPIClient

기상청/환경부 API 공통 클라이언트

#### 생성자

```python
WeatherAPIClient(api_key: str, debug: bool = False)
```

**Parameters:**
- `api_key`: API 서비스 키
- `debug`: 디버그 모드

#### 메서드

##### get()

```python
def get(url: str, params: Dict[str, Any]) -> dict[str, Any]
```

API GET 요청을 수행하고 JSON을 반환합니다.

**자동 추가 파라미터:**
- `serviceKey`: API 키
- `dataType`: JSON

### MongoUploader

날씨 데이터를 MongoDB에 저장하는 클래스

#### 생성자

```python
MongoUploader(
    uri: str,
    db_name: str,
    collection_prefix: str = "weather_data",
    debug: bool = False
)
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `uri` | string | 필수 | MongoDB 연결 URI |
| `db_name` | string | 필수 | 데이터베이스 이름 |
| `collection_prefix` | string | "weather_data" | 컬렉션 접두사 |
| `debug` | boolean | False | 디버그 모드 |

#### 메서드

##### ping()

```python
def ping() -> None
```

MongoDB 연결을 확인합니다.

**Raises:** `pymongo.errors.ServerSelectionTimeoutError`

##### insert()

```python
def insert(service: str, metadata: Dict[str, Any], payload: Any) -> None
```

데이터를 삽입합니다.

**Parameters:**
- `service`: 서비스 이름
- `metadata`: 메타데이터 (요청 파라미터)
- `payload`: 실제 데이터

**컬렉션 명명:**
- `weather_data_short_term`
- `weather_data_mid_term`
- `weather_data_warnings`
- `weather_data_air`

**문서 구조:**
```python
{
    "service": "short-term",
    "metadata": {
        "base_date": "20251119",
        "base_time": "1400",
        "nx": 60,
        "ny": 127
    },
    "payload": [...],
    "created_at": datetime.utcnow()
}
```

## 사용 예시

### 단기예보 조회

```bash
# 기본 (서울, 최근 발표 시각)
python weather_fetcher.py short-term --api-key YOUR_KEY

# 특정 지역 (부산)
python weather_fetcher.py short-term --api-key YOUR_KEY --nx 98 --ny 76

# 특정 시각
python weather_fetcher.py short-term \
  --api-key YOUR_KEY \
  --base-date 20251119 \
  --base-time 1400
```

**출력 예시:**
```
20251119 1500 T1H: 15
20251119 1500 RN1: 0
20251119 1500 SKY: 3
20251119 1500 REH: 65
...
```

### 중기예보 조회

```bash
# 서울 지역
python weather_fetcher.py mid-term --api-key YOUR_KEY

# 부산 지역
python weather_fetcher.py mid-term --api-key YOUR_KEY --mid-region 11H20000
```

**출력 예시:**
```
Mid-term outlook (tmFc=202511190600, regId=11B10101):
Day3 AM: 맑음
Day3 PM: 구름많음
Day4 AM: 흐림
Day4 PM: 흐리고 비
...
```

### 기상특보 조회

```bash
# 전국 특보
python weather_fetcher.py warnings --api-key YOUR_KEY

# 특정 지역
python weather_fetcher.py warnings --api-key YOUR_KEY --warning-region 105
```

**출력 예시:**
```
- [202511191500] 서울·인천·경기도 폭설주의보
- [202511191400] 강원영서 대설경보
...
```

### 대기질 조회

```bash
# 서울 대기질
python weather_fetcher.py air --api-key YOUR_KEY

# 부산 대기질
python weather_fetcher.py air --api-key YOUR_KEY --sido 부산
```

**출력 예시:**
```
Air quality in 서울:
- 종로구: PM10=45, PM2.5=23, KHAI=78
- 중구: PM10=52, PM2.5=28, KHAI=82
- 용산구: PM10=38, PM2.5=19, KHAI=65
```

### MongoDB 저장

```bash
# 단기예보 조회 및 저장
python weather_fetcher.py short-term \
  --api-key YOUR_KEY \
  --upload \
  --mongo-uri "mongodb://localhost:27017"

# 대기질 조회 및 저장 (커스텀 DB/컬렉션)
python weather_fetcher.py air \
  --api-key YOUR_KEY \
  --sido 부산 \
  --upload \
  --mongo-uri "mongodb://localhost:27017" \
  --mongo-db air_quality \
  --mongo-prefix air
```

### 디버그 모드

```bash
python weather_fetcher.py short-term --api-key YOUR_KEY --debug
```

**디버그 출력:**
```
[debug] Invoking service=short-term
[debug] GET https://apis.data.go.kr/... params={...}
[debug] Response keys: ['response']
[debug] Inserted document into weather_data.weather_data_short_term id=...
```

## API 응답 구조

### 공통 응답 형식

```json
{
  "response": {
    "header": {
      "resultCode": "00",
      "resultMsg": "NORMAL_SERVICE"
    },
    "body": {
      "dataType": "JSON",
      "items": {
        "item": [
          { /* 데이터 */ }
        ]
      },
      "pageNo": 1,
      "numOfRows": 200,
      "totalCount": 156
    }
  }
}
```

### 단기예보 항목 (item)

```json
{
  "baseDate": "20251119",
  "baseTime": "1400",
  "category": "T1H",
  "fcstDate": "20251119",
  "fcstTime": "1500",
  "fcstValue": "15",
  "nx": 60,
  "ny": 127
}
```

**주요 카테고리:**
- `T1H`: 기온 (℃)
- `RN1`: 1시간 강수량 (mm)
- `SKY`: 하늘상태 (1=맑음, 3=구름많음, 4=흐림)
- `REH`: 습도 (%)
- `UUU`, `VVV`: 풍속 성분
- `WSD`: 풍속 (m/s)

### 중기예보 항목

```json
{
  "regId": "11B10101",
  "tmFc": "202511190600",
  "wf3Am": "맑음",
  "wf3Pm": "구름많음",
  "wf4Am": "흐림",
  "wf4Pm": "흐리고 비",
  ...
}
```

### 기상특보 항목

```json
{
  "title": "서울·인천·경기도 폭설주의보",
  "tmFc": "202511191500",
  "tmSeq": "20251119150001",
  "stnId": "108",
  ...
}
```

### 대기질 항목

```json
{
  "stationName": "종로구",
  "dataTime": "2025-11-19 15:00",
  "pm10Value": "45",
  "pm25Value": "23",
  "khaiValue": "78",
  "khaiGrade": "2",
  ...
}
```

## 지역 코드

### 단기예보 격자 좌표 (주요 도시)

| 지역 | nx | ny |
|------|----|----|
| 서울 | 60 | 127 |
| 부산 | 98 | 76 |
| 대구 | 89 | 90 |
| 인천 | 55 | 124 |
| 광주 | 58 | 74 |
| 대전 | 67 | 100 |

### 중기예보 지역 코드

| 지역 | 코드 |
|------|------|
| 서울·인천·경기도 | 11B10101 |
| 강원도영서 | 11D10301 |
| 강원도영동 | 11D20501 |
| 대전·세종·충청남도 | 11C20101 |
| 충청북도 | 11C10301 |
| 광주·전라남도 | 11F20501 |
| 전라북도 | 11F10201 |
| 부산·울산·경상남도 | 11H20000 |
| 대구·경상북도 | 11H10000 |

### 기상특보 관측소 ID

| 지역 | ID |
|------|----|
| 전국 | 108 |
| 서울 | 109 |
| 경기 | 131 |
| 부산 | 159 |

## 에러 처리

### API 키 누락

```bash
$ python weather_fetcher.py short-term
error: API key not provided via --api-key or WEATHER_API_KEY env var.
```

### MongoDB 연결 실패

```bash
$ python weather_fetcher.py short-term --upload --mongo-uri "mongodb://invalid:27017"
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [Errno 61] Connection refused
```

### API 에러 응답

```python
# API가 에러를 반환하는 경우
{
  "response": {
    "header": {
      "resultCode": "03",
      "resultMsg": "NO_DATA"
    }
  }
}
```

## 헬퍼 함수

### extract_items()

```python
def extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]
```

응답에서 `response.body.items.item` 배열을 안전하게 추출합니다.

### get_short_term_timestamp()

```python
def get_short_term_timestamp(args: Namespace) -> tuple[str, str]
```

현재 시각 기준으로 최근 발표 시각을 계산합니다 (1시간 전 정시).

### compute_mid_tmfc()

```python
def compute_mid_tmfc() -> str
```

중기예보 발표 시각을 계산합니다 (06시 또는 18시).

## 의존성

### 외부 라이브러리

| 라이브러리 | 용도 | 설치 |
|-----------|------|------|
| `requests` | HTTP API 호출 | `pip install requests` |
| `pymongo` | MongoDB 연결 | `pip install pymongo` |

### 표준 라이브러리
- `argparse`: CLI 파싱
- `datetime`: 시간 처리
- `typing`: 타입 힌트

## 참고사항

- API 키는 data.go.kr 또는 공공데이터포털에서 발급받아야 합니다
- MongoDB는 선택사항이며 `--upload` 없이도 사용 가능합니다
- 단기예보는 매시간 정각에 발표됩니다
- 중기예보는 06시, 18시에 발표됩니다
- 대기질 데이터는 1시간마다 업데이트됩니다
- 격자 좌표는 기상청 격자 변환 도구를 사용하여 확인할 수 있습니다
