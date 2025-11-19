# Disaster Alert Poller API 명세서

## 개요
재난 문자 API를 주기적으로 폴링하여 새로운 메시지를 감지하고 Firebase Cloud Messaging(FCM)으로 푸시 알림을 전송하는 CLI 도구입니다.

## 실행 방법

```bash
python run_disaster_alert.py [options]
```

## 파라미터

### CLI 옵션

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--config` | string | None | config.json 파일 경로 (기본: 스크립트와 같은 디렉토리) |
| `--dotenv` | string | None | .env 파일 경로 (기본: 스크립트와 같은 디렉토리) |
| `--interval` | integer | None | 폴링 간격(초) - config 값을 덮어씀 |
| `--last-id` | string | None | 초기 마지막 메시지 ID (중복 알림 방지) |
| `--once` | boolean | False | 한 번만 조회하고 종료 |
| `--debug` | boolean | False | API 원본 JSON 출력 |

## 환경 변수

`.env` 파일 또는 환경 변수로 설정:

| 변수명 | 설명 | 필수 |
|--------|------|------|
| `DATA_GO_KR_API_KEY` | data.go.kr API 서비스 키 | ✅ |
| `FIREBASE_CREDENTIALS` | Firebase 서비스 계정 JSON 파일 경로 | ✅ |
| `FIREBASE_TOPIC` | FCM 토픽 이름 | ✅ |

## 설정 파일

### config.json 구조

```json
{
  "api": {
    "url": "https://apis.data.go.kr/...",
    "params": {
      "pageNo": "1",
      "numOfRows": "10"
    }
  },
  "schedule": {
    "interval_seconds": 300
  },
  "firebase": {
    "service_account": "/path/to/firebase-credentials.json",
    "topic": "disaster-alerts"
  },
  "parsing": {
    "items_path": ["response", "body", "items", "item"],
    "id_field": "md101_sn",
    "message_field": "msg_cn",
    "location_field": "rcv_area_nm"
  }
}
```

## 주요 컴포넌트

### DisasterPoller

재난 메시지 폴링 및 알림 전송 담당 클래스

#### 생성자

```python
DisasterPoller(
    api_client: DisasterApiClient,
    notifier: FirebaseNotifier,
    last_message_id: Optional[str] = None
)
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `api_client` | DisasterApiClient | 필수 | 재난 API 클라이언트 |
| `notifier` | FirebaseNotifier | 필수 | FCM 알림 전송자 |
| `last_message_id` | string | None | 마지막으로 처리한 메시지 ID |

#### 메서드

##### check_once()

```python
def check_once(debug: bool = False) -> None
```

재난 메시지를 한 번 조회하고 새 메시지가 있으면 FCM 전송합니다.

**Parameters:**
- `debug`: 디버그 모드 활성화 여부

**동작 흐름:**
1. 현재 시각 출력
2. API 호출하여 최신 메시지 조회
3. 메시지 유효성 검증
4. 마지막 메시지 ID와 비교
5. 새 메시지인 경우 FCM 전송
6. 마지막 메시지 ID 업데이트

**출력 예시:**
```
[Mon Nov 19 10:30:00 2025] 재난 문자 확인 시작...
최신 메시지 ID: 12345
!!! 새로운 재난 문자 발견: [지진] 경기도 부천시...
FCM 푸시 전송 성공: projects/.../messages/...
```

## 함수

### parse_args()

```python
def parse_args() -> argparse.Namespace
```

CLI 인자를 파싱합니다.

**Returns:** 파싱된 인자 네임스페이스

### build_components()

```python
def build_components(args: Namespace) -> tuple[AppConfig, DisasterPoller]
```

설정을 로드하고 필요한 컴포넌트를 초기화합니다.

**Parameters:**
- `args`: CLI 인자

**Returns:** (앱 설정, 폴러) 튜플

**동작:**
1. 설정 파일 로드
2. API 클라이언트 생성
3. Firebase 알림자 생성
4. 폴러 인스턴스 생성

### main()

```python
def main() -> None
```

메인 진입점 - 폴링 루프를 시작하거나 한 번만 실행합니다.

