# Exchange Script

`scripts/exchange` 는 환율 API를 사용해 현재 환율 정보를 JSON 형식으로 저장하는 유틸리티를 담는 폴더입니다.

## Configuration

1. `config.sample.json` 을 복사해 `config.json` 으로 저장합니다.
2. `base_currency` 와 `symbols` 를 원하는 통화 코드(ISO 4217)로 수정합니다.
3. `amount` 필드로 환산 기준 금액을 지정할 수 있습니다.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r scripts/exchange/requirements.txt
```

## Usage

기본 설정으로 최신 환율을 조회하려면:

```bash
python scripts/exchange/get_exchange_rates.py
```

필요에 따라 통화, 대상 리스트, 금액을 즉석에서 덮어쓰고 결과를 파일로 저장할 수 있습니다.

```bash
python scripts/exchange/get_exchange_rates.py ^
  --base USD --symbols KRW,JPY,EUR ^
  --amount 50 --output usd_rates.json
```

오류가 발생하면 표준 오류(stderr)에 원인을 출력하고 종료 코드 1을 반환합니다.
