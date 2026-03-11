# SPEC-NET-001: 네트워크 정보 확장 + Ping 테스트

## 메타데이터

| 항목 | 값 |
|---|---|
| SPEC ID | SPEC-NET-001 |
| 제목 | Network Interface Details & Ping Test |
| 생성일 | 2026-03-11 |
| 상태 | Planned |
| 우선순위 | High |
| 담당 | expert-backend |
| 모듈 | SPEC-NET-001-NI (Network Information) |
| 개발 방법론 | TDD (RED-GREEN-REFACTOR) |

---

## 1. 환경 (Environment)

### 1.1 현재 시스템 상태

- **프레임워크**: PyQt5 5.15.11 + QML (Qt Quick 2.15)
- **데이터 수집**: psutil 6.1.0
- **아키텍처**: MVVM 패턴 (Model-View-ViewModel)
- **네트워크 탭 현황**: `psutil.net_io_counters(pernic=True)`만 사용
  - 인터페이스별 업로드/다운로드 속도 (bytes/sec)
  - 누적 전송/수신 바이트
  - 전송/수신 패킷 수

### 1.2 미사용 psutil API

| API | 반환 정보 |
|---|---|
| `psutil.net_if_addrs()` | 인터페이스별 주소 목록 (AF_INET, AF_INET6, AF_LINK/AF_PACKET) |
| `psutil.net_if_stats()` | 인터페이스 상태 (isup, duplex, speed, mtu, flags) |

### 1.3 관련 파일

| 파일 | 역할 |
|---|---|
| `utils/network_monitor.py` | NetworkMonitor - 네트워크 I/O 카운터 수집 |
| `models/network_model.py` | NetworkModel - QAbstractListModel (7개 역할) |
| `views/network_viewmodel.py` | NetworkViewModel - QML 프로퍼티/슬롯 제공 |
| `qml/tabs/NetworkTab.qml` | 네트워크 탭 UI (ListView delegate) |
| `monitor_base.py` | ResourceMonitor 추상 기본 클래스 |
| `services/worker_thread.py` | QThread 워커 패턴 참조 (ProcessWorker) |

---

## 2. 가정 (Assumptions)

### 2.1 기술적 가정

| ID | 가정 | 신뢰도 | 근거 |
|---|---|---|---|
| A-01 | `psutil.net_if_addrs()`는 Linux에서 AF_INET, AF_INET6, AF_PACKET 주소를 안정적으로 반환한다 | High | psutil 공식 문서, 프로젝트 내 psutil 6.1.0 사용 중 |
| A-02 | `psutil.net_if_stats()`는 isup, duplex, speed, mtu를 제공한다 | High | psutil 공식 문서 |
| A-03 | Linux `ping` 명령어는 `-c` (횟수)와 `-W` (타임아웃) 옵션을 지원한다 | High | POSIX 표준, 모든 주요 Linux 배포판 포함 |
| A-04 | subprocess를 사용한 ping 실행은 외부 패키지 없이 가능하다 | High | Python 표준 라이브러리 |
| A-05 | 기존 NetworkModel의 역할(Role) 확장이 QML 바인딩에 영향 없이 가능하다 | Medium | Qt UserRole 기반 역할 추가는 기존 바인딩에 영향 없음 |

### 2.2 비즈니스 가정

| ID | 가정 | 신뢰도 | 근거 |
|---|---|---|---|
| A-06 | 사용자는 ifconfig 수준의 네트워크 정보를 한 화면에서 확인하길 원한다 | High | 요구사항 명세 |
| A-07 | Ping 테스트는 개발자/관리자가 네트워크 연결 상태를 빠르게 확인하는 용도이다 | High | 요구사항 명세 |

---

## 3. 요구사항 (Requirements)

### 3.1 Ubiquitous 요구사항 (항상 활성)

> 시스템은 **항상** [동작]해야 한다

