"""USB 장치 열거 모듈.

/sys/bus/usb/devices/ 디렉터리에서 USB 장치 정보를 읽습니다.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# USB sysfs 경로
USB_BASE_PATH = "/sys/bus/usb/devices/"


def is_usb_available() -> bool:
    """USB sysfs 인터페이스의 사용 가능 여부를 확인합니다.

    Returns:
        /sys/bus/usb/devices/ 디렉터리가 존재하면 True.
    """
    return os.path.isdir(USB_BASE_PATH)


def _read_sysfs_file(path: str) -> str:
    """sysfs 파일에서 값을 읽습니다. 실패 시 'N/A'를 반환합니다.

    Args:
        path: 읽을 파일 경로.

    Returns:
        파일 내용 (공백 제거) 또는 'N/A'.
    """
    try:
        with open(path) as f:
            return f.read().strip()
    except (FileNotFoundError, PermissionError, OSError):
        return "N/A"


def collect_usb_devices() -> list[dict]:
    """USB 장치 목록을 수집합니다.

    /sys/bus/usb/devices/ 디렉터리에서 각 장치의 idVendor, idProduct,
    manufacturer, product, busnum, devnum 정보를 읽습니다.
    idVendor 파일이 없는 항목(허브 등)은 건너뜁니다.

    Returns:
        USB 장치 정보 딕셔너리 목록.
        각 딕셔너리에 bus, device, vendor_id, product_id, manufacturer,
        product, path 키가 포함됩니다.
    """
    if not os.path.isdir(USB_BASE_PATH):
        return []

    devices: list[dict] = []

    try:
        entries = os.listdir(USB_BASE_PATH)
    except (PermissionError, OSError) as e:
        logger.warning("USB 디렉터리 읽기 실패: %s", e)
        return []

    for entry in entries:
        device_path = os.path.join(USB_BASE_PATH, entry)

        # idVendor 파일 존재 확인 (없으면 건너뜀)
        vendor_file = os.path.join(device_path, "idVendor")
        if not os.path.isfile(vendor_file):
            continue

        vendor_id = _read_sysfs_file(vendor_file)
        product_id = _read_sysfs_file(os.path.join(device_path, "idProduct"))
        manufacturer = _read_sysfs_file(os.path.join(device_path, "manufacturer"))
        product = _read_sysfs_file(os.path.join(device_path, "product"))
        busnum = _read_sysfs_file(os.path.join(device_path, "busnum"))
        devnum = _read_sysfs_file(os.path.join(device_path, "devnum"))

        devices.append({
            "bus": busnum,
            "device": devnum,
            "vendor_id": vendor_id,
            "product_id": product_id,
            "manufacturer": manufacturer,
            "product": product,
            "path": entry,
        })

    return devices
