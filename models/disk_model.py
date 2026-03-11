"""디스크 파티션 목록을 위한 QAbstractListModel 구현.

QML ListView에서 디스크 파티션 데이터를 표시하기 위한 모델입니다.
각 파티션의 장치명, 마운트 포인트, 사용률 등을 역할(Role)로 제공합니다.
"""
import logging
from typing import Any, Optional

from PyQt5.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Qt,
    pyqtSlot,
)

logger = logging.getLogger(__name__)


class DiskModel(QAbstractListModel):
    """디스크 파티션 데이터를 QML에 제공하는 리스트 모델.

    커스텀 UserRole을 사용하여 디스크 속성에 접근합니다.
    """

    # 커스텀 역할 정의
    DeviceRole = Qt.UserRole + 1
    MountpointRole = Qt.UserRole + 2
    FstypeRole = Qt.UserRole + 3
    TotalRole = Qt.UserRole + 4
    UsedRole = Qt.UserRole + 5
    FreeRole = Qt.UserRole + 6
    PercentRole = Qt.UserRole + 7
    ReadBytesRole = Qt.UserRole + 8
    WriteBytesRole = Qt.UserRole + 9

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        self._disks: list[dict] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """모델의 행 수(디스크 파티션 수)를 반환합니다."""
        if parent.isValid():
            return 0
        return len(self._disks)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """지정된 인덱스와 역할에 해당하는 데이터를 반환합니다."""
        if not index.isValid() or index.row() < 0 or index.row() >= len(self._disks):
            return None

        disk = self._disks[index.row()]

        if role == self.DeviceRole:
            return disk.get("device", "")
        elif role == self.MountpointRole:
            return disk.get("mountpoint", "")
        elif role == self.FstypeRole:
            return disk.get("fstype", "")
        elif role == self.TotalRole:
            return disk.get("total", 0)
        elif role == self.UsedRole:
            return disk.get("used", 0)
        elif role == self.FreeRole:
            return disk.get("free", 0)
        elif role == self.PercentRole:
            return disk.get("percent", 0.0)
        elif role == self.ReadBytesRole:
            return disk.get("read_bytes", 0)
        elif role == self.WriteBytesRole:
            return disk.get("write_bytes", 0)

        return None

    def roleNames(self) -> dict[int, bytes]:
        """QML에서 사용할 역할 이름 매핑을 반환합니다."""
        return {
            self.DeviceRole: b"device",
            self.MountpointRole: b"mountpoint",
            self.FstypeRole: b"fstype",
            self.TotalRole: b"total",
            self.UsedRole: b"used",
            self.FreeRole: b"free",
            self.PercentRole: b"percent",
            self.ReadBytesRole: b"readBytes",
            self.WriteBytesRole: b"writeBytes",
        }

    @pyqtSlot(list)
    def update_disks(self, disk_list: list[dict]) -> None:
        """디스크 목록을 새 데이터로 전체 교체합니다.

        beginResetModel/endResetModel을 사용하여 뷰에 변경을 알립니다.

        Args:
            disk_list: 새로운 디스크 딕셔너리 목록.
        """
        self.beginResetModel()
        self._disks = list(disk_list)
        self.endResetModel()
