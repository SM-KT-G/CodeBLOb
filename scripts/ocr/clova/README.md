# Clova OCR

`scripts/ocr/clova` 는 네이버 클로바 OCR API를 호출하는 예제 스크립트를 담는 폴더입니다.

## Configuration

1. `config.sample.json` 을 복사해 `config.json` 으로 저장합니다.
2. 네이버 클라우드 콘솔에서 발급받은 **Invoke URL** 과 **Secret Key** 를 입력합니다.
3. 필요하다면 `.env.sample` 을 `.env` 로 복사해 `CLOVA_OCR_*` 환경변수를 채웁니다. JSON 값보다 환경변수가 우선합니다.
4. 기본 언어나 이미지 포맷을 원하는 값으로 수정합니다.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r scripts/ocr/clova/requirements.txt
```

## Usage

기본 설정을 사용해 이미지를 분석하려면:

```bash
python scripts/ocr/clova/run_ocr.py sample.png \
  --language ko --save-text output/text.txt --save-json output/raw.json
```

- `--language` / `--format` 으로 요청 언어 및 이미지 포맷을 덮어쓸 수 있습니다.
- `--save-text`, `--save-json` 으로 결과를 파일에 저장합니다.
- `--no-json` 옵션을 주면 표준 출력에는 추출 텍스트만 표시합니다.

앞으로 템플릿 기반 호출, 다중 이미지 배치, 테스트 등을 순차적으로 추가할 예정입니다.
