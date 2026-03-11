---
id: SPEC-UI-001
document: acceptance
version: 1.0.0
status: draft
created: 2026-03-11
updated: 2026-03-11
author: oscar
tags: [SPEC-UI-001-PM, SPEC-UI-001-UI, SPEC-UI-001-DK, SPEC-UI-001-NW, SPEC-UI-001-TD]
---

# SPEC-UI-001: 인수 기준 (Acceptance Criteria)

---

## 1. 프로세스 목록 표시 및 자동 갱신

### AC-PM-001: 프로세스 목록 표시

```gherkin
Given 애플리케이션이 실행 중이고 Processes 탭이 활성화되어 있을 때
When 프로세스 탭이 로드되면
Then 현재 실행 중인 프로세스 목록이 테이블 형태로 표시된다
And 각 행에 PID, Name, User, CPU%, MEM%, Status, Threads 컬럼이 포함된다
And 프로세스 수가 0보다 크다
```

### AC-PM-002: 프로세스 자동 갱신

```gherkin
Given 프로세스 목록이 표시되어 있을 때
When 갱신 간격(기본 2초)이 경과하면
Then 프로세스 목록이 자동으로 갱신된다
And 새로 생성된 프로세스가 목록에 추가된다
And 종료된 프로세스가 목록에서 제거된다
And UI가 프리징되지 않는다 (백그라운드 스레드에서 갱신)
```

### AC-PM-003: 갱신 중 UI 반응성

```gherkin
Given 프로세스 목록이 갱신 중일 때
When 사용자가 스크롤하거나 다른 탭으로 전환하면
Then UI가 즉시 반응한다
And 프레임 드롭이 발생하지 않는다
```

---

## 2. 프로세스 검색 및 필터

### AC-SF-001: 이름으로 검색

```gherkin
Given 프로세스 목록이 표시되어 있을 때
When 사용자가 검색바에 "python"을 입력하면
Then 프로세스 이름에 "python"이 포함된 항목만 표시된다
And 대소문자를 구분하지 않는다
And 검색 결과가 300ms 이내에 반영된다 (debounce)
```

### AC-SF-002: PID로 검색

```gherkin
Given 프로세스 목록이 표시되어 있을 때
When 사용자가 검색바에 PID 번호(예: "1234")를 입력하면
Then 해당 PID를 포함하는 프로세스가 필터링되어 표시된다
```

### AC-SF-003: 사용자명으로 검색

```gherkin
Given 프로세스 목록이 표시되어 있을 때
When 사용자가 검색바에 사용자명(예: "root")을 입력하면
Then 해당 사용자가 소유한 프로세스만 표시된다
```

### AC-SF-004: 검색 초기화

```gherkin
Given 검색 필터가 적용되어 일부 프로세스만 표시 중일 때
When 사용자가 검색바의 텍스트를 모두 삭제하면
Then 전체 프로세스 목록이 다시 표시된다
```

### AC-SF-005: 컬럼 정렬

```gherkin
Given 프로세스 목록이 표시되어 있을 때
When 사용자가 CPU% 헤더를 클릭하면
Then 프로세스가 CPU 사용률 기준 내림차순으로 정렬된다
When 사용자가 CPU% 헤더를 다시 클릭하면
Then 프로세스가 CPU 사용률 기준 오름차순으로 정렬된다
```

---

## 3. 프로세스 제어 (Kill/Terminate/Suspend/Resume)

### AC-PC-001: 프로세스 Terminate (SIGTERM)

```gherkin
Given 프로세스 목록에서 자신의 프로세스를 선택했을 때
When 사용자가 컨텍스트 메뉴에서 "Terminate"를 클릭하면
Then 해당 프로세스에 SIGTERM 시그널이 전송된다
And 다음 갱신 주기에 프로세스가 목록에서 제거된다 (정상 종료 시)
```

### AC-PC-002: 프로세스 Kill (SIGKILL)

```gherkin
Given 프로세스 목록에서 자신의 프로세스를 선택했을 때
When 사용자가 컨텍스트 메뉴에서 "Kill"을 클릭하면
Then 해당 프로세스에 SIGKILL 시그널이 전송된다
And 프로세스가 즉시 종료된다
```

