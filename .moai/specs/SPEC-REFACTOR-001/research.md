# SPEC-REFACTOR-001 Deep Research: MVVM 패턴 리팩터링

## 핵심 발견 사항

### 1. 아키텍처 문제: MVC와 MVVM 혼재

현재 코드는 MVVM 아키텍처를 표방하지만, 실제로는 MVC의 Controller와 MVVM의 ViewModel이 동시에 존재하는 혼합 구조입니다.

**MVVM에서 Controller는 존재하지 않아야 합니다.** Controller의 역할은 Model과 ViewModel이 분담해야 합니다.

### 2. 계층별 위반 사항

#### Model (models/monitor_model.py)
- **치명적**: Model이 Controller에 의존 (생성자에서 controller를 받음)
- Model은 순수 데이터 저장소로만 동작하며, 비즈니스 로직이 없음
- Q_PROPERTY가 정의되어 있지 않아 QML 바인딩 불가
- 모니터 인스턴스를 소유하지 않음 (Controller가 소유)

#### Controller (controllers/monitor_controller.py)
- **치명적**: MVVM에 Controller가 존재함
- 모든 모니터 인스턴스를 소유 (Model에 있어야 함)
- measure_all() 비즈니스 로직 수행 (Model에 있어야 함)
- _is_monitoring 상태 관리 (Model에 있어야 함)

#### ViewModel (views/monitor_viewmodel.py)
- Q_PROPERTY를 노출하지 않음 → QML 선언적 바인딩 불가
- updateUI 시그널로 명령형 데이터 전달 (MVVM 안티패턴)
- Controller에 단순 위임만 수행
- 데이터 포맷팅 없음 (QML에서 직접 변환 중)

#### View (qml/main.qml)
- 정적 ListModel 생성 (데이터 중복)
- onUpdateUI에서 수동 setProperty() 호출 (명령형)
- 바이트→GB 변환 등 데이터 포맷팅을 View에서 수행
- 선언적 바인딩 대신 시그널 리스닝 사용

#### 기타
- system_monitor.py: 미사용 데드 코드
- main.py: 타이머가 Controller를 직접 호출 (ViewModel/Model을 통해야 함)

### 3. 시그널 체인 분석

**현재 (8단계):**
```
Timer → controller.measure_all() → controller.dataChanged →
model._update_data → model.dataChanged → viewmodel._on_data_changed →
viewmodel.updateUI → QML onUpdateUI → setProperty() → ListView 갱신
```

**이상적 (3단계):**
```
Timer → model.measure() → Q_PROPERTY NOTIFY → QML 자동 바인딩 갱신
```

### 4. 의존성 방향 문제

**현재 (잘못됨):**
- Model → Controller (역방향 의존)
- ViewModel → Model + Controller (이중 의존)

**이상적:**
- View → ViewModel → Model (단방향)

### 5. 리팩터링 방향

1. Controller 제거 → 비즈니스 로직을 Model로 이동
2. Model에 모니터 인스턴스 소유 + Q_PROPERTY 정의
3. ViewModel에 포맷팅된 Q_PROPERTY 노출
4. QML에서 선언적 바인딩 사용
5. system_monitor.py 제거 (데드 코드)
6. main.py 단순화 (Model + ViewModel만 생성)
