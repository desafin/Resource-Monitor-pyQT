"""GPIO 핀 상태 모니터링 모듈.

/sys/class/gpio/ 디렉터리에서 내보낸 GPIO 핀의 방향과 값을 읽습니다.
"""
import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

# GPIO sysfs 경로
GPIO_BASE_PATH = "/sys/class/gpio/"


def is_gpio_available() -> bool:
    """GPIO sysfs 인터페이스의 사용 가능 여부를 확인합니다.

    Returns:
        /sys/class/gpio/ 디렉터리가 존재하고 읽기 가능하면 True.
    """
    return os.path.isdir(GPIO_BASE_PATH) and os.access(GPIO_BASE_PATH, os.R_OK)


def collect_gpio_pins() -> list[dict]:
    """내보낸 GPIO 핀의 상태를 수집합니다.

    /sys/class/gpio/ 디렉터리에서 gpioN 형태의 디렉터리를 스캔하고,
    각 핀의 direction(in/out)과 value(0/1)를 읽습니다.

    Returns:
        GPIO 핀 정보 딕셔너리 목록.
        각 딕셔너리에 pin(int), direction(str), value(int) 키가 포함됩니다.
    """
    if not os.path.isdir(GPIO_BASE_PATH):
        return []

    pins: list[dict] = []
    gpio_pattern = re.compile(r"^gpio(\d+)$")

    try:
        entries = os.listdir(GPIO_BASE_PATH)
    except (PermissionError, OSError) as e:
        logger.warning("GPIO 디렉터리 읽기 실패: %s", e)
        return []

    for entry in entries:
        match = gpio_pattern.match(entry)
        if not match:
            continue

        pin_number = int(match.group(1))
        pin_path = os.path.join(GPIO_BASE_PATH, entry)

        try:
            # direction 파일 읽기
            with open(os.path.join(pin_path, "direction")) as f:
                direction = f.read().strip()

            # value 파일 읽기
            with open(os.path.join(pin_path, "value")) as f:
                value = int(f.read().strip())

            pins.append({
                "pin": pin_number,
                "direction": direction,
                "value": value,
            })
        except (FileNotFoundError, PermissionError, ValueError, OSError) as e:
            logger.debug("GPIO 핀 %d 읽기 실패: %s", pin_number, e)
            continue

    return pins
