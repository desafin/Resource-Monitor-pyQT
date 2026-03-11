---
id: SPEC-REFACTOR-001
title: MVVM Pattern Refactoring - Acceptance Criteria
version: 1.0.0
status: draft
created: 2026-03-10
updated: 2026-03-10
author: oscar
priority: high
---

# SPEC-REFACTOR-001: MVVM 패턴 리팩터링 - 인수 기준

## 1. 인수 시나리오

### Scenario 1: 앱 시작 시 모든 모니터링 데이터가 QML에 자동 바인딩됨

**관련 요구사항**: REQ-V01, REQ-VM01, REQ-S01

```gherkin
Given 애플리케이션이 시작되고 MonitorModel과 MonitorViewModel이 초기화됨
When 타이머가 첫 번째 측정 주기를 트리거함
Then QML의 CPU 표시 영역에 ViewModel의 cpuUsage property 값이 자동으로 바인딩되어 표시됨
And QML의 Memory 표시 영역에 ViewModel의 memoryUsage property 값이 자동으로 바인딩되어 표시됨
And QML의 GPU 표시 영역에 ViewModel의 gpuUsage property 값이 자동으로 바인딩되어 표시됨
And QML의 FPS 표시 영역에 ViewModel의 fpsDisplay property 값이 자동으로 바인딩되어 표시됨
And onUpdateUI 또는 setProperty() 같은 명령형 호출이 사용되지 않음
```

---

### Scenario 2: Controller 제거 후 앱이 정상 동작함

**관련 요구사항**: REQ-C01, REQ-C02, REQ-A01

```gherkin
Given controllers/ 디렉토리와 system_monitor.py가 삭제됨
And main.py에서 Controller import 및 인스턴스 생성이 제거됨
When 애플리케이션을 시작함
Then 애플리케이션이 오류 없이 시작됨
And 모니터링 데이터가 정상적으로 수집됨
And UI에 모니터링 데이터가 정상적으로 표시됨
And 프로젝트 전체에서 controller 관련 import가 존재하지 않음
```

---

### Scenario 3: QML에 데이터 변환 로직이 없음 (ViewModel에서 처리)

**관련 요구사항**: REQ-V02, REQ-VM03

```gherkin
Given QML 파일(qml/main.qml)이 리팩터링 완료됨
When QML 소스 코드를 검사함
Then bytes에서 GB로의 변환 로직이 QML에 존재하지 않음
And 퍼센트 포맷팅 로직이 QML에 존재하지 않음
And 숫자 반올림 또는 소수점 처리 로직이 QML에 존재하지 않음
And 모든 데이터 표시는 ViewModel의 Q_PROPERTY를 직접 바인딩하여 사용함
And ViewModel의 cpuUsage property가 이미 포맷된 문자열 (예: "45.2%")을 반환함
And ViewModel의 memoryUsage property가 이미 포맷된 문자열 (예: "8.2 / 16.0 GB")을 반환함
```

---

### Scenario 4: Model이 독립적으로 동작 (외부 의존 없음)

**관련 요구사항**: REQ-M01, REQ-M04

```gherkin
Given MonitorModel 클래스가 리팩터링 완료됨
When MonitorModel을 단독으로 인스턴스화함 (ViewModel, Controller 없이)
Then 인스턴스 생성이 오류 없이 완료됨
And model.measure() 호출이 오류 없이 실행됨
And model.cpu property에 유효한 float 값이 반환됨
And model.memory property에 유효한 dict 값이 반환됨
And model.gpu property에 유효한 list 값이 반환됨
And model.fps property에 유효한 float 값이 반환됨
And MonitorModel 소스 코드에 Controller 또는 ViewModel import가 존재하지 않음
```

---

### Scenario 5: 기존 기능 보존 (CPU, Memory, GPU, FPS 모니터링)

**관련 요구사항**: REQ-M02, REQ-M03, REQ-VM01

```gherkin
Given 전체 리팩터링이 완료됨
When 애플리케이션을 실행하고 모니터링을 시작함
Then CPU 사용률이 0-100 범위의 값으로 표시됨
And CPU 값이 타이머 주기마다 갱신됨
And 메모리 사용량이 "사용량 / 전체" GB 형태로 표시됨
And 메모리 값이 타이머 주기마다 갱신됨
And GPU 정보가 정상적으로 표시됨 (GPU가 있는 경우)
And FPS 값이 양수로 표시됨
And FPS 값이 타이머 주기마다 갱신됨
```

---

### Scenario 6: 모니터링 시작/중지 동작

**관련 요구사항**: REQ-VM04, REQ-M02

```gherkin
Given 애플리케이션이 시작됨
When 사용자가 모니터링 시작 버튼을 클릭함
Then ViewModel의 startMonitoring() slot이 호출됨
And Model의 isMonitoring property가 True로 변경됨
And 타이머가 활성화되어 주기적으로 데이터가 수집됨

When 사용자가 모니터링 중지 버튼을 클릭함
Then ViewModel의 stopMonitoring() slot이 호출됨
And Model의 isMonitoring property가 False로 변경됨
And 타이머가 비활성화되어 데이터 수집이 중단됨
```

