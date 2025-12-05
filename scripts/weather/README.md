# Weather Script

`scripts/weather` 는 Open-Meteo API를 사용해 현재 날씨를 JSON 형식으로 가져오는 유틸리티를 담는 폴더입니다.

## Configuration

1. `config.sample.json` 을 복사해 `config.json` 으로 저장합니다.
2. 위도/경도/시간대를 원하는 위치로 수정합니다.
3. 온도, 풍속 단위는 Open-Meteo 에서 허용하는 값으로 지정합니다.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r scripts/weather/requirements.txt
```

## Usage

기본 config 를 사용해 날씨를 출력하려면 아래 명령을 실행합니다.

```bash
python scripts/weather/get_weather.py
```

위치나 단위를 즉석에서 바꾸고, 결과를 파일로 저장할 수도 있습니다.

```bash
python scripts/weather/get_weather.py \
  --latitude 37.5665 --longitude 126.9780 \
  --timezone Asia/Seoul --temperature-unit celsius \
  --wind-speed-unit ms --output seoul_weather.json
```

오류가 발생하면 표준 오류(stderr) 로 원인을 출력하고 종료 코드 1을 반환합니다.
