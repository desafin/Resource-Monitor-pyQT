"""프로세스 목록을 위한 QAbstractListModel 구현.

QML ListView에서 프로세스 데이터를 표시하기 위한 모델입니다.
각 프로세스의 PID, 이름, CPU/메모리 사용률, 상태 등을 역할(Role)로 제공합니다.
"""
import logging
from typing import Any, Optional

from PyQt5.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Qt,
    QVariant,
    pyqtSlot,
)

logger = logging.getLogger(__name__)


class ProcessModel(QAbstractListModel):
    """프로세스 목록 데이터를 QML에 제공하는 리스트 모델.

    커스텀 UserRole을 사용하여 프로세스 속성에 접근합니다.
    """

    # 커스텀 역할 정의
    PidRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    CpuRole = Qt.UserRole + 3
    MemRole = Qt.UserRole + 4
    StatusRole = Qt.UserRole + 5
    UserRole = Qt.UserRole + 6
    ThreadsRole = Qt.UserRole + 7
    PpidRole = Qt.UserRole + 8
    IndentLevelRole = Qt.UserRole + 9

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        self._processes: list[dict] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """모델의 행 수(프로세스 수)를 반환합니다."""
        if parent.isValid():
            return 0
        return len(self._processes)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """지정된 인덱스와 역할에 해당하는 데이터를 반환합니다."""
        if not index.isValid() or index.row() < 0 or index.row() >= len(self._processes):
            return None

        proc = self._processes[index.row()]

        if role == self.PidRole:
            return proc.get("pid", 0)
        elif role == self.NameRole:
            return proc.get("name", "")
        elif role == self.CpuRole:
            return proc.get("cpu_percent", 0.0)
        elif role == self.MemRole:
            return proc.get("memory_percent", 0.0)
        elif role == self.StatusRole:
            return proc.get("status", "unknown")
        elif role == self.UserRole:
            return proc.get("username", "")
        elif role == self.ThreadsRole:
            return proc.get("num_threads", 0)
        elif role == self.PpidRole:
            return proc.get("ppid", 0)
        elif role == self.IndentLevelRole:
            return proc.get("indent_level", 0)

        return None

    def roleNames(self) -> dict[int, bytes]:
        """QML에서 사용할 역할 이름 매핑을 반환합니다."""
        return {
            self.PidRole: b"pid",
            self.NameRole: b"name",
            self.CpuRole: b"cpuPercent",
            self.MemRole: b"memPercent",
            self.StatusRole: b"status",
            self.UserRole: b"user",
            self.ThreadsRole: b"threads",
            self.PpidRole: b"ppid",
            self.IndentLevelRole: b"indentLevel",
        }

    @pyqtSlot(list)
    def update_processes(self, process_list: list[dict]) -> None:
        """프로세스 목록을 새 데이터로 전체 교체합니다.

        beginResetModel/endResetModel을 사용하여 뷰에 변경을 알립니다.

        Args:
            process_list: 새로운 프로세스 딕셔너리 목록.
        """
        self.beginResetModel()
        self._processes = list(process_list)
        self.endResetModel()
