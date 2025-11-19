# Naver Clova OCR API 명세서

## 개요
Naver Clova OCR API를 사용하여 이미지에서 텍스트를 추출하는 CLI 도구입니다. 한국어, 영어 등 다국어 OCR을 지원하며 고품질 텍스트 인식을 제공합니다.

## 실행 방법

```bash
python run_ocr.py <image> [options]
```

## 파라미터

### 위치 인자

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `image` | Path | 분석할 이미지 파일 경로 (필수) |

### CLI 옵션

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--config` | Path | clova/config.json | 설정 파일 경로 |
| `--dotenv` | Path | clova/.env | .env 파일 경로 |
| `--language` | string | None | 언어 코드 (config 값 덮어씀, 예: ko, en) |
| `--format` | string | None | 이미지 포맷 (config 값 덮어씀, 예: jpg, png) |
| `--timeout` | integer | 15 | HTTP 요청 타임아웃 (초) |
| `--save-json` | Path | None | 원본 JSON 응답 저장 경로 |
| `--save-text` | Path | None | 추출된 텍스트만 저장 경로 |
| `--no-json` | boolean | False | stdout에 JSON 출력 안 함 |

## 환경 변수

`.env` 파일 또는 환경 변수로 설정:

| 변수명 | 설명 | 필수 |
|--------|------|------|
| `CLOVA_OCR_INVOKE_URL` | Clova OCR API 엔드포인트 URL | ✅ |
| `CLOVA_OCR_SECRET_KEY` | Clova OCR API 비밀 키 | ✅ |
| `CLOVA_OCR_DEFAULT_LANG` | 기본 언어 (예: ko) | ❌ |
| `CLOVA_OCR_IMAGE_FORMAT` | 기본 이미지 포맷 (예: jpg) | ❌ |

## 설정 파일

### config.json 구조

```json
{
  "invoke_url": "https://xxx.apigw.ntruss.com/custom/v1/1234/xxx",
  "secret_key": "your-secret-key",
  "default_language": "ko",
  "image_format": "jpg"
}
```

**참고:** 민감한 정보는 `.env` 파일로 관리하는 것을 권장합니다.

## 주요 클래스

### ClovaConfig

Clova OCR API 설정을 담는 불변 데이터 클래스

#### 필드

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `invoke_url` | string | 필수 | API 엔드포인트 URL |
| `secret_key` | string | 필수 | API 비밀 키 |
| `default_language` | string | "ko" | 기본 언어 코드 |
| `image_format` | string | "jpg" | 기본 이미지 포맷 |

#### 메서드

##### as_headers()

```python
def as_headers() -> Dict[str, str]
```

HTTP 요청에 사용할 헤더 딕셔너리를 반환합니다.

**Returns:**
```python
{
    "X-OCR-SECRET": "your-secret-key"
}
```

### ClovaOcrClient

Clova OCR REST API 래퍼 클래스

#### 생성자

```python
ClovaOcrClient(config: ClovaConfig, timeout: int = 15)
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `config` | ClovaConfig | 필수 | Clova 설정 |
| `timeout` | integer | 15 | HTTP 타임아웃 (초) |

#### 메서드

##### recognize()

```python
def recognize(
    image_path: Path,
    language: Optional[str] = None,
    image_format: Optional[str] = None
) -> Dict[str, Any]
```

이미지를 Clova OCR로 전송하고 파싱된 JSON 응답을 반환합니다.

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `image_path` | Path | 필수 | 이미지 파일 경로 |
| `language` | string | None | 언어 코드 (config 기본값 사용 가능) |
| `image_format` | string | None | 이미지 포맷 (config 기본값 사용 가능) |

**Returns:** Clova OCR API 응답 JSON

**Raises:**
- `FileNotFoundError`: 이미지 파일이 없을 때
- `requests.HTTPError`: HTTP 요청 실패

**동작:**
1. 이미지 파일 존재 확인
2. 요청 메시지 구성 (version, requestId, timestamp, language, images)
3. MIME 타입 추측
4. multipart/form-data로 이미지 업로드
5. JSON 응답 반환

## 유틸리티 함수

### response_parser 모듈

#### extract_text_lines()

```python
def extract_text_lines(response: Dict[str, Any]) -> List[str]
```

Clova OCR 응답에서 인식된 텍스트 라인을 추출합니다.

**Parameters:**
- `response`: Clova OCR API 응답

**Returns:** 추출된 텍스트 라인 리스트

**처리:**
- 모든 `images[].fields[].inferText` 추출
- 빈 문자열 제외
- 공백 제거

#### summarize()

```python
def summarize(response: Dict[str, Any]) -> Dict[str, Any]
```

응답 메타데이터 요약을 생성합니다.

**Parameters:**
- `response`: Clova OCR API 응답

**Returns:**
```python
{
    "image_count": 1,
    "field_count": 15
}
```

### config_loader 모듈

#### load_config()

```python
def load_config(
    config_path: Optional[Path] = None,
    dotenv_path: Optional[Path] = None
) -> ClovaConfig
```

설정 파일과 환경 변수를 로드합니다.

**Parameters:**
- `config_path`: 설정 파일 경로 (기본: scripts/ocr/clova/config.json)
- `dotenv_path`: .env 파일 경로 (기본: scripts/ocr/clova/.env)

**Returns:** `ClovaConfig` 인스턴스

