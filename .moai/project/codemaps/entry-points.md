# 진입점 및 실행 순서

## 진입점: main.py

`main.py`는 애플리케이션의 유일한 진입점입니다. `if __name__ == "__main__":` 블록에서 `main()` 함수를 호출하고, 반환값을 `sys.exit()`에 전달하여 프로세스 종료 코드를 Qt 이벤트 루프의 종료 코드로 설정합니다.

---

## 초기화 실행 순서

### 단계 1: Qt 환경 설정

```
os.environ["QT_FORCE_STDERR_LOGGING"] = "1"
```

Qt의 로그 메시지가 표준 에러로 출력되도록 환경 변수를 설정합니다. 디버깅 목적으로 사용됩니다.

### 단계 2: Qt 애플리케이션 생성

```
app = QGuiApplication(sys.argv)
```

Qt 이벤트 루프의 기반인 `QGuiApplication`을 생성합니다. 이 객체는 반드시 다른 Qt 객체보다 먼저 생성되어야 합니다.

### 단계 3: MVVM 컴포넌트 초기화

객체 생성 순서는 의존성 그래프를 따릅니다.

```
1. controller = MonitorController()
   ├── CPUMonitor() 인스턴스 생성
   ├── MemoryMonitor() 인스턴스 생성
   ├── FPSMonitor() 인스턴스 생성
   └── GPUMonitor() 인스턴스 생성 (ImportError 시 건너뜀)

2. model = MonitorModel(controller)
   └── controller.dataChanged → model._update_data 시그널 연결

3. viewmodel = MonitorViewModel(model, controller)
   └── model.dataChanged → viewmodel._on_data_changed 시그널 연결
```

### 단계 4: QML 엔진 설정 및 컨텍스트 등록

```
engine = QQmlApplicationEngine()
context = engine.rootContext()
context.setContextProperty("monitorViewModel", viewmodel)
```

`monitorViewModel`이라는 이름으로 `MonitorViewModel` 인스턴스를 QML 컨텍스트에 등록합니다. 이후 QML 파일 내에서 `monitorViewModel` 식별자로 이 객체에 접근할 수 있습니다.

### 단계 5: QML 파일 로드

```
engine.load(QUrl.fromLocalFile("qml/main.qml"))
```

`qml/main.qml`을 파싱하고 렌더링합니다. QML 파일 내의 `Connections { target: monitorViewModel }` 블록이 이 시점에 해석되어 시그널 연결이 완성됩니다.

### 단계 6: QTimer 설정

```
timer = QTimer()
timer.timeout.connect(controller.measure_all)
timer.start(1000)  # 1000ms = 1초
```

1초(1000ms) 간격으로 `controller.measure_all()`을 호출하는 타이머를 설정합니다. 이 타이머가 전체 데이터 흐름의 트리거입니다.

### 단계 7: 모니터링 시작

```
controller.start_monitoring()
```

`_is_monitoring` 플래그를 `True`로 설정합니다. 이 플래그가 활성화되어 있어야 `measure_all()`이 실제로 측정을 수행합니다.

### 단계 8: 이벤트 루프 진입

```
return app.exec_()
```

Qt 이벤트 루프를 시작합니다. 이 시점부터 Qt가 이벤트(타이머, UI 상호작용 등)를 처리하며, 애플리케이션이 종료될 때까지 이 함수는 블록됩니다.

---

## 전체 초기화 시퀀스 다이어그램

```
main.py                MonitorController    MonitorModel    MonitorViewModel    QML Engine
   │                          │                  │                │                │
   ├─ QGuiApplication()       │                  │                │                │
   │                          │                  │                │                │
   ├─ MonitorController() ────►│                  │                │                │
   │    ├─ CPUMonitor()        │                  │                │                │
   │    ├─ MemoryMonitor()     │                  │                │                │
   │    ├─ FPSMonitor()        │                  │                │                │
   │    └─ GPUMonitor()?       │                  │                │                │
   │                          │                  │                │                │
   ├─ MonitorModel(ctrl) ─────────────────────►  │                │                │
   │    └─ ctrl.dataChanged ──────────────────►  │                │                │
   │       연결: _update_data  │                  │                │                │
   │                          │                  │                │                │
   ├─ MonitorViewModel(model,ctrl) ──────────────────────────►    │                │
   │    └─ model.dataChanged ─────────────────── ─────────────►   │                │
   │       연결: _on_data_changed               │                │                │
   │                          │                  │                │                │
   ├─ QQmlApplicationEngine() ─────────────────────────────────────────────────►   │
   ├─ context.setContextProperty("monitorViewModel", viewmodel) ───────────────►   │
   ├─ engine.load("qml/main.qml") ─────────────────────────────────────────────►  │
   │    └─ QML 파싱 및 렌더링                    │                │            │
   │    └─ Connections{ target: monitorViewModel } 연결 완성      │            │
   │                          │                  │                │                │
   ├─ QTimer().timeout ──────►│.measure_all      │                │                │
   │   (1초 간격 설정)         │                  │                │                │
   │                          │                  │                │                │
   ├─ controller.start_monitoring()              │                │                │
   │    └─ _is_monitoring = True                 │                │                │
   │                          │                  │                │                │
   └─ app.exec_()  ← Qt 이벤트 루프 시작 (이후 타이머가 주기적으로 실행)
```

---

## QML 로딩 프로세스

`engine.load()` 호출 시 다음 과정이 발생합니다.

```
1. QUrl.fromLocalFile("qml/main.qml") 경로 해석
2. QML 엔진이 main.qml 파일 파싱
3. import QtQuick 2.15, QtQuick.Controls 2.15 등 모듈 로드
4. ApplicationWindow 루트 컴포넌트 생성
5. ListModel (monitorModel) 초기화 (CPU: "0%", Memory: "0 GB / 0 GB" 등)
6. Connections { target: monitorViewModel } 해석
   → QML 엔진이 컨텍스트에서 "monitorViewModel" 조회
   → Python MonitorViewModel 인스턴스에 연결
   → onUpdateUI 핸들러 등록
7. Component.onCompleted 핸들러 실행 (디버그 로그 출력)
8. 윈도우 화면 표시
```

로드 성공 시 `engine.rootObjects()`는 비어 있지 않으며, 실패 시 빈 리스트를 반환합니다.

---

## 타이머 동작 원리

```
QTimer (1000ms 간격)
    │
    └── timeout 시그널 발행
            │
            └── MonitorController.measure_all() 호출
                    │
                    ├── _is_monitoring 확인 (False면 즉시 반환)
                    ├── CPUMonitor.measure()
                    ├── MemoryMonitor.measure()
                    ├── FPSMonitor.measure()
                    ├── GPUMonitor.measure() (존재할 경우)
                    └── dataChanged.emit(results)
```

타이머는 Qt 이벤트 루프(`app.exec_()`)가 실행 중인 동안에만 동작합니다. `start_monitoring()`이 호출되어 `_is_monitoring`이 `True`인 경우에만 실제 측정이 이루어집니다.