### AC-PC-003: 프로세스 Suspend (SIGSTOP)

```gherkin
Given 프로세스 목록에서 실행 중(running/sleeping) 프로세스를 선택했을 때
When 사용자가 컨텍스트 메뉴에서 "Suspend"를 클릭하면
Then 해당 프로세스에 SIGSTOP 시그널이 전송된다
And 프로세스 상태가 "stopped"으로 변경된다
```

### AC-PC-004: 프로세스 Resume (SIGCONT)

```gherkin
Given 프로세스 목록에서 중지(stopped) 상태의 프로세스를 선택했을 때
When 사용자가 컨텍스트 메뉴에서 "Resume"를 클릭하면
Then 해당 프로세스에 SIGCONT 시그널이 전송된다
And 프로세스 상태가 "running" 또는 "sleeping"으로 변경된다
```

### AC-PC-005: 권한 부족 오류 처리

```gherkin
Given 프로세스 목록에서 다른 사용자(예: root)의 프로세스를 선택했을 때
When 일반 사용자가 "Kill" 또는 "Terminate"를 실행하면
Then 권한 부족 오류 메시지가 사용자에게 표시된다
And 애플리케이션이 크래시하지 않는다
And 오류 메시지에 "Permission denied" 또는 동등한 안내가 포함된다
```

### AC-PC-006: 우선순위(nice) 변경

```gherkin
Given 프로세스 목록에서 자신의 프로세스를 선택했을 때
When 사용자가 컨텍스트 메뉴에서 "Change Priority"를 선택하고
And PriorityDialog에서 nice 값 10을 입력하고 확인하면
Then 해당 프로세스의 nice 값이 10으로 변경된다
```

### AC-PC-007: 우클릭 컨텍스트 메뉴

```gherkin
Given 프로세스 목록이 표시되어 있을 때
When 사용자가 프로세스 행을 우클릭하면
Then 컨텍스트 메뉴가 표시된다
And 메뉴에 Terminate, Kill, Suspend, Resume, Change Priority, Details 항목이 포함된다
```

---

## 4. 탭 전환 동작

### AC-TAB-001: 탭 네비게이션

```gherkin
Given 애플리케이션이 실행 중일 때
When 사용자가 TabBar의 "System" 탭을 클릭하면
Then System Overview 탭이 활성화되고 CPU/Memory/GPU/FPS 정보가 표시된다
When 사용자가 "Processes" 탭을 클릭하면
Then 프로세스 목록 탭이 활성화된다
When 사용자가 "Disk" 탭을 클릭하면
Then 디스크 사용량 정보가 표시된다
When 사용자가 "Network" 탭을 클릭하면
Then 네트워크 트래픽 정보가 표시된다
```

### AC-TAB-002: 탭 전환 시 데이터 유지

```gherkin
Given Processes 탭에서 검색 필터를 적용한 상태에서
When 사용자가 System 탭으로 전환했다가 Processes 탭으로 돌아오면
Then 이전 검색 필터가 유지되어 있다
And 프로세스 데이터가 갱신된 최신 상태이다
```

### AC-TAB-003: 하단 상태바

```gherkin
Given 애플리케이션이 실행 중일 때
When 어떤 탭이 활성화되어 있든
Then 하단 상태바에 현재 CPU 사용률과 메모리 사용률 요약이 표시된다
And 상태바 데이터가 실시간으로 갱신된다
```

---

## 5. 디스크 정보 표시

### AC-DK-001: 디스크 사용량 표시

```gherkin
Given Disk 탭이 활성화되어 있을 때
When 탭이 로드되면
Then 각 마운트 포인트의 전체 용량, 사용량, 남은 용량, 사용률(%)이 표시된다
And 루트(/) 파티션이 반드시 포함된다
And 용량이 GB 또는 TB 단위로 사람이 읽기 쉽게 포맷팅된다
```

### AC-DK-002: 디스크 I/O 카운터