---

### Scenario 7: 시그널 체인 3단계 이하 확인

**관련 요구사항**: REQ-S01

```gherkin
Given 리팩터링이 완료됨
When 타이머가 트리거되어 데이터 갱신이 발생함
Then 시그널 전파 경로가 다음과 같음:
  | 단계 | 동작 |
  | 1 | Timer가 Model.measure() 호출 |
  | 2 | Model이 Q_PROPERTY 값 갱신 후 NOTIFY 시그널 발생 |
  | 3 | QML이 property 변경을 감지하여 UI 자동 갱신 |
And 중간에 Controller를 거치는 경로가 존재하지 않음
And ViewModel의 updateUI 시그널이 사용되지 않음
```

---

### Scenario 8: 의존성 방향 검증

**관련 요구사항**: REQ-M04, REQ-VM02

```gherkin
Given 전체 리팩터링이 완료됨
When 각 레이어의 import 문을 검사함
Then Model(models/monitor_model.py)의 import에 ViewModel 또는 Controller 참조가 없음
And Model은 오직 monitor_base.py와 utils/*.py의 모니터 클래스만 import함
And ViewModel(views/monitor_viewmodel.py)의 import에 Controller 참조가 없음
And ViewModel은 오직 Model만 import함
And QML(qml/main.qml)은 ViewModel의 property만 참조함
And 의존성 방향이 View -> ViewModel -> Model -> Monitors 단방향임
```

## 2. Quality Gate 기준

### 코드 품질

| 항목 | 기준 |
|------|------|
| Controller 참조 | 프로젝트 전체에서 0건 |
| QML 내 데이터 변환 코드 | 0건 |
| updateUI 시그널 사용 | 0건 |
| setProperty() 명령형 호출 | 0건 |
| 미사용 import | 0건 |
| Q_PROPERTY 정의 (Model) | cpu, memory, gpu, fps, isMonitoring (5개) |
| Q_PROPERTY 정의 (ViewModel) | cpuUsage, memoryUsage, gpuUsage, fpsDisplay (4개) |

### 아키텍처 품질

| 항목 | 기준 |
|------|------|
| 시그널 체인 단계 수 | 3 이하 |
| 의존성 방향 위반 | 0건 |
| Controller 레이어 잔존 | 0건 (디렉토리 삭제) |
| 데드 코드 | 0건 (system_monitor.py 삭제) |

### 기능 보존

| 항목 | 기준 |
|------|------|
| CPU 모니터링 | 정상 동작 |
| Memory 모니터링 | 정상 동작 |
| GPU 모니터링 | 정상 동작 |
| FPS 모니터링 | 정상 동작 |
| 모니터링 시작/중지 | 정상 동작 |
| UI 레이아웃 | 기존과 동일 |

## 3. 검증 방법

### 3.1 수동 검증

1. **시각적 검증**: 앱 실행 후 모든 모니터링 데이터가 정상 표시되는지 확인
2. **기능 검증**: 시작/중지 버튼 동작 확인
3. **갱신 검증**: 데이터가 주기적으로 갱신되는지 확인

### 3.2 코드 검증

1. **Grep 검사**: 프로젝트 전체에서 `controller`, `Controller`, `updateUI`, `setProperty` 검색하여 잔존 참조 확인
2. **Import 검사**: 각 레이어의 import문에서 의존성 방향 위반 확인
3. **QML 검사**: QML 파일에서 JavaScript 데이터 변환 코드 부재 확인

### 3.3 아키텍처 검증

1. **파일 구조 확인**: `controllers/` 디렉토리와 `system_monitor.py` 삭제 확인
2. **시그널 추적**: 타이머부터 QML 갱신까지의 시그널 경로 추적
3. **Q_PROPERTY 확인**: Model과 ViewModel의 Q_PROPERTY 선언 확인

## 4. Definition of Done

다음 조건이 **모두** 충족될 때 리팩터링 완료:

- [ ] Model이 모든 모니터 인스턴스를 직접 소유
- [ ] Model에 5개 Q_PROPERTY 정의 (cpu, memory, gpu, fps, isMonitoring)
- [ ] ViewModel에 4개 Q_PROPERTY 정의 (cpuUsage, memoryUsage, gpuUsage, fpsDisplay)
- [ ] ViewModel이 Controller 미의존
- [ ] QML이 선언적 property 바인딩만 사용
- [ ] QML에 데이터 변환 로직 없음
- [ ] main.py에서 Controller 생성/참조 없음
- [ ] 타이머가 Model.measure() 직접 호출
- [ ] controllers/ 디렉토리 삭제 완료
- [ ] system_monitor.py 삭제 완료
- [ ] 시그널 체인 3단계 이하
- [ ] 모든 기존 기능(CPU, Memory, GPU, FPS) 정상 동작
- [ ] 모니터링 시작/중지 정상 동작
- [ ] UI 레이아웃 기존과 동일
