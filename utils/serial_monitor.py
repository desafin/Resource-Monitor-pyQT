"""시리얼 포트 열거 모듈.

/dev/ttyUSB*, /dev/ttyACM*, /dev/ttyS* 패턴으로 시리얼 포트를 탐색합니다.
"""
import glob
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# 시리얼 포트 패턴과 타입 매핑
SERIAL_PATTERNS: list[tuple[str, str]] = [
    ("/dev/ttyUSB*", "USB"),
    ("/dev/ttyACM*", "ACM"),
    ("/dev/ttyS*", "Standard"),
]


def is_serial_available() -> bool:
    """시리얼 포트의 사용 가능 여부를 확인합니다.

    Returns:
        시리얼 포트가 하나라도 존재하면 True.
    """
    for pattern, _ in SERIAL_PATTERNS:
        if glob.glob(pattern):
            return True
    return False


def collect_serial_ports() -> list[dict]:
    """시리얼 포트 목록을 수집합니다.

    /dev/ttyUSB*, /dev/ttyACM*, /dev/ttyS* 패턴으로 포트를 탐색하고,
    각 포트의 존재 여부와 접근 가능 여부를 확인합니다.

    Returns:
        시리얼 포트 정보 딕셔너리 목록.
        각 딕셔너리에 path(str), type(str), exists(bool) 키가 포함됩니다.
    """
    ports: list[dict] = []

    for pattern, port_type in SERIAL_PATTERNS:
        found = glob.glob(pattern)
        for port_path in found:
            exists = os.path.exists(port_path) and os.access(port_path, os.R_OK)
            ports.append({
                "path": port_path,
                "type": port_type,
                "exists": exists,
            })

    return ports
