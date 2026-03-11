---
id: SPEC-DOCS-001
type: plan
version: "1.0.0"
status: draft
created: "2026-03-11"
updated: "2026-03-11"
---

# SPEC-DOCS-001 구현 계획: 프로젝트 아키텍처 문서화

## 1. 마일스톤

### Primary Goal: 기본 문서 구조 및 아키텍처 개요

- `docs/` 디렉토리 생성
- `docs/architecture.md` 파일 생성
- 프로젝트 개요 섹션 작성 (기술 스택, 디자인 패턴 요약)
- 전체 아키텍처 개요 Mermaid `graph TD` 다이어그램 작성
  - Entry Point (main.py) -> Models / ViewModels / Services / Utils / QML 레이어 관계

### Secondary Goal: MVVM 레이어 및 데이터 흐름 다이어그램

- MVVM 레이어 구조 Mermaid `classDiagram` 작성
  - Model 클래스: MonitorModel, ProcessModel, ProcessSortFilterModel, DiskModel, NetworkModel, HardwareModel
  - ViewModel 클래스: MonitorViewModel, ProcessViewModel, DiskViewModel, NetworkViewModel, HardwareViewModel
  - View (QML): 5개 탭 컴포넌트
  - 클래스 간 관계 (의존, 상속, 구성)
- 데이터 흐름 Mermaid `sequenceDiagram` 작성
  - Timer -> Utility Monitor -> Model 업데이트 -> ViewModel 가공 -> QML 렌더링
  - Signal/Slot 연결 표현

### Final Goal: UI 구조, 스레딩, 모듈 의존성 다이어그램

- QML 컴포넌트 계층 Mermaid `graph LR` 작성
  - main.qml (TabBar + StackLayout) 루트
  - tabs/: 5개 탭 컴포넌트
  - components/: SearchBar, ProcessContextMenu, ProcessDetailsDialog, PriorityDialog, SettingsDialog, PingSection
- 스레딩 모델 Mermaid `graph TD` 작성
  - Main Thread (UI + Models + Timers)
  - ProcessWorker Thread (2초 간격)
  - PingWorker Thread (비동기)
  - moveToThread 패턴 표현
  - 타이머 주기 표기
- 모듈 의존성 Mermaid `graph LR` 작성
  - utils/ 모듈 간 의존 관계
  - services/ -> utils/ 관계
  - views/ -> models/ 관계

### Optional Goal: 문서 보완

- 각 다이어그램에 한국어 설명 텍스트 추가
- 디자인 패턴 상세 설명 (MVVM, Observer, Template Method, Graceful Degradation)
- 향후 확장 가이드 섹션

---

## 2. 기술적 접근

### 2.1 Mermaid 다이어그램 전략

| 다이어그램 유형      | Mermaid 구문         | 적합한 표현 대상                    |
| -------------------- | -------------------- | ----------------------------------- |
| 아키텍처 개요        | `graph TD`           | 레이어 간 상하 관계 (Top-Down)      |
| MVVM 클래스 구조     | `classDiagram`       | 클래스 속성/메서드 및 관계          |
| 데이터 흐름          | `sequenceDiagram`    | 시간 순서 기반 메시지 전달          |
| QML 컴포넌트 계층    | `graph LR`           | 좌우 트리 구조 (Left-Right)         |
| 스레딩 모델          | `graph TD`           | 스레드 분리 및 통신 경로            |
| 모듈 의존성          | `graph LR`           | 모듈 간 참조 관계                   |

### 2.2 다이어그램 작성 원칙

- 노드 이름은 영문 기술 용어 사용 (예: `MonitorModel`, `ProcessWorker`)
- 엣지 라벨은 관계 유형 표시 (예: `Signal/Slot`, `imports`, `creates`)
- 서브그래프(subgraph)로 레이어/스레드 경계를 시각적으로 구분
- GitHub Markdown 호환성을 위해 표준 Mermaid 구문만 사용

### 2.3 코드베이스 분석 범위

실제 코드를 분석하여 다이어그램의 정확성을 보장:

- `main.py`: 진입점, ViewModel 생성, QML 컨텍스트 등록, 타이머 시작
- `models/`: QObject/QAbstractListModel 기반 데이터 모델
- `views/`: ViewModel 계층 (프레젠테이션 로직, 포매팅, 타이머)
- `services/`: 백그라운드 워커 스레드 (ProcessWorker, PingWorker)
- `utils/`: 데이터 수집 유틸리티 모듈
- `qml/`: Qt Quick UI (main.qml, tabs/, components/)

---

## 3. 아키텍처 설계 방향

### 3.1 문서 구조 설계

```
docs/
└── architecture.md    # 단일 파일에 모든 아키텍처 다이어그램 포함
```

단일 파일 접근 방식을 채택하는 이유:
- 프로젝트 규모가 중소형이므로 파일 분리 불필요
- GitHub에서 단일 파일 탐색이 용이
- 목차(TOC)로 섹션 간 빠른 이동 지원

### 3.2 다이어그램 상세 설계

**아키텍처 개요 (graph TD):**
- Entry Point -> Models, ViewModels, Services, Utils, QML 5개 레이어
- 각 레이어를 subgraph로 그룹화
- 레이어 간 의존 방향 표시

**MVVM 클래스 다이어그램 (classDiagram):**
- Model 클래스의 주요 속성과 시그널
- ViewModel 클래스의 주요 메서드와 프로퍼티
- Model <-> ViewModel 매핑 관계

**데이터 흐름 시퀀스 (sequenceDiagram):**
- 참여자: Timer, Utility, Model, ViewModel, QML
- 대표적 흐름 1개 (System Overview)를 상세히, 나머지는 요약

**QML 컴포넌트 트리 (graph LR):**
- main.qml을 루트로 TabBar와 StackLayout 분기
- 각 탭 아래 사용하는 컴포넌트 연결

**스레딩 모델 (graph TD):**
- Main Thread subgraph: UI, Models, Timers
- Worker Thread subgraph: ProcessWorker, PingWorker
- 스레드 간 Signal/Slot 통신선

---

## 4. 리스크 및 대응

| 리스크                                    | 영향도 | 대응 방안                                    |
| ----------------------------------------- | ------ | -------------------------------------------- |
| Mermaid 구문이 GitHub에서 렌더링 실패     | 높음   | 표준 구문만 사용, PR 미리보기에서 검증       |
| 다이어그램이 실제 코드와 불일치           | 중간   | 코드 분석 기반 작성, 수동 교차 검증          |
| 다이어그램이 과도하게 복잡해짐            | 중간   | 레이어별 분리, 핵심 관계만 표시              |
| 향후 코드 변경 시 문서 미갱신             | 낮음   | PR 리뷰 체크리스트에 문서 갱신 항목 추가     |

---

## 5. 추적성

| 요구사항      | 마일스톤        | 구현 대상 파일         |
| ------------- | --------------- | ---------------------- |
| REQ-DOCS-001  | Primary Goal    | docs/architecture.md   |
| REQ-DOCS-002  | Secondary Goal  | docs/architecture.md   |
| REQ-DOCS-003  | Secondary Goal  | docs/architecture.md   |
| REQ-DOCS-004  | Final Goal      | docs/architecture.md   |
| REQ-DOCS-005  | Final Goal      | docs/architecture.md   |
