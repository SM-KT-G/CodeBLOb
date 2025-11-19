# Commit Activity Tracker API 명세서

## 개요
Git 저장소의 커밋 활동을 분석하고 추적하는 유틸리티 스크립트입니다. 작성자별, 날짜별 커밋 통계를 제공하며 CSV 형식으로 내보낼 수 있습니다.

## 실행 방법

```bash
python commit_activity_tracker.py [repo] [options]
```

## 파라미터

### 위치 인자

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `repo` | string | `.` (현재 디렉토리) | Git 저장소 경로 |

### 옵션 인자

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--start-date` | string | None | 커밋 조회 시작 날짜 (YYYY-MM-DD) |
| `--end-date` | string | None | 커밋 조회 종료 날짜 (YYYY-MM-DD) |
| `--branch` | string | None | 분석할 브랜치 (기본값: 현재 HEAD) |
| `--include-merges` | boolean | False | 병합 커밋 포함 여부 |
| `--csv-output` | string | None | CSV 파일 출력 경로 |
| `--min-count` | integer | 1 | 최소 커밋 수 (이 값 이상의 커밋만 표시) |

## 응답 형식

### 표준 출력

#### 1. 일별 커밋 통계
```
Daily commit totals:
------------------------------------------------------------
Date         Author                    Commits
------------------------------------------------------------
2025-11-19   John Doe                        5
2025-11-19   Jane Smith                      3
------------------------------------------------------------
```

#### 2. 작성자별 총계
```
Author totals:
------------------------------------------------------------
Author                    Commits
------------------------------------------------------------
John Doe                        15
Jane Smith                      10
------------------------------------------------------------
```

### CSV 출력 형식

`--csv-output` 옵션 사용 시 생성되는 파일 구조:

```csv
date,author,commit_count
2025-11-19,John Doe,5
2025-11-19,Jane Smith,3
```

## 데이터 모델

### CommitRecord
커밋 정보를 담는 데이터 클래스

| 필드 | 타입 | 설명 |
|------|------|------|
| `sha` | string | 커밋 해시 |
| `author` | string | 작성자 이름 |
| `authored_at` | datetime | 커밋 작성 시각 |

### DailySummary
일별 요약 정보를 담는 데이터 클래스

| 필드 | 타입 | 설명 |
|------|------|------|
| `author` | string | 작성자 이름 |
| `day` | date | 날짜 |
| `count` | integer | 커밋 수 |

## 주요 함수

### `load_commits(repo_path: Path, args: Namespace) -> List[CommitRecord]`
Git 로그를 실행하고 커밋 레코드를 파싱합니다.

**Parameters:**
- `repo_path`: 저장소 경로
- `args`: CLI 인자

**Returns:** 커밋 레코드 리스트

**Raises:**
- `RuntimeError`: Git 명령 실행 실패 시

### `summarize_by_day(commits: Iterable[CommitRecord]) -> List[DailySummary]`
커밋을 작성자/날짜 쌍으로 그룹화합니다.

**Parameters:**
- `commits`: 커밋 레코드 이터러블

**Returns:** 일별 요약 리스트 (날짜, 작성자 순으로 정렬)

### `write_csv(summaries: Iterable[DailySummary], destination: Path) -> None`
일별 요약을 CSV 파일로 저장합니다.

**Parameters:**
- `summaries`: 일별 요약 이터러블
- `destination`: 저장 경로

## 사용 예시

### 기본 사용
```bash
# 현재 디렉토리의 저장소 분석
python commit_activity_tracker.py

# 특정 저장소 분석
python commit_activity_tracker.py /path/to/repo
```

### 날짜 필터링
```bash
# 특정 기간의 커밋만 조회
python commit_activity_tracker.py --start-date 2025-01-01 --end-date 2025-11-19
```

### CSV 내보내기
```bash
# 결과를 CSV 파일로 저장
python commit_activity_tracker.py --csv-output ./output/commits.csv
```

### 병합 커밋 포함
```bash
# 병합 커밋을 포함하여 분석
python commit_activity_tracker.py --include-merges
```

### 최소 커밋 수 필터
```bash
# 5개 이상의 커밋이 있는 경우만 표시
python commit_activity_tracker.py --min-count 5
```

### 특정 브랜치 분석
```bash
# develop 브랜치의 커밋 분석
python commit_activity_tracker.py --branch develop
```

## 에러 처리

### FileNotFoundError
저장소 경로가 존재하지 않을 때 발생
```
Error: Repository path does not exist: /invalid/path
```

### RuntimeError
Git 저장소가 아닌 경로를 지정했을 때 발생
```
Error: /path is not a git repository.
```

Git 명령 실행 실패 시 발생
```
Error: Failed to read git log
```

## 의존성

### 표준 라이브러리
- `argparse`: CLI 인자 파싱
- `collections.defaultdict`: 데이터 집계
- `csv`: CSV 파일 작성
- `dataclasses`: 데이터 클래스 정의
- `datetime`: 날짜/시간 처리
- `pathlib`: 파일 경로 처리
- `subprocess`: Git 명령 실행
- `typing`: 타입 힌트

## 참고사항

- Git 명령어 `git log`를 사용하므로 시스템에 Git이 설치되어 있어야 합니다
- ISO 8601 날짜 형식(`YYYY-MM-DD`)을 사용합니다
- 기본적으로 병합 커밋은 제외됩니다 (`--no-merges`)
- CSV 출력 시 디렉토리가 없으면 자동으로 생성됩니다
