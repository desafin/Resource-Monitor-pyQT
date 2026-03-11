---
id: SPEC-UI-001
version: 1.0.0
status: draft
created: 2026-03-11
updated: 2026-03-11
author: oscar
priority: high
tags: [process-manager, ui-redesign, linux, pyqt5, qml]
lifecycle: spec-anchored
---

# SPEC-UI-001: Linux Process Manager - 전체 기능 확장

## 1. 개요

Resource Monitor PyQT를 단순 시스템 모니터에서 본격적인 **Linux 프로세스 관리자**로 확장한다.
Windows 지원을 제거하고 Linux 전용으로 개발하며, 프로세스 관리 기능, 탭 기반 UI, 실시간 그래프,
다크/라이트 테마를 포함하는 3단계 구현을 정의한다.

---

## 2. 환경 (Environment)

| 항목 | 값 |
|---|---|
| 대상 플랫폼 | Linux (Ubuntu 20.04+, Fedora 38+, Arch Linux) |
| Python 버전 | 3.10 이상 |
| GUI 프레임워크 | PyQt5 5.15.x + QML (Qt Quick 2.15) |
| 시스템 데이터 | psutil 6.1.0 |
| GPU 모니터링 | nvidia-smi CLI 또는 GPUtil 1.4.0 (선택적) |
| 아키텍처 패턴 | MVVM (Model-View-ViewModel) |
| 테스트 프레임워크 | pytest + pytest-qt |

---

## 3. 가정 (Assumptions)

- A1: 사용자는 Linux 데스크탑 환경(X11 또는 Wayland)에서 실행한다.
- A2: psutil이 /proc 파일시스템을 통해 프로세스 정보에 접근할 수 있다.
- A3: 프로세스 제어(kill, nice 변경 등)를 위해 적절한 사용자 권한이 필요하다 (root 또는 해당 프로세스 소유자).
- A4: NVIDIA GPU가 없는 환경에서는 GPU 탭이 비활성화되거나 "N/A"를 표시한다.
- A5: QML TabBar 컴포넌트가 PyQt5 5.15의 QtQuick.Controls 2.15에서 안정적으로 동작한다.
- A6: 프로세스 열거(psutil.process_iter)가 수백~수천 개의 프로세스를 다루므로 메인 스레드에서 실행하면 UI가 멈출 수 있다.

---

## 4. 요구사항 (Requirements)

### 4.1 프로세스 관리 (Process Management)

**REQ-PM-001: 프로세스 목록 표시** (Ubiquitous)
시스템은 **항상** 실행 중인 모든 프로세스의 목록을 테이블 형태로 표시해야 한다.
- 표시 컬럼: PID, Name, User, CPU%, MEM%, Status, Threads
- psutil.process_iter()를 사용하여 프로세스 정보를 수집한다.

**REQ-PM-002: 프로세스 자동 갱신** (Event-Driven)
**WHEN** 설정된 갱신 간격(기본 2초)이 경과하면 **THEN** 시스템은 프로세스 목록을 자동으로 갱신해야 한다.

**REQ-PM-003: 프로세스 정렬** (Event-Driven)
**WHEN** 사용자가 테이블 헤더 컬럼을 클릭하면 **THEN** 해당 컬럼 기준으로 오름차순/내림차순 정렬을 전환해야 한다.

**REQ-PM-004: 프로세스 검색 및 필터** (Event-Driven)
**WHEN** 사용자가 검색바에 텍스트를 입력하면 **THEN** 프로세스 이름, PID, 사용자명 중 일치하는 항목만 필터링하여 표시해야 한다.

**REQ-PM-005: 프로세스 종료 (SIGTERM)** (Event-Driven)
**WHEN** 사용자가 프로세스를 선택하고 "Terminate" 액션을 실행하면 **THEN** 해당 프로세스에 SIGTERM 시그널을 전송해야 한다.

**REQ-PM-006: 프로세스 강제 종료 (SIGKILL)** (Event-Driven)
**WHEN** 사용자가 프로세스를 선택하고 "Kill" 액션을 실행하면 **THEN** 해당 프로세스에 SIGKILL 시그널을 전송해야 한다.

