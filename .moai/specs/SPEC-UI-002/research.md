# SPEC-UI-002 Deep Research: 임베디드 개발자 맞춤 고도화

## 1. 현재 코드베이스 상태

### 아키텍처 (MVVM, Phase 1+2+3 완료)
- **Models**: MonitorModel, ProcessModel, DiskModel, NetworkModel, ProcessSortFilterModel
- **ViewModels**: MonitorViewModel(히스토리 그래프), ProcessViewModel(트리/제어), DiskViewModel, NetworkViewModel
- **Utils**: CPU/Memory/GPU/FPS/Disk/Network/Process 모니터, ProcessTree, SettingsManager
- **Services**: ProcessWorker (QThread 백그라운드 수집)
- **QML**: TabBar 4탭(시스템개요/프로세스/디스크/네트워크), 다크/라이트 테마, Canvas 그래프
- **Tests**: 174개 통과, 85% 커버리지

### 코드 통계
- Python: ~2,500줄 (소스) + ~3,200줄 (테스트)
- QML: ~1,800줄
- 총 파일: ~35개

## 2. 미사용 psutil 기능 (즉시 활용 가능)

| 기능 | psutil API | 현재 상태 |
|------|-----------|----------|
| CPU 주파수 (코어별) | cpu_freq(percpu=True) | 미사용 |
| CPU 온도 | sensors_temperatures() | 미사용 |
| 시스템 로드 평균 | getloadavg() | 미사용 |
| 스왑 메모리 | swap_memory() | 미사용 |
| 프로세스 I/O | Process.io_counters() | 미사용 |
| 네트워크 인터페이스 상태 | net_if_stats() | 미사용 |
| IP 주소 | net_if_addrs() | 미사용 |
| 시스템 부팅 시간 | boot_time() | 미사용 |
| 디스크별 I/O | disk_io_counters(perdisk=True) | 미사용 |

## 3. 임베디드 개발자 필수 기능 분석

### Priority 1: 즉시 구현 가능 (psutil 기반)
1. **CPU 주파수 모니터링** - 코어별 현재/최소/최대 주파수, Governor 표시
2. **온도 모니터링** - CPU/보드/메모리 열 센서, 임계값 표시
3. **시스템 로드 평균** - 1/5/15분 로드 + 히스토리 그래프
4. **스왑 메모리** - 사용량/총량, 스왑 I/O
5. **상세 메모리 정보** - MemAvailable, Buffers, Cached, Shared

### Priority 2: Linux /proc 파싱 필요
6. **시스템 로그 뷰어** - journalctl/dmesg 실시간 스트리밍, 필터/검색
7. **IRQ 모니터링** - /proc/interrupts 파싱, CPU별 인터럽트 분포
8. **커널 모듈 목록** - /proc/modules 파싱, 모듈 상태/크기
9. **메모리 압력 지표** - /proc/pressure/memory (PSI), /proc/meminfo 상세

### Priority 3: 특수 하드웨어 연동
10. **GPIO 시각화** - /sys/class/gpio/ 상태 모니터링
11. **시리얼 포트 모니터링** - /dev/ttyUSB*, /dev/ttyACM* 열거
12. **USB 디바이스 트리** - /sys/bus/usb/ 장치 목록

## 4. 현재 성능 이슈

1. **MonitorModel.measure()**: cpu_percent(interval=0.1)이 메인 스레드에서 100ms 블로킹
2. **프로세스 수집**: 1000+ 프로세스 시 200ms+ 소요 가능
3. **갱신 간격 하드코딩**: 프로세스(2초), 디스크(5초), 네트워크(2초) 변경 불가
4. **main.py 테마 저장 버그**: _updateInterval 프로퍼티로 잘못 읽는 코드

## 5. 아키텍처 확장 용이성

현재 MVVM 패턴으로 새 모니터 추가가 체계적:
1. `utils/xxx_monitor.py` - 데이터 수집
2. `models/xxx_model.py` - QAbstractListModel
3. `views/xxx_viewmodel.py` - QML 바인딩 + 포맷팅
4. `qml/tabs/XxxTab.qml` - UI 탭
5. `main.py` - 등록 + 타이머

테스트 패턴도 확립되어 있어 새 모듈 테스트 추가 용이.
