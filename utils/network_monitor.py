"""네트워크 인터페이스 모니터링 모듈.

psutil을 사용하여 네트워크 인터페이스별 전송량 및 속도를 측정합니다.
"""
import logging
import time
from typing import Any

import psutil

from monitor_base import ResourceMonitor
from utils.net_info_monitor import NetInfoMonitor

logger = logging.getLogger(__name__)


class NetworkMonitor(ResourceMonitor):
    """네트워크 인터페이스별 통계 및 속도를 모니터링합니다.

    이전 측정값과 현재 측정값을 비교하여
    업로드/다운로드 속도(bytes/sec)를 계산합니다.
    """

    # 제외할 인터페이스 목록
    _EXCLUDED_INTERFACES = {"lo"}

    def __init__(self) -> None:
        super().__init__()
        self.current_measurement: list[dict[str, Any]] = []
        self._prev_counters: dict[str, dict[str, int]] = {}
        self._prev_time: float = 0.0
        self._net_info = NetInfoMonitor()

    def measure(self) -> list[dict[str, Any]]:
        """네트워크 인터페이스별 통계를 측정합니다.

        이전 측정과 비교하여 속도를 계산합니다.
        첫 번째 호출 시 속도는 0으로 설정됩니다.

        Returns:
            인터페이스별 네트워크 정보 딕셔너리 목록.
            각 딕셔너리에 interface, bytes_sent, bytes_recv,
            packets_sent, packets_recv, speed_up, speed_down 키가 포함됩니다.
        """
        current_time = time.time()
        counters = psutil.net_io_counters(pernic=True)

        # 인터페이스 상세 정보 조회
        net_info = self._net_info.get_interface_details()

        # 상세 정보 기본값
        _default_info: dict[str, Any] = {
            "ip_address": "N/A",
            "ipv6_address": "N/A",
            "mac_address": "N/A",
            "netmask": "N/A",
            "broadcast": "N/A",
            "mtu": 0,
            "is_up": False,
            "link_speed": 0,
            "duplex": "unknown",
        }

        interfaces: list[dict[str, Any]] = []
        elapsed = current_time - self._prev_time if self._prev_time > 0 else 0.0

        for iface_name, nic in counters.items():
            # 루프백 등 제외 인터페이스 필터링
            if iface_name in self._EXCLUDED_INTERFACES:
                continue

            # 속도 계산 (이전 데이터가 있는 경우)
            speed_up = 0.0
            speed_down = 0.0
            if elapsed > 0 and iface_name in self._prev_counters:
                prev = self._prev_counters[iface_name]
                speed_up = (nic.bytes_sent - prev["bytes_sent"]) / elapsed
                speed_down = (nic.bytes_recv - prev["bytes_recv"]) / elapsed

            # I/O 카운터 데이터
            iface_data: dict[str, Any] = {
                "interface": iface_name,
                "bytes_sent": nic.bytes_sent,
                "bytes_recv": nic.bytes_recv,
                "packets_sent": nic.packets_sent,
                "packets_recv": nic.packets_recv,
                "speed_up": speed_up,
                "speed_down": speed_down,
            }

            # 상세 정보 병합
            info = net_info.get(iface_name, _default_info)
            iface_data.update(info)

            interfaces.append(iface_data)

        # 현재 카운터를 이전 값으로 저장
        self._prev_counters = {
            name: {
                "bytes_sent": nic.bytes_sent,
                "bytes_recv": nic.bytes_recv,
            }
            for name, nic in counters.items()
            if name not in self._EXCLUDED_INTERFACES
        }
        self._prev_time = current_time

        self.last_measurement = self.current_measurement
        self.current_measurement = interfaces
        return interfaces

    def get_measurement(self) -> list[dict[str, Any]]:
        """최신 네트워크 측정값을 반환합니다."""
        return self.current_measurement
