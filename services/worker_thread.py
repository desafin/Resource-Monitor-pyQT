"""프로세스 데이터 수집을 위한 QThread 기반 워커.

메인 스레드의 블로킹을 방지하기 위해 백그라운드 스레드에서
프로세스 목록을 주기적으로 수집합니다.
moveToThread() 패턴을 사용합니다.
"""
import logging
from typing import Optional

from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

from utils.process_monitor import collect_processes

logger = logging.getLogger(__name__)

# 프로세스 수집 주기 (밀리초)
_COLLECTION_INTERVAL_MS = 2000


class ProcessWorker(QObject):
    """백그라운드 스레드에서 프로세스 목록을 수집하는 워커.

    moveToThread() 패턴과 함께 사용됩니다.
    start_collecting() 슬롯으로 수집을 시작하고,
    finished 시그널로 결과를 전달합니다.
    """

    # 프로세스 데이터 수집 완료 시그널
    finished = pyqtSignal(list)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._timer: Optional[QTimer] = None
        self._running: bool = False

    @pyqtSlot()
    def start_collecting(self) -> None:
        """프로세스 데이터 주기적 수집을 시작합니다.

        내부 QTimer를 생성하여 _COLLECTION_INTERVAL_MS 간격으로
        collect_processes()를 호출합니다.
        """
        if self._running:
            return

        self._running = True
        self._timer = QTimer()
        self._timer.timeout.connect(self._collect)
        self._timer.start(_COLLECTION_INTERVAL_MS)

        # 즉시 첫 번째 수집 실행
        self._collect()
        logger.info("프로세스 수집 워커가 시작되었습니다 (간격: %dms)", _COLLECTION_INTERVAL_MS)

    @pyqtSlot()
    def stop_collecting(self) -> None:
        """프로세스 데이터 수집을 중지합니다."""
        self._running = False
        if self._timer is not None:
            self._timer.stop()
            self._timer.deleteLater()
            self._timer = None
        logger.info("프로세스 수집 워커가 중지되었습니다")

    def _collect(self) -> None:
        """프로세스 목록을 수집하고 finished 시그널을 발생시킵니다."""
        try:
            processes = collect_processes()
            self.finished.emit(processes)
        except Exception as e:
            logger.error("프로세스 수집 중 오류 발생: %s", e)
            self.finished.emit([])
