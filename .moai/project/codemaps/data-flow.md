# 데이터 흐름

## 전체 데이터 흐름 개요

데이터는 QTimer의 틱을 시작으로, 리소스 측정 → 시그널 전달 → UI 갱신의 단방향 파이프라인으로 흐릅니다. 전체 주기는 1초(1000ms)입니다.

```
[타이머 트리거]
      │
      ▼
[리소스 측정]         CPUMonitor, MemoryMonitor, FPSMonitor, GPUMonitor
      │
      ▼ dict
[Controller 시그널]   MonitorController.dataChanged.emit(results)
      │
      ▼ 슬롯 호출
[Model 갱신]          MonitorModel._update_data(new_data)
      │
      ▼ 시그널
[ViewModel 알림]      MonitorViewModel._on_data_changed()
      │
      ▼ QVariantMap 시그널
[UI 갱신]             QML onUpdateUI(data) → ListModel.setProperty()
```

---

## 단계별 상세 흐름

### 1단계: 타이머 트리거

```
QTimer (1초 간격)
    timeout 시그널 발행
        └── MonitorController.measure_all() 호출
```

Qt 이벤트 루프는 1초마다 `QTimer.timeout` 시그널을 발행합니다. 이 시그널은 `MonitorController.measure_all()`에 연결되어 있어 자동으로 호출됩니다.

### 2단계: 리소스 측정

```python
# MonitorController.measure_all() 내부
results = {}
for name, monitor in self.monitors.items():
    results[name] = monitor.measure()
```

각 모니터의 `measure()` 메서드가 호출되며, 다음 데이터가 수집됩니다.

| 키 | 타입 | 예시 값 |
|----|------|---------|
| `'cpu'` | `float` | `45.3` |
| `'memory'` | `dict` | `{'total': 16GB, 'used': 8GB, 'percent': 50.0}` |
| `'fps'` | `float` | `60.0` |
| `'gpu'` | `list[dict]` | `[{'id': 0, 'load': 30.0, 'memory_used': 2048, 'memory_total': 8192}]` |

측정 중 예외 발생 시 해당 키는 결과 딕셔너리에서 제외되며, 오류 메시지가 콘솔에 출력됩니다.

### 3단계: Controller 시그널 발행

```python
# MonitorController.measure_all() 마지막 부분
self.dataChanged.emit(results)  # results: dict
```

측정 결과 딕셔너리(`dict`)가 `dataChanged` 시그널의 페이로드로 발행됩니다.

### 4단계: Model 데이터 갱신

```python
# MonitorModel._update_data() (슬롯)
def _update_data(self, new_data):
    self._data = new_data        # 딕셔너리 교체
    self.dataChanged.emit()      # 파라미터 없이 발행
```

`MonitorController.dataChanged` → `MonitorModel._update_data` 연결에 의해 슬롯이 호출됩니다. Model은 내부 `_data`를 새 값으로 교체하고, 자체 `dataChanged` 시그널을 발행합니다. 이 시그널은 페이로드 없이 발행됩니다.

### 5단계: ViewModel 알림 수신

```python
# MonitorViewModel._on_data_changed() (슬롯)
def _on_data_changed(self):
    data = self._model.data       # Model에서 데이터 읽기
    self.updateUI.emit(data)      # QVariantMap으로 QML에 전달
```

`MonitorModel.dataChanged` → `MonitorViewModel._on_data_changed` 연결로 슬롯이 호출됩니다. ViewModel은 Model의 `data` 프로퍼티를 통해 최신 데이터를 읽고, `updateUI` 시그널을 `QVariantMap` 타입으로 발행합니다.

### 6단계: QML UI 갱신

```qml
// qml/main.qml
Connections {
    target: monitorViewModel
    function onUpdateUI(data) {
        // CPU 갱신
        if (data.cpu !== undefined)
            monitorModel.setProperty(0, "value", data.cpu.toFixed(1) + "%")
        // Memory 갱신
        if (data.memory !== undefined) {
            let usedGB = (data.memory.used / 1024 / 1024 / 1024).toFixed(1)
            let totalGB = (data.memory.total / 1024 / 1024 / 1024).toFixed(1)
            monitorModel.setProperty(1, "value", usedGB + " GB / " + totalGB + " GB (" + data.memory.percent.toFixed(1) + "%)")
        }
        // FPS 갱신
        if (data.fps !== undefined)
            monitorModel.setProperty(2, "value", data.fps.toFixed(1) + " FPS")
        // GPU 갱신
        if (data.gpu !== undefined && data.gpu.length > 0)
            monitorModel.setProperty(3, "value", data.gpu[0].load.toFixed(1) + "%")
    }
}
```

