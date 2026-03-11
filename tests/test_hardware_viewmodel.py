"""views/hardware_viewmodel.py에 대한 사양 테스트.

HardwareViewModel(QObject)의 프로퍼티 프록시, 카운트 프로퍼티,
refresh 슬롯, 주기적 업데이트 기능을 검증합니다.
"""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

from PyQt5.QtCore import QObject


class TestHardwareViewModelInit:
    """HardwareViewModel 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """HardwareViewModel 인스턴스를 생성할 수 있어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert vm is not None

    def test_is_qobject(self, qapp) -> None:
        """QObject를 상속해야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert isinstance(vm, QObject)


class TestHardwareViewModelProperties:
    """HardwareViewModel의 프로퍼티를 검증합니다."""

    def test_has_gpio_data_property(self, qapp) -> None:
        """gpioData 프로퍼티가 있어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert vm.gpioData is not None or vm.gpioData == []

    def test_has_usb_data_property(self, qapp) -> None:
        """usbData 프로퍼티가 있어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert vm.usbData is not None or vm.usbData == []

    def test_has_serial_data_property(self, qapp) -> None:
        """serialData 프로퍼티가 있어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert vm.serialData is not None or vm.serialData == []

    def test_has_gpio_available_property(self, qapp) -> None:
        """gpioAvailable 프로퍼티가 있어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert isinstance(vm.gpioAvailable, bool)

    def test_has_usb_available_property(self, qapp) -> None:
        """usbAvailable 프로퍼티가 있어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert isinstance(vm.usbAvailable, bool)

    def test_has_serial_available_property(self, qapp) -> None:
        """serialAvailable 프로퍼티가 있어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert isinstance(vm.serialAvailable, bool)


class TestHardwareViewModelCounts:
    """HardwareViewModel의 카운트 프로퍼티를 검증합니다."""

    def test_initial_gpio_count_is_zero(self, qapp) -> None:
        """초기 GPIO 카운트는 0이어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert vm.gpioCount == 0

    def test_initial_usb_count_is_zero(self, qapp) -> None:
        """초기 USB 카운트는 0이어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert vm.usbCount == 0

    def test_initial_serial_count_is_zero(self, qapp) -> None:
        """초기 시리얼 카운트는 0이어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert vm.serialCount == 0


class TestHardwareViewModelRefresh:
    """HardwareViewModel.refresh() 슬롯을 검증합니다."""

    @patch("models.hardware_model.collect_serial_ports", return_value=[])
    @patch("models.hardware_model.collect_usb_devices", return_value=[])
    @patch("models.hardware_model.collect_gpio_pins")
    def test_refresh_updates_data(
        self, mock_gpio: MagicMock, mock_usb: MagicMock,
        mock_serial: MagicMock, qapp
    ) -> None:
        """refresh() 호출 후 데이터가 업데이트되어야 합니다."""
        mock_gpio.return_value = [
            {"pin": 17, "direction": "in", "value": 1},
            {"pin": 4, "direction": "out", "value": 0},
        ]

        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        vm.refresh()

        assert vm.gpioCount == 2

    @patch("models.hardware_model.collect_serial_ports", return_value=[])
    @patch("models.hardware_model.collect_usb_devices")
    @patch("models.hardware_model.collect_gpio_pins", return_value=[])
    def test_refresh_updates_usb_count(
        self, mock_gpio: MagicMock, mock_usb: MagicMock,
        mock_serial: MagicMock, qapp
    ) -> None:
        """refresh() 호출 후 USB 카운트가 업데이트되어야 합니다."""
        mock_usb.return_value = [
            {"bus": "1", "device": "2", "vendor_id": "046d",
             "product_id": "c077", "manufacturer": "Logitech",
             "product": "Mouse", "path": "1-1"},
        ]

        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        vm.refresh()

        assert vm.usbCount == 1

    @patch("models.hardware_model.collect_serial_ports")
    @patch("models.hardware_model.collect_usb_devices", return_value=[])
    @patch("models.hardware_model.collect_gpio_pins", return_value=[])
    def test_refresh_updates_serial_count(
        self, mock_gpio: MagicMock, mock_usb: MagicMock,
        mock_serial: MagicMock, qapp
    ) -> None:
        """refresh() 호출 후 시리얼 카운트가 업데이트되어야 합니다."""
        mock_serial.return_value = [
            {"path": "/dev/ttyUSB0", "type": "USB", "exists": True},
            {"path": "/dev/ttyACM0", "type": "ACM", "exists": True},
        ]

        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        vm.refresh()

        assert vm.serialCount == 2


class TestHardwareViewModelTimer:
    """HardwareViewModel의 타이머 기능을 검증합니다."""

    def test_has_start_timer_method(self, qapp) -> None:
        """startTimer 메서드가 있어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert hasattr(vm, "startTimer")
        assert callable(vm.startTimer)

    def test_has_stop_timer_method(self, qapp) -> None:
        """stopTimer 메서드가 있어야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        assert hasattr(vm, "stopTimer")
        assert callable(vm.stopTimer)

    @patch("models.hardware_model.collect_serial_ports", return_value=[])
    @patch("models.hardware_model.collect_usb_devices", return_value=[])
    @patch("models.hardware_model.collect_gpio_pins", return_value=[])
    def test_start_timer_performs_initial_refresh(
        self, mock_gpio: MagicMock, mock_usb: MagicMock,
        mock_serial: MagicMock, qapp
    ) -> None:
        """startTimer()는 초기 데이터 수집을 수행해야 합니다."""
        from views.hardware_viewmodel import HardwareViewModel
        vm = HardwareViewModel()
        vm.startTimer()

        # measure가 호출되었는지 확인 (초기 refresh)
        mock_gpio.assert_called()

        vm.stopTimer()
