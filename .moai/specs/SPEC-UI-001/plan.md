---
id: SPEC-UI-001
document: plan
version: 1.0.0
status: draft
created: 2026-03-11
updated: 2026-03-11
author: oscar
tags: [SPEC-UI-001-PM, SPEC-UI-001-UI, SPEC-UI-001-DK, SPEC-UI-001-NW, SPEC-UI-001-TD]
---

# SPEC-UI-001: 구현 계획 (Implementation Plan)

## 1. 구현 단계 개요

| 단계 | 설명 | 우선순위 | 의존성 |
|---|---|---|---|
| Phase 1 | 프로세스 관리 핵심 | Primary Goal | 없음 |
| Phase 2 | UI 개선 + 탭 구조 | Secondary Goal | Phase 1 완료 |
| Phase 3 | 고급 기능 | Final Goal | Phase 2 완료 |

---

## 2. Phase 1: 프로세스 관리 핵심 (Primary Goal)

### 마일스톤 1-A: 프로세스 데이터 수집 인프라

**목표**: 백그라운드 스레드에서 프로세스 목록을 안전하게 수집하는 기반 구축

| 작업 | 파일 | 설명 |
|---|---|---|
| 1-A-1 | `services/worker_thread.py` | QThread 기반 ProcessWorker 구현. QObject.moveToThread() 패턴 사용. finished(list) 시그널로 결과 전달 |
| 1-A-2 | `utils/process_monitor.py` | psutil.process_iter()로 프로세스 정보 수집. pid, name, username, cpu_percent, memory_percent, status, num_threads 포함. NoSuchProcess/AccessDenied 예외 처리 |
| 1-A-3 | `monitor_base.py` | 기존 ResourceMonitor ABC에 영향 없음. process_monitor는 독립적인 유틸리티로 구현 |

**기술적 접근**:
- ProcessWorker는 QObject를 상속하고, QThread에 moveToThread()로 이동
- psutil.process_iter(attrs=[...])로 필요한 속성만 선택적 조회 (성능 최적화)
- 프로세스당 cpu_percent()는 interval=None으로 호출하여 비블로킹 수집
- 첫 호출 시 cpu_percent가 0.0을 반환하는 문제는 두 번째 갱신부터 유효값 사용

### 마일스톤 1-B: 프로세스 데이터 모델

**목표**: QML과 네이티브 바인딩 가능한 프로세스 데이터 모델 구현

| 작업 | 파일 | 설명 |
|---|---|---|
| 1-B-1 | `models/process_model.py` | QAbstractListModel 상속. UserRole 정의(PidRole, NameRole, CpuRole, MemRole, StatusRole, UserRole, ThreadsRole). data(), rowCount(), roleNames() 구현 |
| 1-B-2 | `models/process_model.py` | QSortFilterProxyModel 상속 클래스 추가. filterAcceptsRow()로 검색 필터. lessThan()으로 컬럼별 정렬 |
| 1-B-3 | `models/__init__.py` | ProcessModel, ProcessSortFilterModel export 추가 |

**기술적 접근**:
- QAbstractListModel을 사용하여 QML TableView와의 직접 바인딩 지원
- beginResetModel()/endResetModel()로 전체 목록 갱신 (수백 개 프로세스에 효율적)
- QSortFilterProxyModel로 정렬/필터를 모델 레이어에서 처리

### 마일스톤 1-C: 프로세스 ViewModel 및 제어

**목표**: 프로세스 제어 기능(kill, terminate, suspend, resume, nice)과 QML 바인딩 ViewModel

| 작업 | 파일 | 설명 |
|---|---|---|
| 1-C-1 | `views/process_viewmodel.py` | ProcessModel과 WorkerThread를 소유. Q_PROPERTY로 searchText, sortColumn, sortOrder 노출. pyqtSlot으로 killProcess(pid), terminateProcess(pid), suspendProcess(pid), resumeProcess(pid), changeNice(pid, value) 구현 |
| 1-C-2 | `utils/process_monitor.py` | send_signal(pid, signal), change_nice(pid, value) 정적 메서드 추가. PermissionError, ProcessLookupError 처리 |
| 1-C-3 | `views/__init__.py` | ProcessViewModel export 추가 |

**기술적 접근**:
- os.kill(pid, signal)로 SIGTERM/SIGKILL/SIGSTOP/SIGCONT 전송
- psutil.Process(pid).nice(value)로 우선순위 변경
- 모든 제어 함수에서 PermissionError -> 사용자에게 오류 메시지 시그널 전달
- ProcessLookupError -> 이미 종료된 프로세스 처리

### 마일스톤 1-D: 프로세스 탭 QML UI

**목표**: 프로세스 테이블, 검색바, 컨텍스트 메뉴 QML 구현

