# CodeBLOb
Place for all the code

## 설명
- 백엔드와 프론트 레포지토리에 올리기 전 거쳐가는 레포지토리입니다.
- 하루에 1인당 최소 10커밋씩 올려야합니다.
- 중요한 api 키는 올리지 않도록 주의해주시기 바랍니다.

## 📚 Scripts 문서

모든 스크립트에 대한 상세한 API 명세서가 준비되어 있습니다!

👉 **[전체 문서 색인 보기](./scripts/DOCUMENTATION_INDEX.md)**

### 주요 모듈

#### 🔧 유틸리티 도구
- **Git 분석**: [commit_activity_tracker.md](./scripts/commit_activity_tracker.md) - 커밋 활동 통계 및 CSV 내보내기
- **랜덤 도구**: [random_suite](./scripts/random_suite/README_API.md) - 카드, 주사위, 팀 나누기 등 10개 도구
- **변환 도구**: [random_tools](./scripts/random_tools/README_API.md) - 색상 변환, JSON 포맷팅, 비밀번호 생성 등

#### 🌐 API 통합
- **재난 알림**: [disaster_alert](./scripts/disaster_alert/run_disaster_alert.md) - 재난 문자 모니터링 및 FCM 푸시
- **환율 조회**: [exchange](./scripts/exchange/get_exchange_rates.md) - 실시간 환율 정보
- **날씨 정보**: 
  - [weather](./scripts/weather/get_weather.md) - Open-Meteo API
  - [weather_api_suite](./scripts/weather_api_suite/weather_fetcher.md) - 기상청 공공 API

#### 🖼️ OCR (문자 인식)
- **Simple OCR**: [simple_ocr.md](./scripts/ocr/simple_ocr.md) - Tesseract 기반 기본 OCR
- **Clova OCR**: [run_ocr.md](./scripts/ocr/clova/run_ocr.md) - Naver Clova OCR API

### 빠른 시작

```bash
# 저장소 클론
git clone https://github.com/SM-KT-G/CodeBLOb.git
cd CodeBLOb/scripts

# 각 스크립트의 도움말 확인
python <script>.py --help

# 상세 문서 확인
cat <module>/<script>.md
```

자세한 사용법과 예시는 각 문서를 참조하세요.
