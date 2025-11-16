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
