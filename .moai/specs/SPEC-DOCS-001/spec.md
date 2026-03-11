---
id: SPEC-DOCS-001
version: "1.0.0"
status: draft
created: "2026-03-11"
updated: "2026-03-11"
author: oscar
priority: medium
---

# SPEC-DOCS-001: 프로젝트 아키텍처 문서화 (Mermaid 다이어그램)

## HISTORY

| 버전  | 날짜       | 작성자 | 변경 내용        |
| ----- | ---------- | ------ | ---------------- |
| 1.0.0 | 2026-03-11 | oscar  | 초기 SPEC 작성   |

---

## 1. Environment (환경)

### 1.1 프로젝트 개요

- **프로젝트명**: Resource Monitor PyQT
- **기술 스택**: Python 3.7+, PyQt5 5.15.11, QML, psutil 6.1.0, GPUtil 1.4.0 (optional)
- **아키텍처 패턴**: MVVM (Model-View-ViewModel)
- **대상 플랫폼**: Linux 데스크톱 (Ubuntu 등)

### 1.2 현재 문서화 상태

- 프로젝트 루트에 README.md만 존재
- 아키텍처 문서 부재
- 코드 내 구조 파악을 위한 시각적 자료 없음

### 1.3 대상 독자

- 프로젝트 신규 기여자
- 코드 리뷰어
- 유지보수 담당자

---

## 2. Assumptions (가정)

- A1: GitHub Markdown 렌더러가 Mermaid 다이어그램을 지원한다
- A2: 현재 코드베이스의 MVVM 구조가 안정적이며 문서화 시점에 큰 변경이 없다
- A3: 모든 다이어그램은 영문 기술 용어와 한국어 설명을 혼합하여 작성한다
- A4: `docs/` 디렉토리가 프로젝트 루트에 존재하지 않으며 새로 생성한다

---

## 3. Requirements (요구사항)

### REQ-DOCS-001: 아키텍처 문서 파일 생성 (Ubiquitous)

시스템은 **항상** 프로젝트 루트의 `docs/architecture.md` 파일에 전체 아키텍처를 Mermaid 다이어그램으로 문서화해야 한다.

- 문서는 프로젝트 개요, 기술 스택, 디자인 패턴 요약을 포함한다
- 모든 Mermaid 다이어그램은 GitHub Markdown에서 정상 렌더링되어야 한다

### REQ-DOCS-002: MVVM 레이어 구조 다이어그램 (Event-Driven)

**WHEN** 사용자가 `docs/architecture.md`를 열람할 때 **THEN** MVVM 레이어 구조가 Mermaid 클래스 다이어그램으로 표현되어야 한다.

- Model 레이어: MonitorModel, ProcessModel, ProcessSortFilterModel, DiskModel, NetworkModel, HardwareModel
- ViewModel 레이어: MonitorViewModel, ProcessViewModel, DiskViewModel, NetworkViewModel, HardwareViewModel
- View 레이어: QML 탭 컴포넌트 (SystemOverviewTab, ProcessesTab, DiskTab, NetworkTab, HardwareTab)
- 각 레이어 간의 의존 관계를 화살표로 표시한다

### REQ-DOCS-003: 데이터 흐름 시퀀스 다이어그램 (Event-Driven)

**WHEN** 사용자가 데이터 흐름을 이해하려 할 때 **THEN** Mermaid 시퀀스 다이어그램으로 데이터 수집부터 UI 갱신까지의 흐름이 표현되어야 한다.

- Timer/Worker -> Monitor Utility -> Model -> ViewModel -> QML View 순서
- 각 도메인(System, Process, Disk, Network, Hardware)별 데이터 흐름을 포함한다
- Signal/Slot 연결 관계를 명시한다

### REQ-DOCS-004: QML 컴포넌트 계층 구조 다이어그램 (Event-Driven)

**WHEN** 사용자가 UI 구조를 파악하려 할 때 **THEN** QML 컴포넌트 계층이 Mermaid 다이어그램으로 표현되어야 한다.

- main.qml (TabBar + StackLayout)을 루트로 하는 트리 구조
- 5개 탭: SystemOverviewTab, ProcessesTab, DiskTab, NetworkTab, HardwareTab
- 공통 컴포넌트: SearchBar, ProcessContextMenu, ProcessDetailsDialog, PriorityDialog, SettingsDialog, PingSection

### REQ-DOCS-005: 스레딩 모델 다이어그램 (State-Driven)

**IF** 애플리케이션이 멀티스레드 환경에서 동작 중이면 **THEN** 스레딩 모델이 Mermaid 다이어그램으로 표현되어야 한다.

- Main Thread: UI 렌더링, Model 업데이트, Timer 관리
- Worker Threads: ProcessWorker (2초 간격), PingWorker (비동기 ping)
- moveToThread 패턴 및 Signal/Slot 기반 스레드 간 통신
- 각 도메인별 타이머 주기: System(1-10초), Process(2초), Disk(5초), Network(2초), Hardware(3초)

---

## 4. Specifications (세부 사양)

### 4.1 출력 파일

| 파일 경로              | 설명                                      |
| ---------------------- | ----------------------------------------- |
| `docs/architecture.md` | 전체 아키텍처 문서 (Mermaid 다이어그램 포함) |

### 4.2 Mermaid 다이어그램 유형

| 다이어그램              | Mermaid 유형        | 용도                          |
| ----------------------- | ------------------- | ----------------------------- |
| 프로젝트 구조 개요      | `graph TD`          | 전체 레이어 및 모듈 관계      |
| MVVM 레이어 구조        | `classDiagram`      | 클래스/모듈 간 관계           |
| 데이터 흐름             | `sequenceDiagram`   | 데이터 수집-갱신 흐름         |
| QML 컴포넌트 계층       | `graph LR`          | UI 컴포넌트 트리              |
| 스레딩 모델             | `graph TD`          | 스레드 구조 및 통신           |
| 모듈 의존성             | `graph LR`          | utils/ 모듈 간 의존 관계      |

### 4.3 문서 구조

```
docs/architecture.md
├── 1. 프로젝트 개요
│   ├── 기술 스택
│   └── 디자인 패턴
├── 2. 아키텍처 개요 (graph TD)
├── 3. MVVM 레이어 구조 (classDiagram)
├── 4. 데이터 흐름 (sequenceDiagram)
├── 5. QML 컴포넌트 계층 (graph LR)
├── 6. 스레딩 모델 (graph TD)
└── 7. 모듈 의존성 (graph LR)
```

### 4.4 제약 조건

- 시스템은 Mermaid 다이어그램에 **비표준 확장 구문을 사용하지 않아야 한다**
- 시스템은 GitHub Markdown 렌더러에서 지원하지 않는 Mermaid 기능을 **사용하지 않아야 한다**
- 모든 다이어그램 노드 텍스트는 영문 기술 용어를 사용한다
- 설명 텍스트 및 섹션 제목은 한국어로 작성한다

---

## 5. Traceability (추적성)

| 요구사항 ID   | 관련 파일                | 검증 방법                     |
| ------------- | ------------------------ | ----------------------------- |
| REQ-DOCS-001  | docs/architecture.md     | 파일 존재 및 내용 확인        |
| REQ-DOCS-002  | docs/architecture.md     | classDiagram 섹션 확인        |
| REQ-DOCS-003  | docs/architecture.md     | sequenceDiagram 섹션 확인     |
| REQ-DOCS-004  | docs/architecture.md     | graph LR 컴포넌트 트리 확인   |
| REQ-DOCS-005  | docs/architecture.md     | 스레딩 모델 다이어그램 확인   |
