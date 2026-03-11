# SPEC-UI-001 Deep Research: Linux 프로세스 관리자 + UI 개선

## 1. 현재 코드베이스 상태 (MVVM 리팩터링 완료)

### 아키텍처
- Model (models/monitor_model.py, 126줄): 모니터 소유, Q_PROPERTY, measure()
- ViewModel (views/monitor_viewmodel.py, 100줄): 포맷팅, QML 바인딩용 프로퍼티
- View (qml/main.qml, 136줄): 단순 ColumnLayout, 선언적 바인딩
- Utils (utils/*.py): CPU, Memory, GPU, FPS 모니터
- Entry (main.py, 45줄): Model+ViewModel 생성, QTimer 연결

### 현재 한계
- 프로세스 수준 데이터 없음 (시스템 전체 집계만)
- 최소 UI: 단일 뷰, 탭/네비게이션 없음
- 프로세스 제어 기능 없음
- 필터링/정렬 없음
- 하드코딩된 윈도우 크기 (400x600)

## 2. psutil 프로세스 관리 기능

### 프로세스 열거
- `psutil.process_iter(attrs=[...])`: 원자적 속성 프리페치
- 속성: pid, ppid, name, username, status, cpu_percent, memory_percent, memory_info, num_threads, create_time, cmdline, nice, num_fds

### 프로세스 제어
- `terminate()`: SIGTERM (정상 종료)
- `kill()`: SIGKILL (강제 종료)
- `suspend()`: SIGSTOP (일시 중지)
- `resume()`: SIGCONT (재개)
- `nice(val)`: 우선순위 변경 (-20~19)
- `children(recursive=True)`: 프로세스 트리 탐색

### 예외 처리
- `NoSuchProcess`: 프로세스 종료됨 (목록에서 제거)
- `AccessDenied`: 권한 부족 (N/A 표시)
- `ZombieProcess`: 좀비 프로세스 (상태만 표시)

## 3. 제안 아키텍처

### 새 모델
- `ProcessModel`: 프로세스 목록, 캐시, 필터, 정렬, 프로세스 제어
- `DiskModel`: 디스크 사용량, I/O 카운터
- `NetworkModel`: 네트워크 인터페이스 통계

### 새 뷰모델
- `ProcessViewModel`: 프로세스 표시 포맷팅, 정렬/필터 로직
- `DiskViewModel`: 디스크 정보 포맷팅
- `NetworkViewModel`: 네트워크 정보 포맷팅

### QML 탭 구조
```
main.qml (TabBar + StackLayout)
├── tabs/system_overview_tab.qml (기존 시스템 모니터링)
├── tabs/processes_tab.qml (프로세스 테이블 + 검색/정렬)
├── tabs/disk_tab.qml (디스크 사용량)
└── tabs/network_tab.qml (네트워크 통계)

components/
├── ProcessContextMenu.qml (우클릭 메뉴)
├── PriorityDialog.qml (우선순위 변경)
├── ProcessDetailsDialog.qml (프로세스 상세)
└── SearchBar.qml (검색바)
```

## 4. 기술적 제약 및 위험

### 성능
- 1000+ 프로세스 열거: ~500ms-1s → QThread 백그라운드 처리 필요
- cpu_percent(interval=0) 사용으로 비차단 호출
- process_iter(attrs=[...])로 배치 속성 가져오기

### 권한
- 일반 사용자: 자기 프로세스만 제어 가능
- 시스템 프로세스: AccessDenied → 사용자에게 안내
- pkexec 연동으로 권한 상승 가능

### 스레딩
- QThread로 프로세스 열거를 백그라운드에서 실행
- 시그널로 메인 스레드에 안전하게 데이터 전달
- UI 프리징 방지

## 5. 파일 영향 분석

### 새 파일 (~20개)
- Python: process_model.py, disk_model.py, network_model.py, process_viewmodel.py, disk_viewmodel.py, network_viewmodel.py, process_monitor.py, disk_monitor.py, network_monitor.py, worker_thread.py
- QML: main.qml(리팩터), tabs/ 4개, components/ 4개

### 수정 파일
- main.py: 새 모델/뷰모델 추가, 스레딩 설정
- models/__init__.py, views/__init__.py, utils/__init__.py: 새 모듈 추출
- requirements.txt: 의존성 변경

### 삭제/변경
- GPUtil 의존성 제거 (Linux 전용이므로 nvidia-smi 직접 사용 또는 제거)

## 6. 구현 우선순위

### Phase 1: 프로세스 관리 핵심 기능
- ProcessModel + ProcessViewModel + processes_tab.qml
- 프로세스 테이블 (정렬, 필터, 검색)
- 프로세스 제어 (kill, terminate, suspend, resume)
- 백그라운드 스레딩

### Phase 2: UI 개선 + 탭 구조
- TabBar 기반 네비게이션
- System Overview 탭 (기존 기능 이동)
- Disk, Network 탭
- 다크/라이트 테마

### Phase 3: 고급 기능
- 프로세스 트리 시각화
- 프로세스 상세 다이얼로그
- CPU/Memory 실시간 그래프
- 설정 저장 (윈도우 크기, 테마)
