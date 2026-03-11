# SPEC-NET-001: 인수 기준

## 메타데이터

| 항목 | 값 |
|---|---|
| SPEC ID | SPEC-NET-001 |
| 모듈 | SPEC-NET-001-NI (Network Information) |
| 형식 | Given-When-Then (Gherkin) |

---

## 1. 네트워크 인터페이스 상세 정보

### AC-01: IPv4 주소 표시 (REQ-U-01)

```gherkin
Scenario: 활성 인터페이스의 IPv4 주소가 표시된다
  Given 네트워크 인터페이스 "eth0"이 활성 상태이고 IPv4 주소 "192.168.1.100"이 할당되어 있다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0" 인터페이스 카드에 IP 주소 "192.168.1.100"이 표시된다
```

### AC-02: MAC 주소 표시 (REQ-U-02)

```gherkin
Scenario: 인터페이스의 MAC 주소가 표시된다
  Given 네트워크 인터페이스 "eth0"의 MAC 주소가 "aa:bb:cc:dd:ee:ff"이다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0" 인터페이스 카드에 MAC 주소 "aa:bb:cc:dd:ee:ff"가 표시된다
```

### AC-03: Netmask 표시 (REQ-U-03)

```gherkin
Scenario: 인터페이스의 Netmask가 표시된다
  Given 네트워크 인터페이스 "eth0"의 Netmask가 "255.255.255.0"이다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0" 인터페이스 카드에 Netmask "255.255.255.0"이 표시된다
```

### AC-04: MTU 표시 (REQ-U-04)

```gherkin
Scenario: 인터페이스의 MTU 값이 표시된다
  Given 네트워크 인터페이스 "eth0"의 MTU가 1500이다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0" 인터페이스 카드에 MTU "1500"이 표시된다
```

### AC-05: 인터페이스 상태 표시 (REQ-U-05, REQ-S-01)

```gherkin
Scenario: 활성 인터페이스에 녹색 상태 표시기가 나타난다
  Given 네트워크 인터페이스 "eth0"이 활성(up) 상태이다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0" 인터페이스 이름 옆에 녹색 상태 표시기가 나타난다

Scenario: 비활성 인터페이스에 회색 상태 표시기가 나타난다
  Given 네트워크 인터페이스 "eth1"이 비활성(down) 상태이다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth1" 인터페이스 이름 옆에 회색 상태 표시기가 나타난다
```

### AC-06: 링크 속도 표시 (REQ-U-06)

```gherkin
Scenario: 인터페이스의 링크 속도가 Mbps 단위로 표시된다
  Given 네트워크 인터페이스 "eth0"의 링크 속도가 1000 Mbps이다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0" 인터페이스 카드에 "1000 Mbps"가 표시된다
```

### AC-07: Broadcast 주소 표시 (REQ-U-07)

```gherkin
Scenario: 인터페이스의 Broadcast 주소가 표시된다
  Given 네트워크 인터페이스 "eth0"의 Broadcast 주소가 "192.168.1.255"이다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0" 인터페이스 카드에 Broadcast "192.168.1.255"가 표시된다
```

### AC-08: IPv6 주소 표시 (REQ-U-08, REQ-S-02)

```gherkin
Scenario: IPv6 주소가 있는 인터페이스에 IPv6가 표시된다
  Given 네트워크 인터페이스 "eth0"에 IPv6 주소 "fe80::1"이 할당되어 있다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0" 인터페이스 카드에 IPv6 "fe80::1"이 표시된다

Scenario: IPv6 주소가 없는 인터페이스에 "N/A"가 표시된다
  Given 네트워크 인터페이스 "eth0"에 IPv6 주소가 없다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0" 인터페이스 카드의 IPv6 필드에 "N/A"가 표시된다
```

### AC-09: Duplex 모드 표시 (REQ-U-09)

```gherkin
Scenario: Full Duplex 인터페이스에 "full"이 표시된다
  Given 네트워크 인터페이스 "eth0"이 Full Duplex 모드이다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0" 인터페이스 카드에 Duplex "full"이 표시된다
```

---

## 2. Ping 테스트 기능

### AC-10: 정상 Ping 실행 (REQ-E-01, REQ-E-02)

```gherkin
Scenario: 유효한 호스트에 Ping을 실행하면 결과가 표시된다
  Given 사용자가 Ping 입력 필드에 "8.8.8.8"을 입력했다
  When 사용자가 "Ping" 버튼을 클릭한다
  Then 시스템은 "ping -c 4 -W 3 8.8.8.8" 명령을 실행한다
  And 전송 패킷 수, 수신 패킷 수, 손실률이 표시된다
  And min/avg/max/mdev RTT 값이 밀리초 단위로 표시된다
```

### AC-11: Ping 실행 중 표시 (REQ-E-03, REQ-S-04)

```gherkin
Scenario: Ping 실행 중에 진행 표시기가 나타나고 버튼이 비활성화된다
  Given 사용자가 Ping 입력 필드에 "google.com"을 입력했다
  When 사용자가 "Ping" 버튼을 클릭한다
  Then BusyIndicator가 표시된다
  And "Ping" 버튼이 비활성화된다
  When Ping 실행이 완료된다
  Then BusyIndicator가 숨겨진다
  And "Ping" 버튼이 다시 활성화된다
```

### AC-12: 빈 입력 시 Ping 버튼 비활성화 (REQ-S-03)

