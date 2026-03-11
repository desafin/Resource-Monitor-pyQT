---
id: SPEC-REFACTOR-001
title: MVVM Pattern Refactoring
version: 1.0.0
status: draft
created: 2026-03-10
updated: 2026-03-10
author: oscar
priority: high
tags: [refactoring, mvvm, pyqt, architecture]
---

# SPEC-REFACTOR-001: MVVM 패턴 리팩터링

## 1. Environment (환경)

### 1.1 현재 시스템 상태

- **프레임워크**: PyQt6 + QML
- **아키텍처**: MVVM을 표방하나 실제로는 MVC와 혼재된 구조
- **주요 문제**: Controller 레이어가 존재하며, Model이 Controller에 의존하는 역방향 의존성
- **시그널 체인**: 8단계 (Timer -> Controller -> Model -> ViewModel -> QML)
- **데드 코드**: system_monitor.py (미사용)

### 1.2 기술 스택

- Python 3.x
- PyQt6
- QML (Qt Quick)
- 모니터링 유틸리티: CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor

### 1.3 파일 구조 (현재)

```
models/monitor_model.py      - Model (Controller에 의존, 모니터 미소유)
views/monitor_viewmodel.py   - ViewModel (Q_PROPERTY 부재, updateUI 시그널 사용)
controllers/monitor_controller.py - Controller (MVVM에 불필요)
controllers/__init__.py       - Controller 패키지 init
qml/main.qml                 - View (명령형 시그널 연결, 데이터 변환 로직 포함)
main.py                      - 진입점 (Controller 생성 및 연결)
system_monitor.py             - 데드 코드 (미사용)
monitor_base.py               - 추상 베이스 (정상)
utils/*.py                    - 모니터 구현체 (정상)
```

## 2. Assumptions (가정)

