"""프로세스 관리를 위한 ViewModel.

ProcessModel, ProcessSortFilterModel, ProcessWorker를 소유하고 조합하여
QML 뷰에 프로세스 관리 기능을 제공합니다.
"""
import logging
import signal
from typing import Any, Optional

from PyQt5.QtCore import (
    QObject,
    QThread,
    Qt,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
)

from models.process_model import ProcessModel
from models.process_sort_filter_model import ProcessSortFilterModel
from services.worker_thread import ProcessWorker
from utils.process_monitor import send_signal, change_nice, get_process_details
from utils.process_tree import build_process_tree

logger = logging.getLogger(__name__)


class ProcessViewModel(QObject):
    """프로세스 관리 ViewModel.

    QML에서 프로세스 목록 표시, 검색/정렬, 프로세스 제어 기능을 제공합니다.
    백그라운드 스레드에서 프로세스 데이터를 수집합니다.
    """

    # 프로퍼티 변경 시그널
    searchTextChanged = pyqtSignal()
    sortColumnChanged = pyqtSignal()
    sortOrderChanged = pyqtSignal()
    processModelChanged = pyqtSignal()
    isTreeModeChanged = pyqtSignal()

    # 프로세스 상세 정보 준비 시그널
    processDetailsReady = pyqtSignal("QVariant")

    # 에러 발생 시그널
    errorOccurred = pyqtSignal(str)

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)

        # 트리 모드 상태
        self._is_tree_mode: bool = False

        # 모델 생성
        self._process_model = ProcessModel(self)
        self._sort_filter_model = ProcessSortFilterModel(self)
        self._sort_filter_model.setSourceModel(self._process_model)

        # 워커 스레드 설정 (moveToThread 패턴)
        self._worker_thread = QThread(self)
        self._worker = ProcessWorker()
        self._worker.moveToThread(self._worker_thread)

        # 시그널 연결
        self._worker.finished.connect(self._on_processes_collected)
        self._worker_thread.started.connect(self._worker.start_collecting)

        # 워커 스레드 시작
        self._worker_thread.start()
        logger.info("ProcessViewModel이 초기화되었습니다")

    # --- Q_PROPERTY 정의 ---

    @pyqtProperty(QObject, notify=processModelChanged, constant=True)
    def processModel(self) -> ProcessSortFilterModel:
        """QML에서 사용할 프록시 모델을 반환합니다."""
        return self._sort_filter_model

    @pyqtProperty(str, notify=searchTextChanged)
    def searchText(self) -> str:
        """현재 검색 텍스트를 반환합니다."""
        return self._sort_filter_model.searchText

    @searchText.setter  # type: ignore[attr-defined]
    def searchText(self, text: str) -> None:
        """검색 텍스트를 설정합니다."""
        if self._sort_filter_model.searchText != text:
            self._sort_filter_model.searchText = text
            self.searchTextChanged.emit()

    @pyqtProperty(str, notify=sortColumnChanged)
    def sortColumn(self) -> str:
        """현재 정렬 컬럼을 반환합니다."""
        return self._sort_filter_model.sortColumn

    @sortColumn.setter  # type: ignore[attr-defined]
    def sortColumn(self, column: str) -> None:
        """정렬 컬럼을 설정합니다."""
        if self._sort_filter_model.sortColumn != column:
            self._sort_filter_model.sortColumn = column
            self.sortColumnChanged.emit()

    @pyqtProperty(int, notify=sortOrderChanged)
    def sortOrder(self) -> int:
        """현재 정렬 순서를 반환합니다."""
        return self._sort_filter_model.sortOrder

    @sortOrder.setter  # type: ignore[attr-defined]
    def sortOrder(self, order: int) -> None:
        """정렬 순서를 설정합니다."""
        if self._sort_filter_model.sortOrder != order:
            self._sort_filter_model.sortOrder = order
            self.sortOrderChanged.emit()

    @pyqtProperty(bool, notify=isTreeModeChanged)
    def isTreeMode(self) -> bool:
        """트리 모드 활성화 여부를 반환합니다."""
        return self._is_tree_mode

    @pyqtSlot()
    def toggleTreeMode(self) -> None:
        """트리 모드를 토글합니다."""
        self._is_tree_mode = not self._is_tree_mode
        self.isTreeModeChanged.emit()
        logger.info("트리 모드: %s", "활성화" if self._is_tree_mode else "비활성화")

    @pyqtSlot(int)
    def getProcessDetails(self, pid: int) -> None:
        """프로세스 상세 정보를 조회하여 processDetailsReady 시그널로 전달합니다."""
        details = get_process_details(pid)
        self.processDetailsReady.emit(details)

    # --- 프로세스 제어 슬롯 ---

    @pyqtSlot(int)
    def killProcess(self, pid: int) -> None:
        """프로세스를 강제 종료합니다 (SIGKILL)."""
        success, message = send_signal(pid, signal.SIGKILL)
        if not success:
            self.errorOccurred.emit(message)
            logger.warning("프로세스 강제 종료 실패 (PID=%d): %s", pid, message)

    @pyqtSlot(int)
    def terminateProcess(self, pid: int) -> None:
        """프로세스를 정상 종료합니다 (SIGTERM)."""
        success, message = send_signal(pid, signal.SIGTERM)
        if not success:
            self.errorOccurred.emit(message)
            logger.warning("프로세스 종료 실패 (PID=%d): %s", pid, message)

    @pyqtSlot(int)
    def suspendProcess(self, pid: int) -> None:
        """프로세스를 일시 중지합니다 (SIGSTOP)."""
        success, message = send_signal(pid, signal.SIGSTOP)
        if not success:
            self.errorOccurred.emit(message)
            logger.warning("프로세스 일시 중지 실패 (PID=%d): %s", pid, message)

    @pyqtSlot(int)
    def resumeProcess(self, pid: int) -> None:
        """프로세스를 재개합니다 (SIGCONT)."""
        success, message = send_signal(pid, signal.SIGCONT)
        if not success:
            self.errorOccurred.emit(message)
            logger.warning("프로세스 재개 실패 (PID=%d): %s", pid, message)

    @pyqtSlot(int, int)
    def changeNice(self, pid: int, value: int) -> None:
        """프로세스 우선순위를 변경합니다."""
        success, message = change_nice(pid, value)
        if not success:
            self.errorOccurred.emit(message)
            logger.warning("우선순위 변경 실패 (PID=%d): %s", pid, message)

    # --- 내부 슬롯 ---

    @pyqtSlot(list)
    def _on_processes_collected(self, processes: list[dict]) -> None:
        """워커로부터 프로세스 데이터를 수신하여 모델을 업데이트합니다.

        트리 모드 활성화 시 프로세스를 트리 구조로 변환합니다.
        """
        if self._is_tree_mode:
            processes = build_process_tree(processes)
        self._process_model.update_processes(processes)

    # --- 라이프사이클 관리 ---

    @pyqtSlot()
    def cleanup(self) -> None:
        """워커 스레드를 안전하게 종료합니다."""
        if self._worker_thread.isRunning():
            self._worker.stop_collecting()
            self._worker_thread.quit()
            if not self._worker_thread.wait(3000):
                logger.warning("워커 스레드가 3초 내에 종료되지 않아 강제 종료합니다")
                self._worker_thread.terminate()
                self._worker_thread.wait()
        logger.info("ProcessViewModel 정리 완료")
