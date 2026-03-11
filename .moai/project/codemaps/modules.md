# 모듈 및 클래스 상세 설명

## 패키지 구조

```
Resource-Monitor-pyQT/
├── main.py                          # 애플리케이션 진입점
├── monitor_base.py                  # 추상 기반 클래스
├── system_monitor.py                # 시스템 모니터 집계 클래스
├── models/
│   ├── __init__.py
│   └── monitor_model.py             # 데이터 모델 (MVVM - Model)
├── views/
│   ├── __init__.py
│   └── monitor_viewmodel.py         # 뷰모델 (MVVM - ViewModel)
├── controllers/
│   ├── __init__.py
│   └── monitor_controller.py        # 컨트롤러 (비즈니스 로직)
├── utils/
│   ├── __init__.py
│   ├── cpu_monitor.py               # CPU 모니터
│   ├── memory_monitor.py            # 메모리 모니터
│   ├── gpu_monitor.py               # GPU 모니터
│   └── fps_monitor.py               # FPS 모니터
└── qml/
    └── main.qml                     # QML UI 레이아웃
```

---

## monitor_base.py - 추상 기반 클래스

### ResourceMonitor (ABC)

모든 리소스 모니터가 상속하는 추상 기반 클래스입니다. Python의 `abc` 모듈을 사용해 인터페이스를 정의합니다.

**책임**: 측정값의 저장 구조와 측정 인터페이스를 표준화합니다.

| 멤버 | 종류 | 설명 |
|------|------|------|
| `last_measurement` | 속성 | 이전 측정값 (초기값: 0) |
| `current_measurement` | 속성 | 현재 측정값 (초기값: 0) |
| `measure()` | 추상 메서드 | 서브클래스에서 반드시 구현해야 하는 측정 메서드 |
| `get_measurement()` | 메서드 | `current_measurement`를 반환하는 편의 메서드 |

---

## system_monitor.py - 집계 클래스

### SystemMonitor

모든 개별 리소스 모니터를 하나로 묶어 관리하는 집계 클래스입니다.

**책임**: 각 리소스 모니터 인스턴스를 딕셔너리로 관리하고, 일괄 측정을 조율합니다.

| 멤버 | 종류 | 설명 |
|------|------|------|
| `monitors` | 속성 | 리소스 타입별 모니터 딕셔너리 (`'cpu'`, `'memory'`, `'fps'`, `'gpu'`) |
| `measure_all()` | 메서드 | 모든 모니터의 `measure()`를 호출하고 결과 딕셔너리를 반환 |
| `get_monitor(resource_type)` | 메서드 | 특정 리소스 타입의 모니터 인스턴스를 반환 |

> 참고: `SystemMonitor`는 현재 `MonitorController`와 역할이 중복됩니다. `MonitorController`가 직접 모니터 딕셔너리를 관리하기 때문에 실제 실행 경로에서 `SystemMonitor`는 사용되지 않습니다.

---

## models/ - 데이터 모델 패키지

### MonitorModel (QObject)

MVVM 패턴의 **Model** 계층입니다. 측정 데이터를 저장하고, 데이터 변경 시 ViewModel에 알림을 전달합니다.

**책임**: 최신 측정 데이터를 보관하고, 변경 사항을 `dataChanged` 시그널로 발행합니다.

| 멤버 | 종류 | 설명 |
|------|------|------|
| `dataChanged` | `pyqtSignal()` | 데이터 변경 시 발행되는 Qt 시그널 (파라미터 없음) |
| `_controller` | 속성 | 연결된 `MonitorController` 참조 |
| `_data` | 속성 | 최신 측정 데이터 딕셔너리 |
| `_update_data(new_data)` | 슬롯 | 컨트롤러의 `dataChanged` 시그널을 수신하여 `_data`를 갱신하고 자체 시그널을 발행 |
| `data` | 프로퍼티 | `_data`에 대한 읽기 전용 접근자 |

**시그널 연결**: 초기화 시 `controller.dataChanged` → `self._update_data`

---

## views/ - 뷰모델 패키지

### MonitorViewModel (QObject)

MVVM 패턴의 **ViewModel** 계층입니다. QML과 Python 백엔드 사이의 브리지 역할을 합니다.

**책임**: Model의 데이터 변경을 감지하고, QML이 소비할 수 있는 형식으로 `updateUI` 시그널을 발행합니다.

| 멤버 | 종류 | 설명 |
|------|------|------|
| `updateUI` | `pyqtSignal('QVariantMap')` | QML로 데이터를 전달하는 시그널 (딕셔너리를 QVariantMap으로 전달) |
| `_model` | 속성 | 연결된 `MonitorModel` 참조 |
| `_controller` | 속성 | 연결된 `MonitorController` 참조 |
| `startMonitoring()` | `@pyqtSlot` | QML에서 호출 가능한 모니터링 시작 슬롯 |
| `stopMonitoring()` | `@pyqtSlot` | QML에서 호출 가능한 모니터링 중지 슬롯 |
| `_on_data_changed()` | 메서드 | Model의 `dataChanged` 수신 후 `updateUI` 시그널을 발행 |

