# Random Tools API 명세서

## 개요
다양한 유틸리티 도구 모음입니다. 색상 변환, JSON 포맷팅, 회문 검사, 비밀번호 생성, 시간대 변환, UUID 생성 등의 기능을 제공합니다.

---

## color_converter.py

### 기능
HEX와 RGB 색상 형식 간 변환 및 보색 계산을 수행합니다.

### 실행 방법
```bash
python color_converter.py {--hex HEX | --rgb R G B} [--complement]
```

### 파라미터

| 옵션 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `--hex` | string | 택일 | HEX 색상 코드 (예: #FFEE00) |
| `--rgb` | int int int | 택일 | RGB 색상 (0-255) |
| `--complement` | boolean | ❌ | 보색도 함께 표시 |

### 함수

#### hex_to_rgb()
```python
def hex_to_rgb(value: str) -> Tuple[int, int, int]
```

HEX 문자열을 RGB 튜플로 변환합니다.

**Raises:** `ValueError` - 잘못된 HEX 형식

#### rgb_to_hex()
```python
def rgb_to_hex(r: int, g: int, b: int) -> str
```

RGB 값을 HEX 문자열로 변환합니다.

**Raises:** `ValueError` - RGB 값이 0-255 범위 밖

#### complement_rgb()
```python
def complement_rgb(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]
```

보색을 계산합니다 (각 성분을 255에서 뺌).

### 사용 예시

```bash
# HEX to RGB
python color_converter.py --hex #FF5733
# 출력:
# HEX: #FF5733
# RGB: (255, 87, 51)

# RGB to HEX
python color_converter.py --rgb 255 87 51
# 출력:
# HEX: #FF5733
# RGB: (255, 87, 51)

# 보색 계산
python color_converter.py --hex #FF5733 --complement
# 출력:
# HEX: #FF5733
# RGB: (255, 87, 51)
# Complement HEX: #00A8CC
# Complement RGB: (0, 168, 204)
```

---

## json_formatter.py

### 기능
JSON 데이터를 포맷팅하거나 압축합니다.

### 실행 방법
```bash
python json_formatter.py [--file PATH | --text JSON] [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--file` | string | None | JSON 파일 경로 |
| `--text` | string | None | 인라인 JSON 문자열 |
| `--indent` | integer | 2 | 들여쓰기 레벨 |
| `--minify` | boolean | False | 압축 모드 (공백 제거) |
| `--sort-keys` | boolean | False | 키를 알파벳 순으로 정렬 |

**참고:** `--file`과 `--text` 모두 생략 시 STDIN에서 읽습니다.

### 함수

#### load_payload()
```python
def load_payload(source: str | None, text: str | None) -> Any
```

파일, 문자열 또는 STDIN에서 JSON을 로드합니다.

#### format_payload()
```python
def format_payload(payload: Any, minify: bool, indent: int, sort_keys: bool) -> str
```

JSON을 포맷팅하거나 압축합니다.

### 사용 예시

```bash
# 파일 포맷팅
python json_formatter.py --file data.json

# 인라인 JSON 포맷팅
python json_formatter.py --text '{"name":"Alice","age":30}'
# 출력:
# {
#   "name": "Alice",
#   "age": 30
# }

# 압축
python json_formatter.py --file data.json --minify
# 출력: {"name":"Alice","age":30}

# 키 정렬
python json_formatter.py --text '{"z":1,"a":2}' --sort-keys
# 출력:
# {
#   "a": 2,
#   "z": 1
# }

# STDIN 사용
echo '{"key":"value"}' | python json_formatter.py
```

---

## palindrome_inspector.py

### 기능
문자열이 회문인지 검사하고 불일치 위치를 보고합니다.

### 실행 방법
```bash
python palindrome_inspector.py TEXT [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `TEXT` | string | 필수 | 검사할 문자열 |
| `--keep-case` | boolean | False | 대소문자 구분 |
| `--keep-symbols` | boolean | False | 특수문자 유지 |

**기본 동작:** 소문자 변환 + 영숫자만 유지

### 함수

#### normalize()
```python
def normalize(text: str, ignore_case: bool, alnum_only: bool) -> str
```

텍스트를 정규화합니다.

#### find_mismatches()
```python
def find_mismatches(text: str) -> List[Tuple[int, str, str]]
```

회문 대칭에서 불일치하는 위치를 찾습니다.

#### inspect_palindrome()
```python
def inspect_palindrome(
    text: str, 
    ignore_case: bool = True, 
    alnum_only: bool = True
) -> Tuple[bool, List[Tuple[int, str, str]], str]
```

회문 여부, 불일치 목록, 정규화된 텍스트를 반환합니다.

### 사용 예시

```bash
# 회문 검사
python palindrome_inspector.py "A man a plan a canal Panama"
# 출력:
# Normalized text: amanaplanacanalpanama
# ✅ This is a palindrome.
# Exit code: 0

# 회문 아님
python palindrome_inspector.py "hello"
# 출력:
# Normalized text: hello
# ❌ Not a palindrome. First few mismatches:
#   position 0: 'h' != 'o'
#   position 1: 'e' != 'l'
# Exit code: 1

# 대소문자 구분
python palindrome_inspector.py "Racecar" --keep-case
# 출력:
# Normalized text: Racecar
# ❌ Not a palindrome. First few mismatches:
#   position 0: 'R' != 'r'

# 특수문자 유지
python palindrome_inspector.py "A-B-A" --keep-symbols
# 출력:
# Normalized text: A-B-A
# ✅ This is a palindrome.
```

---

## password_generator.py

### 기능
암호학적으로 안전한 비밀번호를 생성합니다 (secrets 모듈 사용).

### 실행 방법
```bash
python password_generator.py [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--length` | integer | 16 | 비밀번호 길이 |
| `--no-upper` | boolean | False | 대문자 제외 |
| `--no-lower` | boolean | False | 소문자 제외 |
| `--no-digits` | boolean | False | 숫자 제외 |
| `--symbols` | boolean | False | 특수문자 포함 |

### 문자 집합

| 클래스 | 문자 |
|--------|------|
| lower | a-z |
| upper | A-Z |
| digits | 0-9 |
| symbols | !@#$%^&*()-_=+[]{};:,.<>/? |

**기본:** lower + upper + digits

### 함수

#### generate_password()
```python
def generate_password(length: int, include: List[str]) -> str
```

안전한 비밀번호를 생성합니다.

**보장:** 각 문자 클래스에서 최소 1개 이상 포함

### 사용 예시

```bash
# 기본 (16자, 영문+숫자)
python password_generator.py
# 출력: aB3dE9fG2hI5jK7l

# 특수문자 포함
python password_generator.py --symbols
# 출력: xY3z!@A7b#C9$D

# 길이 변경
python password_generator.py --length 32

# 소문자와 숫자만
python password_generator.py --no-upper --length 20

# 최대 보안 (모든 문자 포함)
python password_generator.py --symbols --length 24
```

---

## random_fun.py

### 기능
random 모듈의 다양한 기능을 시연합니다.

### 실행 방법
```bash
python random_fun.py [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--count` | integer | 5 | 샘플 개수 |
| `--seed` | integer | None | 난수 시드 |

### 출력 섹션

1. **Random integers**: 1-100 범위의 정수
2. **Integer stats**: 평균, 표준편차, 최소/최대
3. **Random fruit picks**: 과일 이모지 무작위 선택
4. **Sample passwords**: 12자 비밀번호 (최대 3개)

### 사용 예시

```bash
# 기본 실행
python random_fun.py
# 출력:
# Random demo running with count=5
# 
# == Random integers ==
# 42, 87, 13, 95, 28
# 
# == Integer stats ==
# mean=53.00, stdev=34.25, min=13, max=95
# 
# == Random fruit picks ==
# 🍎 apple
# 🍌 banana
# 🍇 grape
# 🥝 kiwi
# 🍓 strawberry
# 
# == Sample passwords ==
# aB3dE9fG2hI5
# xY7zA1bC4dE6
# mN9oP2qR5sT8

# 샘플 수 변경
python random_fun.py --count 10

# 재현 가능한 결과
python random_fun.py --seed 42 --count 3
```

---

## timezone_converter.py

### 기능
시간대 간 datetime 변환을 수행합니다 (zoneinfo 사용).

### 실행 방법
```bash
python timezone_converter.py --from-zone ZONE1 --to-zone ZONE2 [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--time` | string | 현재 시각 | ISO 형식 datetime |
| `--from-zone` | string | 필수 | 원본 시간대 (IANA) |
| `--to-zone` | string | 필수 | 대상 시간대 (IANA) |
| `--format` | string | %Y-%m-%d %H:%M:%S %Z%z | 출력 strftime 형식 |

### 함수

#### convert_time()
```python
def convert_time(
    moment: datetime, 
    from_zone: str, 
    to_zone: str
) -> tuple[datetime, datetime]
```

시간대를 변환합니다.

**Returns:** (원본 aware datetime, 변환된 aware datetime)

### 사용 예시

```bash
# 현재 시각 변환 (서울 -> 뉴욕)
python timezone_converter.py --from-zone Asia/Seoul --to-zone America/New_York
# 출력:
# Source: 2025-11-19 15:30:00 KST+0900
# Target: 2025-11-19 01:30:00 EST-0500

# 특정 시각 변환
python timezone_converter.py \
  --time "2025-12-25T18:00:00" \
  --from-zone Europe/London \
  --to-zone Asia/Tokyo

# 커스텀 포맷
python timezone_converter.py \
  --from-zone UTC \
  --to-zone Asia/Seoul \
  --format "%Y년 %m월 %d일 %H시 %M분"
```

**주요 시간대:**
- `UTC`
- `Asia/Seoul`
- `America/New_York`
- `Europe/London`
- `Asia/Tokyo`

---

## uuid_batcher.py

### 기능
UUID를 배치로 생성합니다 (버전 4, 5 지원).

### 실행 방법
```bash
python uuid_batcher.py [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--count` | integer | 5 | 생성할 UUID 개수 |
| `--version` | integer | 4 | UUID 버전 (4 또는 5) |
| `--namespace` | string | None | V5용 네임스페이스 (dns/url/oid/x500) |
| `--name` | string | None | V5용 이름 |
| `--output` | string | None | 파일 저장 경로 |

### UUID 버전

#### 버전 4 (무작위)
```bash
python uuid_batcher.py --version 4 --count 3
# 출력:
# 8f3b5a21-9c7d-4e2f-a1b3-6d8e9f0a2c4b
# 2a7c6d9e-1f4b-4a8c-9e3d-5b7f8a1c2d3e
# 6c9d2e4f-3a7b-4c8d-a2e5-9f1b3c5d7e8f
```

#### 버전 5 (네임스페이스 기반)
```bash
python uuid_batcher.py --version 5 --namespace dns --name example.com --count 2
# 출력:
# 9073926b-929f-5dcf-b9e5-5f7c9c5e3b1a
# 2f8e5d9c-3a7b-5c8d-a1e4-6b9f2c4d8e7a
```

### 네임스페이스

| 키 | 설명 |
|----|------|
| `dns` | 도메인 이름 |
| `url` | URL |
| `oid` | ISO OID |
| `x500` | X.500 DN |

### 사용 예시

```bash
# 파일 저장
python uuid_batcher.py --count 10 --output uuids.txt

# 재현 가능한 UUID (버전 5)
python uuid_batcher.py --version 5 --namespace url --name "https://example.com" --count 5
```

---

## 공통 사항

### Exit Codes

대부분의 스크립트가 다음 규칙을 따릅니다:
- `0`: 성공
- `1`: 오류 (잘못된 인자, 파일 없음 등)

### 의존성

#### 외부 라이브러리
- 없음 (모두 표준 라이브러리 사용)

#### Python 버전
- Python 3.9+ (zoneinfo 사용하는 스크립트)
- Python 3.7+ (나머지)

### 설치

```bash
# Python 버전 확인
python --version

# 외부 패키지 불필요
```

## 참고사항

- 모든 스크립트는 독립적으로 실행 가능합니다
- `--help` 옵션으로 각 스크립트의 도움말을 볼 수 있습니다
- password_generator.py는 `secrets` 모듈을 사용하여 암호학적으로 안전합니다
- timezone_converter.py는 Python 3.9+의 `zoneinfo`를 사용합니다
- JSON 도구들은 UTF-8 인코딩을 사용합니다
