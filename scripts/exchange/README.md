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

향후 커밋에서 실행 스크립트와 설정을 순차적으로 추가할 예정입니다.
