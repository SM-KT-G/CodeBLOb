# CodeBLOb Scripts API 문서 개요

## 📚 문서 색인

이 저장소의 모든 스크립트에 대한 API 명세서가 준비되어 있습니다. 각 스크립트는 독립적으로 실행 가능하며, 상세한 사용법과 예시를 포함하고 있습니다.

---

## 📂 모듈별 문서

### 1. Git 도구
- **[commit_activity_tracker.md](./commit_activity_tracker.md)** - Git 저장소 커밋 활동 분석 및 통계

### 2. 재난/알림 시스템
- **[disaster_alert/api_client.md](./disaster_alert/api_client.md)** - 재난 문자 API 클라이언트
- **[disaster_alert/run_disaster_alert.md](./disaster_alert/run_disaster_alert.md)** - 재난 문자 폴링 및 FCM 푸시

### 3. 환율 정보
- **[exchange/get_exchange_rates.md](./exchange/get_exchange_rates.md)** - 실시간 환율 조회

### 4. OCR (문자 인식)
- **[ocr/simple_ocr.md](./ocr/simple_ocr.md)** - 기본 OCR (Tesseract)
- **[ocr/clova/run_ocr.md](./ocr/clova/run_ocr.md)** - Naver Clova OCR API

### 5. 랜덤 도구 모음
- **[random_suite/README_API.md](./random_suite/README_API.md)** - 카드, 주사위, 색상, 팀 나누기 등 10개 도구

### 6. 유틸리티 도구
- **[random_tools/README_API.md](./random_tools/README_API.md)** - 색상 변환, JSON 포맷팅, 비밀번호 생성 등 7개 도구

### 7. 날씨 정보
- **[weather/get_weather.md](./weather/get_weather.md)** - Open-Meteo 날씨 API
- **[weather_api_suite/weather_fetcher.md](./weather_api_suite/weather_fetcher.md)** - 기상청 공공 API (예보/경보/대기질)

---

## 🚀 빠른 시작

### 공통 요구사항

대부분의 스크립트는 Python 3.7+ 이상에서 동작합니다.

```bash
# Python 버전 확인
python --version  # 또는 python3 --version

# 저장소 클론
git clone https://github.com/SM-KT-G/CodeBLOb.git
cd CodeBLOb/scripts
```

### 의존성 설치

각 모듈별로 requirements.txt가 있는 경우:

```bash
# 재난 알림 시스템
pip install -r disaster_alert/requirements.txt

# 환율 조회
pip install -r exchange/requirements.txt

# OCR
pip install -r ocr/requirements.txt
pip install -r ocr/clova/requirements.txt

# 날씨 조회
pip install -r weather/requirements.txt
pip install -r weather_api_suite/requirements.txt
```

---

## 📖 사용 예시

### Git 커밋 분석
```bash
python commit_activity_tracker.py --start-date 2025-01-01 --csv-output ./report.csv
```

### 재난 문자 모니터링
```bash
python disaster_alert/run_disaster_alert.py --interval 300
```

### 환율 조회
```bash
python exchange/get_exchange_rates.py --base USD --symbols KRW,JPY,EUR
```

### OCR 실행
```bash
# 간단한 OCR
python ocr/simple_ocr.py --text "Hello World"

# Naver Clova OCR
python ocr/clova/run_ocr.py ./image.jpg --language ko
```

### 랜덤 도구
```bash
# 카드 뽑기
python random_suite/random_card_draw.py --count 5

# 팀 나누기
python random_suite/random_team_picker.py --people Alice Bob Charlie David --teams 2

# 비밀번호 생성
python random_tools/password_generator.py --length 16 --symbols
```

### 날씨 조회
```bash
# 현재 날씨
python weather/get_weather.py --latitude 37.5665 --longitude 126.9780

# 기상청 단기예보
python weather_api_suite/weather_fetcher.py short-term --api-key YOUR_KEY
```

---

## 🔧 설정 파일

대부분의 API 기반 스크립트는 설정 파일을 지원합니다:

```
scripts/
├── disaster_alert/
│   ├── config.sample.json
│   └── .env.sample
├── exchange/
│   └── config.sample.json
├── ocr/clova/
│   ├── config.sample.json
│   └── .env.sample
└── weather/
    └── config.sample.json
```

**설정 방법:**
1. `config.sample.json`을 `config.json`으로 복사
2. `.env.sample`을 `.env`로 복사 (있는 경우)
3. API 키 및 필요한 값 입력

---

## 🔑 필요한 API 키

| 모듈 | API 제공처 | 키 발급 URL |
|------|-----------|-------------|
| 재난 알림 | data.go.kr | https://www.data.go.kr |
| 재난 알림 (FCM) | Firebase | https://console.firebase.google.com |
| Clova OCR | Naver Cloud | https://www.ncloud.com |
| 기상청 API | 공공데이터포털 | https://www.data.go.kr |

**무료 API (키 불필요):**
- 환율 조회 (Open Exchange Rates)
- 날씨 조회 (Open-Meteo)

---

## 📊 문서 구조

각 API 문서는 다음 섹션을 포함합니다:

1. **개요** - 스크립트 기능 요약
2. **실행 방법** - 기본 명령어
3. **파라미터** - CLI 옵션 및 설정
4. **주요 클래스/함수** - API 레퍼런스
5. **사용 예시** - 실전 예제
6. **에러 처리** - 일반적인 오류 및 해결법
7. **의존성** - 필요한 패키지
8. **참고사항** - 추가 팁 및 제약사항

---

## 🛠️ 문제 해결

### 일반적인 오류

#### ImportError
```bash
pip install -r <module>/requirements.txt
```

#### API 키 오류
```
ValueError: API key is required
```
→ 환경 변수 또는 config.json 확인

#### 파일 없음
```
FileNotFoundError: config file not found
```
→ `config.sample.json`을 `config.json`으로 복사

### 도움말 확인

모든 스크립트는 `--help` 옵션을 지원합니다:

```bash
python <script>.py --help
```

---

## 📝 라이선스

각 스크립트의 라이선스는 프로젝트 루트의 LICENSE 파일을 참조하세요.

---

## 🤝 기여

문서 개선이나 버그 수정은 언제든 환영합니다!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📞 지원

문제가 발생하거나 질문이 있으시면 GitHub Issues를 이용해 주세요.

---

**마지막 업데이트:** 2025년 11월 19일