**REQ-PM-007: 프로세스 일시 중지 (SIGSTOP)** (Event-Driven)
**WHEN** 사용자가 프로세스를 선택하고 "Suspend" 액션을 실행하면 **THEN** 해당 프로세스에 SIGSTOP 시그널을 전송해야 한다.

**REQ-PM-008: 프로세스 재개 (SIGCONT)** (Event-Driven)
**WHEN** 사용자가 일시 중지된 프로세스를 선택하고 "Resume" 액션을 실행하면 **THEN** 해당 프로세스에 SIGCONT 시그널을 전송해야 한다.

**REQ-PM-009: 프로세스 우선순위 변경** (Event-Driven)
**WHEN** 사용자가 프로세스를 선택하고 nice 값을 변경하면 **THEN** os.setpriority() 또는 psutil.Process.nice()를 통해 해당 프로세스의 우선순위를 변경해야 한다.

**REQ-PM-010: 우클릭 컨텍스트 메뉴** (Event-Driven)
**WHEN** 사용자가 프로세스 행을 우클릭하면 **THEN** Terminate, Kill, Suspend, Resume, Change Priority, Details 옵션이 포함된 컨텍스트 메뉴를 표시해야 한다.

**REQ-PM-011: 권한 오류 처리** (Unwanted)
시스템은 프로세스 제어 작업 실패 시 예외를 무시하지 **않아야 한다**. 사용자에게 권한 부족 등의 오류 메시지를 명확히 표시해야 한다.

### 4.2 UI 아키텍처 (UI Architecture)

**REQ-UI-001: 탭 기반 네비게이션** (Ubiquitous)
시스템은 **항상** TabBar 기반 네비게이션을 제공하여 System, Processes, Disk, Network 탭 간 전환이 가능해야 한다.

**REQ-UI-002: 기본 윈도우 크기 확대** (Ubiquitous)
시스템은 **항상** 기본 윈도우 크기를 1280x800으로 설정해야 한다.

**REQ-UI-003: 하단 상태바** (Ubiquitous)
시스템은 **항상** 하단 상태바에 CPU 사용률과 메모리 사용률 요약을 표시해야 한다.

**REQ-UI-004: 반응형 레이아웃** (State-Driven)
**IF** 윈도우 크기가 변경되면 **THEN** 각 탭의 레이아웃이 가용 공간에 맞게 적응해야 한다.

### 4.3 System Overview 탭

**REQ-SO-001: 기존 모니터링 이동** (Ubiquitous)
시스템은 **항상** System 탭에서 CPU 사용률, 메모리 사용량, GPU 사용률, FPS를 표시해야 한다. (기존 기능을 System 탭으로 이동)

**REQ-SO-002: 실시간 그래프** (Optional)
**가능하면** CPU와 메모리 사용률을 시계열 실시간 그래프(최근 60초)로 시각화하여 제공한다.

### 4.4 디스크 모니터링 탭

**REQ-DK-001: 디스크 사용량 표시** (Ubiquitous)
시스템은 **항상** Disk 탭에서 각 마운트 포인트의 전체 용량, 사용량, 남은 용량, 사용률(%)을 표시해야 한다.
- psutil.disk_partitions() + psutil.disk_usage()를 사용한다.

**REQ-DK-002: 디스크 I/O 카운터** (Ubiquitous)
시스템은 **항상** Disk 탭에서 읽기/쓰기 바이트 수 및 I/O 횟수를 표시해야 한다.
- psutil.disk_io_counters()를 사용한다.

### 4.5 네트워크 모니터링 탭

**REQ-NW-001: 네트워크 트래픽 표시** (Ubiquitous)
시스템은 **항상** Network 탭에서 인터페이스별 송신/수신 바이트, 패킷 수를 표시해야 한다.
- psutil.net_io_counters(pernic=True)를 사용한다.

