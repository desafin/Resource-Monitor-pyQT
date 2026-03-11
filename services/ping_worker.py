"""Ping 실행을 위한 QObject 기반 워커.

메인 스레드의 블로킹을 방지하기 위해 QThread와 함께 사용됩니다.
moveToThread() 패턴을 따릅니다.
"""
import logging
from typing import Any, Dict, Optional

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from utils.ping_util import run_ping

logger = logging.getLogger(__name__)


class PingWorker(QObject):
    """백그라운드 스레드에서 ping을 실행하는 워커.

    execute_ping() 슬롯으로 ping을 시작하고,
    결과에 따라 pingFinished 또는 pingError 시그널을 발신합니다.
    """

    # ping 시작 시그널
    pingStarted = pyqtSignal()
    # ping 성공 완료 시그널 (결과 딕셔너리)
    pingFinished = pyqtSignal(dict)
    # ping 에러 시그널 (에러 메시지)
    pingError = pyqtSignal(str)

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)

    @pyqtSlot(str)
    def execute_ping(self, target: str) -> None:
        """지정된 대상에 ping을 실행합니다.

        pingStarted 시그널을 먼저 발신한 후,
        성공 시 pingFinished, 실패 시 pingError 시그널을 발신합니다.

        Args:
            target: ping 대상 호스트명 또는 IP 주소.
        """
        self.pingStarted.emit()

        try:
            result = run_ping(target)

            if "error" in result:
                self.pingError.emit(result["error"])
            else:
                self.pingFinished.emit(result)
        except Exception as e:
            logger.error("ping 실행 중 예외 발생: %s", e)
            self.pingError.emit(str(e))
