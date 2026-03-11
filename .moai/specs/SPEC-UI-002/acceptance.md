---
id: SPEC-UI-002
document: acceptance
version: 2.0.0
status: draft
tags: [hardware, gpio, usb, serial, linux]
---

# SPEC-UI-002 수용 기준: 하드웨어 인터페이스 모니터링 탭

## 1. GPIO 시각화

### AC-HW-01: GPIO 핀 목록 표시

**Given** GPIO sysfs 인터페이스가 활성화된 임베디드 보드에서
**When** 하드웨어 탭의 GPIO 섹션을 확인하면
**Then** 각 GPIO 핀의 번호, 방향(in/out), 현재 값(0/1)이 표시된다

### AC-HW-02: GPIO 실시간 갱신

**Given** GPIO 핀 값이 변경될 때
**When** 다음 갱신 주기에
**Then** 해당 핀의 표시가 1초 이내에 업데이트된다

### AC-HW-03: GPIO Graceful Degradation

**Given** `/sys/class/gpio/` 디렉토리가 존재하지 않거나 비어있을 때
**When** 하드웨어 탭의 GPIO 섹션을 확인하면
**Then** "GPIO sysfs 인터페이스를 사용할 수 없습니다" 메시지가 표시된다

---

## 2. USB 디바이스 트리

### AC-HW-04: USB 디바이스 목록 표시

**Given** USB 디바이스가 연결된 리눅스 시스템에서
**When** 하드웨어 탭의 USB 섹션을 확인하면
**Then** 각 USB 디바이스의 Vendor ID, Product ID, 제조사명, 제품명이 트리 구조(버스/포트 계층)로 표시된다

### AC-HW-05: USB 핫플러그 감지

**Given** USB 디바이스가 연결 또는 분리될 때
**When** 다음 갱신 주기에
**Then** USB 디바이스 트리가 업데이트된다

### AC-HW-06: USB 권한 처리

**Given** USB 디바이스 정보 읽기에 권한이 부족할 때
**When** 해당 디바이스의 상세 정보를 확인하면
**Then** "권한 부족"으로 표시되고 나머지 디바이스 정보는 정상 표시된다

---

## 3. 시리얼 포트 모니터링

### AC-HW-07: 시리얼 포트 목록 표시

**Given** USB-시리얼 어댑터가 연결된 시스템에서
**When** 하드웨어 탭의 시리얼 포트 섹션을 확인하면
**Then** `/dev/ttyUSB*`, `/dev/ttyACM*`, `/dev/ttyS*` 포트 목록과 디바이스 경로가 표시된다

### AC-HW-08: 시리얼 포트 갱신

**Given** 새로운 시리얼 포트가 감지될 때
**When** 다음 갱신 주기에
**Then** 시리얼 포트 목록이 갱신된다

### AC-HW-09: 시리얼 포트 없음 처리

**Given** 시리얼 장치가 연결되지 않았을 때
**When** 시리얼 포트 섹션을 확인하면
**Then** "연결된 시리얼 장치 없음" 메시지가 표시된다

---

## 4. 리소스 안전성

### AC-HW-10: GPIO 파일 디스크립터 안전성

**Given** GPIO 모니터가 핀 상태를 읽을 때
**When** sysfs 파일에 접근하면
**Then** 파일 디스크립터가 즉시 닫히고 열린 상태로 유지되지 않는다

```python
# 검증 방법: 파일 디스크립터 누수 테스트
import os
fd_count_before = len(os.listdir(f'/proc/{os.getpid()}/fd'))
for _ in range(100):
    gpio_monitor.measure()
fd_count_after = len(os.listdir(f'/proc/{os.getpid()}/fd'))
assert fd_count_after <= fd_count_before + 1  # 허용 오차 1
```

---

## 5. 비기능적 품질 기준

### 성능 품질 게이트

| 항목 | 기준 | 검증 방법 |
|------|------|----------|
| 메인 스레드 블로킹 | 하드웨어 데이터 수집 50ms 이하 | `time.monotonic()` 측정 |
| UI 갱신 지연 | 1초 이내 | QTimer 주기 준수 확인 |

### 테스트 품질 게이트

| 항목 | 기준 |
|------|------|
| 테스트 커버리지 | 85% 이상 (전체 프로젝트) |
| 신규 모듈 커버리지 | 90% 이상 |
| 단위 테스트 | 모든 utils/ 모듈에 대해 정상/에러/경계 테스트 포함 |
| Graceful Degradation 테스트 | GPIO sysfs 미존재, USB 권한 부족, 시리얼 포트 없음 시나리오 테스트 |
| TDD 준수 | RED-GREEN-REFACTOR 사이클 기록 |

### TRUST 5 품질 게이트

| 차원 | 기준 |
|------|------|
| **Tested** | 모든 신규 코드에 대해 테스트 우선 작성 (TDD) |
| **Readable** | 명확한 함수/변수 명명, 한국어 코드 주석 |
| **Unified** | 기존 MVVM 패턴 및 코딩 스타일 준수, ruff/black 포맷팅 |
| **Secured** | 사용자 입력 없음 (읽기 전용 모니터), 파일 경로 검증 |
| **Trackable** | SPEC-UI-002 참조 커밋 메시지 |

---

## 6. 엣지 케이스 테스트

| ID | 시나리오 | 예상 동작 |
|----|---------|----------|
| EDGE-HW-01 | GPIO 핀 100개 이상 | 스크롤 가능한 목록으로 표시 |
| EDGE-HW-02 | USB 허브 다단 연결 | 트리 깊이 제한 없이 계층 표시 |
| EDGE-HW-03 | /dev/ttyUSB 장치 핫플러그 | 다음 갱신 주기에 목록 업데이트 |
| EDGE-HW-04 | GPIO sysfs deprecated (chardev 방식만 가능) | "GPIO sysfs 사용 불가" 메시지 |
| EDGE-HW-05 | USB 정보 일부만 읽기 가능 | 읽을 수 있는 정보만 표시, 나머지 "N/A" |
| EDGE-HW-06 | /dev/ttyS* 포트 다수 존재 (ttyS0~ttyS31) | 실제 연결된 포트만 필터링하여 표시 |

---

## 7. Definition of Done

SPEC 구현이 완료되었다고 판단하기 위한 최종 체크리스트:

- [ ] 모든 유비쿼터스 요구사항(HW-U01~U03)의 수용 기준 통과
- [ ] 모든 이벤트 기반 요구사항(HW-E01~E03)의 수용 기준 통과
- [ ] 모든 상태 기반 요구사항(HW-S01~S03)의 수용 기준 통과
- [ ] 금지 요구사항(HW-N01)의 수용 기준 통과
- [ ] 엣지 케이스 테스트(EDGE-HW-01~06) 통과
- [ ] 테스트 커버리지 85% 이상 유지
- [ ] 신규 모듈 커버리지 90% 이상
- [ ] Graceful Degradation 시나리오 전부 테스트 완료
- [ ] 기존 174개 테스트 전부 통과 (회귀 없음)
- [ ] TRUST 5 품질 게이트 전부 통과
- [ ] ruff/black 포맷팅 위반 없음
- [ ] 메인 스레드 블로킹 50ms 이하 확인
