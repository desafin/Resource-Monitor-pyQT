# Resource Monitor PyQT - 기술 문서

## 기술 스택 개요

| 분류 | 기술 | 버전 |
|---|---|---|
| 프로그래밍 언어 | Python | 3.7 이상 |
| GUI 프레임워크 | PyQt5 | 5.15.11 |
| UI 마크업 언어 | QML (Qt Quick) | Qt 5.15 |
| 시스템 자원 측정 | psutil | 6.1.0 |
| GPU 측정 (선택적) | GPUtil | 1.4.0 |
| Qt Python 바인딩 | PyQt5-Qt5 | 5.15.2 |
| SIP 바인딩 | PyQt5_sip | 12.15.0 |

---

## 기술 선택 이유

### Python 3.7+
크로스플랫폼 호환성, 풍부한 시스템 라이브러리 생태계, 그리고 PyQt5와의 완성도 높은 통합을 제공합니다. 데이터클래스(dataclass) 등 3.7에서 도입된 현대적 기능을 활용합니다.

### PyQt5 5.15 + QML
Qt5의 Python 바인딩으로 강력한 데스크탑 GUI를 구현합니다. QML(Qt Quick)은 선언형 UI 언어로, JavaScript와 유사한 문법으로 애니메이션과 반응형 레이아웃을 쉽게 구현할 수 있습니다. Python 백엔드와 QML 프론트엔드의 분리는 MVVM 패턴 적용을 자연스럽게 지원합니다.

### psutil 6.1.0
운영체제에 독립적인 방식으로 CPU, 메모리, 디스크, 네트워크 정보를 제공하는 사실상 표준 라이브러리입니다. Windows, macOS, Linux 모두에서 동일한 API로 동작합니다.

### GPUtil 1.4.0 (선택적)
NVIDIA GPU 정보를 Python에서 쉽게 조회할 수 있게 해주는 라이브러리입니다. 선택적 의존성으로 처리하여 GPU가 없는 환경에서도 애플리케이션이 정상 작동합니다.

---

## 아키텍처 - MVVM 패턴

본 프로젝트는 **MVVM(Model-View-ViewModel)** 아키텍처 패턴을 채택합니다. UI와 비즈니스 로직의 명확한 분리를 통해 유지보수성과 테스트 용이성을 높입니다.

### 레이어 책임

**Model (`models/monitor_model.py`)**
자원 측정 데이터를 보관합니다. `QObject`를 상속하며 `dataChanged` PyQt 시그널을 통해 데이터 변경을 외부에 알립니다. UI 로직을 전혀 포함하지 않습니다.

**View (`qml/main.qml`)**
QML로 작성된 순수 UI 레이어입니다. ViewModel이 제공하는 데이터를 표시하고, 사용자 상호작용 이벤트를 ViewModel로 전달합니다. Python 코드에 직접 의존하지 않습니다.

**ViewModel (`views/monitor_viewmodel.py`)**
Model과 View 사이의 브리지 역할을 합니다. Model의 `dataChanged` 시그널을 구독하고, QML이 소비할 수 있는 형태로 데이터를 변환하여 UI를 갱신합니다. Controller와 Model을 생성자 주입 방식으로 받습니다.

**Controller (`controllers/monitor_controller.py`)**
모니터링 시작/중지 등 비즈니스 로직을 담당합니다. QTimer를 사용하여 1초 주기로 `measure_all()`을 호출하고, 수집된 데이터를 Model에 전달합니다.

---

## 데이터 흐름 아키텍처

시스템 자원 데이터는 다음 경로로 흐릅니다.

```
QTimer (1초 주기)
    │
    ▼
controller.measure_all()
    │ 각 모니터에 측정 요청
    ▼
utils/ 모니터들 (cpu, memory, gpu, fps)
    │ 딕셔너리 형태로 결과 반환
    ▼
controller.dataChanged 시그널 발생
    │
    ▼
model._update_data()
    │ 내부 데이터 갱신
    ▼
model.dataChanged 시그널 발생
    │
    ▼
viewmodel._on_data_changed()
    │
    ▼
viewmodel.updateUI()
    │ QML 프로퍼티 업데이트
    ▼
QML ListView 화면 갱신
```

---

## 디자인 패턴

### 템플릿 메서드 패턴 (Template Method)
`monitor_base.py`의 `ResourceMonitor` 추상 클래스가 `measure()` 인터페이스를 정의합니다. 각 유틸리티 모니터(`cpu_monitor`, `memory_monitor` 등)는 이 인터페이스를 구체적으로 구현합니다. 측정 호출 방식을 통일하여 `system_monitor.py`의 코디네이터 코드를 단순하게 유지합니다.

### 옵저버 패턴 (Observer) - PyQt 시그널/슬롯
PyQt5의 시그널(Signal)/슬롯(Slot) 메커니즘으로 구현됩니다. Model이 데이터 변경 시 `dataChanged` 시그널을 발생시키면, 이를 구독하는 ViewModel의 슬롯이 자동으로 호출됩니다. 컴포넌트 간 직접 참조 없이 느슨한 결합(loose coupling)을 실현합니다.

### 의존성 주입 (Dependency Injection)
ViewModel은 생성자를 통해 Controller와 Model 인스턴스를 주입받습니다. 직접 생성하지 않으므로 테스트 시 Mock 객체 교체가 용이합니다.

### 우아한 성능 저하 (Graceful Degradation)
GPU 모니터(`gpu_monitor.py`)는 GPUtil 라이브러리 미설치 환경을 감지하고 자동으로 비활성화됩니다. 애플리케이션은 GPU 기능 없이도 나머지 모든 기능을 정상적으로 제공합니다.

### 타이머 기반 폴링 (Timer-Based Polling)
Qt의 `QTimer`를 사용하여 1초 간격으로 모든 자원 측정을 수행합니다. 이벤트 루프와 통합되어 UI 스레드를 블로킹하지 않고 안정적으로 동작합니다.

---

## 개발 환경 요구사항

| 항목 | 요구사항 |
|---|---|
| Python | 3.7 이상 |
| 패키지 관리자 | pip 또는 Miniconda/Anaconda |
| 권장 IDE | PyCharm (PyQt5 플러그인 지원) 또는 VS Code |
| 운영체제 | Windows, macOS, Linux (psutil 지원 플랫폼) |
| GPU 모니터링 | NVIDIA GPU + GPUtil 설치 (선택 사항) |

---

## 빌드 및 실행

### 의존성 설치

```bash
pip install PyQt5==5.15.11 psutil==6.1.0

# GPU 모니터링이 필요한 경우 추가 설치
pip install GPUtil==1.4.0
```

### 애플리케이션 실행

```bash
python main.py
```

`main.py`가 MVVM 컴포넌트를 순서대로 생성하고 QML 엔진을 초기화한 뒤, `qml/main.qml`을 로드하여 애플리케이션 창을 표시합니다.

---

## 의존성 상세

| 패키지 | 버전 | 용도 |
|---|---|---|
| PyQt5 | 5.15.11 | Qt5 Python 바인딩, GUI 프레임워크 |
| PyQt5-Qt5 | 5.15.2 | Qt5 네이티브 라이브러리 |
| PyQt5_sip | 12.15.0 | Python-C++ SIP 바인딩 레이어 |
| psutil | 6.1.0 | CPU 및 메모리 시스템 정보 수집 |
| GPUtil | 1.4.0 | NVIDIA GPU 정보 수집 (선택적) |