**시그널 연결**: 초기화 시 `model.dataChanged` → `self._on_data_changed`

---

## controllers/ - 컨트롤러 패키지

### MonitorController (QObject)

비즈니스 로직을 담당하는 컨트롤러입니다. 실제 리소스 측정을 조율하고 결과를 시그널로 발행합니다.

**책임**: 리소스 모니터들의 생명주기를 관리하고, 타이머 틱마다 모든 모니터를 호출하여 측정 결과를 발행합니다.

| 멤버 | 종류 | 설명 |
|------|------|------|
| `dataChanged` | `pyqtSignal(dict)` | 측정 완료 후 결과 딕셔너리를 전달하는 시그널 |
| `monitoringStarted` | `pyqtSignal()` | 모니터링 시작 이벤트 시그널 |
| `monitoringStopped` | `pyqtSignal()` | 모니터링 중지 이벤트 시그널 |
| `monitors` | 속성 | 리소스 타입 → 모니터 인스턴스 딕셔너리 |
| `_is_monitoring` | 속성 | 모니터링 활성화 상태 플래그 |
| `start_monitoring()` | 메서드 | 모니터링을 활성화하고 `monitoringStarted` 발행 |
| `stop_monitoring()` | 메서드 | 모니터링을 비활성화하고 `monitoringStopped` 발행 |
| `measure_all()` | 메서드 | 모든 모니터를 순회하며 `measure()`를 호출, 결과를 `dataChanged`로 발행 |
| `get_monitor(resource_type)` | 메서드 | 특정 리소스 모니터 인스턴스를 반환 |
| `cleanup()` | 메서드 | 모니터링 중지 및 각 모니터의 `cleanup()` 호출 |

---

## utils/ - 리소스 모니터 패키지

### CPUMonitor (ResourceMonitor)

**책임**: `psutil.cpu_percent()`를 사용하여 CPU 사용률(%)을 측정합니다.

| 메서드 | 반환값 | 설명 |
|--------|--------|------|
| `measure()` | `float` | CPU 사용률 백분율 (예: `45.3`) |

**외부 의존성**: `psutil`

---

### MemoryMonitor (ResourceMonitor)

**책임**: `psutil.virtual_memory()`를 사용하여 시스템 RAM 사용 현황을 측정합니다.

| 메서드 | 반환값 | 설명 |
|--------|--------|------|
| `measure()` | `dict` | `{'total': int, 'used': int, 'percent': float}` (바이트 단위) |

**외부 의존성**: `psutil`

---

### GPUMonitor (ResourceMonitor)

**책임**: `GPUtil`을 사용하여 GPU 부하 및 메모리 사용량을 측정합니다. GPUtil 미설치 시 `ImportError`를 발생시킵니다.

| 메서드 | 반환값 | 설명 |
|--------|--------|------|
| `measure()` | `list[dict]` | 각 GPU별 `{'id', 'load', 'memory_used', 'memory_total'}` 리스트 |

**외부 의존성**: `GPUtil` (선택적)

---

### FPSMonitor (ResourceMonitor)

**책임**: 시간 경과를 추적하여 초당 프레임 수(FPS)를 계산합니다. `time.time()`을 사용하여 1초 간격으로 FPS를 갱신합니다.

| 멤버 | 종류 | 설명 |
|------|------|------|
| `frame_count` | 속성 | 1초 구간 내 누적 프레임 수 |
| `last_time` | 속성 | 마지막 FPS 계산 시각 (Unix 타임스탬프) |
| `measure()` | 메서드 | 프레임을 카운트하고, 1초 경과 시 FPS를 계산하여 반환 |

**외부 의존성**: 표준 라이브러리 `time`

---

## qml/main.qml - UI 레이어

QML로 작성된 UI 파일입니다. PyQt5가 제공하는 QML 엔진이 이 파일을 렌더링합니다.

**책임**: 모니터링 데이터를 사용자에게 표시하고, Python ViewModel과 신호를 주고받습니다.

| 구성 요소 | 역할 |
|-----------|------|
| `ApplicationWindow` | 최상위 윈도우 (400×600px) |
| `ListModel (monitorModel)` | CPU, Memory, FPS, GPU 항목을 보유하는 QML 로컬 데이터 모델 |
| `ListView` | `monitorModel`을 기반으로 각 리소스 항목을 렌더링 |
| `monitorDelegate` | 각 항목의 이름과 값을 표시하는 행 레이아웃 |
| `Connections { target: monitorViewModel }` | `monitorViewModel.updateUI` 시그널을 수신하여 ListModel을 갱신 |