**REQ-NW-002: 네트워크 속도 표시** (Event-Driven)
**WHEN** 갱신 주기마다 **THEN** 이전 측정값과의 차이를 계산하여 초당 송수신 속도(bytes/s)를 표시해야 한다.

### 4.6 테마 및 설정

**REQ-TH-001: 다크/라이트 테마** (Event-Driven)
**WHEN** 사용자가 테마 전환 버튼을 클릭하면 **THEN** 다크 테마와 라이트 테마가 전환되어야 한다.

**REQ-TH-002: 설정 영속화** (Event-Driven)
**WHEN** 사용자가 설정(테마, 윈도우 크기, 갱신 간격)을 변경하면 **THEN** QSettings 또는 JSON 파일로 저장하여 다음 실행 시 복원해야 한다.

### 4.7 프로세스 상세 다이얼로그

**REQ-PD-001: 프로세스 상세 정보** (Event-Driven)
**WHEN** 사용자가 프로세스를 더블클릭하거나 컨텍스트 메뉴에서 "Details"를 선택하면 **THEN** 다이얼로그를 표시하여 다음 정보를 보여줘야 한다:
- 명령줄(cmdline), 열린 파일(open_files), 네트워크 연결(connections), 환경 변수(environ)

### 4.8 스레딩 (Threading)

**REQ-TH-001: 백그라운드 프로세스 열거** (Ubiquitous)
시스템은 **항상** 프로세스 열거 작업을 QThread를 사용한 별도 워커 스레드에서 실행해야 한다.
- UI 스레드 블로킹을 방지한다.
- 시그널/슬롯을 통해 메인 스레드로 결과를 전달한다.

**REQ-TH-002: 스레드 안전성** (Unwanted)
시스템은 워커 스레드에서 직접 UI 요소를 갱신하지 **않아야 한다**. 반드시 시그널을 통해 메인 스레드에서 처리해야 한다.

### 4.9 Linux 전용 요구사항

**REQ-LX-001: Linux 시그널 지원** (Ubiquitous)
시스템은 **항상** os.kill()을 통한 POSIX 시그널(SIGTERM, SIGKILL, SIGSTOP, SIGCONT) 전송을 지원해야 한다.

**REQ-LX-002: /proc 파일시스템 활용** (Optional)
**가능하면** psutil이 제공하지 않는 추가 프로세스 정보를 /proc/{pid}/ 파일시스템에서 직접 읽어 보완한다.

**REQ-LX-003: Windows 코드 제거** (Ubiquitous)
시스템은 **항상** Windows 전용 코드 경로나 호환성 분기를 포함하지 않아야 한다.

---

## 5. 명세 (Specifications)

### 5.1 MVVM 계층 구조

```
View (QML)                    ViewModel (Python)              Model (Python)
---------------------------   ---------------------------     ---------------------------
qml/main.qml (TabBar)        views/process_viewmodel.py      models/process_model.py
qml/tabs/system_tab.qml      views/disk_viewmodel.py         models/disk_model.py
qml/tabs/processes_tab.qml   views/network_viewmodel.py      models/network_model.py
qml/tabs/disk_tab.qml        views/monitor_viewmodel.py      models/monitor_model.py (기존)
qml/tabs/network_tab.qml
qml/components/*.qml

Utils / Services
---------------------------
utils/process_monitor.py      - psutil 기반 프로세스 데이터 수집
utils/disk_monitor.py         - psutil 기반 디스크 데이터 수집
utils/network_monitor.py      - psutil 기반 네트워크 데이터 수집
services/worker_thread.py     - QThread 기반 백그라운드 워커
```

### 5.2 새로 생성할 파일 목록

