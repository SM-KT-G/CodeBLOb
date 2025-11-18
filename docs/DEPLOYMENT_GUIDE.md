# 🚀 배포 가이드

## 📋 목차
1. [사전 준비](#사전-준비)
2. [로컬 Docker 실행](#로컬-docker-실행)
3. [프로덕션 배포](#프로덕션-배포)
4. [헬스체크 및 모니터링](#헬스체크-및-모니터링)
5. [문제 해결](#문제-해결)

---

## 🔧 사전 준비

### 1. 필수 소프트웨어
- Docker 20.10 이상
- Docker Compose 2.0 이상

### 2. 환경 변수 설정
프로젝트 루트에 `.env` 파일 생성:

```bash
cp .env.example .env
# .env 파일 편집하여 OPENAI_API_KEY 설정
```

**필수 환경 변수:**
- `OPENAI_API_KEY`: OpenAI API 키 (필수)

---

## 🐳 로컬 Docker 실행

### 1. 전체 스택 실행 (DB + Redis + 백엔드)

```bash
# Docker Compose로 모든 서비스 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f backend
```

### 2. 서비스 확인

```bash
# 모든 컨테이너 상태 확인
docker-compose ps

# 헬스체크
curl http://localhost:8000/health

# Prometheus 메트릭
curl http://localhost:8000/metrics
```

### 3. 데이터 초기화 (최초 1회)

```bash
# PostgreSQL에 벡터 DB 스키마 생성됨 (자동)
# MariaDB에 채팅 히스토리 테이블 생성됨 (자동)

# 초기 데이터 임베딩 (선택)
docker-compose exec backend python scripts/embed_initial_data_v1.1.py
```

### 4. 서비스 중지

```bash
# 서비스 중지 (데이터 보존)
docker-compose down

# 서비스 중지 + 데이터 삭제
docker-compose down -v
```

---

## 🌐 프로덕션 배포

### 옵션 1: Docker Compose (단일 서버)

```bash
# 프로덕션 모드로 실행
docker-compose -f docker-compose.yml up -d

# 백엔드만 재시작 (코드 변경 시)
docker-compose restart backend
```

### 옵션 2: Kubernetes (클러스터 환경)

```bash
# 이미지 빌드 및 레지스트리 푸시
docker build -t your-registry/tourism-backend:latest .
docker push your-registry/tourism-backend:latest

# Kubernetes 배포 (별도 k8s 매니페스트 필요)
# kubectl apply -f k8s/
```

### 환경 변수 설정 (프로덕션)

**Docker Compose 사용 시:**
- `.env` 파일 또는 `docker-compose.yml`의 `environment` 섹션 수정

**Kubernetes 사용 시:**
- Secret/ConfigMap 생성
```bash
kubectl create secret generic tourism-secrets \
  --from-literal=OPENAI_API_KEY=sk-...
```

---

## 📊 헬스체크 및 모니터링

### 1. 헬스체크 엔드포인트

```bash
# 기본 헬스체크
curl http://localhost:8000/health

# 응답 예시:
# {
#   "status": "healthy",
#   "timestamp": "2025-11-18T12:00:00",
#   "services": {
#     "postgres": "connected",
#     "mariadb": "connected",
#     "redis": "connected"
#   }
# }
```

### 2. Prometheus 메트릭

```bash
# Prometheus 메트릭 수집
curl http://localhost:8000/metrics

# 주요 메트릭:
# - rag_query_duration_seconds: RAG 쿼리 응답 시간
# - query_expansion_duration_seconds: Query Expansion 실행 시간
# - cache_hits_total: 캐시 히트 횟수
# - rag_errors_total: RAG 오류 횟수
# - active_requests: 현재 활성 요청 수
```

### 3. 로그 확인

```bash
# 백엔드 로그 (실시간)
docker-compose logs -f backend

# 최근 100줄
docker-compose logs --tail=100 backend

# 특정 컨테이너
docker logs tourism_backend
```

---

## 🛠️ 문제 해결

### 1. 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose logs backend

# 컨테이너 재시작
docker-compose restart backend

# 완전 재빌드
docker-compose up -d --build
```

### 2. DB 연결 실패

```bash
# DB 헬스체크 확인
docker-compose ps

# PostgreSQL 연결 테스트
docker-compose exec postgres psql -U tourism_user -d tourism_db -c "SELECT 1;"

# MariaDB 연결 테스트
docker-compose exec mariadb mariadb -u tourism_user -ptourism_pass -e "SELECT 1;"
```

### 3. 캐시 초기화

```bash
# Redis 캐시 삭제
docker-compose exec redis redis-cli FLUSHALL
```

### 4. 포트 충돌

```bash
# 포트 사용 확인
lsof -i :8000
lsof -i :5432
lsof -i :6379
lsof -i :3306

# docker-compose.yml에서 포트 변경
# ports:
#   - "8001:8000"  # 호스트:컨테이너
```

### 5. 디스크 공간 부족

```bash
# 사용하지 않는 이미지/컨테이너 삭제
docker system prune -a

# 볼륨 확인
docker volume ls

# 특정 볼륨 삭제 (주의!)
docker volume rm training_postgres_data
```

---

## 📝 체크리스트

### 배포 전 확인 사항

- [ ] `.env` 파일에 `OPENAI_API_KEY` 설정
- [ ] Docker 및 Docker Compose 설치 확인
- [ ] 포트 8000, 5432, 6379, 3306 사용 가능 확인
- [ ] 디스크 공간 충분 확인 (최소 10GB)

### 배포 후 확인 사항

- [ ] `docker-compose ps`로 모든 서비스 `Up` 상태 확인
- [ ] `curl http://localhost:8000/health` 응답 확인
- [ ] `curl http://localhost:8000/metrics` Prometheus 메트릭 확인
- [ ] 로그에 에러 없는지 확인 (`docker-compose logs`)

---

## 🔗 관련 문서

- [API 명세서](docs/CHAT_API_SPEC.md)
- [프로젝트 계획](docs/PROJECT_PLAN.md)
- [RAG 파이프라인 아키텍처](docs/RAG_PIPELINE_ARCHITECTURE.md)
- [Redis 캐시 가이드](docs/REDIS_CACHE_GUIDE.md)

---

## 📞 지원

문제가 발생하면:
1. `docker-compose logs backend` 로그 확인
2. GitHub Issues에 로그 첨부하여 문의
3. `/health` 엔드포인트 응답 첨부

**내일까지 배포 일정** ✅
- [x] Dockerfile 작성
- [x] Docker Compose 업데이트
- [ ] 초기 데이터 임베딩
- [ ] 프로덕션 환경 테스트
