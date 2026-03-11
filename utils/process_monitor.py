"""프로세스 모니터링 유틸리티.

psutil을 사용하여 시스템 프로세스 정보를 수집하고,
프로세스 제어(시그널 전송, 우선순위 변경) 기능을 제공합니다.
"""
import logging
from typing import Optional

import psutil

logger = logging.getLogger(__name__)

# collect_processes()에서 수집할 프로세스 속성 목록
_PROCESS_ATTRS = [
    "pid", "name", "username", "cpu_percent",
    "memory_percent", "status", "num_threads", "ppid",
]


def collect_processes() -> list[dict]:
    """실행 중인 모든 프로세스의 정보를 수집하여 반환합니다.

    Returns:
        각 프로세스의 pid, name, username, cpu_percent,
        memory_percent, status, num_threads를 포함하는 딕셔너리 목록.
    """
    processes: list[dict] = []
    try:
        for proc in psutil.process_iter(attrs=_PROCESS_ATTRS):
            try:
                info = proc.info
                # None 값을 기본값으로 대체
                processes.append({
                    "pid": info.get("pid", 0),
                    "name": info.get("name", "") or "",
                    "username": info.get("username", "") or "",
                    "cpu_percent": info.get("cpu_percent", 0.0) or 0.0,
                    "memory_percent": info.get("memory_percent", 0.0) or 0.0,
                    "status": info.get("status", "unknown") or "unknown",
                    "num_threads": info.get("num_threads", 0) or 0,
                    "ppid": info.get("ppid", 0) or 0,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                logger.debug("프로세스 정보 수집 건너뜀: %s", e)
                continue
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        logger.warning("프로세스 목록 조회 실패: %s", e)

    return processes


def send_signal(pid: int, signal_num: int) -> tuple[bool, str]:
    """지정된 PID의 프로세스에 시그널을 전송합니다.

    Args:
        pid: 대상 프로세스 ID.
        signal_num: 전송할 시그널 번호 (예: signal.SIGTERM).

    Returns:
        (성공 여부, 결과 메시지) 튜플.
    """
    try:
        proc = psutil.Process(pid)
        proc.send_signal(signal_num)
        return True, f"프로세스 {pid}에 시그널 {signal_num} 전송 성공"
    except psutil.NoSuchProcess:
        return False, f"프로세스 {pid}가 존재하지 않습니다"
    except psutil.AccessDenied:
        return False, f"프로세스 {pid}에 대한 권한이 없습니다"
    except Exception as e:
        logger.error("시그널 전송 실패 (PID=%d): %s", pid, e)
        return False, f"시그널 전송 실패: {e}"


def get_process_details(pid: int) -> dict:
    """지정된 PID의 프로세스 상세 정보를 수집하여 반환합니다.

    Args:
        pid: 대상 프로세스 ID.

    Returns:
        cmdline, open_files, connections, environ, create_time, exe, cwd를
        포함하는 딕셔너리. 프로세스가 존재하지 않거나 접근 거부 시
        error 키를 포함하는 딕셔너리를 반환합니다.
    """
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return {"error": f"프로세스 {pid}가 존재하지 않습니다"}
    except psutil.AccessDenied:
        return {"error": f"프로세스 {pid}에 대한 권한이 없습니다"}

    result: dict = {}

    # 커맨드 라인
    try:
        result["cmdline"] = proc.cmdline()
    except (psutil.AccessDenied, psutil.ZombieProcess):
        result["cmdline"] = []

    # 열린 파일 목록
    try:
        files = proc.open_files()
        result["open_files"] = [f.path for f in files]
    except (psutil.AccessDenied, psutil.ZombieProcess):
        result["open_files"] = []

    # 네트워크 연결 목록
    try:
        conns = proc.net_connections()
        result["connections"] = [
            {
                "fd": c.fd,
                "family": str(c.family),
                "type": str(c.type),
                "laddr": f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "",
                "raddr": f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "",
                "status": c.status,
            }
            for c in conns
        ]
    except (psutil.AccessDenied, psutil.ZombieProcess):
        result["connections"] = []

    # 환경 변수
    try:
        result["environ"] = proc.environ()
    except (psutil.AccessDenied, psutil.ZombieProcess):
        result["environ"] = {}

    # 생성 시간
    try:
        result["create_time"] = proc.create_time()
    except (psutil.AccessDenied, psutil.ZombieProcess):
        result["create_time"] = 0.0

    # 실행 파일 경로
    try:
        result["exe"] = proc.exe()
    except (psutil.AccessDenied, psutil.ZombieProcess):
        result["exe"] = ""

    # 작업 디렉토리
    try:
        result["cwd"] = proc.cwd()
    except (psutil.AccessDenied, psutil.ZombieProcess):
        result["cwd"] = ""

    return result


def change_nice(pid: int, value: int) -> tuple[bool, str]:
    """지정된 PID의 프로세스 우선순위(nice 값)를 변경합니다.

    Args:
        pid: 대상 프로세스 ID.
        value: 새로운 nice 값 (-20 ~ 19, 낮을수록 높은 우선순위).

    Returns:
        (성공 여부, 결과 메시지) 튜플.
    """
    try:
        proc = psutil.Process(pid)
        proc.nice(value)
        return True, f"프로세스 {pid}의 우선순위를 {value}로 변경 성공"
    except psutil.NoSuchProcess:
        return False, f"프로세스 {pid}가 존재하지 않습니다"
    except psutil.AccessDenied:
        return False, f"프로세스 {pid}에 대한 권한이 없습니다"
    except Exception as e:
        logger.error("우선순위 변경 실패 (PID=%d): %s", pid, e)
        return False, f"우선순위 변경 실패: {e}"