**우선순위:** 환경 변수 > config.json

**Raises:**
- `FileNotFoundError`: 설정 파일 없음
- `ValueError`: 필수 값 누락 (invoke_url, secret_key)

## 사용 예시

### 기본 실행

```bash
python run_ocr.py ./sample.jpg
```

**출력:**
```
=== OCR TEXT ===
안녕하세요
환영합니다
[summary] images=1 fields=2
=== RAW JSON ===
{
  "version": "V2",
  "requestId": "...",
  "timestamp": 1700380801000,
  "images": [
    {
      "uid": "...",
      "name": "sample",
      "inferResult": "SUCCESS",
      "message": "SUCCESS",
      "fields": [
        {
          "valueType": "ALL",
          "boundingPoly": {...},
          "inferText": "안녕하세요",
          "inferConfidence": 0.9876
        },
        ...
      ]
    }
  ]
}
```

### 영어 OCR

```bash
python run_ocr.py ./english.png --language en
```

### 텍스트만 저장

```bash
python run_ocr.py ./doc.jpg --save-text ./output.txt
```

**output.txt:**
```
안녕하세요
환영합니다
```

### JSON 응답 저장

```bash
python run_ocr.py ./image.png --save-json ./response.json
```

### JSON 출력 숨기기

```bash
python run_ocr.py ./image.jpg --no-json
```

**출력:**
```
=== OCR TEXT ===
텍스트 내용
[summary] images=1 fields=1
```

### 타임아웃 조정

```bash
# 30초 타임아웃
python run_ocr.py ./large.jpg --timeout 30
```

### 커스텀 설정

```bash
python run_ocr.py ./image.jpg \
  --config ./custom_config.json \
  --dotenv ./prod.env
```

### 조합 사용

```bash
python run_ocr.py ./receipt.jpg \
  --language ko \
  --format jpg \
  --timeout 20 \
  --save-text ./receipt.txt \
  --save-json ./receipt.json \
  --no-json
```

## API 요청 구조

### 요청 메시지

```python
{
    "version": "V2",
    "requestId": "uuid-string",
    "timestamp": 1700380801000,
    "lang": "ko",
    "images": [
        {
            "format": "jpg",
            "name": "sample"
        }
    ]
}
```

### multipart/form-data

```
POST /custom/v1/.../recognize
Content-Type: multipart/form-data; boundary=...

--boundary
Content-Disposition: form-data; name="message"

{JSON 메시지}
--boundary
Content-Disposition: form-data; name="file"; filename="sample.jpg"
Content-Type: image/jpeg

[바이너리 이미지 데이터]
--boundary--
```

### 응답 구조

```python
{
    "version": "V2",
    "requestId": "...",
    "timestamp": 1700380801000,
    "images": [
        {
            "uid": "...",
            "name": "sample",
            "inferResult": "SUCCESS",
            "message": "SUCCESS",
            "validationResult": {
                "result": "NO_REQUESTED"
            },
            "fields": [
                {
                    "valueType": "ALL",
                    "boundingPoly": {
                        "vertices": [
                            {"x": 10, "y": 20},
                            {"x": 100, "y": 20},
                            {"x": 100, "y": 40},
                            {"x": 10, "y": 40}
                        ]
                    },
                    "inferText": "안녕하세요",
                    "inferConfidence": 0.9876
                }
            ]
        }
    ]
}
```

## 지원 언어

| 언어 코드 | 언어 |
|----------|------|
| `ko` | 한국어 |
| `en` | 영어 |
| `ja` | 일본어 |
| `zh-CN` | 중국어 (간체) |
| `zh-TW` | 중국어 (번체) |

## 지원 이미지 포맷

- `jpg` / `jpeg`
- `png`
- `pdf` (일부 API 버전)
- `tiff`

## 에러 처리

### 이미지 파일 없음

```python
FileNotFoundError: image file not found: /path/to/image.jpg
```

### 설정 오류

```python
ValueError: invoke_url is required (config or CLOVA_OCR_INVOKE_URL)
ValueError: secret_key is required (config or CLOVA_OCR_SECRET_KEY)
```

### HTTP 오류

```python
requests.exceptions.HTTPError: 401 Client Error: Unauthorized
requests.exceptions.HTTPError: 429 Too Many Requests
```

### 타임아웃

```python
requests.exceptions.Timeout: HTTPSConnectionPool(...): Read timed out.
```

## 의존성

### 외부 라이브러리
- `requests`: HTTP 클라이언트
- `python-dotenv`: 환경 변수 로드

### 표준 라이브러리
- `argparse`: CLI 파싱
- `json`: JSON 처리
- `pathlib`: 파일 경로
- `mimetypes`: MIME 타입 추측
- `time`: 타임스탬프
- `uuid`: 고유 ID 생성
- `dataclasses`: 데이터 클래스
- `typing`: 타입 힌트

## 참고사항

- Naver Cloud Platform 계정과 Clova OCR 서비스 신청이 필요합니다
- API 키는 환경 변수로 관리하는 것이 안전합니다
- 각 요청마다 고유한 `requestId`(UUID)가 생성됩니다
- timestamp는 밀리초 단위 Unix 시간입니다
- 인식 신뢰도(`inferConfidence`)는 0~1 사이의 값입니다
- 복잡한 문서일수록 타임아웃을 늘려야 할 수 있습니다
