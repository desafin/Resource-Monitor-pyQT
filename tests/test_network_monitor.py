"""utils/network_monitor.py에 대한 사양 테스트.

NetworkMonitor(ResourceMonitor)의 measure(), get_measurement() 메서드를 검증합니다.
네트워크 인터페이스별 통계 및 속도 계산을 확인합니다.
"""
import pytest
from unittest.mock import patch, MagicMock
import time


class TestNetworkMonitorInit:
    """NetworkMonitor 초기화를 검증합니다."""

    def test_creates_instance(self) -> None:
        """NetworkMonitor 인스턴스를 생성할 수 있어야 합니다."""
        from utils.network_monitor import NetworkMonitor
        monitor = NetworkMonitor()
        assert monitor is not None

    def test_inherits_resource_monitor(self) -> None:
        """ResourceMonitor를 상속해야 합니다."""
        from utils.network_monitor import NetworkMonitor
        from monitor_base import ResourceMonitor
        monitor = NetworkMonitor()
        assert isinstance(monitor, ResourceMonitor)


class TestNetworkMonitorMeasure:
    """NetworkMonitor.measure() 메서드를 검증합니다."""

    @patch("utils.network_monitor.psutil")
    @patch("utils.network_monitor.time")
    def test_measure_returns_list(self, mock_time: MagicMock, mock_psutil: MagicMock) -> None:
        """measure()는 리스트를 반환해야 합니다."""
        mock_time.time.return_value = 1000.0

        nic = MagicMock()
        nic.bytes_sent = 1000
        nic.bytes_recv = 2000
        nic.packets_sent = 10
        nic.packets_recv = 20
        mock_psutil.net_io_counters.return_value = {"eth0": nic}

        from utils.network_monitor import NetworkMonitor
        monitor = NetworkMonitor()
        result = monitor.measure()

        assert isinstance(result, list)

    @patch("utils.network_monitor.psutil")
    @patch("utils.network_monitor.time")
    def test_measure_returns_correct_fields(self, mock_time: MagicMock, mock_psutil: MagicMock) -> None:
        """measure() 결과에 필수 필드가 포함되어야 합니다."""
        mock_time.time.return_value = 1000.0

        nic = MagicMock()
        nic.bytes_sent = 1000
        nic.bytes_recv = 2000
        nic.packets_sent = 10
        nic.packets_recv = 20
        mock_psutil.net_io_counters.return_value = {"eth0": nic}

        from utils.network_monitor import NetworkMonitor
        monitor = NetworkMonitor()
        result = monitor.measure()

        required_fields = {
            "interface", "bytes_sent", "bytes_recv",
            "packets_sent", "packets_recv",
            "speed_up", "speed_down",
        }
        assert len(result) >= 1
        assert required_fields.issubset(set(result[0].keys()))

    @patch("utils.network_monitor.psutil")
    @patch("utils.network_monitor.time")
    def test_measure_calculates_speed(self, mock_time: MagicMock, mock_psutil: MagicMock) -> None:
        """두 번째 measure() 호출 시 속도를 계산해야 합니다."""
        # 첫 번째 측정: 시간 1000, bytes_sent=1000, bytes_recv=2000
        nic1 = MagicMock()
        nic1.bytes_sent = 1000
        nic1.bytes_recv = 2000
        nic1.packets_sent = 10
        nic1.packets_recv = 20

        # 두 번째 측정: 시간 1002 (2초 후), bytes_sent=3000, bytes_recv=6000
        nic2 = MagicMock()
        nic2.bytes_sent = 3000
        nic2.bytes_recv = 6000
        nic2.packets_sent = 30
        nic2.packets_recv = 40

        mock_time.time.side_effect = [1000.0, 1002.0]
        mock_psutil.net_io_counters.side_effect = [
            {"eth0": nic1},
            {"eth0": nic2},
        ]

        from utils.network_monitor import NetworkMonitor
        monitor = NetworkMonitor()

        # 첫 번째 측정 (속도 = 0, 이전 데이터 없음)
        monitor.measure()

        # 두 번째 측정 (속도 계산 가능)
        result = monitor.measure()

        eth0 = result[0]
        # speed_up = (3000 - 1000) / 2 = 1000 bytes/sec
        assert eth0["speed_up"] == pytest.approx(1000.0)
        # speed_down = (6000 - 2000) / 2 = 2000 bytes/sec
        assert eth0["speed_down"] == pytest.approx(2000.0)

    @patch("utils.network_monitor.psutil")
    @patch("utils.network_monitor.time")
    def test_first_measure_speed_is_zero(self, mock_time: MagicMock, mock_psutil: MagicMock) -> None:
        """첫 번째 measure()에서 속도는 0이어야 합니다."""
        mock_time.time.return_value = 1000.0

        nic = MagicMock()
        nic.bytes_sent = 5000
        nic.bytes_recv = 10000
        nic.packets_sent = 50
        nic.packets_recv = 100
        mock_psutil.net_io_counters.return_value = {"eth0": nic}

        from utils.network_monitor import NetworkMonitor
        monitor = NetworkMonitor()
        result = monitor.measure()

        assert result[0]["speed_up"] == 0.0
        assert result[0]["speed_down"] == 0.0

    @patch("utils.network_monitor.psutil")
    @patch("utils.network_monitor.time")
    def test_measure_multiple_interfaces(self, mock_time: MagicMock, mock_psutil: MagicMock) -> None:
        """여러 네트워크 인터페이스를 모두 반환해야 합니다."""
        mock_time.time.return_value = 1000.0

        eth0 = MagicMock(bytes_sent=1000, bytes_recv=2000, packets_sent=10, packets_recv=20)
        wlan0 = MagicMock(bytes_sent=500, bytes_recv=800, packets_sent=5, packets_recv=8)
        mock_psutil.net_io_counters.return_value = {"eth0": eth0, "wlan0": wlan0}

        from utils.network_monitor import NetworkMonitor
        monitor = NetworkMonitor()
        result = monitor.measure()

        assert len(result) == 2
        iface_names = {r["interface"] for r in result}
        assert "eth0" in iface_names
        assert "wlan0" in iface_names

    @patch("utils.network_monitor.psutil")
    @patch("utils.network_monitor.time")
    def test_filters_loopback(self, mock_time: MagicMock, mock_psutil: MagicMock) -> None:
        """루프백(lo) 인터페이스는 제외해야 합니다."""
        mock_time.time.return_value = 1000.0

        lo = MagicMock(bytes_sent=100, bytes_recv=100, packets_sent=1, packets_recv=1)
        eth0 = MagicMock(bytes_sent=1000, bytes_recv=2000, packets_sent=10, packets_recv=20)
        mock_psutil.net_io_counters.return_value = {"lo": lo, "eth0": eth0}

        from utils.network_monitor import NetworkMonitor
        monitor = NetworkMonitor()
        result = monitor.measure()

        iface_names = {r["interface"] for r in result}
        assert "lo" not in iface_names
        assert "eth0" in iface_names

    @patch("utils.network_monitor.psutil")
    @patch("utils.network_monitor.time")
    def test_get_measurement_after_measure(self, mock_time: MagicMock, mock_psutil: MagicMock) -> None:
        """measure() 후 get_measurement()가 동일한 결과를 반환해야 합니다."""
        mock_time.time.return_value = 1000.0

        nic = MagicMock(bytes_sent=1000, bytes_recv=2000, packets_sent=10, packets_recv=20)
        mock_psutil.net_io_counters.return_value = {"eth0": nic}

        from utils.network_monitor import NetworkMonitor
        monitor = NetworkMonitor()
        result = monitor.measure()
        assert monitor.get_measurement() == result