| 작업 | 파일 | 설명 |
|---|---|---|
| 1-D-1 | `qml/tabs/processes_tab.qml` | ListView + delegate로 프로세스 테이블 표현. 헤더 행(클릭 시 정렬). 행 선택 하이라이트 |
| 1-D-2 | `qml/components/SearchBar.qml` | TextField + 아이콘. 입력 시 processViewModel.searchText 바인딩. 300ms debounce 적용 |
| 1-D-3 | `qml/components/ProcessContextMenu.qml` | Menu QML 타입. Terminate, Kill, Suspend, Resume, Change Priority, Details 메뉴 항목 |
| 1-D-4 | `qml/components/PriorityDialog.qml` | Dialog + SpinBox(-20~19). 확인 시 processViewModel.changeNice(pid, value) 호출 |

**기술적 접근**:
- QML ListView는 DelegateModel + delegate Row로 테이블 모양 구현
- 각 delegate에 MouseArea 추가하여 좌클릭 선택, 우클릭 메뉴 트리거
- SearchBar의 onTextChanged에 Timer로 debounce 구현

---

## 3. Phase 2: UI 개선 + 탭 구조 (Secondary Goal)

### 마일스톤 2-A: TabBar 기반 네비게이션

| 작업 | 파일 | 설명 |
|---|---|---|
| 2-A-1 | `qml/main.qml` | 전면 리팩터링: ApplicationWindow에 TabBar + SwipeView/StackLayout 추가. 기본 크기 1280x800. 하단 상태바 추가 |
| 2-A-2 | `qml/tabs/system_overview_tab.qml` | 기존 main.qml의 CPU/Memory/GPU/FPS 표시를 이 탭으로 이동 |

**기술적 접근**:
- TabBar + StackLayout 조합 (SwipeView보다 탭 전환에 적합)
- 각 탭은 Loader로 lazy loading 적용 가능 (성능 최적화)
- 하단 Rectangle에 CPU/Memory 요약 텍스트를 monitorViewModel에서 바인딩

### 마일스톤 2-B: 디스크 모니터링

| 작업 | 파일 | 설명 |
|---|---|---|
| 2-B-1 | `utils/disk_monitor.py` | ResourceMonitor 상속. disk_partitions() + disk_usage() 수집. disk_io_counters() 수집 |
| 2-B-2 | `models/disk_model.py` | 디스크 파티션 데이터 모델. mountpoint, total, used, free, percent, read_bytes, write_bytes |
| 2-B-3 | `views/disk_viewmodel.py` | DiskModel 소유. Q_PROPERTY로 포맷팅된 디스크 데이터 노출. GB/TB 단위 변환 |
| 2-B-4 | `qml/tabs/disk_tab.qml` | 파티션별 사용량 바 + I/O 카운터 표시 |

### 마일스톤 2-C: 네트워크 모니터링

| 작업 | 파일 | 설명 |
|---|---|---|
| 2-C-1 | `utils/network_monitor.py` | ResourceMonitor 상속. net_io_counters(pernic=True) 수집. 이전 값과 비교하여 속도 계산 |
| 2-C-2 | `models/network_model.py` | 네트워크 인터페이스 데이터 모델. interface, bytes_sent, bytes_recv, packets_sent, packets_recv, speed_up, speed_down |
| 2-C-3 | `views/network_viewmodel.py` | NetworkModel 소유. 바이트 -> KB/MB/s 단위 변환 |
| 2-C-4 | `qml/tabs/network_tab.qml` | 인터페이스별 송수신 속도 + 누적 트래픽 표시 |

### 마일스톤 2-D: 다크/라이트 테마

| 작업 | 파일 | 설명 |
|---|---|---|
| 2-D-1 | `qml/main.qml` | ThemeManager QtObject 추가. isDarkTheme property. 색상 팔레트(background, foreground, accent, surface) 정의 |
| 2-D-2 | 모든 QML 파일 | 색상을 ThemeManager 속성에 바인딩. 하드코딩 색상 제거 |

---

## 4. Phase 3: 고급 기능 (Final Goal)

### 마일스톤 3-A: 프로세스 상세 다이얼로그

| 작업 | 파일 | 설명 |
|---|---|---|
| 3-A-1 | `qml/components/ProcessDetailsDialog.qml` | TabBar가 포함된 Dialog. General/Files/Network/Environment 탭 |
| 3-A-2 | `views/process_viewmodel.py` | getProcessDetails(pid) 슬롯 추가. cmdline, open_files, connections, environ 수집 |

### 마일스톤 3-B: 실시간 그래프

| 작업 | 파일 | 설명 |
|---|---|---|
| 3-B-1 | `qml/tabs/system_overview_tab.qml` | QML Canvas 기반 시계열 그래프. 최근 60초 데이터 버퍼. CPU/Memory 각각 별도 그래프 |
| 3-B-2 | `views/monitor_viewmodel.py` | cpuHistory, memoryHistory QVariantList property 추가. 최대 60개 데이터 포인트 유지 |

