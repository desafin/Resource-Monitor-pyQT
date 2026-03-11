---
id: SPEC-UI-002
title: "Hardware Interface Monitoring Tab"
version: 2.0.0
status: draft
priority: High
created: 2026-03-11
updated: 2026-03-11
author: manager-spec
tags: [hardware, gpio, usb, serial, linux]
related_specs: [SPEC-UI-001, SPEC-REFACTOR-001]
lifecycle: spec-anchored
---

# SPEC-UI-002: 하드웨어 인터페이스 모니터링 탭

## 1. 환경 (Environment)

### 1.1 시스템 환경
- **운영체제**: Linux (Ubuntu 20.04+, Debian, Raspberry Pi OS)
- **Python**: 3.7 이상
- **GUI 프레임워크**: PyQt5 5.15.11 + QML (Qt Quick)
- **아키텍처**: MVVM (Model-View-ViewModel)
- **현재 상태**: 4탭 구성 (시스템개요/프로세스/디스크/네트워크), 174개 테스트, 85% 커버리지

### 1.2 대상 사용자
- 임베디드 리눅스 개발자 (Raspberry Pi, BeagleBone, 커스텀 보드)
- 하드웨어 엔지니어 (GPIO/USB/시리얼 디바이스 확인)

### 1.3 제약 조건
- PyQt5 전용 (PyQt6 미지원)
- Linux 전용 기능 (/sys 파싱)은 Graceful Degradation 적용
- TDD 방법론 (RED-GREEN-REFACTOR)
- 테스트 커버리지 85% 이상 유지
- 기존 MVVM 패턴 준수 (utils/ -> models/ -> views/ -> qml/)

---

## 2. 가정 (Assumptions)

- `/sys/class/gpio/`는 GPIO sysfs 인터페이스가 활성화된 보드에서만 사용 가능하다
- USB 디바이스 열거를 위한 `/sys/bus/usb/devices/`는 표준 리눅스에서 항상 접근 가능하다
- 시리얼 포트 (/dev/ttyUSB*, /dev/ttyACM*, /dev/ttyS*)는 해당 장치가 연결된 경우에만 표시된다
- GPIO sysfs deprecated 환경에서는 Graceful Degradation으로 안내 메시지를 표시한다

---

## 3. 요구사항 (Requirements)

### 요구사항 모듈 구조

| 모듈 ID | 모듈명 |
|---------|--------|
| SPEC-UI-002-HW | 하드웨어 인터페이스 |

---

### 3.1 모듈: SPEC-UI-002-HW (하드웨어 인터페이스)

#### 유비쿼터스 요구사항 (Ubiquitous)

**[HW-U01]** 시스템은 **항상** `/sys/class/gpio/` 하위의 GPIO 핀 목록을 열거하고, 각 핀의 방향(in/out), 현재 값(0/1)을 표시해야 한다.

**[HW-U02]** 시스템은 **항상** `/sys/bus/usb/devices/` 하위의 USB 디바이스를 트리 구조로 열거하고, Vendor ID, Product ID, 제조사명, 제품명을 표시해야 한다.

**[HW-U03]** 시스템은 **항상** `/dev/ttyUSB*`, `/dev/ttyACM*`, `/dev/ttyS*` 패턴의 시리얼 포트를 열거하고, 각 포트의 존재 여부와 디바이스 경로를 표시해야 한다.

#### 이벤트 기반 요구사항 (Event-Driven)

**[HW-E01]** **WHEN** GPIO 핀의 값이 변경 **THEN** 시스템은 해당 핀의 표시를 1초 이내에 갱신해야 한다.

**[HW-E02]** **WHEN** USB 디바이스가 연결 또는 분리 **THEN** 시스템은 USB 디바이스 트리를 다음 갱신 주기에 업데이트해야 한다.

**[HW-E03]** **WHEN** 새로운 시리얼 포트가 감지 **THEN** 시스템은 시리얼 포트 목록을 갱신해야 한다.

#### 상태 기반 요구사항 (State-Driven)

**[HW-S01]** **IF** `/sys/class/gpio/` 디렉토리가 존재하지 않거나 비어있는 경우 **THEN** GPIO 섹션은 "GPIO sysfs 인터페이스를 사용할 수 없습니다" 메시지를 표시해야 한다.

**[HW-S02]** **IF** `/sys/bus/usb/devices/`에서 디바이스 정보 읽기에 권한 부족인 경우 **THEN** 해당 디바이스의 상세 정보는 "권한 부족"으로 표시해야 한다.

**[HW-S03]** **IF** 시리얼 포트가 하나도 감지되지 않는 경우 **THEN** 시리얼 포트 섹션은 "연결된 시리얼 장치 없음" 메시지를 표시해야 한다.

#### 금지 요구사항 (Unwanted)

**[HW-N01]** GPIO 모니터는 sysfs 접근 시 파일 디스크립터를 열린 상태로 유지**하지 않아야 한다**. (리소스 누수 방지)

---

## 4. 사양 (Specifications)

### 4.1 UI 구조 변경

#### 신규 탭 생성
- **하드웨어 탭**: 새로운 5번째 탭으로 TabBar에 추가
  - GPIO 시각화 섹션
  - USB 디바이스 트리 섹션
  - 시리얼 포트 모니터링 섹션

### 4.2 MVVM 구조 확장

| Layer | 신규 파일 |
|-------|----------|
| utils/ | `gpio_monitor.py`, `usb_monitor.py`, `serial_monitor.py` |
| models/ | `hardware_model.py` |
| views/ | `hardware_viewmodel.py` |
| qml/tabs/ | `HardwareTab.qml` |

### 4.3 성능 요구사항

| 항목 | 목표값 |
|------|--------|
| 메인 스레드 블로킹 | 50ms 이하 (모든 데이터 수집) |
| UI 갱신 지연 | 1초 이내 |
| 테스트 커버리지 | 85% 이상 유지 |

### 4.4 Graceful Degradation 전략

모든 하드웨어 모니터링 기능은 다음 패턴을 따른다:

1. 기능 사용 가능 여부를 시작 시 감지
2. 사용 불가능한 경우 해당 UI 섹션에 안내 메시지 표시
3. 나머지 기능은 정상 동작 유지
4. 로그에 비활성화 사유 기록

---

## 5. 추적성 (Traceability)

| 요구사항 ID | plan.md 마일스톤 | acceptance.md 시나리오 |
|------------|-----------------|----------------------|
| HW-U01~U03 | M1 | AC-HW-01~03 |
| HW-E01~E03 | M2, M3 | AC-HW-04~06 |
| HW-S01~S03 | M4 | AC-HW-07~09 |
| HW-N01 | M1 | AC-HW-10 |
