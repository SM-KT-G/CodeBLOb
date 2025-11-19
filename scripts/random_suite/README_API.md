# Random Suite API 명세서

## 개요
다양한 무작위 생성 도구 모음입니다. 카드 뽑기, 주사위 굴리기, 색상 생성, 팀 나누기 등의 기능을 제공합니다.

---

## random_card_draw.py

### 기능
트럼프 카드 덱에서 무작위로 카드를 뽑습니다.

### 실행 방법
```bash
python random_card_draw.py [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--count` | integer | 5 | 뽑을 카드 개수 |
| `--seed` | integer | None | 난수 시드 (재현 가능한 결과) |

### 데이터 모델

#### Card
```python
@dataclass(frozen=True)
class Card:
    rank: str  # A, 2-10, J, Q, K
    suit: str  # ♠, ♥, ♦, ♣
```

### 사용 예시

```bash
# 기본 5장 뽑기
python random_card_draw.py
# 출력: Drawn cards: A♠ 5♥ K♦ 2♣ 9♠

# 10장 뽑기
python random_card_draw.py --count 10

# 재현 가능한 결과
python random_card_draw.py --seed 42
```

---

## random_coin.py

### 기능
가상 동전을 여러 번 던지고 통계를 보고합니다.

### 실행 방법
```bash
python random_coin.py [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--flips` | integer | 10 | 던질 횟수 |
| `--seed` | integer | None | 난수 시드 |

### 사용 예시

```bash
# 기본 10회 던지기
python random_coin.py
# 출력:
# Flipped the coin 10 times:
# Heads: 6
# Tails: 4

# 100회 던지기
python random_coin.py --flips 100

# 재현 가능한 결과
python random_coin.py --seed 123 --flips 20
```

---

## random_color.py

### 기능
무작위 색상을 HEX와 RGB 형식으로 생성합니다.

### 실행 방법
```bash
python random_color.py [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--count` | integer | 5 | 생성할 색상 개수 |

### 사용 예시

```bash
# 기본 5개 색상 생성
python random_color.py
# 출력:
# #3F7A2B -> RGB(63, 122, 43)
# #E8A41D -> RGB(232, 164, 29)
# #9C2F8E -> RGB(156, 47, 142)
# #1B5FA3 -> RGB(27, 95, 163)
# #D4C719 -> RGB(212, 199, 25)

# 10개 색상 생성
python random_color.py --count 10
```

---

## random_die.py

### 기능
N면 주사위를 여러 번 굴리고 통계를 보여줍니다.

### 실행 방법
```bash
python random_die.py [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--sides` | integer | 6 | 주사위 면 개수 |
| `--rolls` | integer | 12 | 굴릴 횟수 |
| `--seed` | integer | None | 난수 시드 |

### 사용 예시

```bash
# 6면 주사위 12회
python random_die.py
# 출력:
# Rolled a 6-sided die 12 times:
# 1: 2
# 2: 3
# 3: 1
# 4: 2
# 5: 2
# 6: 2

# 20면 주사위 (D20)
python random_die.py --sides 20 --rolls 10

# 재현 가능한 결과
python random_die.py --seed 999 --sides 10 --rolls 20
```

---

## random_password.py

### 기능
무작위 비밀번호를 생성합니다.

