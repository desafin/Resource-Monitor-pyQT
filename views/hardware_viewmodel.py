"""하드웨어 모니터링을 위한 ViewModel.

HardwareModel을 소유하고 QML 뷰에 하드웨어 인터페이스
정보를 제공합니다. 3초 간격으로 주기적 업데이트를 수행합니다.
"""
import logging
from typing import Any, Optional

from PyQt5.QtCore import (
    QObject,
    QTimer,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
)

from models.hardware_model import HardwareModel

logger = logging.getLogger(__name__)


class HardwareViewModel(QObject):
    """하드웨어 모니터링 ViewModel.

    QML에서 GPIO, USB, 시리얼 장치 정보를 표시하기 위한
    프로퍼티와 슬롯을 제공합니다.
    """

    # 프로퍼티 변경 시그널
    gpioDataChanged = pyqtSignal()
    usbDataChanged = pyqtSignal()
    serialDataChanged = pyqtSignal()
    gpioAvailableChanged = pyqtSignal()
    usbAvailableChanged = pyqtSignal()
    serialAvailableChanged = pyqtSignal()
    gpioCountChanged = pyqtSignal()
    usbCountChanged = pyqtSignal()
    serialCountChanged = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)

        self._model = HardwareModel(self)

        # 모델 시그널을 ViewModel 시그널로 연결
        self._model.gpioDataChanged.connect(self._on_gpio_changed)
        self._model.usbDataChanged.connect(self._on_usb_changed)
        self._model.serialDataChanged.connect(self._on_serial_changed)

        # 3초 간격 업데이트 타이머
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.setInterval(3000)

        logger.info("HardwareViewModel이 초기화되었습니다")

    # --- 시그널 핸들러 ---

    def _on_gpio_changed(self) -> None:
        """GPIO 데이터 변경 시 관련 시그널을 모두 발행합니다."""
        self.gpioDataChanged.emit()
        self.gpioCountChanged.emit()

    def _on_usb_changed(self) -> None:
        """USB 데이터 변경 시 관련 시그널을 모두 발행합니다."""
        self.usbDataChanged.emit()
        self.usbCountChanged.emit()

    def _on_serial_changed(self) -> None:
        """시리얼 데이터 변경 시 관련 시그널을 모두 발행합니다."""
        self.serialDataChanged.emit()
        self.serialCountChanged.emit()

    # --- 데이터 프로퍼티 (모델에서 프록시) ---

    @pyqtProperty("QVariant", notify=gpioDataChanged)
    def gpioData(self) -> list[dict]:
        """GPIO 핀 데이터 목록을 반환합니다."""
        return self._model.gpioData

    @pyqtProperty("QVariant", notify=usbDataChanged)
    def usbData(self) -> list[dict]:
        """USB 장치 데이터 목록을 반환합니다."""
        return self._model.usbData

    @pyqtProperty("QVariant", notify=serialDataChanged)
    def serialData(self) -> list[dict]:
        """시리얼 포트 데이터 목록을 반환합니다."""
        return self._model.serialData

    # --- 가용성 프로퍼티 ---

    @pyqtProperty(bool, notify=gpioAvailableChanged)
    def gpioAvailable(self) -> bool:
        """GPIO 인터페이스 사용 가능 여부를 반환합니다."""
        return self._model.gpioAvailable

    @pyqtProperty(bool, notify=usbAvailableChanged)
    def usbAvailable(self) -> bool:
        """USB 인터페이스 사용 가능 여부를 반환합니다."""
        return self._model.usbAvailable

    @pyqtProperty(bool, notify=serialAvailableChanged)
    def serialAvailable(self) -> bool:
        """시리얼 인터페이스 사용 가능 여부를 반환합니다."""
        return self._model.serialAvailable

    # --- 카운트 프로퍼티 ---

    @pyqtProperty(int, notify=gpioCountChanged)
    def gpioCount(self) -> int:
        """GPIO 핀 수를 반환합니다."""
        return len(self._model.gpioData)

    @pyqtProperty(int, notify=usbCountChanged)
    def usbCount(self) -> int:
        """USB 장치 수를 반환합니다."""
        return len(self._model.usbData)

    @pyqtProperty(int, notify=serialCountChanged)
    def serialCount(self) -> int:
        """시리얼 포트 수를 반환합니다."""
        return len(self._model.serialData)

    # --- 데이터 수집 ---

    @pyqtSlot()
    def refresh(self) -> None:
        """하드웨어 데이터를 수동으로 수집합니다."""
        self._model.measure()

    def startTimer(self) -> None:
        """주기적 업데이트 타이머를 시작합니다."""
        self.refresh()  # 초기 데이터 수집
        self._timer.start()
        logger.info("하드웨어 모니터링 타이머가 시작되었습니다 (3초 간격)")

    def stopTimer(self) -> None:
        """주기적 업데이트 타이머를 중지합니다."""
        self._timer.stop()
        logger.info("하드웨어 모니터링 타이머가 중지되었습니다")
