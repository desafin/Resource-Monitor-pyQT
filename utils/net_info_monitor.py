"""네트워크 인터페이스 상세 정보 조회 모듈.

psutil을 사용하여 각 인터페이스의 IP, MAC, MTU 등 상세 정보를 스냅샷으로 제공합니다.
ResourceMonitor를 상속하지 않는 독립적인 유틸리티 클래스입니다.
"""
import logging
import socket
from typing import Any, Dict

import psutil

logger = logging.getLogger(__name__)

# 제외할 인터페이스 목록
_EXCLUDED_INTERFACES = {"lo"}


class NetInfoMonitor:
    """네트워크 인터페이스의 상세 정보를 조회하는 스냅샷 유틸리티.

    psutil.net_if_addrs()와 net_if_stats()를 결합하여
    각 인터페이스의 IP, MAC, MTU, 링크 속도 등을 제공합니다.
    """

    def get_interface_details(self) -> Dict[str, Dict[str, Any]]:
        """모든 네트워크 인터페이스의 상세 정보를 반환합니다.

        루프백(lo) 인터페이스는 제외됩니다.

        Returns:
            인터페이스 이름을 키로 하는 딕셔너리.
            각 값에는 ip_address, ipv6_address, mac_address,
            netmask, broadcast, mtu, is_up, link_speed, duplex가 포함됩니다.
        """
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        # 듀플렉스 매핑 테이블
        duplex_map = {
            psutil.NIC_DUPLEX_FULL: "full",
            psutil.NIC_DUPLEX_HALF: "half",
            psutil.NIC_DUPLEX_UNKNOWN: "unknown",
        }

        result: Dict[str, Dict[str, Any]] = {}

        for iface_name, addr_list in addrs.items():
            # 루프백 제외
            if iface_name in _EXCLUDED_INTERFACES:
                continue

            # 주소 정보 파싱
            ip_address = "N/A"
            ipv6_address = "N/A"
            mac_address = "N/A"
            netmask = "N/A"
            broadcast = "N/A"

            for addr in addr_list:
                if addr.family == socket.AF_INET:
                    ip_address = addr.address or "N/A"
                    netmask = addr.netmask or "N/A"
                    broadcast = addr.broadcast or "N/A"
                elif addr.family == socket.AF_INET6:
                    ipv6_address = addr.address or "N/A"
                elif addr.family == psutil.AF_LINK:
                    mac_address = addr.address or "N/A"

            # 통계 정보 파싱
            if iface_name in stats:
                stat = stats[iface_name]
                mtu = stat.mtu
                is_up = stat.isup
                link_speed = stat.speed
                duplex = duplex_map.get(stat.duplex, "unknown")
            else:
                # stats에 없는 경우 기본값
                mtu = 0
                is_up = False
                link_speed = 0
                duplex = "unknown"

            result[iface_name] = {
                "ip_address": ip_address,
                "ipv6_address": ipv6_address,
                "mac_address": mac_address,
                "netmask": netmask,
                "broadcast": broadcast,
                "mtu": mtu,
                "is_up": is_up,
                "link_speed": link_speed,
                "duplex": duplex,
            }

        return result