### 실행 방법
```bash
python random_password.py [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--length` | integer | 12 | 비밀번호 길이 |
| `--count` | integer | 5 | 생성할 비밀번호 개수 |
| `--digits` | boolean | False | 숫자 포함 |
| `--symbols` | boolean | False | 특수문자 포함 (!@#$%^&*) |

### 문자 집합

- 기본: 영문자 (대소문자)
- `--digits`: + 숫자 (0-9)
- `--symbols`: + 특수문자 (!@#$%^&*)

### 사용 예시

```bash
# 기본 (영문자만, 12자, 5개)
python random_password.py
# 출력:
# aBcDeFgHiJkL
# XyZwVuTsRqPo
# ...

# 숫자 포함
python random_password.py --digits

# 숫자와 특수문자 포함
python random_password.py --digits --symbols

# 긴 비밀번호
python random_password.py --length 20 --digits --symbols --count 3
```

---

## random_quote.py

### 기능
무작위 동기부여 명언을 출력합니다.

### 실행 방법
```bash
python random_quote.py
```

### 파라미터
없음 (인자를 받지 않음)

### 내장 명언

- "Stay hungry, stay foolish."
- "Done is better than perfect."
- "Measure twice, cut once."
- "The best time to code was yesterday. The second best is now."
- "Simplicity is the soul of efficiency."

### 사용 예시

```bash
python random_quote.py
# 출력: Done is better than perfect.

python random_quote.py
# 출력: Simplicity is the soul of efficiency.
```

---

## random_schedule.py

### 기능
작업 목록을 무작위로 섞어 시간표를 생성합니다.

### 실행 방법
```bash
python random_schedule.py --tasks TASK1 TASK2 ... [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--tasks` | string[] | 필수 | 스케줄링할 작업 목록 |
| `--start` | string | 09:00 | 시작 시간 (HH:MM, 24시간 형식) |
| `--slot-minutes` | integer | 30 | 슬롯당 할당 시간 (분) |
| `--seed` | integer | None | 난수 시드 |

### 사용 예시

```bash
# 기본 사용
python random_schedule.py --tasks "Meeting" "Coding" "Review" "Break"
# 출력:
# 09:00 - Coding
# 09:30 - Break
# 10:00 - Meeting
# 10:30 - Review

# 시작 시간 변경
python random_schedule.py --tasks "Task1" "Task2" "Task3" --start 14:00

# 슬롯 시간 조정 (1시간)
python random_schedule.py --tasks "Study" "Exercise" "Rest" --slot-minutes 60

# 재현 가능한 스케줄
python random_schedule.py --tasks "A" "B" "C" "D" --seed 42
```

---

## random_stream.py

### 기능
난수를 스트리밍하며 누적 합이 임계값을 초과할 때까지 생성합니다.

### 실행 방법
```bash
python random_stream.py [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--threshold` | float | 10.0 | 목표 누적 합 |
| `--seed` | integer | None | 난수 시드 |

### 사용 예시

```bash
# 기본 (합계 10.0 도달까지)
python random_stream.py
# 출력:
# 01: 0.5123 (total=0.5123)
# 02: 0.8456 (total=1.3579)
# 03: 0.2341 (total=1.5920)
# ...
# 15: 0.6789 (total=10.0123)

# 목표 값 변경
python random_stream.py --threshold 5.0

# 재현 가능한 스트림
python random_stream.py --seed 777 --threshold 20.0
```

---

## random_team_picker.py

### 기능
참가자를 무작위로 팀에 배정합니다.

### 실행 방법
```bash
python random_team_picker.py --people NAME1 NAME2 ... [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--people` | string[] | 필수 | 참가자 이름 목록 |
| `--teams` | integer | 2 | 팀 개수 |
| `--seed` | integer | None | 난수 시드 |

### 사용 예시

```bash
# 2팀으로 나누기
python random_team_picker.py --people Alice Bob Charlie David Eve Frank
# 출력:
# Team 1: Charlie, Eve, Bob
# Team 2: Frank, Alice, David

# 3팀으로 나누기
python random_team_picker.py --people A B C D E F G H I --teams 3
# 출력:
# Team 1: D, B, G
# Team 2: H, A, F
# Team 3: E, C, I

# 재현 가능한 팀 구성
python random_team_picker.py --people Alice Bob Charlie David --teams 2 --seed 100
```

---

## random_walk.py

### 기능
2D 평면에서 무작위 보행을 시뮬레이션합니다.

### 실행 방법
```bash
python random_walk.py [options]
```

### 파라미터

| 옵션 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `--steps` | integer | 20 | 이동 횟수 |
| `--seed` | integer | None | 난수 시드 |

### 이동 방향

| 방향 | 기호 | 좌표 변화 |
|------|------|----------|
| 북 | N | (0, +1) |
| 남 | S | (0, -1) |
| 동 | E | (+1, 0) |
| 서 | W | (-1, 0) |

### 사용 예시

```bash
# 기본 20스텝
python random_walk.py
# 출력:
# Start at (0, 0)
# 01. N -> (0, 1)
# 02. E -> (1, 1)
# 03. N -> (1, 2)
# 04. W -> (0, 2)
# ...
# 20. S -> (3, -2)
# End position: (3, -2)

# 100스텝
python random_walk.py --steps 100

# 재현 가능한 경로
python random_walk.py --seed 456 --steps 50
```

---

## 공통 기능

### 난수 시드

대부분의 스크립트가 `--seed` 옵션을 지원합니다:

```bash
# 같은 시드 = 같은 결과
python random_coin.py --seed 42 --flips 10
python random_coin.py --seed 42 --flips 10  # 동일한 결과
```

### 의존성

모든 스크립트는 표준 라이브러리만 사용합니다:

- `random`: 난수 생성
- `argparse`: CLI 파싱
- `dataclasses`: 데이터 클래스 (일부 스크립트)
- `collections.Counter`: 통계 (일부 스크립트)
- `datetime`: 시간 처리 (random_schedule.py)
- `itertools.count`: 무한 카운터 (random_stream.py)
- `math.ceil`: 올림 계산 (random_team_picker.py)

### 설치

```bash
# 외부 의존성 없음 - Python 3.7+ 만 필요
python --version  # Python 3.7 이상 확인
```

## 참고사항

- 모든 스크립트는 독립적으로 실행 가능합니다
- `--seed` 옵션을 사용하면 재현 가능한 결과를 얻을 수 있습니다
- 대부분의 스크립트는 `--help` 옵션으로 도움말을 볼 수 있습니다
- random_quote.py를 제외한 모든 스크립트는 CLI 인자를 받습니다
