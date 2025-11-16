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
