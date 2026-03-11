"""디스크 모니터링을 위한 ViewModel.

DiskModel과 DiskMonitor를 소유하고 조합하여
QML 뷰에 디스크 사용량 정보를 제공합니다.
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

from models.disk_model import DiskModel
from utils.disk_monitor import DiskMonitor

logger = logging.getLogger(__name__)


class DiskViewModel(QObject):
    """디스크 모니터링 ViewModel.

    QML에서 디스크 파티션 사용량을 표시하기 위한 프로퍼티와 슬롯을 제공합니다.
    5초 간격으로 자동 업데이트합니다.
    """

    # 프로퍼티 변경 시그널
    diskModelChanged = pyqtSignal()

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)

        self._disk_model = DiskModel(self)
        self._monitor = DiskMonitor()

        # 5초 간격 업데이트 타이머
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.setInterval(5000)

        logger.info("DiskViewModel이 초기화되었습니다")

    # --- Q_PROPERTY 정의 ---

    @pyqtProperty(QObject, notify=diskModelChanged, constant=True)
    def diskModel(self) -> DiskModel:
        """QML에서 사용할 디스크 모델을 반환합니다."""
        return self._disk_model

    # --- 포맷팅 유틸리티 ---

    @pyqtSlot(float, result=str)
    @pyqtSlot(int, result=str)
    def formatBytes(self, bytes_value: float) -> str:
        """바이트 값을 사람이 읽기 쉬운 형태로 포맷합니다.

        Args:
            bytes_value: 바이트 단위 값.

        Returns:
            포맷된 문자열 (예: "1.5 GB").
        """
        if bytes_value == 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        value = float(bytes_value)
        unit_index = 0

        while value >= 1024.0 and unit_index < len(units) - 1:
            value /= 1024.0
            unit_index += 1

        # 소수점 이하가 0이면 정수로 표시
        if value == int(value):
            return f"{int(value)} {units[unit_index]}"
        return f"{value:.1f} {units[unit_index]}"

    # --- 데이터 수집 ---

    @pyqtSlot()
    def refresh(self) -> None:
        """디스크 데이터를 수동으로 수집하여 모델을 업데이트합니다."""
        disk_data = self._monitor.measure()
        self._disk_model.update_disks(disk_data)

    def startTimer(self) -> None:
        """주기적 업데이트 타이머를 시작합니다."""
        self.refresh()  # 초기 데이터 수집
        self._timer.start()
        logger.info("디스크 모니터링 타이머가 시작되었습니다 (5초 간격)")

    def stopTimer(self) -> None:
        """주기적 업데이트 타이머를 중지합니다."""
        self._timer.stop()
        logger.info("디스크 모니터링 타이머가 중지되었습니다")
