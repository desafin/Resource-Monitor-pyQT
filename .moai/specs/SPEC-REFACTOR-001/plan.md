---
id: SPEC-REFACTOR-001
title: MVVM Pattern Refactoring - Implementation Plan
version: 1.0.0
status: draft
created: 2026-03-10
updated: 2026-03-10
author: oscar
priority: high
---

# SPEC-REFACTOR-001: MVVM 패턴 리팩터링 - 구현 계획

## 1. 구현 전략

### 1.1 핵심 원칙

- **행동 보존 우선**: 기존 모니터링 기능(CPU, Memory, GPU, FPS)이 리팩터링 후에도 동일하게 동작해야 함
- **단계적 전환**: 한 번에 전체를 변경하지 않고, 레이어별로 순차 전환
- **의존성 방향 준수**: View -> ViewModel -> Model -> Monitors (단방향만 허용)

### 1.2 기술 접근 방식

- PyQt6의 `pyqtProperty` 데코레이터를 사용한 Q_PROPERTY 선언
- `pyqtSignal`을 사용한 NOTIFY 시그널 정의
- QML의 선언적 property 바인딩으로 imperative 시그널 교체
- `pyqtSlot` 데코레이터를 사용한 QML-callable 메서드 노출

## 2. 구현 단계

### Phase 1: Model 리팩터링 (Primary Goal)

**목표**: Model이 모니터 인스턴스를 직접 소유하고 Q_PROPERTY를 노출

**관련 요구사항**: REQ-M01, REQ-M02, REQ-M03, REQ-M04

**작업 내역**:

1. `models/monitor_model.py` 수정:
   - CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor 인스턴스를 Model 내부에서 생성
   - Q_PROPERTY 정의: `cpu`(float), `memory`(dict), `gpu`(list), `fps`(float), `isMonitoring`(bool)
   - 각 property에 대한 NOTIFY 시그널 정의 (cpuChanged, memoryChanged 등)
   - `measure()` 메서드 구현: 모든 모니터에서 데이터를 수집하고 property 갱신
   - Controller 의존성 완전 제거

2. 검증 기준:
   - Model이 독립적으로 인스턴스화 가능
   - `measure()` 호출 시 모든 Q_PROPERTY가 갱신되고 NOTIFY 시그널 발생
   - 외부 의존성 없음 (Controller, ViewModel 미참조)

**의존성**: 없음 (첫 번째 단계)

---

### Phase 2: ViewModel 리팩터링 (Primary Goal)

**목표**: ViewModel이 Model의 Q_PROPERTY를 구독하고 포맷된 문자열을 Q_PROPERTY로 노출

**관련 요구사항**: REQ-VM01, REQ-VM02, REQ-VM03, REQ-VM04

**작업 내역**:

1. `views/monitor_viewmodel.py` 수정:
   - 생성자에서 Model 인스턴스를 받아 저장
   - Controller 의존성 완전 제거
   - 포맷 Q_PROPERTY 정의:
     - `cpuUsage`(str): `f"{cpu:.1f}%"` 형태
     - `memoryUsage`(str): `f"{used:.1f} / {total:.1f} GB"` 형태
     - `gpuUsage`(str): GPU 정보 포맷
     - `fpsDisplay`(str): `f"{fps:.1f} FPS"` 형태
   - Model의 NOTIFY 시그널에 연결하여 포맷 데이터 자동 갱신
   - `startMonitoring()`, `stopMonitoring()` pyqtSlot 메서드 구현
   - `updateUI` 시그널 제거 (Q_PROPERTY NOTIFY로 대체)

2. 검증 기준:
   - ViewModel이 Model만 의존
   - Model 데이터 변경 시 ViewModel의 포맷 property가 자동 갱신
   - QML에서 호출 가능한 slot 메서드 정상 동작

**의존성**: Phase 1 완료 필요

---

### Phase 3: View 리팩터링 (Secondary Goal)

**목표**: QML을 선언적 바인딩으로 전환

**관련 요구사항**: REQ-V01, REQ-V02, REQ-V03

**작업 내역**:

1. `qml/main.qml` 수정:
   - `onUpdateUI` 등 명령형 시그널 핸들러 제거
   - 선언적 property 바인딩으로 교체:
     ```qml
     Text { text: viewModel.cpuUsage }
     Text { text: viewModel.memoryUsage }
     Text { text: viewModel.fpsDisplay }
     ```
   - QML 내부의 데이터 변환 로직 제거 (JavaScript 포맷팅 코드)
   - static ListModel 대신 ViewModel property 직접 바인딩
   - `setProperty()` 호출을 property 바인딩으로 대체

2. 검증 기준:
   - QML에 JavaScript 데이터 변환 코드 없음
   - 모든 데이터 표시가 ViewModel Q_PROPERTY 바인딩으로 동작
   - UI가 기존과 동일하게 표시됨

