# Weather API 명세서

## 개요
Open-Meteo API를 사용하여 현재 날씨 정보를 조회하는 CLI 도구입니다. JSON 형식으로 날씨 데이터를 출력하고 파일로 저장할 수 있습니다.

## 실행 방법

```bash
python get_weather.py [options]
```

## 파라미터

### CLI 옵션

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--config` | Path | config.json | 설정 파일 경로 |
| `--latitude` | float | None | 위도 (config 값 덮어씀) |
| `--longitude` | float | None | 경도 (config 값 덮어씀) |
| `--timezone` | string | None | 시간대 (예: Asia/Seoul, auto) |
| `--temperature-unit` | string | None | 온도 단위 (celsius, fahrenheit) |
| `--wind-speed-unit` | string | None | 풍속 단위 (ms, kmh, mph, kn) |
| `--output` | Path | None | 결과 JSON 저장 경로 |

## 설정 파일

### config.json 구조

```json
{
  "latitude": 37.5665,
  "longitude": 126.9780,
  "timezone": "Asia/Seoul",
  "temperature_unit": "celsius",
  "wind_speed_unit": "ms"
}
```

**예시 좌표:**
- 서울: `37.5665, 126.9780`
- 부산: `35.1796, 129.0756`
- 뉴욕: `40.7128, -74.0060`
- 런던: `51.5074, -0.1278`

## 주요 클래스 및 함수

### WeatherQuery

날씨 조회 요청을 나타내는 데이터 클래스

#### 필드

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `latitude` | float | 필수 | 위도 (-90 ~ 90) |
| `longitude` | float | 필수 | 경도 (-180 ~ 180) |
| `timezone` | string | "auto" | IANA 시간대 또는 "auto" |
| `temperature_unit` | string | "celsius" | 온도 단위 |
| `wind_speed_unit` | string | "ms" | 풍속 단위 |

#### 메서드

##### to_params()

```python
def to_params() -> Dict[str, Any]
```

API 요청 파라미터 딕셔너리로 변환합니다.

**Returns:**
```python
{
    "latitude": 37.5665,
    "longitude": 126.9780,
    "timezone": "Asia/Seoul",
    "current_weather": True,
    "temperature_unit": "celsius",
    "wind_speed_unit": "ms"
}
```

### WeatherClient

Open-Meteo API 클라이언트

#### 생성자

```python
WeatherClient(
    base_url: str = "https://api.open-meteo.com/v1/forecast",
    session: Optional[requests.Session] = None,
    timeout: int = 10
)
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `base_url` | string | open-meteo.com | API 베이스 URL |
| `session` | requests.Session | None | 재사용할 HTTP 세션 |
| `timeout` | integer | 10 | HTTP 타임아웃 (초) |

#### 메서드

##### fetch_current_weather()

```python
def fetch_current_weather(query: WeatherQuery) -> Dict[str, Any]
```

지정된 위치의 현재 날씨를 조회합니다.

**Parameters:**
- `query`: 날씨 조회 쿼리

**Returns:** 날씨 데이터 딕셔너리

**응답 구조:**

```python
{
    "latitude": 37.5,
    "longitude": 127.0,
    "generationtime_ms": 0.123,
    "utc_offset_seconds": 32400,
    "timezone": "Asia/Seoul",
    "timezone_abbreviation": "KST",
    "elevation": 38.0,
    "current_weather": {
        "temperature": 15.2,
        "windspeed": 3.5,
        "winddirection": 180,
        "weathercode": 1,
        "is_day": 1,
        "time": "2025-11-19T15:00"
    }
}
```

**Raises:**
- `requests.HTTPError`: HTTP 요청 실패
- `ValueError`: 응답에 current_weather 필드 없음

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
3. `WeatherQuery` 생성 (CLI 인자가 우선)
4. API 호출
5. JSON 출력 및 파일 저장 (선택)

## 사용 예시

### 기본 사용 (config.json 사용)

```bash
python get_weather.py
```

**출력:**
```json
{
  "latitude": 37.5,
  "longitude": 127.0,
  "generationtime_ms": 0.456,
  "utc_offset_seconds": 32400,
  "timezone": "Asia/Seoul",
  "timezone_abbreviation": "KST",
  "elevation": 38.0,
  "current_weather": {
    "temperature": 15.2,
    "windspeed": 3.5,
    "winddirection": 180,
    "weathercode": 1,
    "is_day": 1,
    "time": "2025-11-19T15:00"
  }
}
```