```gherkin
Scenario: 입력 필드가 비어 있으면 Ping 버튼이 비활성화된다
  Given Ping 입력 필드가 비어 있다
  Then "Ping" 버튼이 비활성화 상태이다

Scenario: 입력 필드에 값이 입력되면 Ping 버튼이 활성화된다
  Given Ping 입력 필드가 비어 있다
  When 사용자가 "192.168.1.1"을 입력한다
  Then "Ping" 버튼이 활성화 상태이다
```

### AC-13: 호스트 도달 불가 에러 처리

```gherkin
Scenario: 도달할 수 없는 호스트에 Ping을 실행하면 에러가 표시된다
  Given 사용자가 Ping 입력 필드에 "192.168.255.255"를 입력했다
  When 사용자가 "Ping" 버튼을 클릭한다
  And Ping 실행이 완료된다
  Then 에러 메시지가 표시된다 (예: "호스트에 도달할 수 없습니다")
  And 패킷 손실률이 100%로 표시된다
```

### AC-14: DNS 해석 실패 에러 처리

```gherkin
Scenario: 존재하지 않는 도메인에 Ping을 실행하면 DNS 에러가 표시된다
  Given 사용자가 Ping 입력 필드에 "invalid.domain.xyz123"을 입력했다
  When 사용자가 "Ping" 버튼을 클릭한다
  And Ping 실행이 완료된다
  Then DNS 해석 실패 에러 메시지가 표시된다
```

### AC-15: Ping 타임아웃 처리

```gherkin
Scenario: Ping이 타임아웃되면 타임아웃 에러가 표시된다
  Given 사용자가 응답하지 않는 호스트에 Ping을 실행했다
  When 15초 이상 응답이 없다
  Then 타임아웃 에러 메시지가 표시된다
```

---

## 3. 비기능 요구사항

### AC-16: UI 스레드 비블로킹 (REQ-N-01)

```gherkin
Scenario: Ping 실행 중에도 UI가 반응한다
  Given Ping이 실행 중이다
  When 사용자가 다른 탭으로 이동한다
  Then 탭 전환이 지연 없이 수행된다
  And UI가 정상적으로 반응한다
```

### AC-17: loopback 인터페이스 제외 (REQ-N-02)

```gherkin
Scenario: loopback 인터페이스가 목록에서 제외된다
  Given 시스템에 "lo", "eth0", "wlan0" 인터페이스가 있다
  When 네트워크 탭이 데이터를 갱신한다
  Then "eth0"과 "wlan0"만 목록에 표시된다
  And "lo" 인터페이스는 목록에 나타나지 않는다
```

### AC-18: 외부 패키지 미사용 (REQ-N-03)

```gherkin
Scenario: Ping 기능이 표준 라이브러리만 사용한다
  Given Ping 기능의 구현 코드를 검토한다
  Then subprocess 모듈만 사용하여 ping 명령을 실행한다
  And 외부 Python 패키지가 requirements.txt에 추가되지 않는다
```

### AC-19: 데이터 갱신 주기 (REQ-E-04)

```gherkin
Scenario: 인터페이스 상세 정보가 2초마다 갱신된다
  Given 네트워크 모니터링이 시작되었다
  When 2초가 경과한다
  Then 인터페이스의 IP, MAC, MTU 등 상세 정보가 최신 값으로 갱신된다
  And 기존의 속도/전송량 데이터도 함께 갱신된다
```

---

## 4. 입력 검증

### AC-20: Command Injection 방지

```gherkin
Scenario: Ping 대상에 특수 문자가 포함되면 거부된다
  Given 사용자가 Ping 입력 필드에 "8.8.8.8; rm -rf /"를 입력했다
  When 사용자가 "Ping" 버튼을 클릭한다
  Then 시스템은 입력값 검증 에러를 표시한다
  And ping 명령이 실행되지 않는다

Scenario: 유효한 호스트명 형식만 허용된다
  Given 다음 입력값이 유효하다:
    | 입력값 |
    | 8.8.8.8 |
    | google.com |
    | 192.168.1.1 |
    | fe80::1 |
    | my-server.local |
  And 다음 입력값이 거부된다:
    | 입력값 |
    | 8.8.8.8; ls |
    | $(whoami) |
    | google.com && echo |
    | 8.8.8.8 \| cat |
```

---

## 5. 품질 게이트 (Quality Gate)

### Definition of Done

- [ ] 모든 단위 테스트 통과 (pytest)
- [ ] 테스트 커버리지 85% 이상
- [ ] ruff 린트 에러 0건
- [ ] mypy 타입 체크 에러 0건
- [ ] 모든 공개 함수에 docstring 작성
- [ ] 모든 함수 시그니처에 타입 힌트 적용
- [ ] REQ-U-01 ~ REQ-U-09: 인터페이스 상세 정보가 정확히 표시됨
- [ ] REQ-E-01 ~ REQ-E-04: Ping 실행 및 결과 표시가 정상 동작함
- [ ] REQ-S-01 ~ REQ-S-04: 상태 기반 UI 동작이 올바름
- [ ] REQ-N-01: Ping이 UI를 블로킹하지 않음
- [ ] REQ-N-02: loopback 인터페이스가 제외됨
- [ ] REQ-N-03: 외부 패키지가 추가되지 않음
- [ ] AC-20: Command injection이 방지됨

### 검증 방법

| 검증 항목 | 방법 | 도구 |
|---|---|---|
| 단위 테스트 | 자동화 테스트 실행 | pytest |
| 커버리지 | 커버리지 측정 | pytest-cov |
| 코드 품질 | 린트 검사 | ruff |
| 타입 안전성 | 타입 체크 | mypy |
| UI 동작 | 수동 테스트 | 애플리케이션 실행 |
| 보안 | 입력 검증 테스트 | pytest (parametrize) |