class TestNetworkMonitorNetInfo:
    """NetworkMonitor.measure()에서 NetInfoMonitor 데이터 병합을 검증합니다."""

    @patch("utils.network_monitor.NetInfoMonitor")
    @patch("utils.network_monitor.psutil")
    @patch("utils.network_monitor.time")
    def test_measure_includes_ip_address(
        self, mock_time: MagicMock, mock_psutil: MagicMock,
        mock_net_info_cls: MagicMock
    ) -> None:
        """measure() 결과에 ip_address가 포함되어야 합니다."""
        mock_time.time.return_value = 1000.0

        nic = MagicMock(bytes_sent=1000, bytes_recv=2000, packets_sent=10, packets_recv=20)
        mock_psutil.net_io_counters.return_value = {"eth0": nic}

        mock_net_info_cls.return_value.get_interface_details.return_value = {
            "eth0": {
                "ip_address": "192.168.1.10",
                "ipv6_address": "fe80::1",
                "mac_address": "aa:bb:cc:dd:ee:ff",
                "netmask": "255.255.255.0",
                "broadcast": "192.168.1.255",
                "mtu": 1500,
                "is_up": True,
                "link_speed": 1000,
                "duplex": "full",
            }
        }

        from utils.network_monitor import NetworkMonitor
        monitor = NetworkMonitor()
        result = monitor.measure()

        eth0 = result[0]
        assert eth0["ip_address"] == "192.168.1.10"
        assert eth0["ipv6_address"] == "fe80::1"
        assert eth0["mac_address"] == "aa:bb:cc:dd:ee:ff"
        assert eth0["netmask"] == "255.255.255.0"
        assert eth0["broadcast"] == "192.168.1.255"
        assert eth0["mtu"] == 1500
        assert eth0["is_up"] is True
        assert eth0["link_speed"] == 1000
        assert eth0["duplex"] == "full"

    @patch("utils.network_monitor.NetInfoMonitor")
    @patch("utils.network_monitor.psutil")
    @patch("utils.network_monitor.time")
    def test_measure_handles_missing_net_info(
        self, mock_time: MagicMock, mock_psutil: MagicMock,
        mock_net_info_cls: MagicMock
    ) -> None:
        """NetInfoMonitor에 해당 인터페이스가 없으면 기본값을 사용해야 합니다."""
        mock_time.time.return_value = 1000.0

        nic = MagicMock(bytes_sent=1000, bytes_recv=2000, packets_sent=10, packets_recv=20)
        mock_psutil.net_io_counters.return_value = {"eth0": nic}

        # eth0에 대한 상세 정보 없음
        mock_net_info_cls.return_value.get_interface_details.return_value = {}

        from utils.network_monitor import NetworkMonitor
        monitor = NetworkMonitor()
        result = monitor.measure()

        eth0 = result[0]
        assert eth0["ip_address"] == "N/A"
        assert eth0["mac_address"] == "N/A"
        assert eth0["mtu"] == 0
        assert eth0["is_up"] is False