```gherkin
Given Disk 탭이 활성화되어 있을 때
When 디스크 I/O 정보가 로드되면
Then 읽기 바이트 수, 쓰기 바이트 수가 표시된다
And I/O 횟수(read_count, write_count)가 표시된다
```

---

## 6. 네트워크 정보 표시

### AC-NW-001: 네트워크 인터페이스별 트래픽

```gherkin
Given Network 탭이 활성화되어 있을 때
When 탭이 로드되면
Then 각 네트워크 인터페이스(eth0, wlan0 등)의 송수신 바이트와 패킷 수가 표시된다
And lo(loopback) 인터페이스도 포함된다
```

### AC-NW-002: 네트워크 속도 표시

```gherkin
Given Network 탭이 활성화되어 있을 때
When 갱신 주기마다 데이터가 갱신되면
Then 각 인터페이스의 초당 송수신 속도(bytes/s)가 계산되어 표시된다
And 속도가 KB/s 또는 MB/s 단위로 포맷팅된다
```

---

## 7. 다크 테마 전환

### AC-TH-001: 다크 테마 활성화

```gherkin
Given 애플리케이션이 라이트 테마로 실행 중일 때
When 사용자가 테마 전환 버튼을 클릭하면
Then 전체 UI가 다크 테마로 전환된다
And 배경색이 어두운 색상(#1e1e1e 계열)으로 변경된다
And 텍스트가 밝은 색상으로 변경된다
And 모든 탭에 테마가 일관되게 적용된다
```

### AC-TH-002: 테마 설정 영속화

```gherkin
Given 사용자가 다크 테마를 선택한 상태에서
When 애플리케이션을 종료하고 다시 실행하면
Then 이전에 선택한 다크 테마가 자동으로 적용된다
```

---

## 8. 프로세스 상세 다이얼로그

### AC-PD-001: 상세 다이얼로그 열기

```gherkin
Given 프로세스 목록에서 프로세스를 선택했을 때
When 사용자가 해당 프로세스를 더블클릭하면
Then 프로세스 상세 다이얼로그가 표시된다
And 다이얼로그에 프로세스 이름과 PID가 타이틀에 표시된다
```

### AC-PD-002: 상세 정보 탭 - General

```gherkin
Given 프로세스 상세 다이얼로그가 열려 있을 때
When General 탭이 활성화되면
Then 프로세스의 명령줄(cmdline), 실행 경로, 시작 시간, 상태가 표시된다
```

### AC-PD-003: 상세 정보 탭 - Open Files

```gherkin
Given 프로세스 상세 다이얼로그가 열려 있을 때
When Files 탭이 활성화되면
Then 해당 프로세스가 열고 있는 파일 목록이 표시된다
And 접근 권한이 없는 경우 "Permission denied" 메시지가 표시된다
```

### AC-PD-004: 상세 정보 탭 - Network Connections

```gherkin
Given 프로세스 상세 다이얼로그가 열려 있을 때
When Network 탭이 활성화되면
Then 해당 프로세스의 네트워크 연결 목록(로컬 주소, 원격 주소, 상태)이 표시된다
```

### AC-PD-005: 상세 정보 탭 - Environment

```gherkin
Given 프로세스 상세 다이얼로그가 열려 있을 때
When Environment 탭이 활성화되면
Then 해당 프로세스의 환경 변수 목록(KEY=VALUE)이 표시된다
And 접근 권한이 없는 경우 "Permission denied" 메시지가 표시된다
```

---

## 9. 실시간 그래프 업데이트

### AC-GR-001: CPU 그래프

```gherkin
Given System Overview 탭이 활성화되어 있을 때
When 1초마다 CPU 데이터가 갱신되면
Then CPU 사용률 시계열 그래프가 업데이트된다
And 그래프에 최근 60초 데이터가 표시된다
And 그래프 Y축 범위가 0~100%이다
```

### AC-GR-002: Memory 그래프

```gherkin
Given System Overview 탭이 활성화되어 있을 때
When 1초마다 메모리 데이터가 갱신되면
Then 메모리 사용률 시계열 그래프가 업데이트된다
And 그래프에 최근 60초 데이터가 표시된다
```

### AC-GR-003: 그래프 렌더링 성능

