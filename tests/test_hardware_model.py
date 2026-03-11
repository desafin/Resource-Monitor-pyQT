"""models/hardware_model.py에 대한 사양 테스트.

HardwareModel(QObject)의 Q_PROPERTY, measure() 슬롯, 시그널 동작을 검증합니다.
GPIO, USB, 시리얼 하드웨어 데이터를 수집하고 QML에 노출하는 기능을 테스트합니다.
"""
import pytest
from unittest.mock import patch, MagicMock

from PyQt5.QtCore import QObject


class TestHardwareModelInit:
    """HardwareModel 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """HardwareModel 인스턴스를 생성할 수 있어야 합니다."""
        from models.hardware_model import HardwareModel
        model = HardwareModel()
        assert model is not None

    def test_is_qobject(self, qapp) -> None:
        """QObject를 상속해야 합니다."""
        from models.hardware_model import HardwareModel
        model = HardwareModel()
        assert isinstance(model, QObject)

    def test_initial_gpio_data_is_empty(self, qapp) -> None:
        """초기 GPIO 데이터는 빈 리스트여야 합니다."""
        from models.hardware_model import HardwareModel
        model = HardwareModel()
        assert model.gpioData == []

    def test_initial_usb_data_is_empty(self, qapp) -> None:
        """초기 USB 데이터는 빈 리스트여야 합니다."""
        from models.hardware_model import HardwareModel
        model = HardwareModel()
        assert model.usbData == []

    def test_initial_serial_data_is_empty(self, qapp) -> None:
        """초기 시리얼 데이터는 빈 리스트여야 합니다."""
        from models.hardware_model import HardwareModel
        model = HardwareModel()
        assert model.serialData == []


class TestHardwareModelAvailability:
    """HardwareModel의 가용성 프로퍼티를 검증합니다."""

    @patch("models.hardware_model.is_gpio_available", return_value=True)
    def test_gpio_available_true(self, mock_fn: MagicMock, qapp) -> None:
        """GPIO가 사용 가능하면 gpioAvailable이 True여야 합니다."""
        from models.hardware_model import HardwareModel
        model = HardwareModel()
        assert model.gpioAvailable is True

    @patch("models.hardware_model.is_gpio_available", return_value=False)
    def test_gpio_available_false(self, mock_fn: MagicMock, qapp) -> None:
        """GPIO가 사용 불가하면 gpioAvailable이 False여야 합니다."""
        from models.hardware_model import HardwareModel
        model = HardwareModel()
        assert model.gpioAvailable is False

    @patch("models.hardware_model.is_usb_available", return_value=True)
    def test_usb_available_true(self, mock_fn: MagicMock, qapp) -> None:
        """USB가 사용 가능하면 usbAvailable이 True여야 합니다."""
        from models.hardware_model import HardwareModel
        model = HardwareModel()
        assert model.usbAvailable is True

    @patch("models.hardware_model.is_serial_available", return_value=True)
    def test_serial_available_true(self, mock_fn: MagicMock, qapp) -> None:
        """시리얼이 사용 가능하면 serialAvailable이 True여야 합니다."""
        from models.hardware_model import HardwareModel
        model = HardwareModel()
        assert model.serialAvailable is True


class TestHardwareModelMeasure:
    """HardwareModel.measure() 메서드를 검증합니다."""

    @patch("models.hardware_model.collect_serial_ports")
    @patch("models.hardware_model.collect_usb_devices")
    @patch("models.hardware_model.collect_gpio_pins")
    def test_measure_updates_gpio_data(
        self, mock_gpio: MagicMock, mock_usb: MagicMock,
        mock_serial: MagicMock, qapp
    ) -> None:
        """measure() 호출 후 GPIO 데이터가 업데이트되어야 합니다."""
        gpio_data = [{"pin": 17, "direction": "in", "value": 1}]
        mock_gpio.return_value = gpio_data
        mock_usb.return_value = []
        mock_serial.return_value = []

        from models.hardware_model import HardwareModel
        model = HardwareModel()
        model.measure()

        assert model.gpioData == gpio_data

    @patch("models.hardware_model.collect_serial_ports")
    @patch("models.hardware_model.collect_usb_devices")
    @patch("models.hardware_model.collect_gpio_pins")
    def test_measure_updates_usb_data(
        self, mock_gpio: MagicMock, mock_usb: MagicMock,
        mock_serial: MagicMock, qapp
    ) -> None:
        """measure() 호출 후 USB 데이터가 업데이트되어야 합니다."""
        usb_data = [{"bus": "1", "device": "3", "vendor_id": "046d",
                     "product_id": "c077", "manufacturer": "Logitech",
                     "product": "Mouse", "path": "1-1"}]
        mock_gpio.return_value = []
        mock_usb.return_value = usb_data
        mock_serial.return_value = []

        from models.hardware_model import HardwareModel
        model = HardwareModel()
        model.measure()

        assert model.usbData == usb_data

    @patch("models.hardware_model.collect_serial_ports")
    @patch("models.hardware_model.collect_usb_devices")
    @patch("models.hardware_model.collect_gpio_pins")
    def test_measure_updates_serial_data(
        self, mock_gpio: MagicMock, mock_usb: MagicMock,
        mock_serial: MagicMock, qapp
    ) -> None:
        """measure() 호출 후 시리얼 데이터가 업데이트되어야 합니다."""
        serial_data = [{"path": "/dev/ttyUSB0", "type": "USB", "exists": True}]
        mock_gpio.return_value = []
        mock_usb.return_value = []
        mock_serial.return_value = serial_data

        from models.hardware_model import HardwareModel
        model = HardwareModel()
        model.measure()

        assert model.serialData == serial_data

    @patch("models.hardware_model.collect_serial_ports")
    @patch("models.hardware_model.collect_usb_devices")
    @patch("models.hardware_model.collect_gpio_pins")
    def test_measure_emits_signal_on_change(
        self, mock_gpio: MagicMock, mock_usb: MagicMock,
        mock_serial: MagicMock, qapp
    ) -> None:
        """데이터가 변경되면 시그널을 발행해야 합니다."""
        mock_gpio.return_value = [{"pin": 4, "direction": "out", "value": 0}]
        mock_usb.return_value = []
        mock_serial.return_value = []

        from models.hardware_model import HardwareModel
        model = HardwareModel()

        signal_spy = MagicMock()
        model.gpioDataChanged.connect(signal_spy)

        model.measure()

        signal_spy.assert_called_once()

    @patch("models.hardware_model.collect_serial_ports")
    @patch("models.hardware_model.collect_usb_devices")
    @patch("models.hardware_model.collect_gpio_pins")
    def test_measure_no_signal_when_data_unchanged(
        self, mock_gpio: MagicMock, mock_usb: MagicMock,
        mock_serial: MagicMock, qapp
    ) -> None:
        """데이터가 변경되지 않으면 시그널을 발행하지 않아야 합니다."""
        mock_gpio.return_value = []
        mock_usb.return_value = []
        mock_serial.return_value = []

        from models.hardware_model import HardwareModel
        model = HardwareModel()

        # 첫 번째 measure (빈 데이터 -> 빈 데이터, 변경 없음)
        model.measure()

        signal_spy = MagicMock()
        model.gpioDataChanged.connect(signal_spy)

        # 두 번째 measure (동일 데이터)
        model.measure()

        signal_spy.assert_not_called()