| ID | 요구사항 |
|---|---|
| REQ-U-01 | 시스템은 **항상** 각 네트워크 인터페이스의 IPv4 주소를 표시해야 한다 |
| REQ-U-02 | 시스템은 **항상** 각 네트워크 인터페이스의 MAC 주소(하드웨어 주소)를 표시해야 한다 |
| REQ-U-03 | 시스템은 **항상** 각 네트워크 인터페이스의 Netmask를 표시해야 한다 |
| REQ-U-04 | 시스템은 **항상** 각 네트워크 인터페이스의 MTU 값을 표시해야 한다 |
| REQ-U-05 | 시스템은 **항상** 각 네트워크 인터페이스의 활성/비활성 상태(up/down)를 표시해야 한다 |
| REQ-U-06 | 시스템은 **항상** 각 네트워크 인터페이스의 링크 속도(Mbps)를 표시해야 한다 |
| REQ-U-07 | 시스템은 **항상** 각 네트워크 인터페이스의 Broadcast 주소를 표시해야 한다 |
| REQ-U-08 | 시스템은 **항상** 각 네트워크 인터페이스의 IPv6 주소를 표시해야 한다 (사용 가능한 경우) |
| REQ-U-09 | 시스템은 **항상** 각 네트워크 인터페이스의 Duplex 모드(full/half/unknown)를 표시해야 한다 |

### 3.2 Event-Driven 요구사항 (이벤트 기반)

> **WHEN** [이벤트] **THEN** [동작]

| ID | 요구사항 |
|---|---|
| REQ-E-01 | **WHEN** 사용자가 대상 호스트명/IP를 입력하고 Ping 버튼을 클릭하면 **THEN** 시스템은 `ping -c 4 -W 3 <target>` 명령을 실행하고 결과를 표시해야 한다 |
| REQ-E-02 | **WHEN** Ping 실행이 완료되면 **THEN** 시스템은 전송/수신/손실 패킷 수와 min/avg/max/mdev RTT 값을 표시해야 한다 |
| REQ-E-03 | **WHEN** Ping이 실행 중이면 **THEN** 시스템은 실행 중 표시(running indicator)를 보여야 한다 |
| REQ-E-04 | **WHEN** 네트워크 데이터가 2초 주기로 갱신되면 **THEN** 인터페이스 상세 정보(IP, MAC, MTU 등)도 함께 갱신되어야 한다 |

### 3.3 State-Driven 요구사항 (상태 기반)

> **IF** [조건] **THEN** [동작]

| ID | 요구사항 |
|---|---|
| REQ-S-01 | **IF** 네트워크 인터페이스가 비활성(down) 상태이면 **THEN** 시스템은 시각적 상태 표시기(빨간색/회색 인디케이터)로 비활성 상태를 나타내야 한다 |
| REQ-S-02 | **IF** 네트워크 인터페이스에 IPv6 주소가 없으면 **THEN** IPv6 필드를 "N/A"로 표시해야 한다 |
| REQ-S-03 | **IF** Ping 대상 입력 필드가 비어 있으면 **THEN** Ping 버튼은 비활성화 상태여야 한다 |
| REQ-S-04 | **IF** Ping이 실행 중이면 **THEN** Ping 버튼은 비활성화 상태여야 한다 |

### 3.4 Unwanted 요구사항 (금지 사항)

> 시스템은 [동작]**하지 않아야 한다**

| ID | 요구사항 |
|---|---|
| REQ-N-01 | Ping 실행은 UI 메인 스레드를 **블로킹하지 않아야 한다** (QThread 사용 필수) |
| REQ-N-02 | 시스템은 loopback 인터페이스(lo)의 상세 정보를 **표시하지 않아야 한다** (기존 필터링 정책 유지) |
| REQ-N-03 | Ping 기능은 외부 Python 패키지를 **추가하지 않아야 한다** (subprocess 사용) |

### 3.5 Optional 요구사항 (선택 사항)

> **가능하면** [동작] 제공

| ID | 요구사항 |
|---|---|
| REQ-O-01 | **가능하면** 인터페이스 타입(ethernet, wifi 등)을 표시 제공 |
| REQ-O-02 | **가능하면** Ping 히스토리(최근 5회 결과)를 표시 제공 |

---

## 4. 사양 (Specifications)

### 4.1 데이터 수집 사양

#### 4.1.1 인터페이스 상세 정보 수집

`psutil.net_if_addrs()` 반환 구조:

```
{
    "eth0": [
        snicaddr(family=AF_INET, address="192.168.1.100", netmask="255.255.255.0", broadcast="192.168.1.255", ptp=None),
        snicaddr(family=AF_INET6, address="fe80::1", netmask="ffff:ffff:ffff:ffff::", broadcast=None, ptp=None),
        snicaddr(family=AF_PACKET, address="aa:bb:cc:dd:ee:ff", netmask=None, broadcast="ff:ff:ff:ff:ff:ff", ptp=None),
    ]
}
```

