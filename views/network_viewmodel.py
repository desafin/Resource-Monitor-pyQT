"""네트워크 모니터링을 위한 ViewModel.

NetworkModel과 NetworkMonitor를 소유하고 조합하여
QML 뷰에 네트워크 인터페이스 정보를 제공합니다.
"""
import logging
from typing import Any, Optional

from PyQt5.QtCore import (
    QObject,
    QThread,
    QTimer,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
)

from models.network_model import NetworkModel
from services.ping_worker import PingWorker
from utils.network_monitor import NetworkMonitor

logger = logging.getLogger(__name__)


class NetworkViewModel(QObject):
    """네트워크 모니터링 ViewModel.

    QML에서 네트워크 인터페이스 통계를 표시하기 위한 프로퍼티와 슬롯을 제공합니다.
    2초 간격으로 자동 업데이트합니다.
    """

    # 프로퍼티 변경 시그널
    networkModelChanged = pyqtSignal()
    pingTargetChanged = pyqtSignal()
    isPingingChanged = pyqtSignal()
    pingResultChanged = pyqtSignal()
    pingErrorChanged = pyqtSignal()

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)

        self._network_model = NetworkModel(self)
        self._monitor = NetworkMonitor()

        # 2초 간격 업데이트 타이머
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.setInterval(2000)

        # Ping 관련 상태
        self._ping_target: str = ""
        self._is_pinging: bool = False
        self._ping_result: str = ""
        self._ping_error: str = ""

        # Ping 워커 및 스레드 (지연 초기화)
        self._ping_thread: Optional[QThread] = None
        self._ping_worker: Optional[PingWorker] = None

        logger.info("NetworkViewModel이 초기화되었습니다")

    # --- Q_PROPERTY 정의 ---

    @pyqtProperty(QObject, notify=networkModelChanged, constant=True)
    def networkModel(self) -> NetworkModel:
        """QML에서 사용할 네트워크 모델을 반환합니다."""
        return self._network_model

    # --- 포맷팅 유틸리티 ---

    @pyqtSlot(float, result=str)
    @pyqtSlot(int, result=str)
    def formatSpeed(self, bytes_per_sec: float) -> str:
        """속도 값(bytes/sec)을 사람이 읽기 쉬운 형태로 포맷합니다.

        Args:
            bytes_per_sec: 초당 바이트 단위 속도.

        Returns:
            포맷된 문자열 (예: "1.5 MB/s").
        """
        if bytes_per_sec == 0:
            return "0 B/s"

        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        value = float(bytes_per_sec)
        unit_index = 0

        while value >= 1024.0 and unit_index < len(units) - 1:
            value /= 1024.0
            unit_index += 1

        if value == int(value):
            return f"{int(value)} {units[unit_index]}"
        return f"{value:.1f} {units[unit_index]}"

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

        if value == int(value):
            return f"{int(value)} {units[unit_index]}"
        return f"{value:.1f} {units[unit_index]}"

    # --- 데이터 수집 ---

    def _update(self) -> None:
        """네트워크 데이터를 수집하여 모델을 업데이트합니다."""
        net_data = self._monitor.measure()
        self._network_model.update_interfaces(net_data)

    def startTimer(self) -> None:
        """주기적 업데이트 타이머를 시작합니다."""
        self._update()  # 초기 데이터 수집
        self._timer.start()
        logger.info("네트워크 모니터링 타이머가 시작되었습니다 (2초 간격)")

    def stopTimer(self) -> None:
        """주기적 업데이트 타이머를 중지합니다."""
        self._timer.stop()
        logger.info("네트워크 모니터링 타이머가 중지되었습니다")

    # --- Ping 관련 프로퍼티 ---

    @pyqtProperty(str, notify=pingTargetChanged)
    def pingTarget(self) -> str:
        """현재 ping 대상을 반환합니다."""
        return self._ping_target

    @pingTarget.setter  # type: ignore[attr-defined]
    def pingTarget(self, value: str) -> None:
        """ping 대상을 설정합니다."""
        if self._ping_target != value:
            self._ping_target = value
            self.pingTargetChanged.emit()

    @pyqtProperty(bool, notify=isPingingChanged)
    def isPinging(self) -> bool:
        """ping 실행 중 여부를 반환합니다."""
        return self._is_pinging

    @pyqtProperty(str, notify=pingResultChanged)
    def pingResult(self) -> str:
        """마지막 ping 결과를 반환합니다."""
        return self._ping_result

    @pyqtProperty(str, notify=pingErrorChanged)
    def pingError(self) -> str:
        """마지막 ping 에러를 반환합니다."""
        return self._ping_error

    # --- Ping 슬롯 ---

    def _ensure_ping_thread(self) -> None:
        """ping 스레드와 워커를 필요 시 초기화합니다."""
        if self._ping_thread is None:
            self._ping_thread = QThread(self)
            self._ping_worker = PingWorker()
            self._ping_worker.moveToThread(self._ping_thread)
            self._ping_worker.pingStarted.connect(self._on_ping_started)
            self._ping_worker.pingFinished.connect(self._on_ping_finished)
            self._ping_worker.pingError.connect(self._on_ping_error)
            self._ping_thread.start()

    @pyqtSlot(str)
    def executePing(self, target: str) -> None:
        """지정된 대상에 ping을 실행합니다.

        백그라운드 스레드에서 PingWorker를 통해 실행됩니다.

        Args:
            target: ping 대상 호스트명 또는 IP 주소.
        """
        if self._is_pinging:
            return
        self._ping_error = ""
        self.pingErrorChanged.emit()
        self._ping_result = ""
        self.pingResultChanged.emit()
        self._ensure_ping_thread()
        self._ping_worker.execute_ping(target)

    def _on_ping_started(self) -> None:
        """ping 시작 시 호출되는 슬롯."""
        self._is_pinging = True
        self.isPingingChanged.emit()

    def _on_ping_finished(self, result: dict) -> None:
        """ping 완료 시 호출되는 슬롯."""
        self._is_pinging = False
        self.isPingingChanged.emit()

        # 결과를 읽기 쉬운 문자열로 포맷
        lines = [
            f"대상: {result.get('target', 'N/A')}",
            f"전송: {result.get('packets_transmitted', 0)}개, "
            f"수신: {result.get('packets_received', 0)}개, "
            f"손실: {result.get('packet_loss', 0):.1f}%",
            f"RTT (ms): min={result.get('rtt_min', 0):.1f}, "
            f"avg={result.get('rtt_avg', 0):.1f}, "
            f"max={result.get('rtt_max', 0):.1f}, "
            f"mdev={result.get('rtt_mdev', 0):.1f}",
        ]
        self._ping_result = "\n".join(lines)
        self.pingResultChanged.emit()

    def _on_ping_error(self, error_msg: str) -> None:
        """ping 에러 시 호출되는 슬롯."""
        self._is_pinging = False
        self.isPingingChanged.emit()
        self._ping_error = error_msg
        self.pingErrorChanged.emit()

    def cleanup(self) -> None:
        """ping 스레드를 안전하게 종료합니다."""
        if self._ping_thread is not None and self._ping_thread.isRunning():
            self._ping_thread.quit()
            self._ping_thread.wait(3000)
        logger.info("NetworkViewModel ping 스레드가 정리되었습니다")
