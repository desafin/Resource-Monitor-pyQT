# SPEC-NET-001: 구현 계획

## 메타데이터

| 항목 | 값 |
|---|---|
| SPEC ID | SPEC-NET-001 |
| 모듈 | SPEC-NET-001-NI (Network Information) |
| 개발 방법론 | TDD (RED-GREEN-REFACTOR) |

---

## 1. 마일스톤

### M1: 네트워크 정보 유틸리티 (Priority High - 1차 목표)

**목표**: `psutil.net_if_addrs()`, `psutil.net_if_stats()` 래퍼 구현

**TDD 사이클**:
1. **RED**: `tests/test_net_info_monitor.py` 작성 - 인터페이스별 IP, MAC, MTU, 상태 반환 검증
2. **GREEN**: `utils/net_info_monitor.py` 구현
3. **REFACTOR**: 코드 정리 및 타입 힌트 보강

**산출물**:
- `utils/net_info_monitor.py` (신규)
- `tests/test_net_info_monitor.py` (신규)

**상세 구현**:
- `NetInfoMonitor` 클래스 생성 (ResourceMonitor 상속하지 않음 - 주기적 측정이 아닌 스냅샷 조회)
- `get_interface_details() -> dict[str, dict]` 메서드
  - `psutil.net_if_addrs()`에서 AF_INET(IPv4), AF_INET6(IPv6), AF_PACKET(MAC) 분류
  - `psutil.net_if_stats()`에서 isup, duplex, speed, mtu 추출
  - loopback(lo) 인터페이스 제외
- Duplex 값 매핑: `NicDuplex.NIC_DUPLEX_FULL` -> "full", `NIC_DUPLEX_HALF` -> "half", `NIC_DUPLEX_UNKNOWN` -> "unknown"

---

### M2: Ping 유틸리티 (Priority High - 1차 목표)

**목표**: subprocess 기반 ping 명령 실행 및 출력 파싱

**TDD 사이클**:
1. **RED**: `tests/test_ping_util.py` 작성 - 정상 응답, 호스트 불가, DNS 실패, 타임아웃 시나리오
2. **GREEN**: `utils/ping_util.py` 구현
3. **REFACTOR**: 정규식 최적화, 에러 메시지 표준화

**산출물**:
- `utils/ping_util.py` (신규)
- `tests/test_ping_util.py` (신규)

**상세 구현**:
- `run_ping(target: str) -> dict` 함수
  - `subprocess.run(["ping", "-c", "4", "-W", "3", target], capture_output=True, text=True, timeout=15)`
  - 정규식으로 출력 파싱:
    - 패킷 통계: `r"(\d+) packets transmitted, (\d+) received.*?(\d+(?:\.\d+)?)% packet loss"`
    - RTT 통계: `r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)"`
  - 에러 처리:
    - `subprocess.TimeoutExpired` -> 타임아웃 에러
    - `returncode != 0` -> 호스트 불가/DNS 실패
    - 파싱 실패 -> 알 수 없는 오류
- 반환 딕셔너리: `target`, `packets_transmitted`, `packets_received`, `packet_loss`, `rtt_min`, `rtt_avg`, `rtt_max`, `rtt_mdev`, `error` (에러 시)

---

### M3: Ping QThread 워커 (Priority High - 2차 목표)

**목표**: UI 블로킹 방지를 위한 QThread 기반 Ping 워커

**TDD 사이클**:
1. **RED**: `tests/test_ping_worker.py` 작성 - 시그널 발생, 비동기 실행 검증
2. **GREEN**: `services/ping_worker.py` 구현
3. **REFACTOR**: ProcessWorker 패턴과 일관성 확보

**산출물**:
- `services/ping_worker.py` (신규)
- `tests/test_ping_worker.py` (신규)

**상세 구현**:
- `PingWorker(QObject)` 클래스
  - `services/worker_thread.py`의 ProcessWorker 패턴 참조
  - Signals: `pingStarted()`, `pingFinished(dict)`, `pingError(str)`
  - `@pyqtSlot(str) execute_ping(target)` 메서드
  - QThread에서 `run_ping()` 호출 후 결과를 시그널로 전달

---

### M4: NetworkModel 역할 확장 (Priority High - 2차 목표)

**목표**: 기존 NetworkModel에 인터페이스 상세 정보 역할 추가

**TDD 사이클**:
1. **RED**: `tests/test_network_model.py` 확장 - 새 역할 반환값 검증
2. **GREEN**: `models/network_model.py` 수정
3. **REFACTOR**: 역할 상수 정리

**산출물**:
- `models/network_model.py` (수정)
- `tests/test_network_model.py` (수정)

