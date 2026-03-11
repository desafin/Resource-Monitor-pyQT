# 의존성 그래프

## 외부 라이브러리 의존성

### 전체 의존성 목록

| 라이브러리 | 버전 | 역할 | 필수 여부 |
|-----------|------|------|----------|
| PyQt5 | 5.15.11 | Qt UI 프레임워크 (QObject, 시그널/슬롯, QML 엔진) | 필수 |
| PyQt5-Qt5 | 5.15.2 | Qt5 네이티브 바이너리 런타임 | 필수 |
| PyQt5-sip | 12.15.0 | Python-C++ 바인딩 레이어 | 필수 |
| psutil | 6.1.0 | OS 시스템 자원 조회 (CPU, 메모리) | 필수 |
| GPUtil | 1.4.0 | NVIDIA GPU 상태 조회 | 선택적 |

### 외부 의존성 그래프

```
Resource Monitor PyQT
│
├── PyQt5 5.15.11
│   ├── PyQt5.QtCore        → QObject, QTimer, QUrl, pyqtSignal, pyqtSlot, pyqtProperty
│   ├── PyQt5.QtGui         → QGuiApplication
│   ├── PyQt5.QtQml         → QQmlApplicationEngine
│   ├── PyQt5.QtWidgets     → QApplication (임포트만 됨, 현재 미사용)
│   └── PyQt5-Qt5 5.15.2    → Qt5 네이티브 런타임 (자동 의존)
│       └── PyQt5-sip 12.15.0 → C++ ↔ Python 브리지 (자동 의존)
│
├── psutil 6.1.0
│   ├── psutil.cpu_percent()       → CPUMonitor.measure()
│   └── psutil.virtual_memory()   → MemoryMonitor.measure()
│
└── GPUtil 1.4.0  [선택적]
    └── GPUtil.getGPUs()           → GPUMonitor.measure()
```

---

## 내부 모듈 관계

### 임포트 의존성 맵

```
main.py
├── system_monitor.SystemMonitor        (직접 임포트, 현재 실행 경로에서 미사용)
├── controllers.MonitorController
├── models.MonitorModel
└── views.MonitorViewModel

controllers/monitor_controller.py
├── PyQt5.QtCore (QObject, pyqtSignal)
└── utils (CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor)

models/monitor_model.py
├── PyQt5.QtCore (QObject, pyqtSignal)
└── utils (CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor)
    └── (임포트는 되어 있으나 모델 내에서 직접 인스턴스화하지 않음)

views/monitor_viewmodel.py
├── PyQt5.QtCore (QObject, pyqtSignal, pyqtSlot, pyqtProperty)
└── utils (CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor)
    └── (임포트는 되어 있으나 뷰모델 내에서 직접 인스턴스화하지 않음)

system_monitor.py
└── utils (CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor)

utils/cpu_monitor.py
├── monitor_base.ResourceMonitor
└── psutil

utils/memory_monitor.py
├── monitor_base.ResourceMonitor
└── psutil

utils/gpu_monitor.py
├── monitor_base.ResourceMonitor
└── GPUtil  [선택적]

utils/fps_monitor.py
├── monitor_base.ResourceMonitor
└── time  (표준 라이브러리)

monitor_base.py
└── abc  (표준 라이브러리)
```

### 계층별 의존 방향

```
[QML 레이어]
    qml/main.qml
        │ (컨텍스트 프로퍼티를 통해 접근)
        ▼
[ViewModel 레이어]
    views/monitor_viewmodel.py
        │ (참조)          │ (참조)
        ▼                 ▼
[Model 레이어]     [Controller 레이어]
 models/                controllers/
 monitor_model.py       monitor_controller.py
                             │ (직접 인스턴스화)
                             ▼
                    [Utils 레이어]
                    utils/cpu_monitor.py
                    utils/memory_monitor.py
                    utils/gpu_monitor.py
                    utils/fps_monitor.py
                             │ (상속)
                             ▼
                    [Base 레이어]
                    monitor_base.py
                    ResourceMonitor (ABC)
```

---

## 시그널/슬롯 연결 의존성

PyQt5의 시그널/슬롯 메커니즘은 런타임 의존성을 형성합니다. 정적 임포트와 별개로 실행 시점에 다음 연결이 수립됩니다.

```
MonitorController.dataChanged (pyqtSignal)
    └── 연결 대상: MonitorModel._update_data (슬롯)
            └── 연결 대상: MonitorViewModel._on_data_changed (슬롯)
                    └── 발행: MonitorViewModel.updateUI (pyqtSignal)
                            └── QML Connections.onUpdateUI (핸들러)

QTimer.timeout (내장 시그널)
    └── 연결 대상: MonitorController.measure_all (슬롯)
```

---

## 의존성 순환 분석

현재 프로젝트에는 의존성 순환이 없습니다. 의존성은 단방향으로 흐릅니다.

```
monitor_base (의존 없음)
    ↑
utils/* (monitor_base에 의존)
    ↑
controllers/ (utils에 의존)
    ↑
models/ (controllers에 의존)
    ↑
views/ (models, controllers에 의존)
    ↑
main.py (모든 계층에 의존)
```

---

## 선택적 의존성 처리 패턴

GPUtil은 선택적 라이브러리로, 다음과 같이 `try/except`로 안전하게 처리됩니다.

```
MonitorController.__init__()
    try:
        self.monitors['gpu'] = GPUMonitor()   ← GPUtil 필요
    except ImportError:
        print("GPU 모니터링을 사용할 수 없습니다.")
        # 'gpu' 키는 monitors 딕셔너리에 추가되지 않음
        # QML은 data.gpu !== undefined 확인으로 안전하게 처리
```

QML 측에서도 `data.gpu !== undefined && data.gpu.length > 0` 조건을 통해 GPU 데이터 부재 상황을 처리합니다.
