# Resource Monitor PyQT - 프로젝트 구조

## 디렉터리 트리

```
Resource-Monitor-pyQT/
├── main.py                        # 애플리케이션 진입점
├── system_monitor.py              # 자원 모니터 통합 코디네이터
├── monitor_base.py                # ResourceMonitor 추상 기반 클래스
│
├── models/
│   └── monitor_model.py           # QObject 데이터 모델 (dataChanged 시그널)
│
├── controllers/
│   └── monitor_controller.py      # 비즈니스 로직 및 측정 제어
│
├── views/
│   └── monitor_viewmodel.py       # Model/Controller와 QML 간의 ViewModel 브리지
│
├── utils/
│   ├── cpu_monitor.py             # CPU 사용률 측정 (psutil)
│   ├── memory_monitor.py          # 메모리 사용률 측정 (psutil)
│   ├── gpu_monitor.py             # GPU 사용률 측정 (GPUtil, 선택적)
│   └── fps_monitor.py             # 프레임 레이트 측정
│
└── qml/
    └── main.qml                   # Qt Quick UI 레이아웃 및 ListView
```

---

## 디렉터리별 역할

### 루트 (`/`)

프로젝트의 핵심 진입 파일과 공통 기반 클래스가 위치합니다.

| 파일 | 역할 |
|---|---|
| `main.py` | 앱 부트스트랩. MVVM 컴포넌트를 생성하고 QML 엔진을 초기화합니다. |
| `system_monitor.py` | 모든 자원 모니터(`cpu_monitor`, `memory_monitor` 등)를 통합하는 코디네이터 클래스입니다. |
| `monitor_base.py` | 모든 자원 모니터가 구현해야 하는 `measure()` 인터페이스를 정의하는 추상 기반 클래스입니다. |

### `models/` - 데이터 모델 레이어

MVVM 패턴의 **Model** 역할을 담당합니다. QObject를 상속하여 PyQt 신호/슬롯 시스템에 통합됩니다.

| 파일 | 역할 |
|---|---|
| `monitor_model.py` | 측정된 자원 데이터를 보관하는 QObject 모델입니다. 데이터 변경 시 `dataChanged` 시그널을 발생시켜 ViewModel에 변경을 알립니다. |

### `controllers/` - 제어 레이어

비즈니스 로직을 담당합니다. 모니터링 시작/중지 및 주기적 측정을 제어합니다.

| 파일 | 역할 |
|---|---|
| `monitor_controller.py` | QTimer를 사용해 1초 간격으로 `measure_all()`을 호출합니다. 모든 모니터에서 수집된 결과를 딕셔너리로 집계한 뒤 `dataChanged` 시그널로 Model에 전달합니다. |

### `views/` - 뷰모델 레이어

MVVM 패턴의 **ViewModel** 역할을 담당합니다. Model과 Controller의 데이터를 QML이 소비할 수 있는 형태로 변환합니다.

| 파일 | 역할 |
|---|---|
| `monitor_viewmodel.py` | Model의 `dataChanged` 시그널을 구독합니다. 데이터 변경 시 `updateUI` 메서드를 호출하여 QML의 ListView를 갱신합니다. Controller와 Model을 의존성 주입(Dependency Injection) 방식으로 받습니다. |

### `utils/` - 자원 모니터 유틸리티

각 시스템 자원을 측정하는 개별 모니터 모듈이 위치합니다. 모든 모듈은 `monitor_base.py`의 `ResourceMonitor` 기반 클래스를 상속합니다.

| 파일 | 측정 대상 | 의존 라이브러리 |
|---|---|---|
| `cpu_monitor.py` | CPU 사용률 (%) | psutil |
| `memory_monitor.py` | 메모리 사용률 (%) | psutil |
| `gpu_monitor.py` | GPU 사용률 (%) | GPUtil (선택적) |
| `fps_monitor.py` | 애플리케이션 프레임 레이트 | - |

> **참고**: `gpu_monitor.py`는 GPUtil 라이브러리가 설치되어 있지 않은 환경에서도 애플리케이션이 정상적으로 실행되도록 예외 처리가 되어 있습니다.

### `qml/` - UI 레이어

Qt Quick(QML) 기반의 사용자 인터페이스 파일이 위치합니다.

| 파일 | 역할 |
|---|---|
| `main.qml` | 전체 UI 레이아웃을 정의합니다. ListView 컴포넌트를 사용하여 ViewModel에서 전달된 자원 정보(CPU, 메모리, GPU, FPS)를 실시간으로 표시합니다. |

---

## MVVM 레이어 매핑

```
┌─────────────────────────────────────────┐
│  View Layer (QML)                       │
│  qml/main.qml                           │
└────────────────┬────────────────────────┘
                 │ QML 바인딩
┌────────────────▼────────────────────────┐
│  ViewModel Layer                        │
│  views/monitor_viewmodel.py             │
└──────┬─────────────────┬───────────────┘
       │ 접근             │ 접근
┌──────▼──────┐  ┌───────▼───────────────┐
│ Model Layer │  │ Controller Layer      │
│ models/     │  │ controllers/          │
│ monitor_    │  │ monitor_controller.py │
│ model.py    │  └───────────┬───────────┘
└─────────────┘              │ 의존
                 ┌───────────▼───────────────────────────┐
                 │ Utils Layer (Resource Monitors)        │
                 │ utils/cpu_monitor.py                  │
                 │ utils/memory_monitor.py               │
                 │ utils/gpu_monitor.py                  │
                 │ utils/fps_monitor.py                  │
                 └───────────────┬───────────────────────┘
                                 │ 상속
                 ┌───────────────▼───────────────────────┐
                 │ Base Class                            │
                 │ monitor_base.py (ResourceMonitor)     │
                 └───────────────────────────────────────┘
```
