# Weather API Suite

This folder gathers scripts that interact with the public weather data APIs
documented in `Weatherapi.md`. The key services are:

- **단기 예보** (`https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0`)
- **중기 예보** (`https://apis.data.go.kr/1360000/MidFcstInfoService`)
- **기상 특보 조회** (`https://apis.data.go.kr/1360000/WthrWrnInfoService`)
- **대기질 정보** (`https://apis.data.go.kr/B552584/ArpltnStatsSvc`)

Each script exposes a CLI so you can quickly inspect current weather conditions,
forecast data, alerts, and air quality metrics. Remember to set the API key via
environment variable or configuration file before running any script.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/weather_api_suite/requirements.txt
export WEATHER_API_KEY="YOUR_SERVICE_KEY"
```

## Usage

The `weather_fetcher.py` entry point aggregates all four services under a single
CLI interface. Examples:

```bash
# Short-term village forecast for Seoul grid
python scripts/weather_api_suite/weather_fetcher.py short-term --nx 60 --ny 127

# Mid-term land forecast (tmFc auto-computed)
python scripts/weather_api_suite/weather_fetcher.py mid-term --mid-region 11B10101

# Weather warnings and air quality samples
python scripts/weather_api_suite/weather_fetcher.py warnings
python scripts/weather_api_suite/weather_fetcher.py air --sido 서울
```

Use `--debug` to inspect raw request metadata if you are troubleshooting request
parameters or responses.

## MongoDB 업로드

API 응답을 MongoDB에 저장하려면 `--upload` 플래그와 접속 정보를 넘겨주세요.
예시는 다음과 같습니다.

```bash
python scripts/weather_api_suite/weather_fetcher.py short-term \
  --nx 60 --ny 127 \
  --upload \
  --mongo-uri "mongodb://admin:Admin1234!@probius.homes:27017/?authSource=admin" \
  --mongo-db weather \
  --mongo-prefix kma
```

서비스별 응답이 `kma_short_term`, `kma_mid_term`와 같은 컬렉션에 저장되며,
각 문서는 호출 시각, 입력 파라미터와 원본 payload를 함께 기록합니다.
