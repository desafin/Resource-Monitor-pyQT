"""하드웨어 인터페이스 모니터링 모델.

GPIO, USB, 시리얼 장치 데이터를 수집하고 QML에 노출하는 QObject 모델입니다.
"""
import logging
from typing import Any, Optional

from PyQt5.QtCore import (
    QObject,
    QVariant,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
)

from utils.gpio_monitor import collect_gpio_pins, is_gpio_available
from utils.usb_monitor import collect_usb_devices, is_usb_available
from utils.serial_monitor import collect_serial_ports, is_serial_available

logger = logging.getLogger(__name__)


class HardwareModel(QObject):
    """하드웨어 인터페이스 데이터를 QML에 제공하는 모델.

    GPIO 핀, USB 장치, 시리얼 포트 정보를 수집하고
    변경 시 시그널을 발행합니다.
    """

    # 변경 시그널
    gpioDataChanged = pyqtSignal()
    usbDataChanged = pyqtSignal()
    serialDataChanged = pyqtSignal()
    gpioAvailableChanged = pyqtSignal()
    usbAvailableChanged = pyqtSignal()
    serialAvailableChanged = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._gpio_data: list[dict] = []
        self._usb_data: list[dict] = []
        self._serial_data: list[dict] = []
        logger.info("HardwareModel이 초기화되었습니다")

    # --- GPIO 프로퍼티 ---

    @pyqtProperty("QVariant", notify=gpioDataChanged)
    def gpioData(self) -> list[dict]:
        """GPIO 핀 데이터 목록을 반환합니다."""
        return self._gpio_data

    @pyqtProperty(bool, notify=gpioAvailableChanged)
    def gpioAvailable(self) -> bool:
        """GPIO 인터페이스 사용 가능 여부를 반환합니다."""
        return is_gpio_available()

    # --- USB 프로퍼티 ---

    @pyqtProperty("QVariant", notify=usbDataChanged)
    def usbData(self) -> list[dict]:
        """USB 장치 데이터 목록을 반환합니다."""
        return self._usb_data

    @pyqtProperty(bool, notify=usbAvailableChanged)
    def usbAvailable(self) -> bool:
        """USB 인터페이스 사용 가능 여부를 반환합니다."""
        return is_usb_available()

    # --- 시리얼 프로퍼티 ---

    @pyqtProperty("QVariant", notify=serialDataChanged)
    def serialData(self) -> list[dict]:
        """시리얼 포트 데이터 목록을 반환합니다."""
        return self._serial_data

    @pyqtProperty(bool, notify=serialAvailableChanged)
    def serialAvailable(self) -> bool:
        """시리얼 인터페이스 사용 가능 여부를 반환합니다."""
        return is_serial_available()

    # --- 데이터 수집 ---

    @pyqtSlot()
    def measure(self) -> None:
        """모든 하드웨어 데이터를 수집합니다.

        GPIO, USB, 시리얼 데이터를 각각 수집하고,
        데이터가 변경된 경우에만 시그널을 발행합니다.
        """
        # GPIO 데이터 수집
        new_gpio = collect_gpio_pins()
        if new_gpio != self._gpio_data:
            self._gpio_data = new_gpio
            self.gpioDataChanged.emit()

        # USB 데이터 수집
        new_usb = collect_usb_devices()
        if new_usb != self._usb_data:
            self._usb_data = new_usb
            self.usbDataChanged.emit()

        # 시리얼 데이터 수집
        new_serial = collect_serial_ports()
        if new_serial != self._serial_data:
            self._serial_data = new_serial
            self.serialDataChanged.emit()