**의존성**: Phase 2 완료 필요

---

### Phase 4: main.py 단순화 (Secondary Goal)

**목표**: 진입점에서 Controller를 제거하고 Model-ViewModel 직접 연결

**관련 요구사항**: REQ-A01, REQ-A02, REQ-S01

**작업 내역**:

1. `main.py` 수정:
   - Controller import 및 인스턴스 생성 제거
   - Model과 ViewModel만 생성:
     ```python
     model = MonitorModel()
     view_model = MonitorViewModel(model)
     ```
   - 타이머가 `model.measure()`를 직접 호출하도록 연결
   - ViewModel을 QML context에 등록
   - Controller 관련 시그널 연결 코드 제거

2. 검증 기준:
   - Controller 참조 완전 제거
   - 애플리케이션 정상 시작 및 모니터링 동작
   - 시그널 체인 3단계 이하

**의존성**: Phase 1, 2, 3 완료 필요

---

### Phase 5: 데드 코드 제거 (Final Goal)

**목표**: 불필요한 파일 삭제

**관련 요구사항**: REQ-C01, REQ-C02

**작업 내역**:

1. 삭제 대상:
   - `controllers/monitor_controller.py` 삭제
   - `controllers/__init__.py` 삭제
   - `controllers/` 디렉토리 삭제
   - `system_monitor.py` 삭제 (데드 코드)

2. 추가 확인:
   - 프로젝트 전체에서 삭제 대상 파일에 대한 import 참조가 없는지 확인
   - `__init__.py` 등에서 controllers 패키지 참조가 없는지 확인

**의존성**: Phase 4 완료 필요 (모든 참조 제거 확인 후 삭제)

---

### Phase 6: 검증 (Final Goal)

**목표**: 리팩터링 결과 종합 검증

**작업 내역**:

1. 기능 검증:
   - CPU 모니터링 데이터 정상 표시
   - Memory 모니터링 데이터 정상 표시
   - GPU 모니터링 데이터 정상 표시
   - FPS 모니터링 데이터 정상 표시
   - 모니터링 시작/중지 동작 확인

2. 아키텍처 검증:
   - 시그널 체인 3단계 이하 확인
   - 의존성 방향 단방향 확인 (View -> ViewModel -> Model -> Monitors)
   - Controller 참조 완전 제거 확인
   - QML 내 데이터 변환 로직 부재 확인

3. 코드 품질 검증:
   - 미사용 import 제거
   - 불필요한 시그널/슬롯 제거
   - 네이밍 컨벤션 일관성

**의존성**: Phase 5 완료 필요

## 3. 위험 분석 및 대응

| 위험 요소 | 심각도 | 대응 방안 |
|-----------|--------|-----------|
| Q_PROPERTY와 QML 바인딩 호환성 문제 | High | Phase 1 완료 후 간단한 QML 테스트로 바인딩 동작 조기 확인 |
| dict/list 타입의 Q_PROPERTY 갱신 미감지 | High | QVariant 변환 확인, 필요시 JSON 문자열로 전달 후 QML에서 파싱 |
| GPU 모니터 데이터 구조 복잡성 | Medium | GPU 데이터를 ViewModel에서 단일 문자열로 포맷하여 단순화 |
| 기존 기능 회귀 | Medium | Phase별 수동 테스트 체크리스트 활용 |
| QML 레이아웃 깨짐 | Low | 바인딩 전환 시 UI 크기/정렬 확인 |

## 4. Phase 간 의존성 다이어그램

```
Phase 1 (Model) ─────────────┐
                              ├──> Phase 4 (main.py) ──> Phase 5 (삭제) ──> Phase 6 (검증)
Phase 2 (ViewModel) ──────────┤
         |                    │
         v                    │
Phase 3 (View/QML) ──────────┘
```

- Phase 1은 독립적으로 시작 가능
- Phase 2는 Phase 1에 의존
- Phase 3는 Phase 2에 의존
- Phase 4는 Phase 1, 2, 3 모두 완료 후 진행
- Phase 5, 6은 순차적으로 진행

## 5. 아키텍처 변경 요약

### Before (현재)

```
Timer -> Controller.measure_all()
      -> Controller.dataChanged
      -> Model._update_data
      -> Model.dataChanged
      -> ViewModel._on_data_changed
      -> ViewModel.updateUI
      -> QML.onUpdateUI
      -> setProperty()
```

**8단계, Controller 의존, 명령형 갱신**

### After (목표)

```
Timer -> Model.measure()
      -> Q_PROPERTY NOTIFY
      -> QML 자동 바인딩
```

**3단계, Controller 제거, 선언적 바인딩**
