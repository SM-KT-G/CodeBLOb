# 🎯 내일까지 배포 체크리스트

## 📅 일정: 2025년 11월 19일까지

---

## ✅ 1단계: Docker 컨테이너화 (완료)

- [x] **Dockerfile 작성**
  - Python 3.10 slim 베이스
  - 필수 시스템 패키지 설치 (gcc, libmariadb-dev, libpq-dev)
  - requirements.txt 의존성 설치
  - Uvicorn 멀티 워커 설정 (4 workers)
  - 헬스체크 설정

- [x] **.dockerignore 작성**
  - 테스트 파일 제외
  - 문서 파일 제외
  - 개발 환경 파일 제외
  - 데이터 파일 제외

- [x] **docker-compose.yml 업데이트**
  - backend 서비스 추가
  - 환경 변수 설정
  - 서비스 의존성 설정 (depends_on)
  - 헬스체크 설정

- [x] **배포 가이드 문서 작성**
  - 로컬 실행 방법
  - 프로덕션 배포 방법
  - 헬스체크 및 모니터링
  - 문제 해결 가이드

---

## 🔄 2단계: 빌드 및 테스트 (진행 중)

- [ ] **Docker 이미지 빌드**
  ```bash
  docker build -t tourism-backend:latest .
  ```

- [ ] **로컬 전체 스택 실행**
  ```bash
  docker-compose up -d
  ```

- [ ] **서비스 헬스체크**
  ```bash
  curl http://localhost:8000/health
  curl http://localhost:8000/metrics
  ```

- [ ] **API 기능 테스트**
  - RAG 쿼리 테스트
  - 통합 채팅 테스트
  - 여행 일정 추천 테스트

---

## 📊 3단계: 초기 데이터 준비

- [ ] **벡터 DB 스키마 확인**
  ```bash
  docker-compose exec postgres psql -U tourism_user -d tourism_db -c "\dt"
  ```

- [ ] **채팅 히스토리 테이블 확인**
  ```bash
  docker-compose exec mariadb mariadb -u tourism_user -ptourism_pass -D tourism_db -e "SHOW TABLES;"
  ```

- [ ] **초기 데이터 임베딩** (선택)
  ```bash
  docker-compose exec backend python scripts/embed_initial_data_v1.1.py
  ```

---

## 🚀 4단계: 프로덕션 배포 준비

### 환경 설정

- [ ] **프로덕션 환경 변수 준비**
  - `.env` 파일에 실제 OPENAI_API_KEY 설정
  - 데이터베이스 비밀번호 변경 권장
  - 로그 레벨 확인 (INFO 또는 WARNING)

- [ ] **보안 설정**
  - `.env` 파일 Git에 커밋되지 않도록 확인 (.gitignore)
  - 프로덕션 DB 비밀번호 강화
  - CORS 설정 확인 (필요 시)

### 서버 설정

- [ ] **서버 환경 확인**
  - Docker 설치 확인
  - Docker Compose 설치 확인
  - 포트 8000, 5432, 6379, 3306 사용 가능 확인
  - 디스크 공간 충분 확인 (최소 10GB)

- [ ] **방화벽 설정** (클라우드 환경)
  - 포트 8000 인바운드 허용
  - 필요시 DB 포트는 내부망만 허용

---

## 🧪 5단계: 배포 후 검증

- [ ] **서비스 상태 확인**
  ```bash
  docker-compose ps
  ```
  - 모든 서비스 `Up` 상태 확인
  - 헬스체크 `healthy` 확인

- [ ] **로그 확인**
  ```bash
  docker-compose logs backend | grep -i error
  ```
  - 에러 로그 없는지 확인

- [ ] **엔드포인트 테스트**
  ```bash
  # 헬스체크
  curl http://your-server-ip:8000/health
  
  # Prometheus 메트릭
  curl http://your-server-ip:8000/metrics
  
  # RAG 쿼리 (샘플)
  curl -X POST http://your-server-ip:8000/rag/query \
    -H "Content-Type: application/json" \
    -d '{"query": "서울 맛집 추천해줘", "top_k": 5}'
  ```

- [ ] **성능 확인**
  - 응답 시간 측정 (< 2초)
  - 메모리 사용량 확인
  - CPU 사용량 확인

---

## 📝 6단계: 문서화 및 인수인계

- [ ] **API 문서 공유**
  - `docs/CHAT_API_SPEC.md` 확인
  - Node.js 팀에게 엔드포인트 URL 전달

- [ ] **운영 가이드 공유**
  - `docs/DEPLOYMENT_GUIDE.md` 전달
  - 헬스체크 방법 안내
  - 로그 확인 방법 안내

- [ ] **모니터링 설정**
  - Prometheus 메트릭 수집 설정
  - 알림 설정 (선택)

---

## 🔧 예상 문제 및 해결책

### 문제 1: 빌드 실패
**원인:** 의존성 충돌 또는 시스템 패키지 부족
**해결:**
```bash
# 캐시 없이 재빌드
docker-compose build --no-cache
```

### 문제 2: DB 연결 실패
**원인:** DB 컨테이너가 아직 준비되지 않음
**해결:**
```bash
# DB 로그 확인
docker-compose logs postgres
docker-compose logs mariadb

# 백엔드 재시작
docker-compose restart backend
```

### 문제 3: 메모리 부족
**원인:** 임베딩 모델 로드 시 메모리 과다 사용
**해결:**
```bash
# Uvicorn 워커 수 감소 (Dockerfile CMD 수정)
# --workers 4 → --workers 2
```

### 문제 4: 느린 응답 속도
**원인:** Redis 캐시 미작동 또는 Query Expansion 타임아웃
**해결:**
```bash
# Redis 연결 확인
docker-compose exec redis redis-cli ping

# 캐시 히트율 확인
curl http://localhost:8000/metrics | grep cache_hits_total
```

---

## 📊 배포 완료 기준

### 필수 조건
- ✅ 모든 Docker 컨테이너 정상 실행
- ✅ `/health` 엔드포인트 200 응답
- ✅ RAG 쿼리 정상 동작 (< 2초)
- ✅ Prometheus 메트릭 수집 확인

### 선택 조건
- ⚪ 초기 데이터 임베딩 완료
- ⚪ 모니터링 대시보드 설정
- ⚪ 자동 재시작 설정 (systemd/supervisord)

---

## 🎉 최종 확인

- [ ] **기능 테스트 완료**
  - RAG 쿼리
  - 통합 채팅
  - 여행 일정 추천

- [ ] **성능 테스트 완료**
  - Query Expansion 병렬 처리 (4배 속도)
  - 캐시 히트율 > 50%
  - 평균 응답 시간 < 2초

- [ ] **모니터링 설정 완료**
  - Prometheus 메트릭 수집
  - 로그 수집 (선택)

- [ ] **문서 전달 완료**
  - API 명세서
  - 배포 가이드
  - 헬스체크 방법

---

## 📞 긴급 연락망

**배포 중 문제 발생 시:**
1. 로그 확인: `docker-compose logs backend`
2. 서비스 재시작: `docker-compose restart backend`
3. 완전 재시작: `docker-compose down && docker-compose up -d`

**롤백 절차:**
```bash
# 모든 서비스 중지
docker-compose down

# 이전 버전으로 복구 (Git)
git checkout <previous-commit>

# 재시작
docker-compose up -d --build
```

---

**✅ 내일 배포 목표: 2025년 11월 19일 18:00까지 프로덕션 환경 정상 가동**
