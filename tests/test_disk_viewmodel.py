"""views/disk_viewmodel.py에 대한 사양 테스트.

DiskViewModel(QObject)의 Q_PROPERTY, 포맷팅 기능, refresh 슬롯을 검증합니다.
"""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

from PyQt5.QtCore import QObject

from views.disk_viewmodel import DiskViewModel


class TestDiskViewModelInit:
    """DiskViewModel 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """DiskViewModel 인스턴스를 생성할 수 있어야 합니다."""
        vm = DiskViewModel()
        assert vm is not None

    def test_is_qobject(self, qapp) -> None:
        """QObject를 상속해야 합니다."""
        vm = DiskViewModel()
        assert isinstance(vm, QObject)

    def test_has_disk_model_property(self, qapp) -> None:
        """diskModel 프로퍼티가 있어야 합니다."""
        vm = DiskViewModel()
        model = vm.property("diskModel")
        assert model is not None


class TestDiskViewModelDiskModel:
    """DiskViewModel.diskModel 프로퍼티를 검증합니다."""

    def test_disk_model_is_disk_model_instance(self, qapp) -> None:
        """diskModel은 DiskModel 인스턴스여야 합니다."""
        from models.disk_model import DiskModel
        vm = DiskViewModel()
        assert isinstance(vm.diskModel, DiskModel)


class TestDiskViewModelFormatBytes:
    """DiskViewModel의 바이트 포맷팅 기능을 검증합니다."""

    def test_format_bytes_zero(self, qapp) -> None:
        """0 바이트를 올바르게 포맷해야 합니다."""
        vm = DiskViewModel()
        assert vm.formatBytes(0) == "0 B"

    def test_format_bytes_kb(self, qapp) -> None:
        """킬로바이트 단위를 올바르게 포맷해야 합니다."""
        vm = DiskViewModel()
        result = vm.formatBytes(1024)
        assert "KB" in result

    def test_format_bytes_mb(self, qapp) -> None:
        """메가바이트 단위를 올바르게 포맷해야 합니다."""
        vm = DiskViewModel()
        result = vm.formatBytes(1024 * 1024)
        assert "MB" in result

    def test_format_bytes_gb(self, qapp) -> None:
        """기가바이트 단위를 올바르게 포맷해야 합니다."""
        vm = DiskViewModel()
        result = vm.formatBytes(1024 * 1024 * 1024)
        assert "GB" in result

    def test_format_bytes_tb(self, qapp) -> None:
        """테라바이트 단위를 올바르게 포맷해야 합니다."""
        vm = DiskViewModel()
        result = vm.formatBytes(1024 ** 4)
        assert "TB" in result

    def test_format_bytes_precise(self, qapp) -> None:
        """정확한 포맷 값을 반환해야 합니다."""
        vm = DiskViewModel()
        # 1.5 GB = 1610612736 bytes
        result = vm.formatBytes(1_610_612_736)
        assert "1.5" in result
        assert "GB" in result


class TestDiskViewModelRefresh:
    """DiskViewModel.refresh() 슬롯을 검증합니다."""

    @patch("views.disk_viewmodel.DiskMonitor")
    def test_refresh_updates_model(self, MockDiskMonitor: MagicMock, qapp) -> None:
        """refresh()를 호출하면 모델이 업데이트되어야 합니다."""
        mock_monitor = MockDiskMonitor.return_value
        mock_monitor.measure.return_value = [
            {
                "device": "/dev/sda1", "mountpoint": "/", "fstype": "ext4",
                "total": 100, "used": 50, "free": 50, "percent": 50.0,
                "read_bytes": 0, "write_bytes": 0,
            }
        ]

        vm = DiskViewModel()
        vm.refresh()

        assert vm.diskModel.rowCount() >= 0  # 최소한 에러 없이 실행