`psutil.net_if_stats()` 반환 구조:

```
{
    "eth0": snicstats(isup=True, duplex=2, speed=1000, mtu=1500, flags="up,broadcast,running,multicast")
}
```

#### 4.1.2 Ping 명령 사양

- 명령: `ping -c 4 -W 3 <target>`
- `-c 4`: 4개 패킷 전송
- `-W 3`: 3초 대기 타임아웃
- 출력 파싱 대상:
  - `4 packets transmitted, 4 received, 0% packet loss`
  - `rtt min/avg/max/mdev = 0.031/0.045/0.067/0.014 ms`

### 4.2 모델 역할 확장 사양

기존 NetworkModel 7개 역할에 다음 역할 추가:

| 역할 이름 | Role 상수 | 데이터 타입 | 설명 |
|---|---|---|---|
| `ipAddress` | `IpAddressRole` | `str` | IPv4 주소 |
| `ipv6Address` | `Ipv6AddressRole` | `str` | IPv6 주소 (없으면 "N/A") |
| `macAddress` | `MacAddressRole` | `str` | MAC 주소 |
| `netmask` | `NetmaskRole` | `str` | 서브넷 마스크 |
| `broadcast` | `BroadcastRole` | `str` | Broadcast 주소 |
| `mtu` | `MtuRole` | `int` | MTU 값 |
| `isUp` | `IsUpRole` | `bool` | 인터페이스 활성 여부 |
| `linkSpeed` | `LinkSpeedRole` | `int` | 링크 속도 (Mbps) |
| `duplex` | `DuplexRole` | `str` | Duplex 모드 ("full"/"half"/"unknown") |

### 4.3 Ping 실행 사양

- **QThread 사용**: `services/worker_thread.py`의 ProcessWorker 패턴 참조
- **Signal 구조**:
  - `pingStarted` - Ping 시작 시그널
  - `pingFinished(dict)` - Ping 완료 시그널 (결과 딕셔너리)
  - `pingError(str)` - Ping 오류 시그널
- **결과 딕셔너리 구조**:
  - `target`: 대상 호스트
  - `packets_transmitted`: 전송 패킷 수
  - `packets_received`: 수신 패킷 수
  - `packet_loss`: 패킷 손실률 (%)
  - `rtt_min`: 최소 RTT (ms)
  - `rtt_avg`: 평균 RTT (ms)
  - `rtt_max`: 최대 RTT (ms)
  - `rtt_mdev`: RTT 편차 (ms)

### 4.4 UI 사양

#### 4.4.1 인터페이스 카드 확장

기존 delegate (높이 90px)를 확장하여 인터페이스 상세 정보 포함:
- 인터페이스 이름 옆에 상태 표시기 (녹색 원: up, 회색 원: down)
- 기존 속도/전송량 아래에 상세 정보 행 추가:
  - IP: {ipAddress} | MAC: {macAddress} | MTU: {mtu}
  - Netmask: {netmask} | Speed: {linkSpeed} Mbps | Duplex: {duplex}

#### 4.4.2 PingSection 컴포넌트

NetworkTab 하단에 배치되는 Ping 테스트 UI:
- TextField: 대상 호스트명/IP 입력
- Button: "Ping" 실행 버튼 (실행 중 비활성화)
- BusyIndicator: 실행 중 표시
- 결과 영역: 패킷 통계 + RTT 값 표시

---

## 5. 추적성 (Traceability)

| 요구사항 | 구현 파일 | 테스트 파일 |
|---|---|---|
| REQ-U-01 ~ REQ-U-09 | `utils/net_info_monitor.py`, `models/network_model.py` | `tests/test_net_info_monitor.py`, `tests/test_network_model.py` |
| REQ-E-01 ~ REQ-E-04 | `utils/ping_util.py`, `services/ping_worker.py`, `views/network_viewmodel.py` | `tests/test_ping_util.py`, `tests/test_ping_worker.py`, `tests/test_network_viewmodel.py` |
| REQ-S-01 ~ REQ-S-04 | `qml/tabs/NetworkTab.qml`, `qml/components/PingSection.qml` | 수동 UI 테스트 + ViewModel 단위 테스트 |
| REQ-N-01 ~ REQ-N-03 | `services/ping_worker.py` | `tests/test_ping_worker.py` |
| REQ-O-01 ~ REQ-O-02 | 선택적 구현 | 선택적 테스트 |