- [A1] PyQt6의 Q_PROPERTY와 NOTIFY 시그널을 통한 QML 선언적 바인딩이 현재 PyQt6 버전에서 정상 동작함
- [A2] 기존 모니터 구현체(utils/*.py)와 monitor_base.py는 올바르게 동작하며 변경 불필요
- [A3] 모든 모니터링 데이터(CPU, Memory, GPU, FPS)는 단일 타이머로 주기적 갱신 가능
- [A4] QML UI 레이아웃 변경 없이 바인딩 방식만 전환 가능
- [A5] Controller 제거 후 기존 기능이 모두 보존됨

## 3. Requirements (요구사항)

### 3.1 Model 레이어 리팩터링

- **[REQ-M01]** (Ubiquitous) Model은 **항상** 모든 모니터 인스턴스(CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor)를 직접 소유해야 한다.

- **[REQ-M02]** (Ubiquitous) Model은 **항상** 다음 Q_PROPERTY를 정의해야 한다:
  - `cpu` (float): CPU 사용률
  - `memory` (dict): 메모리 사용 정보
  - `gpu` (list): GPU 사용 정보 리스트
  - `fps` (float): FPS 값
  - `isMonitoring` (bool): 모니터링 활성 상태

- **[REQ-M03]** (Event-Driven) **WHEN** 타이머가 트리거될 때 **THEN** Model의 `measure()` 메서드가 모든 모니터에서 데이터를 수집해야 한다.

- **[REQ-M04]** (Unwanted) Model은 Controller 또는 ViewModel에 의존**하지 않아야 한다**.

### 3.2 ViewModel 레이어 리팩터링

- **[REQ-VM01]** (Ubiquitous) ViewModel은 **항상** 포맷된 표시 문자열을 위한 Q_PROPERTY를 노출해야 한다:
  - `cpuUsage` (str): CPU 사용률 포맷 (예: "45.2%")
  - `memoryUsage` (str): 메모리 사용량 포맷 (예: "8.2 / 16.0 GB")
  - `gpuUsage` (str): GPU 사용 정보 포맷
  - `fpsDisplay` (str): FPS 표시 포맷 (예: "60.0 FPS")

- **[REQ-VM02]** (Ubiquitous) ViewModel은 **항상** Model에만 의존해야 한다 (Controller 의존 금지).

- **[REQ-VM03]** (Ubiquitous) ViewModel은 **항상** 데이터 포맷팅을 담당해야 한다 (bytes -> GB 변환, 퍼센트 포맷팅 등).

- **[REQ-VM04]** (Event-Driven) **WHEN** 사용자가 모니터링을 시작/중지할 때 **THEN** ViewModel의 `startMonitoring()` / `stopMonitoring()` pyqtSlot 메서드가 호출되어야 한다.

### 3.3 View 레이어 리팩터링

- **[REQ-V01]** (Ubiquitous) QML은 **항상** 명령형 시그널 연결(onUpdateUI) 대신 선언적 property 바인딩을 사용해야 한다.

- **[REQ-V02]** (Unwanted) QML은 데이터 변환 로직을 포함**하지 않아야 한다** (모든 포맷팅은 ViewModel에서 처리).

- **[REQ-V03]** (Unwanted) QML은 모니터링 데이터에 static ListModel을 사용**하지 않아야 한다**.

### 3.4 Controller 레이어 제거

- **[REQ-C01]** (Ubiquitous) `controllers/` 디렉토리는 **항상** 전체 제거되어야 한다.

- **[REQ-C02]** (Ubiquitous) `system_monitor.py`는 **항상** 제거되어야 한다 (데드 코드).

### 3.5 Application 레이어 단순화

- **[REQ-A01]** (Ubiquitous) `main.py`는 **항상** Model과 ViewModel만 생성해야 한다 (Controller 생성 금지).

- **[REQ-A02]** (Event-Driven) **WHEN** 애플리케이션이 시작될 때 **THEN** 타이머가 Model.measure()를 직접 트리거해야 한다 (Controller를 거치지 않음).

### 3.6 시그널 체인 단순화

- **[REQ-S01]** (Ubiquitous) 시그널 체인은 **항상** 3단계 이하여야 한다:
  ```
  Timer -> Model.measure() + Q_PROPERTY NOTIFY -> QML 자동 바인딩
  ```

## 4. Specifications (명세)

### 4.1 목표 아키텍처

```
[Model Layer]
  MonitorModel(QObject)
    - _cpu_monitor: CPUMonitor
    - _memory_monitor: MemoryMonitor
    - _gpu_monitor: GPUMonitor
    - _fps_monitor: FPSMonitor
    - cpu: Q_PROPERTY(float, NOTIFY=cpuChanged)
    - memory: Q_PROPERTY(dict, NOTIFY=memoryChanged)
    - gpu: Q_PROPERTY(list, NOTIFY=gpuChanged)
    - fps: Q_PROPERTY(float, NOTIFY=fpsChanged)
    - isMonitoring: Q_PROPERTY(bool, NOTIFY=isMonitoringChanged)
    + measure(): void  # 모든 모니터에서 데이터 수집

[ViewModel Layer]
  MonitorViewModel(QObject)
    - _model: MonitorModel
    - cpuUsage: Q_PROPERTY(str, NOTIFY=cpuUsageChanged)
    - memoryUsage: Q_PROPERTY(str, NOTIFY=memoryUsageChanged)
    - gpuUsage: Q_PROPERTY(str, NOTIFY=gpuUsageChanged)
    - fpsDisplay: Q_PROPERTY(str, NOTIFY=fpsDisplayChanged)
    + startMonitoring(): pyqtSlot
    + stopMonitoring(): pyqtSlot

[View Layer - QML]
  Text { text: viewModel.cpuUsage }      // 선언적 바인딩
  Text { text: viewModel.memoryUsage }    // 선언적 바인딩
  Text { text: viewModel.fpsDisplay }     // 선언적 바인딩

[Application - main.py]
  model = MonitorModel()
  viewModel = MonitorViewModel(model)
  timer -> model.measure()
```

### 4.2 의존성 방향

```
View(QML) --> ViewModel --> Model --> Monitors(utils/*.py)
```

- 단방향 의존성만 허용
- 하위 레이어는 상위 레이어를 알지 못함

### 4.3 수정 대상 파일

| 파일 | 작업 | 우선순위 |
|------|------|----------|
| models/monitor_model.py | 리팩터링 (모니터 소유, Q_PROPERTY 추가) | High |
| views/monitor_viewmodel.py | 리팩터링 (Q_PROPERTY 포맷팅, Controller 의존 제거) | High |
| qml/main.qml | 리팩터링 (선언적 바인딩 전환) | High |
| main.py | 단순화 (Controller 제거, 타이머 직접 연결) | High |
| controllers/monitor_controller.py | 삭제 | Medium |
| controllers/__init__.py | 삭제 | Medium |
| system_monitor.py | 삭제 (데드 코드) | Low |

### 4.4 보존 대상 파일

| 파일 | 이유 |
|------|------|
| monitor_base.py | 올바른 추상 베이스 클래스 |
| utils/*.py | 올바른 모니터 구현체 |

## 5. Traceability (추적성)

| 요구사항 ID | 카테고리 | EARS 패턴 | 관련 파일 |
|-------------|----------|-----------|-----------|
| REQ-M01 | Model | Ubiquitous | models/monitor_model.py |
| REQ-M02 | Model | Ubiquitous | models/monitor_model.py |
| REQ-M03 | Model | Event-Driven | models/monitor_model.py |
| REQ-M04 | Model | Unwanted | models/monitor_model.py |
| REQ-VM01 | ViewModel | Ubiquitous | views/monitor_viewmodel.py |
| REQ-VM02 | ViewModel | Ubiquitous | views/monitor_viewmodel.py |
| REQ-VM03 | ViewModel | Ubiquitous | views/monitor_viewmodel.py |
| REQ-VM04 | ViewModel | Event-Driven | views/monitor_viewmodel.py |
| REQ-V01 | View | Ubiquitous | qml/main.qml |
| REQ-V02 | View | Unwanted | qml/main.qml |
| REQ-V03 | View | Unwanted | qml/main.qml |
| REQ-C01 | Controller | Ubiquitous | controllers/ |
| REQ-C02 | Controller | Ubiquitous | system_monitor.py |
| REQ-A01 | Application | Ubiquitous | main.py |
| REQ-A02 | Application | Event-Driven | main.py |
| REQ-S01 | Signal Chain | Ubiquitous | 전체 |
