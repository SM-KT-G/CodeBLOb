# Simple OCR API 명세서

## 개요
Pillow와 pytesseract를 사용한 기본 OCR 파이프라인 데모 스크립트입니다. 텍스트를 이미지로 렌더링하고 OCR 엔진으로 다시 추출하는 과정을 보여줍니다.

## 실행 방법

```bash
python simple_ocr.py [options]
```

## 파라미터

### CLI 옵션

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--text` | string | "Hello OCR!" | 샘플 이미지에 렌더링할 텍스트 |
| `--font-size` | integer | 48 | 폰트 크기 (포인트 단위) |
| `--output` | string | None | 생성된 이미지 저장 경로 |
| `--show-image` | boolean | False | 기본 이미지 뷰어로 이미지 열기 |
| `--debug` | boolean | False | 추가 로깅 출력 |

## 주요 함수

### build_parser()

```python
def build_parser() -> argparse.ArgumentParser
```

CLI 인자 파서를 생성합니다.

**Returns:** ArgumentParser 인스턴스

### main()

```python
def main() -> None
```

스크립트 진입점 - 전체 OCR 파이프라인을 실행합니다.

**동작:**
1. CLI 인자 파싱
2. 샘플 이미지 생성
3. 이미지 저장 (선택)
4. 이미지 표시 (선택)
5. OCR 텍스트 추출
6. 결과 출력

### generate_sample_image()

```python
def generate_sample_image(text: str, font_size: int) -> Image.Image
```

텍스트를 Pillow 이미지로 렌더링합니다.

**Parameters:**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `text` | string | 렌더링할 텍스트 |
| `font_size` | integer | 폰트 크기 (포인트) |

**Returns:** Pillow Image 객체

**동작:**
1. 폰트 로드 (DejaVuSans.ttf 또는 기본 폰트)
2. 텍스트 크기 계산
3. 이미지 크기 결정 (텍스트 + 패딩 20px)
4. 흰색 배경 이미지 생성
5. 검은색 텍스트 그리기

**이미지 사양:**
- 배경: 흰색 (RGB: 255, 255, 255)
- 텍스트: 검은색 (RGB: 0, 0, 0)
- 패딩: 상하좌우 20px
- 모드: RGB

### extract_text()

```python
def extract_text(image: Image.Image) -> str
```

pytesseract로 이미지에서 텍스트를 추출합니다.

**Parameters:**
- `image`: Pillow Image 객체

**Returns:** 추출된 텍스트 (공백 제거됨)

**사용 OCR 엔진:** Tesseract OCR

### _load_font() (내부 함수)

```python
def _load_font(font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont
```

폰트를 로드하며, 실패 시 기본 폰트로 폴백합니다.

**Parameters:**
- `font_size`: 폰트 크기

**Returns:** 로드된 폰트 객체

**폰트 우선순위:**
1. DejaVuSans.ttf (TrueType)
2. Pillow 기본 폰트

## 사용 예시

### 기본 실행

```bash
python simple_ocr.py
```

**출력:**
```
Recognized text:
Hello OCR!
```

### 커스텀 텍스트

```bash
python simple_ocr.py --text "Python OCR Demo"
```

**출력:**
```
Recognized text:
Python OCR Demo
```

### 디버그 모드

```bash
python simple_ocr.py --text "Test" --debug
```

**출력:**
```
Rendering sample image for text: 'Test'
Running pytesseract on generated image...
Recognized text:
Test
```

### 이미지 저장

```bash
python simple_ocr.py --text "Save Me" --output ./sample.png
```

**디버그 출력 추가 시:**
```
Sample image saved to ./sample.png
```

### 이미지 표시

```bash
python simple_ocr.py --show-image
```

기본 이미지 뷰어로 생성된 이미지가 열립니다.

### 큰 폰트 크기

```bash
python simple_ocr.py --text "Big Text" --font-size 72
```

### 조합 사용

```bash
python simple_ocr.py \
  --text "Complete Demo" \
  --font-size 60 \
  --output ./demo.png \
  --show-image \
  --debug
```

**출력:**
```
Rendering sample image for text: 'Complete Demo'
Sample image saved to ./demo.png
Running pytesseract on generated image...
Recognized text:
Complete Demo
```

## 출력 형식

### 성공 시

```
Recognized text:
[추출된 텍스트]
```

### 텍스트 없음

```
Recognized text:
(no text found)
```

## 기술 세부사항

### 이미지 생성 알고리즘

1. **더미 이미지로 텍스트 크기 측정**
   ```python
   dummy_img = Image.new("RGB", (1, 1), color="white")
   draw = ImageDraw.Draw(dummy_img)
   bbox = draw.textbbox((0, 0), text, font=font)
   ```

2. **실제 이미지 크기 계산**
   ```python
   width = bbox[2] - bbox[0] + padding * 2
   height = bbox[3] - bbox[1] + padding * 2
   ```

3. **최종 이미지 생성 및 텍스트 그리기**
   ```python
   image = Image.new("RGB", (width, height), color="white")
   draw = ImageDraw.Draw(image)
   draw.text((padding, padding), text, fill="black", font=font)
   ```

### OCR 처리

```python
recognized = pytesseract.image_to_string(image).strip()
```

- Tesseract의 기본 설정 사용
- 언어: 영어 (기본)
- PSM 모드: 자동
- 후처리: 양쪽 공백 제거

## 에러 처리

### 폰트 로드 실패

```python
try:
    return ImageFont.truetype("DejaVuSans.ttf", font_size)
except OSError:
    return ImageFont.load_default()  # 폴백
```

폰트 파일을 찾을 수 없으면 자동으로 기본 폰트 사용

### Tesseract 미설치

```bash
$ python simple_ocr.py
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**해결방법:**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# https://github.com/UB-Mannheim/tesseract/wiki 에서 설치
```

## 의존성

### 외부 라이브러리

| 라이브러리 | 용도 | 설치 |
|-----------|------|------|
| `Pillow` | 이미지 생성 및 처리 | `pip install Pillow` |
| `pytesseract` | OCR 엔진 래퍼 | `pip install pytesseract` |

### 시스템 의존성

| 패키지 | 용도 | 필수 |
|--------|------|------|
| `tesseract-ocr` | OCR 엔진 | ✅ |

### 표준 라이브러리
- `argparse`: CLI 인자 파싱

## 제한사항

- 영어 텍스트에 최적화되어 있습니다
- 폰트가 시스템에 설치되어 있지 않으면 기본 폰트 사용
- 복잡한 레이아웃이나 여러 줄의 텍스트는 처리하지 않습니다
- Tesseract OCR이 시스템에 설치되어 있어야 합니다

## 확장 가능성

이 스크립트는 기본 데모이며, 다음과 같이 확장 가능합니다:

1. **다국어 지원**: `pytesseract.image_to_string(image, lang='kor')`
2. **이미지 파일 입력**: 외부 이미지 파일 읽기
3. **여러 OCR 엔진**: EasyOCR, Naver Clova OCR 등
4. **전처리**: 이미지 이진화, 노이즈 제거
5. **후처리**: 신뢰도 점수, 좌표 정보

## 참고사항

- 이미지 품질이 OCR 정확도에 큰 영향을 미칩니다
- 생성된 이미지는 메모리에만 존재하며, `--output` 옵션으로 저장 가능합니다
- `--show-image` 사용 시 OS의 기본 이미지 뷰어가 열립니다
- 디버그 모드는 각 단계를 추적하는 데 유용합니다
