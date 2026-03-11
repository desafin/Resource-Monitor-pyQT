"""utils/net_info_monitor.py에 대한 사양 테스트.

NetInfoMonitor의 get_interface_details() 메서드를 검증합니다.
네트워크 인터페이스별 IP, MAC, MTU 등 상세 정보를 확인합니다.
"""
import pytest
from unittest.mock import patch, MagicMock
from collections import namedtuple


# psutil에서 사용하는 namedtuple 정의
SnicAddr = namedtuple("snicaddr", ["family", "address", "netmask", "broadcast", "ptp"])
SnicStat = namedtuple("snicstat", ["isup", "duplex", "speed", "mtu"])


def _make_addr(family: int, address: str, netmask: str = None,
               broadcast: str = None, ptp: str = None) -> SnicAddr:
    """테스트용 네트워크 주소 객체를 생성합니다."""
    return SnicAddr(family=family, address=address, netmask=netmask,
                    broadcast=broadcast, ptp=ptp)


class TestNetInfoMonitorInit:
    """NetInfoMonitor 초기화를 검증합니다."""

    def test_creates_instance(self) -> None:
        """NetInfoMonitor 인스턴스를 생성할 수 있어야 합니다."""
        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        assert monitor is not None

    def test_not_inherit_resource_monitor(self) -> None:
        """ResourceMonitor를 상속하지 않아야 합니다 (스냅샷 유틸리티)."""
        from utils.net_info_monitor import NetInfoMonitor
        from monitor_base import ResourceMonitor
        monitor = NetInfoMonitor()
        assert not isinstance(monitor, ResourceMonitor)