### 특정 위치 조회

```bash
# 뉴욕 날씨
python get_weather.py --latitude 40.7128 --longitude -74.0060

# 런던 날씨
python get_weather.py --latitude 51.5074 --longitude -0.1278
```

### 시간대 설정

```bash
# 자동 시간대
python get_weather.py --timezone auto

# 특정 시간대
python get_weather.py --latitude 35.6762 --longitude 139.6503 --timezone Asia/Tokyo
```

### 온도 단위 변경

```bash
# 화씨
python get_weather.py --temperature-unit fahrenheit

# 섭씨 (기본값)
python get_weather.py --temperature-unit celsius
```

### 풍속 단위 변경

```bash
# km/h
python get_weather.py --wind-speed-unit kmh

# mph
python get_weather.py --wind-speed-unit mph

# knots
python get_weather.py --wind-speed-unit kn
```

### 결과 파일 저장

```bash
python get_weather.py --output ./weather.json
```

### 조합 사용

```bash
python get_weather.py \
  --latitude 37.5665 \
  --longitude 126.9780 \
  --timezone Asia/Seoul \
  --temperature-unit celsius \
  --wind-speed-unit ms \
  --output ./seoul_weather.json
```

### 커스텀 설정 파일

```bash
python get_weather.py --config ./custom_config.json
```

## 응답 필드 상세

### current_weather

| 필드 | 타입 | 설명 |
|------|------|------|
| `temperature` | float | 기온 (설정된 단위) |
| `windspeed` | float | 풍속 (설정된 단위) |
| `winddirection` | integer | 풍향 (도, 0-360) |
| `weathercode` | integer | 날씨 코드 (WMO) |
| `is_day` | integer | 낮(1) 또는 밤(0) |
| `time` | string | 관측 시각 (ISO 8601) |

### WMO 날씨 코드

| 코드 | 설명 |
|------|------|
| 0 | 맑음 |
| 1, 2, 3 | 대체로 맑음, 부분적으로 흐림, 흐림 |
| 45, 48 | 안개 |
| 51, 53, 55 | 이슬비 |
| 61, 63, 65 | 비 |
| 71, 73, 75 | 눈 |
| 80, 81, 82 | 소나기 |
| 95, 96, 99 | 뇌우 |

### 풍향 (winddirection)

| 도 | 방향 |
|----|------|
| 0 | 북 (N) |
| 90 | 동 (E) |
| 180 | 남 (S) |
| 270 | 서 (W) |

## 단위

### 온도 (temperature_unit)

| 값 | 단위 |
|----|------|
| `celsius` | 섭씨 (°C) |
| `fahrenheit` | 화씨 (°F) |

### 풍속 (wind_speed_unit)

| 값 | 단위 |
|----|------|
| `ms` | 미터/초 (m/s) |
| `kmh` | 킬로미터/시간 (km/h) |
| `mph` | 마일/시간 (mph) |
| `kn` | 노트 (knots) |

## 에러 처리

### 설정 파일 오류

```bash
$ python get_weather.py --config missing.json
[config] config file not found: missing.json
# Exit code: 1
```

### 필수 필드 누락

```bash
[config] missing required field: 'latitude'
# Exit code: 1
```

### API 요청 실패

```bash
[weather] 요청에 실패했습니다: HTTPSConnectionPool(host='api.open-meteo.com', port=443)
# Exit code: 1
```

### 잘못된 응답

```python
ValueError: API response did not include current_weather field
```

## 프로그래밍 방식 사용

```python
from weather_client import WeatherClient, WeatherQuery

# 클라이언트 생성
client = WeatherClient()

# 쿼리 생성
query = WeatherQuery(
    latitude=37.5665,
    longitude=126.9780,
    timezone="Asia/Seoul",
    temperature_unit="celsius",
    wind_speed_unit="ms"
)

# 날씨 조회
weather = client.fetch_current_weather(query)

# 온도 추출
temp = weather["current_weather"]["temperature"]
print(f"현재 기온: {temp}°C")
```

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

- Open-Meteo는 무료 날씨 API입니다 (API 키 불필요)
- 좌표는 소수점 4자리까지 권장합니다
- timezone "auto"는 좌표에 따라 자동으로 시간대를 감지합니다
- API는 15분마다 업데이트됩니다
- elevation(고도)은 미터 단위로 제공됩니다
- 응답 시간은 일반적으로 100ms 이내입니다
