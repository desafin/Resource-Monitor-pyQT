# 프로젝트 아키텍처 개요

## 프로젝트 소개

**Resource Monitor PyQT**는 실시간으로 시스템 자원(CPU, 메모리, GPU, FPS)을 모니터링하는 데스크탑 애플리케이션입니다. Python 3.7+와 PyQt5 프레임워크를 기반으로 구축되었으며, QML을 통해 현대적인 UI를 제공합니다.

## MVVM 아키텍처 패턴

이 프로젝트는 **MVVM(Model-View-ViewModel)** 디자인 패턴을 채택합니다. MVVM은 UI 로직과 비즈니스 로직을 분리하여 코드의 유지보수성과 테스트 가능성을 높입니다.

### MVVM 각 계층의 역할

- **Model**: 데이터 저장 및 변경 알림 담당. PyQt5의 `QObject`와 `pyqtSignal`을 활용해 데이터 변경 이벤트를 발행합니다.
- **View**: QML로 구현된 UI 레이어. 사용자에게 정보를 시각적으로 표시하며, ViewModel의 시그널을 구독합니다.
- **ViewModel**: Model과 View 사이의 중개자. Model의 데이터를 View에 적합한 형식으로 변환하여 전달합니다.
- **Controller**: 비즈니스 로직(리소스 측정 조율)을 담당합니다. 엄밀히는 MVVM 패턴 외부 요소이나, 측정 흐름을 제어하기 위해 별도 계층으로 분리되었습니다.

## 시스템 경계

```
┌─────────────────────────────────────────────────────────────┐
│                    애플리케이션 경계                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               UI 계층 (QML)                          │   │
│  │  qml/main.qml - ApplicationWindow, ListView         │   │
│  └───────────────────┬─────────────────────────────────┘   │
│                      │ Connections / pyqtSignal             │
│  ┌───────────────────▼─────────────────────────────────┐   │
│  │            ViewModel 계층 (Python)                   │   │
│  │  views/monitor_viewmodel.py - MonitorViewModel       │   │
│  └───────────┬──────────────────────┬──────────────────┘   │
│              │ dataChanged signal    │ 직접 참조             │
│  ┌───────────▼──────────┐  ┌────────▼─────────────────┐   │
│  │    Model 계층         │  │    Controller 계층        │   │
│  │  models/             │  │  controllers/             │   │
│  │  monitor_model.py    │  │  monitor_controller.py    │   │
│  └──────────────────────┘  └────────┬─────────────────┘   │
│                                      │ measure() 호출       │
│  ┌───────────────────────────────────▼─────────────────┐   │
│  │             리소스 모니터 계층 (utils/)               │   │
│  │  CPUMonitor / MemoryMonitor / GPUMonitor / FPSMonitor│   │
│  └───────────────────────────────────┬─────────────────┘   │
│                                      │ 상속                  │
│  ┌───────────────────────────────────▼─────────────────┐   │
│  │            추상 기반 클래스 (monitor_base.py)         │   │
│  │  ResourceMonitor (ABC)                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │ psutil 호출               │ GPUtil 호출
         ▼                           ▼
   OS 시스템 API              GPU 드라이버 API
```

## 레이어 다이어그램

```
계층 1 (UI 표현)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  qml/main.qml
  - QML ApplicationWindow
  - ListView + ListModel
  - Connections { target: monitorViewModel }

계층 2 (뷰-모델 연결)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  views/monitor_viewmodel.py
  - MonitorViewModel (QObject)
  - updateUI 시그널 (QML로 전달)
  - _on_data_changed() 슬롯

계층 3 (데이터 및 비즈니스 로직)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  models/monitor_model.py          controllers/monitor_controller.py
  - MonitorModel (QObject)         - MonitorController (QObject)
  - dataChanged 시그널              - dataChanged 시그널 (dict)
  - _data 딕셔너리 저장              - measure_all() 조율

계층 4 (리소스 측정)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  utils/cpu_monitor.py             utils/memory_monitor.py
  utils/gpu_monitor.py             utils/fps_monitor.py
  - 각각 ResourceMonitor 상속
  - measure() 메서드 구현

계층 5 (추상 기반)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  monitor_base.py
  - ResourceMonitor (ABC)
  - measure() 추상 메서드 정의
```

## 핵심 설계 원칙

- **단일 책임 원칙**: 각 클래스는 하나의 명확한 역할만 수행합니다.
- **의존성 역전**: 고수준 모듈(Controller)이 저수준 모듈(각 Monitor)의 구체 구현에 직접 의존하지 않고 추상 기반 클래스(`ResourceMonitor`)를 통해 상호작용합니다.
- **옵셔널 의존성**: GPU 모니터는 `ImportError`를 포착하여 GPUtil 미설치 환경에서도 정상 동작합니다.
- **이벤트 드리븐 업데이트**: PyQt5 시그널/슬롯 메커니즘을 통해 계층 간 결합도를 낮춥니다.
