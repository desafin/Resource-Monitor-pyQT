# Resource Monitor PyQt - 아키텍처 문서

## 목차

1. [개요](#개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [MVVM 패턴](#mvvm-패턴)
4. [데이터 흐름](#데이터-흐름)
5. [스레딩 모델](#스레딩-모델)
6. [QML 컴포넌트 구조](#qml-컴포넌트-구조)
7. [모듈 의존성](#모듈-의존성)
8. [디자인 패턴](#디자인-패턴)
9. [타이머 조정](#타이머-조정)
10. [기술 스택](#기술-스택)

---

## 개요

Resource Monitor PyQt는 Python 3.7+, PyQt5, 그리고 QML을 기반으로 한 시스템 리소스 모니터링 애플리케이션입니다. 이 프로젝트는 CPU, 메모리, GPU, FPS, 디스크, 네트워크, GPIO, USB, 직렬 통신 등 다양한 시스템 리소스를 실시간으로 모니터링합니다.

### 주요 특징

- **다중 리소스 모니터링**: CPU, 메모리, GPU, FPS, 디스크, 네트워크, 하드웨어 정보 제공
- **우아한 성능 저하**: 선택적 의존성(GPU, GPIO, USB, Serial)을 지원하며 누락 시에도 정상 작동
- **MVVM 아키텍처**: PyQt Model-ViewModel 패턴으로 깔끔한 계층 분리
- **멀티스레드 처리**: 메인 스레드 블로킹 방지를 위해 백그라운드 워커 스레드 사용
- **QML UI**: 최신 Qt Quick 프레임워크로 반응형 사용자 인터페이스 제공
- **설정 관리**: QSettings 기반 다크/라이트 테마, 윈도우 크기, 업데이트 간격 저장

---

## 시스템 아키텍처

```mermaid
graph TD
    A["main.py<br/>(엔트리 포인트)"] --> B["Models<br/>(데이터 계층)"]
    A --> C["Views<br/>(프레젠테이션 로직)"]
    A --> D["QML<br/>(사용자 인터페이스)"]

    B --> E["Utils<br/>(데이터 수집)"]
    C --> B
    C --> F["Services<br/>(백그라운드 워커)"]
    F --> E

    E --> G["psutil<br/>GPUtil<br/>기타 시스템 라이브러리"]

    style A fill:#4fc3f7,color:#000
    style B fill:#81c784,color:#000
    style C fill:#ffb74d,color:#000
    style D fill:#e57373,color:#000
    style E fill:#ba68c8,color:#fff
    style F fill:#64b5f6,color:#000
```

### 계층 설명

**Entry Point (main.py)**
- 애플리케이션 부트스트랩: QGuiApplication 생성 및 QML 엔진 초기화
- 모든 Model과 ViewModel 인스턴스 생성
- 저장된 설정(테마, 윈도우 크기, 업데이트 간격) 로드
- 모니터링 타이머 및 워커 스레드 초기화
- 애플리케이션 종료 시 안전한 리소스 정리

**Models (데이터 계층)**
- QObject/QAbstractListModel 기반으로 PyQt 신호-슬롯 메커니즘 활용
- 실시간 리소스 데이터 관리 및 상태 변경 시그널 발출
- MonitorModel: CPU, 메모리, GPU, FPS 통합 데이터 제공
- ProcessModel: 프로세스 리스트 데이터 제공
- DiskModel, NetworkModel, HardwareModel: 각각 디스크, 네트워크, 하드웨어 데이터 제공

**Views (프레젠테이션 로직)**
- Model의 원시 데이터를 표시용 문자열과 그래프 데이터로 변환
- ViewModel은 신호-슬롯 연결로 Model 변경 감지 및 QML 프로퍼티 업데이트
- ProcessViewModel: 프로세스 컨트롤 및 워커 스레드 관리
- 각 탭별 ViewModel이 해당 데이터 관리 (DiskViewModel, NetworkViewModel, HardwareViewModel)

**QML (사용자 인터페이스)**
- ApplicationWindow를 기반으로 TabBar와 StackLayout으로 5개 탭 구성
- 각 탭(SystemOverviewTab, ProcessesTab, DiskTab, NetworkTab, HardwareTab)이 담당 ViewModel과 연결
- 컴포넌트: SearchBar, ProcessContextMenu, PriorityDialog, SettingsDialog, PingSection 등

**Services (백그라운드 워커)**
- ProcessWorker: QThread 기반 2초 주기 프로세스 수집
- PingWorker: 비동기 Ping 작업 처리

**Utils (데이터 수집)**
- 각 모니터 클래스가 ResourceMonitor 추상 클래스 상속
- CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor: 주기적 측정
- DiskMonitor, NetworkMonitor, ProcessMonitor, GPIOMonitor, USBMonitor, SerialMonitor: 시스템 정보 수집
- 선택적 의존성 처리로 라이브러리 미설치 시 우아하게 무시

---

## MVVM 패턴

Resource Monitor는 PyQt의 강력한 신호-슬롯 메커니즘을 활용한 MVVM 아키텍처를 구현합니다.

```mermaid
classDiagram
    class MonitorModel {
        -CPUMonitor cpu_monitor
        -MemoryMonitor memory_monitor
        -GPUMonitor gpu_monitor
        -FPSMonitor fps_monitor
        +measure()
        +cpuChanged pyqtSignal
        +memoryChanged pyqtSignal
        +gpuChanged pyqtSignal
        +fpsChanged pyqtSignal
    }

    class MonitorViewModel {
        -MonitorModel model
        -deque cpu_history
        -deque memory_history
        +cpuUsageChanged pyqtSignal
        +memoryUsageChanged pyqtSignal
        +_on_cpu_changed()
        +_on_memory_changed()
    }

    class SystemOverviewTab {
        +monitorViewModel binding
        +cpu_gauge display
        +memory_gauge display
        +history_charts display
    }

    class ProcessModel {
        -list processes
        +roleNames dict
        +data method
        +setProcesses method
    }

    class ProcessViewModel {
        -ProcessModel model
        -ProcessWorker worker
        -QThread thread
        +processesChanged pyqtSignal
        +start_worker()
        +cleanup()
    }

    class ProcessesTab {
        +processViewModel binding
        +processModel display
        +sortFilterProxyModel proxy
        +search_bar input
    }

    class DiskModel {
        -list disk_partitions
    }

    class DiskViewModel {
        -DiskModel model
        -QTimer refresh_timer
        +refresh()
    }

    class DiskTab {
        +diskViewModel binding
    }

    class NetworkModel {
        -list network_interfaces
    }

    class NetworkViewModel {
        -NetworkModel model
        -PingWorker ping_worker
        -QTimer refresh_timer
        +ping_host()
    }

    class NetworkTab {
        +networkViewModel binding
        +PingSection component
    }

    class HardwareModel {
        -GPIO info
        -USB info
        -Serial info
    }

    class HardwareViewModel {
        -HardwareModel model
        -QTimer refresh_timer
    }

    class HardwareTab {
        +hardwareViewModel binding
    }

    MonitorModel --> MonitorViewModel : Model Data
    MonitorViewModel --> SystemOverviewTab : Display Data

    ProcessModel --> ProcessViewModel : Model Data
    ProcessViewModel --> ProcessesTab : Display Data

    DiskModel --> DiskViewModel : Model Data
    DiskViewModel --> DiskTab : Display Data

    NetworkModel --> NetworkViewModel : Model Data
    NetworkViewModel --> NetworkTab : Display Data

    HardwareModel --> HardwareViewModel : Model Data
    HardwareViewModel --> HardwareTab : Display Data
```

### MVVM 흐름

1. **Model**: 시스템으로부터 실시간 데이터 수집 및 내부 상태 유지
2. **View Model**: Model의 시그널 감지 → 데이터 포맷팅 → pyqtProperty로 QML에 노출
3. **View (QML)**: ViewModel의 바인딩된 프로퍼티 감시 → UI 자동 업데이트

### 신호-슬롯 메커니즘

- **Model → ViewModel**: `model.cpuChanged.connect(viewmodel._on_cpu_changed)`
- **ViewModel → QML**: `@pyqtProperty`로 선언된 프로퍼티가 자동으로 바인딩
- **QML → ViewModel**: `onClicked`, `onTextChanged` 등 QML 신호가 ViewModel 슬롯 호출

---

## 데이터 흐름

```mermaid
sequenceDiagram
    participant App as main.py<br/>Application
    participant Timer as QTimer
    participant Model as MonitorModel
    participant CPU as CPUMonitor
    participant MVM as MonitorViewModel
    participant QML as QML View

    App->>Timer: timer.start(interval)

    loop 주기적 모니터링
        Timer->>Model: measure()
        Model->>CPU: measure()
        CPU->>CPU: psutil로 CPU 사용률 계산
        CPU-->>Model: cpu_value
        Model->>Model: update _cpu
        Model->>Model: emit cpuChanged()

        Model-->>MVM: cpuChanged signal
        MVM->>MVM: _on_cpu_changed()
        MVM->>MVM: _cpu_usage = "%.1f%%" % cpu
        MVM->>MVM: emit cpuUsageChanged()

        MVM-->>QML: cpuUsageChanged signal
        QML->>QML: cpuText binding 업데이트
        Note over QML: UI 렌더링
    end
```

### 프로세스 수집 흐름

```mermaid
sequenceDiagram
    participant Main as Main Thread
    participant App as QApplication
    participant VM as ProcessViewModel
    participant Worker as ProcessWorker
    participant WorkerThread as Worker Thread
    participant Monitor as ProcessMonitor
    participant Model as ProcessModel
    participant QML as QML View

    App->>VM: ProcessViewModel 생성
    VM->>WorkerThread: moveToThread(worker_thread)
    WorkerThread->>WorkerThread: start()

    Main->>Worker: start_collecting()
    activate WorkerThread

    loop 2초마다
        Worker->>Monitor: collect_processes()
        activate Monitor
        Monitor->>Monitor: psutil로 프로세스 정보 수집
        Monitor-->>Worker: processes list
        deactivate Monitor

        Worker->>Worker: emit finished(processes)
        Worker-->>Main: finished signal
    end

    Main->>VM: _on_worker_finished(processes)
    VM->>Model: setProcesses(processes)
    VM->>Model: emit processesChanged()

    Model-->>QML: processesChanged signal
    QML->>QML: ListView 업데이트
    Note over QML: UI 렌더링
```

---

## 스레딩 모델

```mermaid
graph LR
    subgraph MainThread[Main Thread]
        QML["QML 렌더링"]
        Timer["QTimer"]
        ViewModel["ViewModel"]
        Model["Model"]
    end

    subgraph WorkerThread1[Worker Thread 1]
        ProcessWorker["ProcessWorker<br/>(2초 주기)"]
    end

    subgraph WorkerThread2[Worker Thread 2]
        PingWorker["PingWorker<br/>(온디맨드)"]
    end

    subgraph SystemLibs[System Libraries]
        psutil["psutil"]
        GPUtil["GPUtil"]
        gpiod["gpiod/RPi.GPIO"]
        pyusb["pyusb"]
        pyserial["pyserial"]
    end

    Timer -->|timeout signal| Model
    Model -->|raw data| ViewModel
    ViewModel -->|formatted data| QML

    ProcessWorker -->|signal-slot| Model
    PingWorker -->|signal-slot| ViewModel

    Model -.->|collect_processes| psutil
    Model -.->|get_gpu_info| GPUtil
    ProcessWorker -.->|collect| psutil

    style MainThread fill:#81c784,color:#000
    style WorkerThread1 fill:#64b5f6,color:#000
    style WorkerThread2 fill:#4fc3f7,color:#000
    style SystemLibs fill:#ba68c8,color:#fff
```

### 스레딩 안전성

**Main Thread 책임**:
- QML 렌더링
- Timer 관리
- Model/ViewModel 상태 관리
- Signal-Slot 신호 처리

**Worker Thread 책임**:
- CPU 집약적 작업 처리 (프로세스 수집, Ping)
- 메인 스레드 블로킹 방지
- `finished` 시그널로 결과 반환

**Signal-Slot 안전성**:
- Qt의 신호-슬롯 메커니즘은 자동으로 스레드 간 안전성 보장
- Worker 스레드에서 Main 스레드 객체의 슬롯 호출 시 메시지 큐를 통해 직렬화

---

## QML 컴포넌트 구조

```mermaid
graph TD
    A["main.qml<br/>(ApplicationWindow)"]

    A --> B["ThemeManager<br/>(다크/라이트 테마)"]
    A --> C["MenuBar"]
    A --> D["TabBar<br/>(5개 탭)"]
    A --> E["StackLayout"]

    D --> D1["System Overview"]
    D --> D2["Processes"]
    D --> D3["Disk"]
    D --> D4["Network"]
    D --> D5["Hardware"]

    E --> T1["SystemOverviewTab.qml"]
    E --> T2["ProcessesTab.qml"]
    E --> T3["DiskTab.qml"]
    E --> T4["NetworkTab.qml"]
    E --> T5["HardwareTab.qml"]

    T1 --> C1["GaugeChart"]
    T1 --> C2["LineChart"]

    T2 --> C3["SearchBar"]
    T2 --> C4["ProcessContextMenu"]
    T2 --> C5["ProcessDetailsDialog"]
    T2 --> C6["PriorityDialog"]

    T4 --> C7["PingSection"]

    A -.->|contextProperty| B1["monitorViewModel"]
    A -.->|contextProperty| B2["processViewModel"]
    A -.->|contextProperty| B3["diskViewModel"]
    A -.->|contextProperty| B4["networkViewModel"]
    A -.->|contextProperty| B5["hardwareViewModel"]

    style A fill:#e57373,color:#000
    style B fill:#ff9800,color:#000
    style C fill:#ffb74d,color:#000
    style D fill:#fdd835,color:#000
    style E fill:#c5e1a5,color:#000
    style T1 fill:#a5d6a7,color:#000
    style T2 fill:#80deea,color:#000
    style T3 fill:#80cbc4,color:#000
    style T4 fill:#81c784,color:#000
    style T5 fill:#64b5f6,color:#000
```

### 탭 설명

| 탭 이름 | 파일 | 설명 | ViewModel |
|---------|------|------|-----------|
| System Overview | SystemOverviewTab.qml | CPU/메모리/GPU/FPS 게이지 및 히스토리 그래프 | MonitorViewModel |
| Processes | ProcessesTab.qml | 프로세스 목록, 검색, 정렬, 트리 모드 | ProcessViewModel |
| Disk | DiskTab.qml | 디스크 파티션 및 사용률 바 | DiskViewModel |
| Network | NetworkTab.qml | 네트워크 인터페이스 및 Ping 테스트 | NetworkViewModel |
| Hardware | HardwareTab.qml | GPIO, USB, 직렬 통신 정보 | HardwareViewModel |

---

## 모듈 의존성

```mermaid
graph LR
    A["main.py<br/>(진입점)"] --> B["models/"]
    A --> C["views/"]
    A --> D["utils/"]
    A --> E["services/"]

    C --> B
    C --> E

    E --> D
    B --> D

    D --> F["monitor_base.py<br/>(ResourceMonitor)"]

    F -.->|상속| G["CPUMonitor"]
    F -.->|상속| H["MemoryMonitor"]
    F -.->|상속| I["GPUMonitor"]
    F -.->|상속| J["FPSMonitor"]
    F -.->|상속| K["DiskMonitor"]
    F -.->|상속| L["NetworkMonitor"]
    F -.->|상속| M["GPIOMonitor"]
    F -.->|상속| N["USBMonitor"]
    F -.->|상속| O["SerialMonitor"]

    G -.-> P["psutil"]
    H -.-> P
    I -.-> Q["GPUtil"]
    K -.-> P
    L -.-> P
    M -.-> R["gpiod/RPi.GPIO"]
    N -.-> S["pyusb"]
    O -.-> T["pyserial"]

    style A fill:#4fc3f7,color:#000
    style F fill:#ffb74d,color:#000
    style P fill:#ba68c8,color:#fff
    style Q fill:#ba68c8,color:#fff
    style R fill:#ba68c8,color:#fff
    style S fill:#ba68c8,color:#fff
    style T fill:#ba68c8,color:#fff
```

### 모듈 역할

**models/** - 데이터 저장소
- `monitor_model.py`: CPU, 메모리, GPU, FPS 통합 모니터 (QObject)
- `process_model.py`: 프로세스 목록 (QAbstractListModel)
- `process_sort_filter_model.py`: 프로세스 정렬/필터링 (QSortFilterProxyModel)
- `disk_model.py`: 디스크 파티션 (QAbstractListModel)
- `network_model.py`: 네트워크 인터페이스 (QAbstractListModel)
- `hardware_model.py`: GPIO/USB/직렬 정보 (QObject)

**views/** - 프레젠테이션 로직
- `monitor_viewmodel.py`: CPU/메모리/GPU/FPS 포맷팅 및 히스토리 관리
- `process_viewmodel.py`: 프로세스 제어 및 워커 스레드 관리
- `disk_viewmodel.py`: 디스크 새로고침 타이머 관리
- `network_viewmodel.py`: 네트워크 새로고침 및 Ping 워커
- `hardware_viewmodel.py`: 하드웨어 새로고침 타이머 관리

**services/** - 백그라운드 워커
- `worker_thread.py`: ProcessWorker (QThread, 2초 주기)
- `ping_worker.py`: PingWorker (비동기 Ping)

**utils/** - 데이터 수집
- 각 모니터 클래스: `monitor_base.py` 상속
- 유틸리티: `process_tree.py`, `ping_util.py`, `settings_manager.py`

---

## 디자인 패턴

### 1. Template Method Pattern (템플릿 메서드)

```python
# monitor_base.py의 ResourceMonitor 추상 클래스
class ResourceMonitor(ABC):
    def __init__(self):
        self.last_measurement = 0
        self.current_measurement = 0

    @abstractmethod
    def measure(self):
        """서브클래스가 구현할 추상 메서드"""
        pass

    def get_measurement(self):
        """모든 모니터가 공유하는 인터페이스"""
        return self.current_measurement
```

**사용처**: CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor 등이 ResourceMonitor를 상속하여 measure() 구현

### 2. MVVM Pattern (Model-View-ViewModel)

**Model**: 실시간 데이터 소유 및 신호 발출
**ViewModel**: Model 감시 → 데이터 포맷팅 → pyqtProperty로 노출
**View (QML)**: ViewModel 바인딩 → 자동 UI 업데이트

### 3. Observer Pattern (옵저버)

PyQt의 Signal-Slot 메커니즘으로 구현
- Model의 신호가 변경되면 ViewModel이 슬롯으로 감지
- ViewModel의 신호가 발출되면 QML이 바인딩으로 감지

### 4. Proxy Pattern (프록시)

ProcessSortFilterProxyModel이 ProcessModel의 프록시로 동작
- 정렬 및 필터링 기능 제공
- 원본 Model 수정 없이 표시 방식 변경

### 5. Dependency Injection (의존성 주입)

```python
# main.py
model = MonitorModel()
view_model = MonitorViewModel(model)  # Model을 ViewModel에 주입

# ViewModel은 받은 model 사용
class MonitorViewModel(QObject):
    def __init__(self, model, parent=None):
        self._model = model
        self._model.cpuChanged.connect(self._on_cpu_changed)
```

### 6. Graceful Degradation (우아한 성능 저하)

```python
# monitor_model.py
try:
    self._monitors['gpu'] = GPUMonitor()
except ImportError:
    print(f"GPU 모니터링을 사용할 수 없습니다.")
```

**특징**: 선택적 의존성 누락 시에도 애플리케이션 정상 작동

### 7. Worker Thread Pattern (워커 스레드)

ProcessWorker와 PingWorker는 QThread 기반으로 CPU 집약적 작업을 백그라운드에서 처리
- `moveToThread()` 패턴 사용
- `finished` 신호로 결과 반환
- 메인 스레드 블로킹 방지

---

## 타이머 조정

```mermaid
graph LR
    subgraph MainTimers[Main Thread Timers]
        T1["System Overview<br/>Timer"]
        T2["Disk Timer<br/>(5s)"]
        T3["Network Timer<br/>(2s)"]
        T4["Hardware Timer<br/>(3s)"]
    end

    subgraph WorkerTimers[Worker Thread Timers]
        T5["ProcessWorker<br/>Timer (2s)"]
    end

    subgraph OnDemand[On-Demand]
        T6["PingWorker"]
    end

    T1 -->|"configurable (1-10s)"| M1["MonitorModel.measure()"]
    T2 --> M2["DiskViewModel.refresh()"]
    T3 --> M3["NetworkViewModel.refresh()"]
    T4 --> M4["HardwareViewModel.refresh()"]
    T5 --> M5["ProcessWorker<br/>collect_processes()"]
    T6 --> M6["PingWorker<br/>ping_host()"]

    style T1 fill:#fdd835,color:#000
    style T2 fill:#fdd835,color:#000
    style T3 fill:#fdd835,color:#000
    style T4 fill:#fdd835,color:#000
    style T5 fill:#64b5f6,color:#000
    style T6 fill:#ba68c8,color:#fff
```

| 컴포넌트 | 주기 | 스레드 | 설정 가능 |
|---------|------|--------|----------|
| System Overview | 1-10초 | Main | O (사용자 설정) |
| Process List | 2초 | Worker | X (고정) |
| Disk | 5초 | Main | X (고정) |
| Network | 2초 | Main | X (고정) |
| Hardware | 3초 | Main | X (고정) |
| Ping | On-demand | Worker | - (사용자 요청) |

### 설정 관리

```python
# main.py
interval_ms = saved_interval * 1000  # QSettings에서 로드
timer = QTimer()
timer.timeout.connect(model.measure)
timer.start(interval_ms)

# settings_manager.py
def load_update_interval() -> int:
    """저장된 업데이트 간격 로드 (기본값: 1초)"""
    settings = QSettings(...)
    return settings.value("updateInterval", 1, type=int)

def save_update_interval(interval: int) -> None:
    """업데이트 간격 저장"""
    settings = QSettings(...)
    settings.setValue("updateInterval", interval)
```

---

## 기술 스택

### Core Framework

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| Python | 3.7+ | 언어 |
| PyQt5 | 5.15.11 | GUI 프레임워크 |
| Qt Quick (QML) | 2.15 | 선언형 UI |

### System Monitoring

| 라이브러리 | 버전 | 용도 | 필수 여부 |
|-----------|------|------|----------|
| psutil | 6.1.0 | CPU, 메모리, 디스크, 네트워크, 프로세스 | O |
| GPUtil | 1.4.0 | GPU 모니터링 | X (선택) |
| RPi.GPIO / gpiod | - | GPIO 제어 | X (선택) |
| pyusb | - | USB 장치 정보 | X (선택) |
| pyserial | - | 직렬 통신 | X (선택) |

### Optional Dependencies

**GPU 모니터링** (선택사항):
- `pip install gputil`
- 누락 시 자동으로 비활성화되고 GPU 섹션 표시 안 함

**GPIO 제어** (라즈베리파이):
- `pip install RPi.GPIO` 또는 `pip install libgpiod`
- 하드웨어 비활성화 시 자동으로 무시

**USB 정보** (선택사항):
- `pip install pyusb`
- 누락 시 USB 섹션 표시 안 함

**직렬 통신** (선택사항):
- `pip install pyserial`
- 누락 시 직렬 포트 섹션 표시 안 함

### Development Tools

| 도구 | 용도 |
|------|------|
| pytest | 단위 테스트 |
| black | 코드 포맷팅 |
| ruff | 린팅 |
| mypy | 타입 검사 |

---

## 실행 흐름

### 애플리케이션 시작

```
1. main() 함수 호출
2. QGuiApplication 생성
3. MonitorModel, ViewModels 인스턴스 생성
4. QML 엔진 초기화
5. 저장된 설정 로드 (테마, 윈도우 크기, 업데이트 간격)
6. QML Context Property로 ViewModels 등록
7. main.qml 로드
8. Timer 시작 및 모니터링 시작
9. Model.startMonitoring() 호출
10. ProcessWorker 시작
11. app.exec_() 실행 (이벤트 루프)
```

### 모니터링 주기

```
Timer Timeout (1초마다, 기본값)
  ├─ Model.measure() 호출
  │  ├─ CPUMonitor.measure()
  │  ├─ MemoryMonitor.measure()
  │  ├─ GPUMonitor.measure()
  │  └─ FPSMonitor.measure()
  └─ cpuChanged, memoryChanged 등 시그널 발출
       ├─ ViewModel._on_cpu_changed()
       ├─ ViewModel._on_memory_changed()
       └─ QML 바인딩 자동 업데이트
```

### 프로세스 수집 (2초 주기, 워커 스레드)

```
Worker Thread Timer (2초)
  ├─ ProcessWorker.collect_processes() 호출
  ├─ ProcessMonitor.collect_processes() 실행
  ├─ 프로세스 정보 수집 및 트리 구조 생성
  └─ finished 시그널 발출 (Main Thread)
       ├─ ViewModel._on_worker_finished()
       ├─ ProcessModel.setProcesses()
       └─ QML ListView 업데이트
```

### 애플리케이션 종료

```
1. 사용자 윈도우 닫기 또는 앱 종료
2. aboutToQuit 시그널 발출
3. on_about_to_quit() 콜백 실행
   ├─ 윈도우 크기 저장
   ├─ ProcessWorker 정리 (cleanup())
   ├─ 타이머 중지
   ├─ 워커 스레드 정리
4. 앱 종료
```

---

## 결론

Resource Monitor PyQt는 다음과 같은 아키텍처 특징을 가지고 있습니다:

1. **계층 분리**: Model, ViewModel, View의 명확한 계층 분리로 유지보수성 향상
2. **멀티스레딩**: 메인 스레드 블로킹 방지로 반응성 있는 UI 제공
3. **신호-슬롯**: PyQt의 강력한 신호-슬롯 메커니즘으로 느슨한 결합 구현
4. **우아한 성능 저하**: 선택적 의존성 처리로 다양한 환경 지원
5. **설정 관리**: QSettings 기반 지속적 사용자 설정 관리
6. **확장성**: Template Method와 다양한 디자인 패턴으로 새로운 기능 추가 용이

이러한 설계는 복잡한 시스템 모니터링 애플리케이션을 유지보수하기 쉽고 확장 가능한 구조로 만들어줍니다.