**동작:**
- `--once` 모드: 한 번만 조회하고 종료
- 일반 모드: 지정된 간격으로 무한 폴링
- Ctrl+C로 종료 가능

## 사용 예시

### 기본 실행 (연속 폴링)

```bash
# 기본 설정 파일 사용 (config.json, .env)
python run_disaster_alert.py

# 출력:
# 300초 간격으로 재난 문자를 모니터링합니다.
# [Mon Nov 19 10:30:00 2025] 재난 문자 확인 시작...
```

### 한 번만 조회

```bash
python run_disaster_alert.py --once
```

### 커스텀 설정 파일

```bash
python run_disaster_alert.py \
  --config ./custom_config.json \
  --dotenv ./custom.env
```

### 폴링 간격 변경

```bash
# 60초마다 조회
python run_disaster_alert.py --interval 60
```

### 초기 메시지 ID 설정

```bash
# 특정 ID 이후의 메시지만 처리
python run_disaster_alert.py --last-id "12345"
```

### 디버그 모드

```bash
# API 원본 JSON 확인
python run_disaster_alert.py --debug --once
```

### 조합 사용

```bash
python run_disaster_alert.py \
  --config ./prod_config.json \
  --interval 120 \
  --last-id "67890" \
  --debug
```

## FCM 알림 형식

### 알림 페이로드

```json
{
  "notification": {
    "title": "서울특별시",
    "body": "[지진] 경기도 부천시에서 규모 3.2 지진 발생"
  },
  "topic": "disaster-alerts",
  "data": {
    "message_id": "12345",
    "location": "서울특별시"
  }
}
```

## 에러 처리

### 설정 오류

```python
try:
    config, poller = build_components(args)
except FileNotFoundError as e:
    print(f"설정 파일을 찾을 수 없습니다: {e}")
except ValueError as e:
    print(f"설정 값 오류: {e}")
```

### API 호출 오류

```
[Mon Nov 19 10:30:00 2025] 재난 문자 확인 시작...
API 호출 오류: Failed to reach disaster API at ...
```

### FCM 전송 오류

```
!!! 새로운 재난 문자 발견: [지진] ...
FCM 전송 오류: Invalid service account credentials
```

### 응답 파싱 오류

```
오류: API 응답에서 메시지 ID 또는 내용을 찾을 수 없습니다.
```

## 종료

### 정상 종료
```bash
# Ctrl+C 입력
^C
사용자 종료 요청을 받아 모니터링을 중단합니다.
```

## 의존성

### 외부 라이브러리
- `schedule`: 주기적 작업 스케줄링
- `requests`: HTTP API 호출
- `firebase-admin`: FCM 푸시 알림
- `python-dotenv`: 환경 변수 로드

### 내부 모듈
- `api_client.DisasterApiClient`: 재난 API 클라이언트
- `config_loader`: 설정 로더
- `notifier.FirebaseNotifier`: FCM 알림 전송자
- `poller.DisasterPoller`: 폴링 로직

### 표준 라이브러리
- `argparse`: CLI 인자 파싱
- `time`: 시간 처리

## 동작 원리

### 연속 폴링 모드

1. 초기화: 설정 로드, 컴포넌트 생성
2. 스케줄 등록: `schedule.every(interval).seconds.do(poller.check_once)`
3. 무한 루프:
   - `schedule.run_pending()` 호출
   - 1초 대기
   - 반복
4. Ctrl+C 감지 시 종료

### 한 번 실행 모드

1. 초기화: 설정 로드, 컴포넌트 생성
2. `poller.check_once()` 한 번 호출
3. 즉시 종료

## 참고사항

- Firebase 서비스 계정 JSON 파일이 필요합니다
- data.go.kr API 키는 환경 변수 또는 .env 파일에 설정해야 합니다
- 기본 폴링 간격은 300초(5분)입니다
- 새 메시지 여부는 `message_id` 비교로 판단합니다
- 중복 알림을 방지하기 위해 마지막 메시지 ID를 추적합니다
- 메시지가 없거나 변경이 없으면 푸시를 전송하지 않습니다