class TestGetInterfaceDetails:
    """NetInfoMonitor.get_interface_details() 메서드를 검증합니다."""

    @patch("utils.net_info_monitor.psutil")
    def test_returns_dict(self, mock_psutil: MagicMock) -> None:
        """get_interface_details()는 딕셔너리를 반환해야 합니다."""
        mock_psutil.net_if_addrs.return_value = {}
        mock_psutil.net_if_stats.return_value = {}

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert isinstance(result, dict)

    @patch("utils.net_info_monitor.psutil")
    def test_returns_correct_structure(self, mock_psutil: MagicMock) -> None:
        """각 인터페이스에 필수 필드가 포함되어야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0", broadcast="192.168.1.255"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "eth0": SnicStat(isup=True, duplex=2, speed=1000, mtu=1500),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        required_fields = {
            "ip_address", "ipv6_address", "mac_address",
            "netmask", "broadcast", "mtu",
            "is_up", "link_speed", "duplex",
        }
        assert "eth0" in result
        assert required_fields.issubset(set(result["eth0"].keys()))

    @patch("utils.net_info_monitor.psutil")
    def test_excludes_loopback(self, mock_psutil: MagicMock) -> None:
        """루프백(lo) 인터페이스는 제외해야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "lo": [
                _make_addr(family=socket.AF_INET, address="127.0.0.1",
                          netmask="255.0.0.0"),
            ],
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "lo": SnicStat(isup=True, duplex=0, speed=0, mtu=65536),
            "eth0": SnicStat(isup=True, duplex=2, speed=1000, mtu=1500),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert "lo" not in result
        assert "eth0" in result

    @patch("utils.net_info_monitor.psutil")
    def test_parses_ipv4_address(self, mock_psutil: MagicMock) -> None:
        """IPv4 주소를 올바르게 파싱해야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="10.0.0.5",
                          netmask="255.255.0.0", broadcast="10.0.255.255"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "eth0": SnicStat(isup=True, duplex=2, speed=100, mtu=1500),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result["eth0"]["ip_address"] == "10.0.0.5"
        assert result["eth0"]["netmask"] == "255.255.0.0"
        assert result["eth0"]["broadcast"] == "10.0.255.255"

    @patch("utils.net_info_monitor.psutil")
    def test_parses_ipv6_address(self, mock_psutil: MagicMock) -> None:
        """IPv6 주소를 올바르게 파싱해야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0"),
                _make_addr(family=socket.AF_INET6,
                          address="fe80::1%eth0", netmask="ffff:ffff:ffff:ffff::"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "eth0": SnicStat(isup=True, duplex=2, speed=1000, mtu=1500),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result["eth0"]["ipv6_address"] == "fe80::1%eth0"

    @patch("utils.net_info_monitor.psutil")
    def test_parses_mac_address(self, mock_psutil: MagicMock) -> None:
        """MAC 주소를 올바르게 파싱해야 합니다."""
        import socket
        AF_PACKET = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.AF_LINK = AF_PACKET
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0"),
                _make_addr(family=AF_PACKET,
                          address="aa:bb:cc:dd:ee:ff"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "eth0": SnicStat(isup=True, duplex=2, speed=1000, mtu=1500),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result["eth0"]["mac_address"] == "aa:bb:cc:dd:ee:ff"

    @patch("utils.net_info_monitor.psutil")
    def test_handles_missing_ipv6(self, mock_psutil: MagicMock) -> None:
        """IPv6 주소가 없으면 기본값 'N/A'를 반환해야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "eth0": SnicStat(isup=True, duplex=2, speed=1000, mtu=1500),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result["eth0"]["ipv6_address"] == "N/A"

    @patch("utils.net_info_monitor.psutil")
    def test_duplex_mapping_full(self, mock_psutil: MagicMock) -> None:
        """NIC_DUPLEX_FULL은 'full'로 매핑되어야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "eth0": SnicStat(isup=True, duplex=2, speed=1000, mtu=1500),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result["eth0"]["duplex"] == "full"

    @patch("utils.net_info_monitor.psutil")
    def test_duplex_mapping_half(self, mock_psutil: MagicMock) -> None:
        """NIC_DUPLEX_HALF은 'half'로 매핑되어야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "eth0": SnicStat(isup=True, duplex=1, speed=100, mtu=1500),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result["eth0"]["duplex"] == "half"

    @patch("utils.net_info_monitor.psutil")
    def test_duplex_mapping_unknown(self, mock_psutil: MagicMock) -> None:
        """NIC_DUPLEX_UNKNOWN은 'unknown'으로 매핑되어야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "eth0": SnicStat(isup=True, duplex=0, speed=0, mtu=1500),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result["eth0"]["duplex"] == "unknown"

    @patch("utils.net_info_monitor.psutil")
    def test_mtu_and_link_speed(self, mock_psutil: MagicMock) -> None:
        """MTU와 링크 속도를 올바르게 반환해야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "eth0": SnicStat(isup=True, duplex=2, speed=1000, mtu=9000),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result["eth0"]["mtu"] == 9000
        assert result["eth0"]["link_speed"] == 1000

    @patch("utils.net_info_monitor.psutil")
    def test_is_up_flag(self, mock_psutil: MagicMock) -> None:
        """인터페이스 활성화 상태를 올바르게 반환해야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0"),
            ],
            "eth1": [
                _make_addr(family=socket.AF_INET, address="10.0.0.1",
                          netmask="255.0.0.0"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {
            "eth0": SnicStat(isup=True, duplex=2, speed=1000, mtu=1500),
            "eth1": SnicStat(isup=False, duplex=0, speed=0, mtu=1500),
        }
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result["eth0"]["is_up"] is True
        assert result["eth1"]["is_up"] is False

    @patch("utils.net_info_monitor.psutil")
    def test_empty_interfaces(self, mock_psutil: MagicMock) -> None:
        """인터페이스가 없으면 빈 딕셔너리를 반환해야 합니다."""
        mock_psutil.net_if_addrs.return_value = {}
        mock_psutil.net_if_stats.return_value = {}

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result == {}

    @patch("utils.net_info_monitor.psutil")
    def test_interface_without_stats(self, mock_psutil: MagicMock) -> None:
        """stats에 없는 인터페이스는 기본값을 사용해야 합니다."""
        import socket
        mock_psutil.AF_LINK = socket.AF_PACKET if hasattr(socket, "AF_PACKET") else 17
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                _make_addr(family=socket.AF_INET, address="192.168.1.10",
                          netmask="255.255.255.0"),
            ],
        }
        mock_psutil.net_if_stats.return_value = {}  # stats 없음
        mock_psutil.NIC_DUPLEX_FULL = 2
        mock_psutil.NIC_DUPLEX_HALF = 1
        mock_psutil.NIC_DUPLEX_UNKNOWN = 0

        from utils.net_info_monitor import NetInfoMonitor
        monitor = NetInfoMonitor()
        result = monitor.get_interface_details()

        assert result["eth0"]["mtu"] == 0
        assert result["eth0"]["is_up"] is False
        assert result["eth0"]["link_speed"] == 0
        assert result["eth0"]["duplex"] == "unknown"
