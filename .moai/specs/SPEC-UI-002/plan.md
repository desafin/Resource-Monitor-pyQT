---
id: SPEC-UI-002
document: plan
version: 2.0.0
status: draft
tags: [hardware, gpio, usb, serial, linux]
---

# SPEC-UI-002 구현 계획: 하드웨어 인터페이스 모니터링 탭

## 1. 구현 개요

하드웨어 탭을 새로운 5번째 탭으로 추가하여 GPIO, USB, 시리얼 포트 모니터링 기능을 제공한다.

```
M1: 하드웨어 모니터 유틸리티 ──> M2: Model/ViewModel ──> M3: QML UI + 통합 ──> M4: Graceful Degradation + 테스트
```

---

## 2. 마일스톤 M1: 하드웨어 모니터 유틸리티 (Primary Goal)

**범위**: /sys, /dev 파싱 기반 하드웨어 데이터 수집 레이어

**신규 파일**:

| 파일 | 역할 |
|------|------|
| `utils/gpio_monitor.py` | `/sys/class/gpio/` 핀 상태 읽기 (방향, 값) |
| `utils/usb_monitor.py` | `/sys/bus/usb/devices/` 디바이스 열거 (Vendor ID, Product ID, 제조사, 제품명, 버스/포트 계층) |
| `utils/serial_monitor.py` | `/dev/ttyUSB*`, `/dev/ttyACM*`, `/dev/ttyS*` 포트 열거 |
| `tests/test_gpio_monitor.py` | GPIO 모니터 단위 테스트 |
| `tests/test_usb_monitor.py` | USB 모니터 단위 테스트 |
| `tests/test_serial_monitor.py` | 시리얼 모니터 단위 테스트 |

**기술 접근**:
- GPIO: `/sys/class/gpio/gpioN/direction`, `/sys/class/gpio/gpioN/value` 파일 읽기, 즉시 close
- USB: `/sys/bus/usb/devices/*/idVendor`, `idProduct`, `manufacturer`, `product` 파일 읽기, 버스-포트 계층 구조 파싱
- Serial: `glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyS*')` + `os.path.exists` 검증
- 모든 sysfs 파일 접근은 `with open()` 패턴으로 파일 디스크립터 즉시 해제

---

## 3. 마일스톤 M2: Hardware Model/ViewModel (Primary Goal)

**범위**: MVVM 패턴에 따른 데이터 바인딩 레이어

**신규 파일**:

| 파일 | 역할 |
|------|------|
| `models/hardware_model.py` | QObject 모델 - GPIO 핀 목록, USB 디바이스 트리, 시리얼 포트 목록 |
| `views/hardware_viewmodel.py` | QML 바인딩 ViewModel - 하드웨어 데이터 노출 |
| `tests/test_hardware_model.py` | 모델 단위 테스트 |
| `tests/test_hardware_viewmodel.py` | ViewModel 단위 테스트 |

**기술 접근**:
- 기존 `MonitorModel` 패턴을 참고하여 `HardwareModel` 구현
- QProperty 기반 데이터 바인딩 (기존 패턴과 동일)
- GPIO 데이터: `List[Dict]` (pin, direction, value)
- USB 데이터: 트리 구조 `List[Dict]` (bus, port, vendor_id, product_id, manufacturer, product, children)
- Serial 데이터: `List[Dict]` (path, exists)

---

## 4. 마일스톤 M3: Hardware Tab QML + 통합 (Secondary Goal)

**범위**: 하드웨어 탭 UI 및 main.py/main.qml 통합

**신규 파일**:

| 파일 | 역할 |
|------|------|
| `qml/tabs/HardwareTab.qml` | 하드웨어 탭 QML UI (GPIO/USB/시리얼 세 섹션) |

**수정 파일**:

| 파일 | 변경 내용 |
|------|----------|
| `main.py` | HardwareModel/ViewModel 등록, 타이머 연결 |
| `qml/main.qml` | 하드웨어 탭 추가 (TabBar에 5번째 탭), contextProperty 등록 |

**기술 접근**:
- GPIO 섹션: 핀 번호, 방향(in/out), 값(0/1) 테이블 표시
- USB 섹션: TreeView 또는 들여쓰기된 ListView로 버스/포트 계층 표시
- 시리얼 섹션: 포트 경로와 존재 여부 목록 표시

---

## 5. 마일스톤 M4: Graceful Degradation + 테스트 보강 (Secondary Goal)

**범위**: 모든 하드웨어 기능의 가용성 감지, 비활성화 처리, 통합 테스트

**기술 접근**:
- 각 하드웨어 기능별 가용성 플래그를 ViewModel에 QProperty로 노출
- QML에서 조건부 렌더링: 가용 시 데이터 표시, 불가 시 안내 메시지
- GPIO sysfs 미지원 시: "GPIO sysfs 인터페이스를 사용할 수 없습니다" 표시
- USB 권한 부족 시: 해당 디바이스만 "권한 부족" 표시
- 시리얼 포트 없음 시: "연결된 시리얼 장치 없음" 표시

---

## 6. 파일 영향 분석 요약

### 신규 파일 (총 ~11개)

| 디렉토리 | 파일 수 | 주요 파일 |
|----------|---------|----------|
| `utils/` | 3 | gpio_monitor, usb_monitor, serial_monitor |
| `models/` | 1 | hardware_model |
| `views/` | 1 | hardware_viewmodel |
| `qml/tabs/` | 1 | HardwareTab |
| `tests/` | ~5 | 각 utils/models/views 모듈별 테스트 |

### 수정 파일 (총 2개)

| 파일 | 변경 범위 |
|------|----------|
| `main.py` | HardwareModel/ViewModel 등록, 타이머 연결 |
| `qml/main.qml` | contextProperty 등록, TabBar에 5번째 탭 추가 |

---

## 7. 위험 분석

| 위험 | 영향 | 확률 | 대응 전략 |
|------|------|------|----------|
| GPIO sysfs deprecated (chardev 방식만 가능) | Medium | Medium | /sys/class/gpio/ 존재 여부 사전 체크, 비활성화 처리 |
| USB 디바이스 정보 권한 부족 | Low | Medium | 읽을 수 있는 정보만 표시, 나머지 "권한 부족" |
| 시리얼 포트 핫플러그 감지 지연 | Low | Low | 다음 갱신 주기(1초 이내)에 반영 |
| 메인 스레드 블로킹 (sysfs 파일 읽기) | Medium | Low | 파일 I/O 최소화, 필요 시 QThread 워커 분리 |
| GPIO 파일 디스크립터 누수 | High | Low | `with open()` 패턴 강제 적용, 테스트로 검증 |

---

## 8. 기술 스택 확인

| 항목 | 버전 | 용도 |
|------|------|------|
| Python | 3.7+ | 기존 유지 |
| PyQt5 | 5.15.11 | 기존 유지 |
| pytest | 최신 안정 | TDD 테스트 프레임워크 |
| pytest-qt | 최신 안정 | PyQt5 테스트 지원 |

> 신규 외부 라이브러리 추가 없음 - 리눅스 /sys, /dev 파싱 및 표준 라이브러리(glob, os)만 사용