**상세 구현**:
- 9개 신규 역할 추가 (IpAddressRole ~ DuplexRole)
- `roleNames()` 업데이트
- `data()` 메서드에 새 역할 처리 추가

---

### M5: NetworkMonitor 확장 + ViewModel 통합 (Priority High - 3차 목표)

**목표**: 기존 NetworkMonitor에 인터페이스 상세 정보 수집 통합, ViewModel에 Ping 기능 추가

**TDD 사이클**:
1. **RED**: 기존 테스트 확장 - 새 데이터 필드 검증
2. **GREEN**: NetworkMonitor, NetworkViewModel 수정
3. **REFACTOR**: 데이터 흐름 최적화

**산출물**:
- `utils/network_monitor.py` (수정)
- `views/network_viewmodel.py` (수정)
- `tests/test_network_monitor.py` (수정)
- `tests/test_network_viewmodel.py` (수정)

**상세 구현**:

NetworkMonitor 수정:
- `measure()` 메서드에서 `NetInfoMonitor.get_interface_details()` 호출
- 기존 I/O 카운터 데이터에 상세 정보 병합
- 인터페이스별 딕셔너리에 `ip_address`, `ipv6_address`, `mac_address`, `netmask`, `broadcast`, `mtu`, `is_up`, `link_speed`, `duplex` 추가

NetworkViewModel 수정:
- PingWorker 인스턴스 생성 및 QThread 관리
- Ping 관련 pyqtProperty 추가:
  - `pingTarget` (str): 대상 호스트
  - `isPinging` (bool): 실행 중 여부
  - `pingResult` (str): 결과 텍스트
  - `pingError` (str): 에러 메시지
- `@pyqtSlot(str) executePing(target)` 슬롯
- PingWorker 시그널 연결

---

### M6: QML UI 업데이트 (Priority High - 최종 목표)

**목표**: NetworkTab UI 확장 및 PingSection 컴포넌트 추가

**산출물**:
- `qml/tabs/NetworkTab.qml` (수정)
- `qml/components/PingSection.qml` (신규)

**상세 구현**:

NetworkTab.qml 수정:
- delegate 높이 확장 (90px -> ~180px)
- 인터페이스 이름 옆에 상태 원(녹색/회색) 추가
- 상세 정보 행 2줄 추가:
  - Row 1: IP | MAC | MTU
  - Row 2: Netmask | Speed | Duplex
- IPv6, Broadcast 정보 표시

PingSection.qml:
- ColumnLayout 기반
- 헤더: "Ping 테스트"
- RowLayout: TextField (placeholder: "호스트명 또는 IP 입력") + Button ("Ping")
- BusyIndicator: isPinging 바인딩
- 결과 영역: Rectangle 내부에 결과 텍스트
- 에러 메시지 표시 영역 (빨간색 텍스트)

---

## 2. 파일 영향 분석

### 신규 파일 (~7개)

| 파일 경로 | 설명 | 마일스톤 |
|---|---|---|
| `utils/net_info_monitor.py` | 네트워크 인터페이스 상세 정보 수집 | M1 |
| `utils/ping_util.py` | Ping 명령 실행 및 출력 파싱 | M2 |
| `services/ping_worker.py` | QThread 기반 Ping 워커 | M3 |
| `tests/test_net_info_monitor.py` | NetInfoMonitor 단위 테스트 | M1 |
| `tests/test_ping_util.py` | run_ping 단위 테스트 | M2 |
| `tests/test_ping_worker.py` | PingWorker 시그널/스레드 테스트 | M3 |
| `qml/components/PingSection.qml` | Ping UI 컴포넌트 | M6 |

### 수정 파일 (~5개)

| 파일 경로 | 변경 내용 | 마일스톤 |
|---|---|---|
| `models/network_model.py` | 9개 신규 역할 추가 | M4 |
| `utils/network_monitor.py` | 인터페이스 상세 정보 병합 로직 | M5 |
| `views/network_viewmodel.py` | Ping 슬롯/프로퍼티, PingWorker 통합 | M5 |
| `qml/tabs/NetworkTab.qml` | delegate 확장, PingSection 포함 | M6 |
| `tests/test_network_monitor.py` | 새 데이터 필드 검증 추가 | M5 |
| `tests/test_network_model.py` | 새 역할 검증 추가 | M4 |
| `tests/test_network_viewmodel.py` | Ping 기능 검증 추가 | M5 |

### 변경 불필요 파일

| 파일 경로 | 이유 |
|---|---|
| `main.py` | NetworkViewModel이 이미 QML에 등록됨 |
| `monitor_base.py` | NetInfoMonitor는 ResourceMonitor를 상속하지 않음 |