QML의 `Connections` 블록이 `monitorViewModel.updateUI` 시그널을 수신하면 `onUpdateUI` 핸들러가 실행됩니다. 각 리소스 데이터를 사람이 읽기 쉬운 문자열로 변환하여 `ListModel`의 해당 항목을 갱신합니다.

---

## 시그널/슬롯 연결 체인 전체도

```
[런타임 연결 체인]

QTimer.timeout
    └──(연결)──► MonitorController.measure_all()
                    │ (반환값 + emit)
                    └──(emit)──► MonitorController.dataChanged(dict)
                                    └──(연결)──► MonitorModel._update_data(new_data)
                                                    │ (emit)
                                                    └──(emit)──► MonitorModel.dataChanged()
                                                                    └──(연결)──► MonitorViewModel._on_data_changed()
                                                                                    │ (emit)
                                                                                    └──(emit)──► MonitorViewModel.updateUI(QVariantMap)
                                                                                                    └──(QML Connections)──► onUpdateUI(data)
                                                                                                                                └── ListModel.setProperty()
                                                                                                                                        └── ListView 자동 갱신
```

---

## 상태 관리 패턴

### 측정값 상태

각 `ResourceMonitor` 서브클래스는 `last_measurement`와 `current_measurement` 두 가지 상태를 유지합니다.

```
ResourceMonitor
├── last_measurement    ← 이전 1초의 측정값 (비교/델타 계산에 활용 가능)
└── current_measurement ← 가장 최근 측정값 (UI에 표시되는 값)
```

`measure()` 호출 시마다 `current_measurement`가 `last_measurement`로 이동하고, 새 측정값이 `current_measurement`에 저장됩니다.

### 모니터링 상태

`MonitorController`는 `_is_monitoring` 불리언 플래그로 전체 측정 활성화 상태를 관리합니다.

```
_is_monitoring = False  (초기 상태)
    │
    └── start_monitoring() 호출
            │
            ├── _is_monitoring = True
            └── monitoringStarted 시그널 발행

_is_monitoring = True  (모니터링 중)
    │
    └── QTimer 틱마다 measure_all() 실행

_is_monitoring = True
    │
    └── stop_monitoring() 호출
            │
            ├── _is_monitoring = False
            └── monitoringStopped 시그널 발행
```

### 데이터 상태 (MonitorModel)

`MonitorModel`은 `_data` 딕셔너리 하나로 전체 시스템 상태를 저장합니다. 매 측정 주기마다 딕셔너리 전체가 교체됩니다(불변 교체 방식).

```
초기 상태:   _data = {}
첫 틱 후:    _data = {'cpu': 45.3, 'memory': {...}, 'fps': 0.0}
두 번째 틱:  _data = {'cpu': 47.1, 'memory': {...}, 'fps': 60.0}  ← 전체 교체
```

---

## FPS 모니터의 특수 상태 관리

FPS 모니터는 다른 모니터와 달리 내부에 자체 시간 상태를 유지합니다.

```
FPSMonitor 내부 상태:
├── frame_count = 0       ← 1초 구간의 누적 프레임 카운트
└── last_time = time.time() ← 마지막 FPS 계산 시각

measure() 호출 시:
    frame_count += 1
    time_diff = now - last_time

    if time_diff >= 1.0:
        current_measurement = frame_count / time_diff
        frame_count = 0         ← 리셋
        last_time = now         ← 리셋
    else:
        current_measurement 변경 없음 (이전 값 유지)
```

QTimer가 1초마다 `measure_all()`을 호출하므로, FPS 값은 이론적으로 매 틱마다 갱신됩니다. 그러나 정확한 간격이 보장되지 않을 경우 2~3초에 한 번 갱신될 수 있습니다.

---

## UI 데이터 변환 규칙

QML에서 Python 측 원시 데이터를 사용자 표시 문자열로 변환하는 규칙은 다음과 같습니다.

| 리소스 | Python 원시값 | QML 표시 문자열 형식 |
|--------|-------------|---------------------|
| CPU | `float` (예: `45.3`) | `"45.3%"` |
| Memory | `dict {'total': bytes, 'used': bytes, 'percent': float}` | `"7.8 GB / 15.6 GB (50.0%)"` |
| FPS | `float` (예: `59.8`) | `"59.8 FPS"` |
| GPU | `list[dict]` (첫 번째 GPU 사용) | `"30.0%"` (load 값) |