```gherkin
Given 실시간 그래프가 표시 중일 때
When 그래프가 매초 업데이트되면
Then 그래프 렌더링이 100ms 이내에 완료된다
And UI 스레드가 블로킹되지 않는다
```

---

## 10. 백그라운드 스레딩 (UI 프리징 없음)

### AC-TD-001: 프로세스 열거 스레딩

```gherkin
Given 애플리케이션이 실행 중일 때
When 프로세스 열거가 시작되면
Then 열거 작업이 별도 QThread에서 실행된다
And 메인(UI) 스레드가 블로킹되지 않는다
And 열거 결과가 pyqtSignal을 통해 메인 스레드로 전달된다
```

### AC-TD-002: 스레드 안전한 UI 갱신

```gherkin
Given 워커 스레드에서 프로세스 데이터가 수집되었을 때
When 데이터가 메인 스레드로 전달되면
Then ProcessModel.update_data()가 메인 스레드에서 실행된다
And QML ListView가 정상적으로 갱신된다
And 어떤 스레드에서도 직접 UI 요소에 접근하지 않는다
```

### AC-TD-003: 스레드 정리

```gherkin
Given 워커 스레드가 실행 중일 때
When 애플리케이션이 종료되면
Then 워커 스레드가 안전하게 종료된다
And 스레드 관련 리소스가 정리된다
And 메모리 누수가 발생하지 않는다
```

---

## 11. Definition of Done

### Phase 1 완료 조건

- [ ] ProcessModel이 QAbstractListModel을 상속하고 모든 Role이 정의됨
- [ ] ProcessWorker가 QThread에서 프로세스를 열거하고 시그널로 결과 전달
- [ ] 프로세스 검색/필터가 이름, PID, 사용자명으로 동작
- [ ] 컬럼 헤더 클릭 시 정렬 전환
- [ ] SIGTERM, SIGKILL, SIGSTOP, SIGCONT 전송 동작 확인
- [ ] nice 값 변경 동작 확인
- [ ] 우클릭 컨텍스트 메뉴 표시 및 기능 연결
- [ ] 권한 오류 시 사용자에게 오류 메시지 표시
- [ ] 단위 테스트: ProcessMonitor, ProcessModel, ProcessViewModel
- [ ] UI 프리징 없이 1000+ 프로세스 환경에서 정상 동작

### Phase 2 완료 조건

- [ ] TabBar(System/Processes/Disk/Network) 네비게이션 동작
- [ ] 기존 CPU/Memory/GPU/FPS가 System 탭으로 이동
- [ ] Disk 탭에 파티션별 사용량 + I/O 카운터 표시
- [ ] Network 탭에 인터페이스별 트래픽 + 속도 표시
- [ ] 다크/라이트 테마 전환 동작
- [ ] 하단 상태바에 CPU/Memory 요약 표시
- [ ] 윈도우 기본 크기 1280x800 적용
- [ ] 단위 테스트: DiskMonitor, NetworkMonitor, DiskViewModel, NetworkViewModel

### Phase 3 완료 조건

- [ ] 프로세스 상세 다이얼로그에 cmdline, open_files, connections, environ 표시
- [ ] CPU/Memory 실시간 그래프(최근 60초) 동작
- [ ] 프로세스 트리 시각화(ppid 기반 계층 표시)
- [ ] 설정(테마, 윈도우 크기, 갱신 간격) 저장 및 복원
- [ ] 전체 테스트 커버리지 85% 이상
- [ ] ruff 린팅 오류 0개
- [ ] mypy 타입 체크 통과

### 품질 기준 (Quality Gate)

| 항목 | 기준 |
|---|---|
| 테스트 커버리지 | 85% 이상 (pytest --cov) |
| 린팅 | ruff 오류 0개 |
| 타입 체크 | mypy strict 모드 통과 |
| UI 반응성 | 프로세스 갱신 시 UI 프리징 없음 |
| 메모리 | 장시간 실행 시 메모리 누수 없음 |
| 프로세스 제어 | 모든 시그널 전송 정상 동작 |
| 오류 처리 | 권한 부족/프로세스 미존재 시 크래시 없음 |
