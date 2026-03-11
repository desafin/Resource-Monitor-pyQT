"""utils/disk_monitor.py에 대한 사양 테스트.

DiskMonitor(ResourceMonitor)의 measure(), get_measurement() 메서드를 검증합니다.
디스크 파티션 정보와 I/O 통계를 올바르게 수집하는지 확인합니다.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestDiskMonitorInit:
    """DiskMonitor 초기화를 검증합니다."""

    def test_creates_instance(self) -> None:
        """DiskMonitor 인스턴스를 생성할 수 있어야 합니다."""
        from utils.disk_monitor import DiskMonitor
        monitor = DiskMonitor()
        assert monitor is not None

    def test_inherits_resource_monitor(self) -> None:
        """ResourceMonitor를 상속해야 합니다."""
        from utils.disk_monitor import DiskMonitor
        from monitor_base import ResourceMonitor
        monitor = DiskMonitor()
        assert isinstance(monitor, ResourceMonitor)

    def test_initial_measurement_is_empty_list(self) -> None:
        """초기 측정값은 빈 리스트여야 합니다."""
        from utils.disk_monitor import DiskMonitor
        monitor = DiskMonitor()
        result = monitor.get_measurement()
        assert result == [] or result == 0  # ResourceMonitor 기본값 또는 빈 리스트


class TestDiskMonitorMeasure:
    """DiskMonitor.measure() 메서드를 검증합니다."""

    @patch("utils.disk_monitor.psutil")
    def test_measure_returns_list(self, mock_psutil: MagicMock) -> None:
        """measure()는 리스트를 반환해야 합니다."""
        # Arrange: psutil mock 설정
        partition = MagicMock()
        partition.device = "/dev/sda1"
        partition.mountpoint = "/"
        partition.fstype = "ext4"
        mock_psutil.disk_partitions.return_value = [partition]

        usage = MagicMock()
        usage.total = 500_000_000_000
        usage.used = 200_000_000_000
        usage.free = 300_000_000_000
        usage.percent = 40.0
        mock_psutil.disk_usage.return_value = usage

        io_counters = MagicMock()
        io_counters.read_bytes = 1_000_000
        io_counters.write_bytes = 2_000_000
        mock_psutil.disk_io_counters.return_value = io_counters

        from utils.disk_monitor import DiskMonitor
        monitor = DiskMonitor()

        # Act
        result = monitor.measure()

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1

    @patch("utils.disk_monitor.psutil")
    def test_measure_returns_correct_fields(self, mock_psutil: MagicMock) -> None:
        """measure() 결과에 필수 필드가 포함되어야 합니다."""
        partition = MagicMock()
        partition.device = "/dev/sda1"
        partition.mountpoint = "/"
        partition.fstype = "ext4"
        mock_psutil.disk_partitions.return_value = [partition]

        usage = MagicMock()
        usage.total = 500_000_000_000
        usage.used = 200_000_000_000
        usage.free = 300_000_000_000
        usage.percent = 40.0
        mock_psutil.disk_usage.return_value = usage

        io_counters = MagicMock()
        io_counters.read_bytes = 1_000_000
        io_counters.write_bytes = 2_000_000
        mock_psutil.disk_io_counters.return_value = io_counters

        from utils.disk_monitor import DiskMonitor
        monitor = DiskMonitor()
        result = monitor.measure()

        required_fields = {
            "device", "mountpoint", "fstype",
            "total", "used", "free", "percent",
            "read_bytes", "write_bytes",
        }
        assert required_fields.issubset(set(result[0].keys()))

    @patch("utils.disk_monitor.psutil")
    def test_measure_correct_values(self, mock_psutil: MagicMock) -> None:
        """measure() 결과가 올바른 값을 포함해야 합니다."""
        partition = MagicMock()
        partition.device = "/dev/sda1"
        partition.mountpoint = "/"
        partition.fstype = "ext4"
        mock_psutil.disk_partitions.return_value = [partition]

        usage = MagicMock()
        usage.total = 500_000_000_000
        usage.used = 200_000_000_000
        usage.free = 300_000_000_000
        usage.percent = 40.0
        mock_psutil.disk_usage.return_value = usage

        io_counters = MagicMock()
        io_counters.read_bytes = 1_000_000
        io_counters.write_bytes = 2_000_000
        mock_psutil.disk_io_counters.return_value = io_counters

        from utils.disk_monitor import DiskMonitor
        monitor = DiskMonitor()
        result = monitor.measure()

        disk = result[0]
        assert disk["device"] == "/dev/sda1"
        assert disk["mountpoint"] == "/"
        assert disk["fstype"] == "ext4"
        assert disk["total"] == 500_000_000_000
        assert disk["used"] == 200_000_000_000
        assert disk["free"] == 300_000_000_000
        assert disk["percent"] == 40.0
        assert disk["read_bytes"] == 1_000_000
        assert disk["write_bytes"] == 2_000_000

    @patch("utils.disk_monitor.psutil")
    def test_measure_multiple_partitions(self, mock_psutil: MagicMock) -> None:
        """여러 파티션이 있으면 각각의 정보를 반환해야 합니다."""
        p1 = MagicMock(device="/dev/sda1", mountpoint="/", fstype="ext4")
        p2 = MagicMock(device="/dev/sda2", mountpoint="/home", fstype="ext4")
        mock_psutil.disk_partitions.return_value = [p1, p2]

        usage = MagicMock(total=100, used=50, free=50, percent=50.0)
        mock_psutil.disk_usage.return_value = usage

        io_counters = MagicMock(read_bytes=0, write_bytes=0)
        mock_psutil.disk_io_counters.return_value = io_counters

        from utils.disk_monitor import DiskMonitor
        monitor = DiskMonitor()
        result = monitor.measure()

        assert len(result) == 2
        assert result[0]["mountpoint"] == "/"
        assert result[1]["mountpoint"] == "/home"

    @patch("utils.disk_monitor.psutil")
    def test_measure_handles_permission_error(self, mock_psutil: MagicMock) -> None:
        """접근 불가 파티션은 건너뛰어야 합니다."""
        partition = MagicMock(device="/dev/sda1", mountpoint="/secret", fstype="ext4")
        mock_psutil.disk_partitions.return_value = [partition]
        mock_psutil.disk_usage.side_effect = PermissionError("접근 거부")

        io_counters = MagicMock(read_bytes=0, write_bytes=0)
        mock_psutil.disk_io_counters.return_value = io_counters

        from utils.disk_monitor import DiskMonitor
        monitor = DiskMonitor()
        result = monitor.measure()

        assert isinstance(result, list)
        assert len(result) == 0

    @patch("utils.disk_monitor.psutil")
    def test_get_measurement_after_measure(self, mock_psutil: MagicMock) -> None:
        """measure() 후 get_measurement()가 동일한 결과를 반환해야 합니다."""
        partition = MagicMock(device="/dev/sda1", mountpoint="/", fstype="ext4")
        mock_psutil.disk_partitions.return_value = [partition]

        usage = MagicMock(total=100, used=50, free=50, percent=50.0)
        mock_psutil.disk_usage.return_value = usage

        io_counters = MagicMock(read_bytes=0, write_bytes=0)
        mock_psutil.disk_io_counters.return_value = io_counters

        from utils.disk_monitor import DiskMonitor
        monitor = DiskMonitor()
        result = monitor.measure()
        assert monitor.get_measurement() == result
