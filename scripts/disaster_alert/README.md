# Disaster Alert

`scripts/disaster_alert` 는 재난 문자 API(재난안전데이터공유플랫폼 DSSP-IF-00247)를 주기적으로 조회하고 새 메시지를 Firebase Cloud Messaging(FCM)으로 전달하는 예제입니다.

## Configuration

1. `config.sample.json` 을 복사해 `config.json` 으로 저장합니다.
2. [.env.sample](.env.sample)을 `.env` 로 복사하고 아래 값을 채웁니다.
   - `DATA_GO_KR_API_KEY`: data.go.kr에서 발급받은 서비스 키.
   - `FIREBASE_CREDENTIALS`: Firebase Admin SDK 서비스 계정 JSON 경로.
   - `FIREBASE_TOPIC`: 푸시를 수신할 토픽명.
3. 필요 시 `config.json` 의 `parsing.items_path` 와 각 필드 이름을 실제 응답 구조에 맞게 조정합니다.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r scripts/disaster_alert/requirements.txt
```

## Usage

- 한 번만 호출:

```bash
python scripts/disaster_alert/run_disaster_alert.py --once --debug
```

- 5분 간격(기본값)으로 반복 실행:

```bash
python scripts/disaster_alert/run_disaster_alert.py
```

주요 옵션:

- `--interval 120` : 폴링 주기를 120초로 변경합니다.
- `--last-id 12345` : 초기 마지막 메시지 ID를 지정해 중복 발송을 방지합니다.
- `--debug` : API 응답 전체(JSON)를 출력해 키 경로를 쉽게 확인합니다.

FCM 토픽 구독은 클라이언트 앱(안드로이드/iOS)에서 사전에 이루어져 있어야 하며, 서비스 계정 JSON은 로컬에 안전하게 보관해야 합니다.