**기술적 접근**:
- QML Canvas 2D로 직접 그리기 (외부 의존성 없음)
- requestAnimationFrame 또는 Timer로 1초마다 다시 그리기
- deque(maxlen=60)로 히스토리 관리

### 마일스톤 3-C: 프로세스 트리 시각화

| 작업 | 파일 | 설명 |
|---|---|---|
| 3-C-1 | `models/process_model.py` | ppid 관계를 기반으로 트리 구조 구축. QAbstractItemModel 또는 flat list + indent level |
| 3-C-2 | `qml/tabs/processes_tab.qml` | 트리뷰 모드 토글 버튼. indent 기반 계층 표시 |

### 마일스톤 3-D: 설정 저장

| 작업 | 파일 | 설명 |
|---|---|---|
| 3-D-1 | `main.py` | QSettings 초기화. 윈도우 크기/위치 저장 및 복원 |
| 3-D-2 | `qml/main.qml` | Settings 다이얼로그. 테마 선택, 갱신 간격 설정 |

---

## 5. Phase 간 의존성

```
Phase 1 (프로세스 관리)
    |
    +-- 1-A (WorkerThread) --> 1-B (ProcessModel) --> 1-C (ViewModel) --> 1-D (QML UI)
    |
Phase 2 (UI 개선) [Phase 1의 1-D 완료 후]
    |
    +-- 2-A (TabBar) --> 2-B (Disk) [독립]
    |                 --> 2-C (Network) [독립]
    |                 --> 2-D (Theme) [모든 탭 완료 후]
    |
Phase 3 (고급 기능) [Phase 2의 2-A 완료 후]
    |
    +-- 3-A (프로세스 상세) [1-C 필요]
    +-- 3-B (그래프) [2-A 필요]
    +-- 3-C (트리뷰) [1-B 필요]
    +-- 3-D (설정) [2-D 필요]
```

---

## 6. main.py 수정 계획

현재 main.py의 변경 사항:

```python
# 추가 import
from models import ProcessModel, DiskModel, NetworkModel
from views import ProcessViewModel, DiskViewModel, NetworkViewModel
from services.worker_thread import ProcessWorker

# 모델 + ViewModel 생성
process_model = ProcessModel()
process_viewmodel = ProcessViewModel(process_model)
disk_model = DiskModel()
disk_viewmodel = DiskViewModel(disk_model)
network_model = NetworkModel()
network_viewmodel = NetworkViewModel(network_model)

# QML context property 등록
context.setContextProperty("processViewModel", process_viewmodel)
context.setContextProperty("diskViewModel", disk_viewmodel)
context.setContextProperty("networkViewModel", network_viewmodel)
context.setContextProperty("monitorViewModel", view_model)  # 기존 유지

# QThread 설정
worker_thread = QThread()
process_worker = ProcessWorker()
process_worker.moveToThread(worker_thread)
worker_thread.started.connect(...)
worker_thread.start()

# 종료 시 스레드 정리
app.aboutToQuit.connect(worker_thread.quit)
```

---

## 7. 위험 분석

### 성능 위험

| 위험 | 영향 | 대응 |
|---|---|---|
| 프로세스 수가 1000+ 일 때 열거 시간 | UI 갱신 지연 | QThread 사용 + psutil.process_iter(attrs=...) 선택적 조회 |
| QML ListView 대량 항목 렌더링 | 스크롤 버벅임 | ListView.cacheBuffer 조정 + delegate 최적화 |
| CPU/Memory 그래프 Canvas 그리기 | 프레임 드롭 | 60포인트 제한 + requestAnimationFrame |

### 권한 위험

| 위험 | 영향 | 대응 |
|---|---|---|
| root 아닌 사용자가 다른 사용자 프로세스 제어 | PermissionError | try/except + 사용자에게 권한 부족 오류 표시 |
| nice 값 음수(-20~-1) 설정 시 root 필요 | 우선순위 변경 실패 | UI에서 일반 사용자는 0~19 범위만 허용하도록 제한 |

### 스레딩 위험

| 위험 | 영향 | 대응 |
|---|---|---|
| 워커 스레드에서 직접 UI 갱신 | 크래시/정의되지 않은 동작 | pyqtSignal로만 메인 스레드와 통신 |
| 스레드 종료 시 리소스 누수 | 메모리 누수 | app.aboutToQuit에 worker_thread.quit() + wait() 연결 |
| 프로세스 열거 중 프로세스 종료 | NoSuchProcess 예외 | psutil.process_iter()의 안전한 예외 처리 |

### 호환성 위험

| 위험 | 영향 | 대응 |
|---|---|---|
| Wayland에서 윈도우 위치 저장 불가 | 설정 복원 실패 | 윈도우 크기만 저장, 위치는 Wayland 기본값 사용 |
| 일부 Linux 배포판에서 /proc 접근 제한 | 프로세스 정보 누락 | psutil 기본 기능에 의존, /proc 직접 접근은 Optional |