---

## 3. 기술적 접근

### 3.1 데이터 수집 전략

NetworkMonitor의 `measure()` 메서드에서 기존 I/O 카운터 수집과 함께 `NetInfoMonitor.get_interface_details()`를 호출하여 데이터를 병합합니다. NetInfoMonitor를 별도 클래스로 분리하여 단일 책임 원칙을 유지합니다.

```
NetworkMonitor.measure()
    |
    +-- psutil.net_io_counters(pernic=True)  [기존]
    |
    +-- NetInfoMonitor.get_interface_details()  [신규]
    |
    +-- 인터페이스별 데이터 병합
    |
    +-- return merged_interfaces
```

### 3.2 Ping 실행 아키텍처

ProcessWorker 패턴을 따르되, 주기적 실행 대신 일회성 실행 방식:

```
QML (PingSection)
    |  executePing(target) 슬롯 호출
    v
NetworkViewModel
    |  PingWorker.execute_ping(target) 호출
    v
PingWorker (QThread)
    |  subprocess.run(["ping", ...])
    v
ping_util.run_ping(target)
    |  출력 파싱
    v
PingWorker.pingFinished(result) 시그널
    |
    v
NetworkViewModel
    |  프로퍼티 업데이트
    v
QML 자동 갱신
```

### 3.3 QThread 관리

- NetworkViewModel이 QThread 인스턴스를 소유
- PingWorker를 moveToThread()로 백그라운드 스레드에 배치
- startTimer()/stopTimer()와 함께 스레드 수명 주기 관리
- 앱 종료 시 스레드 정리 (main.py의 on_about_to_quit에서 처리)

---

## 4. 리스크 분석

| 리스크 | 확률 | 영향 | 대응 방안 |
|---|---|---|---|
| `psutil.net_if_addrs()`가 일부 가상 인터페이스에서 불완전한 데이터 반환 | Medium | Low | 누락 필드에 기본값("N/A", 0) 적용 |
| Ping 명령 출력 형식이 Linux 배포판마다 미세하게 다를 수 있음 | Low | Medium | 유연한 정규식 패턴 사용, 파싱 실패 시 원본 출력 표시 |
| QThread 종료 시 subprocess가 여전히 실행 중일 수 있음 | Low | Medium | subprocess timeout 설정 (15초), QThread 종료 전 프로세스 kill |
| 기존 NetworkModel delegate 높이 변경으로 UI 레이아웃 깨짐 | Medium | Low | delegate 높이를 동적으로 조정, 접기/펼치기 고려 |
| Ping 대상에 악의적 입력(command injection) | Low | High | target 문자열 검증 (영숫자, '.', '-', ':' 만 허용), shell=False 유지 |

---

## 5. 의존성 그래프

```
M1 (NetInfoMonitor)  ─────────────────┐
                                       │
M2 (ping_util) ──> M3 (PingWorker) ──>│──> M5 (통합) ──> M6 (UI)
                                       │
                   M4 (Model 확장) ────┘
```

- M1과 M2는 독립적으로 병렬 진행 가능
- M3는 M2에 의존
- M4는 독립적으로 진행 가능
- M5는 M1, M3, M4에 의존
- M6는 M5에 의존

---

## 6. 테스트 전략

### 단위 테스트 (pytest)

| 테스트 파일 | 대상 | 주요 검증 항목 |
|---|---|---|
| `test_net_info_monitor.py` | NetInfoMonitor | psutil mock 기반 반환값 검증, loopback 제외, 빈 인터페이스 처리 |
| `test_ping_util.py` | run_ping | subprocess mock 기반 정상/실패/타임아웃 출력 파싱 |
| `test_ping_worker.py` | PingWorker | QSignalSpy 기반 시그널 발생 검증 |
| `test_network_model.py` | NetworkModel | 새 역할 반환값, roleNames 포함 여부 |
| `test_network_monitor.py` | NetworkMonitor | 확장된 데이터 필드 포함 여부 |
| `test_network_viewmodel.py` | NetworkViewModel | Ping 프로퍼티/슬롯 동작 검증 |

### Mock 전략

- `psutil.net_if_addrs()`: `unittest.mock.patch`로 고정 데이터 반환
- `psutil.net_if_stats()`: `unittest.mock.patch`로 고정 데이터 반환
- `subprocess.run`: `unittest.mock.patch`로 ping 출력 시뮬레이션
- QThread: 테스트에서는 동기 실행으로 대체

### 커버리지 목표

- 전체 커버리지: 85% 이상
- 핵심 유틸리티 (`net_info_monitor.py`, `ping_util.py`): 90% 이상