| 파일 경로 | 설명 | 예상 줄 수 |
|---|---|---|
| models/process_model.py | 프로세스 데이터 모델 (QAbstractListModel) | ~280 |
| models/disk_model.py | 디스크 사용량/IO 데이터 모델 | ~150 |
| models/network_model.py | 네트워크 트래픽 데이터 모델 | ~100 |
| views/process_viewmodel.py | 프로세스 탭 ViewModel | ~220 |
| views/disk_viewmodel.py | 디스크 탭 ViewModel | ~120 |
| views/network_viewmodel.py | 네트워크 탭 ViewModel | ~100 |
| utils/process_monitor.py | 프로세스 열거 + 제어 유틸리티 | ~150 |
| utils/disk_monitor.py | 디스크 모니터링 유틸리티 | ~100 |
| utils/network_monitor.py | 네트워크 모니터링 유틸리티 | ~80 |
| services/worker_thread.py | QThread 워커 (프로세스 열거용) | ~60 |
| qml/main.qml | TabBar 추가 리팩터링 | 리팩터 |
| qml/tabs/system_overview_tab.qml | System 탭 (기존 기능 이동) | ~120 |
| qml/tabs/processes_tab.qml | 프로세스 테이블 + 검색바 | ~250 |
| qml/tabs/disk_tab.qml | 디스크 정보 탭 | ~100 |
| qml/tabs/network_tab.qml | 네트워크 정보 탭 | ~100 |
| qml/components/ProcessContextMenu.qml | 우클릭 메뉴 | ~50 |
| qml/components/PriorityDialog.qml | nice 값 변경 다이얼로그 | ~60 |
| qml/components/ProcessDetailsDialog.qml | 프로세스 상세 팝업 | ~100 |
| qml/components/SearchBar.qml | 검색/필터 바 | ~40 |

### 5.3 수정할 기존 파일

| 파일 경로 | 변경 내용 |
|---|---|
| main.py | 새 모델/ViewModel 등록, QThread 초기화, QML context property 추가 |
| models/__init__.py | 새 모델 클래스 export 추가 |
| views/__init__.py | 새 ViewModel 클래스 export 추가 |
| utils/__init__.py | 새 모니터 클래스 export 추가 |
| requirements.txt | pytest, pytest-qt 추가 |

### 5.4 ProcessModel 핵심 설계

- QAbstractListModel을 상속하여 QML ListView/TableView와 네이티브 바인딩
- 역할(Role) 정의: PidRole, NameRole, UserRole, CpuRole, MemRole, StatusRole, ThreadsRole
- 정렬: sort() 오버라이드 또는 QSortFilterProxyModel 활용
- 필터: QSortFilterProxyModel.filterAcceptsRow() 오버라이드

### 5.5 WorkerThread 설계

```python
class ProcessWorker(QObject):
    finished = pyqtSignal(list)  # 프로세스 데이터 리스트
    error = pyqtSignal(str)

    @pyqtSlot()
    def enumerate_processes(self):
        # psutil.process_iter()로 프로세스 수집
        # finished.emit(process_list)
```

- QThread에 moveToThread()로 워커를 이동
- 타이머 시그널 -> enumerate_processes 슬롯 연결
- finished 시그널 -> ProcessModel.update_data() 연결

### 5.6 의존성 추가

```
# requirements.txt 추가 항목
pytest>=8.0.0
pytest-qt>=4.4.0
```

---

## 6. 추적성 (Traceability)

| TAG | 설명 | 관련 요구사항 |
|---|---|---|
| SPEC-UI-001-PM | 프로세스 관리 | REQ-PM-001 ~ REQ-PM-011 |
| SPEC-UI-001-UI | UI 아키텍처 | REQ-UI-001 ~ REQ-UI-004 |
| SPEC-UI-001-SO | System Overview 탭 | REQ-SO-001 ~ REQ-SO-002 |
| SPEC-UI-001-DK | 디스크 모니터링 | REQ-DK-001 ~ REQ-DK-002 |
| SPEC-UI-001-NW | 네트워크 모니터링 | REQ-NW-001 ~ REQ-NW-002 |
| SPEC-UI-001-TH | 테마 및 설정 | REQ-TH-001 ~ REQ-TH-002 |
| SPEC-UI-001-PD | 프로세스 상세 | REQ-PD-001 |
| SPEC-UI-001-TD | 스레딩 | REQ-TH-001 ~ REQ-TH-002 |
| SPEC-UI-001-LX | Linux 전용 | REQ-LX-001 ~ REQ-LX-003 |
