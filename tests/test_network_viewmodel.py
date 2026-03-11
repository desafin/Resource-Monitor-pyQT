"""views/network_viewmodel.py에 대한 사양 테스트.

NetworkViewModel(QObject)의 Q_PROPERTY, 속도 포맷팅 기능을 검증합니다.
"""
import pytest
from unittest.mock import patch, MagicMock

from PyQt5.QtCore import QObject

from views.network_viewmodel import NetworkViewModel


class TestNetworkViewModelInit:
    """NetworkViewModel 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """NetworkViewModel 인스턴스를 생성할 수 있어야 합니다."""
        vm = NetworkViewModel()
        assert vm is not None

    def test_is_qobject(self, qapp) -> None:
        """QObject를 상속해야 합니다."""
        vm = NetworkViewModel()
        assert isinstance(vm, QObject)

    def test_has_network_model_property(self, qapp) -> None:
        """networkModel 프로퍼티가 있어야 합니다."""
        vm = NetworkViewModel()
        model = vm.property("networkModel")
        assert model is not None


class TestNetworkViewModelNetworkModel:
    """NetworkViewModel.networkModel 프로퍼티를 검증합니다."""

    def test_network_model_is_network_model_instance(self, qapp) -> None:
        """networkModel은 NetworkModel 인스턴스여야 합니다."""
        from models.network_model import NetworkModel
        vm = NetworkViewModel()
        assert isinstance(vm.networkModel, NetworkModel)


class TestNetworkViewModelFormatSpeed:
    """NetworkViewModel의 속도 포맷팅 기능을 검증합니다."""

    def test_format_speed_zero(self, qapp) -> None:
        """0 B/s를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        assert vm.formatSpeed(0) == "0 B/s"

    def test_format_speed_bytes(self, qapp) -> None:
        """바이트 단위 속도를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatSpeed(500)
        assert "B/s" in result

    def test_format_speed_kb(self, qapp) -> None:
        """킬로바이트 단위 속도를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatSpeed(1024)
        assert "KB/s" in result

    def test_format_speed_mb(self, qapp) -> None:
        """메가바이트 단위 속도를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatSpeed(1024 * 1024)
        assert "MB/s" in result

    def test_format_speed_gb(self, qapp) -> None:
        """기가바이트 단위 속도를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatSpeed(1024 ** 3)
        assert "GB/s" in result

    def test_format_speed_precise(self, qapp) -> None:
        """정확한 속도 값을 반환해야 합니다."""
        vm = NetworkViewModel()
        # 1.5 MB/s = 1572864 bytes/sec
        result = vm.formatSpeed(1_572_864)
        assert "1.5" in result
        assert "MB/s" in result


class TestNetworkViewModelFormatBytes:
    """NetworkViewModel의 바이트 포맷팅 기능을 검증합니다."""

    def test_format_bytes_zero(self, qapp) -> None:
        """0 바이트를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        assert vm.formatBytes(0) == "0 B"

    def test_format_bytes_gb(self, qapp) -> None:
        """기가바이트 단위를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatBytes(1024 ** 3)
        assert "GB" in result


class TestNetworkViewModelPing:
    """NetworkViewModel의 ping 관련 기능을 검증합니다."""

    def test_has_ping_target_property(self, qapp) -> None:
        """pingTarget 프로퍼티가 있어야 합니다."""
        vm = NetworkViewModel()
        assert vm.property("pingTarget") is not None or vm.property("pingTarget") == ""

    def test_has_is_pinging_property(self, qapp) -> None:
        """isPinging 프로퍼티가 있어야 합니다."""
        vm = NetworkViewModel()
        # 초기값은 False
        assert vm.property("isPinging") is False

    def test_has_ping_result_property(self, qapp) -> None:
        """pingResult 프로퍼티가 있어야 합니다."""
        vm = NetworkViewModel()
        result = vm.property("pingResult")
        assert result is not None or result == ""

    def test_has_ping_error_property(self, qapp) -> None:
        """pingError 프로퍼티가 있어야 합니다."""
        vm = NetworkViewModel()
        error = vm.property("pingError")
        assert error is not None or error == ""

    def test_initial_ping_target_is_empty(self, qapp) -> None:
        """초기 pingTarget은 빈 문자열이어야 합니다."""
        vm = NetworkViewModel()
        assert vm.property("pingTarget") == ""

    def test_initial_is_pinging_is_false(self, qapp) -> None:
        """초기 isPinging은 False여야 합니다."""
        vm = NetworkViewModel()
        assert vm.property("isPinging") is False

    def test_has_execute_ping_slot(self, qapp) -> None:
        """executePing 슬롯이 있어야 합니다."""
        vm = NetworkViewModel()
        assert hasattr(vm, "executePing")

    def test_cleanup_method_exists(self, qapp) -> None:
        """cleanup 메서드가 있어야 합니다."""
        vm = NetworkViewModel()
        assert hasattr(vm, "cleanup")
        assert callable(vm.cleanup)
