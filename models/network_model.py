"""네트워크 인터페이스 목록을 위한 QAbstractListModel 구현.

QML ListView에서 네트워크 인터페이스 데이터를 표시하기 위한 모델입니다.
각 인터페이스의 전송량, 속도 등을 역할(Role)로 제공합니다.
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


class NetworkModel(QAbstractListModel):
    """네트워크 인터페이스 데이터를 QML에 제공하는 리스트 모델.

    커스텀 UserRole을 사용하여 네트워크 속성에 접근합니다.
    """

    # 커스텀 역할 정의
    InterfaceRole = Qt.UserRole + 1
    BytesSentRole = Qt.UserRole + 2
    BytesRecvRole = Qt.UserRole + 3
    PacketsSentRole = Qt.UserRole + 4
    PacketsRecvRole = Qt.UserRole + 5
    SpeedUpRole = Qt.UserRole + 6
    SpeedDownRole = Qt.UserRole + 7
    IpAddressRole = Qt.UserRole + 8
    Ipv6AddressRole = Qt.UserRole + 9
    MacAddressRole = Qt.UserRole + 10
    NetmaskRole = Qt.UserRole + 11
    BroadcastRole = Qt.UserRole + 12
    MtuRole = Qt.UserRole + 13
    IsUpRole = Qt.UserRole + 14
    LinkSpeedRole = Qt.UserRole + 15
    DuplexRole = Qt.UserRole + 16

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        self._interfaces: list[dict] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """모델의 행 수(네트워크 인터페이스 수)를 반환합니다."""
        if parent.isValid():
            return 0
        return len(self._interfaces)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """지정된 인덱스와 역할에 해당하는 데이터를 반환합니다."""
        if not index.isValid() or index.row() < 0 or index.row() >= len(self._interfaces):
            return None

        iface = self._interfaces[index.row()]

        if role == self.InterfaceRole:
            return iface.get("interface", "")
        elif role == self.BytesSentRole:
            return iface.get("bytes_sent", 0)
        elif role == self.BytesRecvRole:
            return iface.get("bytes_recv", 0)
        elif role == self.PacketsSentRole:
            return iface.get("packets_sent", 0)
        elif role == self.PacketsRecvRole:
            return iface.get("packets_recv", 0)
        elif role == self.SpeedUpRole:
            return iface.get("speed_up", 0.0)
        elif role == self.SpeedDownRole:
            return iface.get("speed_down", 0.0)
        elif role == self.IpAddressRole:
            return iface.get("ip_address", "N/A")
        elif role == self.Ipv6AddressRole:
            return iface.get("ipv6_address", "N/A")
        elif role == self.MacAddressRole:
            return iface.get("mac_address", "N/A")
        elif role == self.NetmaskRole:
            return iface.get("netmask", "N/A")
        elif role == self.BroadcastRole:
            return iface.get("broadcast", "N/A")
        elif role == self.MtuRole:
            return iface.get("mtu", 0)
        elif role == self.IsUpRole:
            return iface.get("is_up", False)
        elif role == self.LinkSpeedRole:
            return iface.get("link_speed", 0)
        elif role == self.DuplexRole:
            return iface.get("duplex", "unknown")

        return None

    def roleNames(self) -> dict[int, bytes]:
        """QML에서 사용할 역할 이름 매핑을 반환합니다."""
        return {
            self.InterfaceRole: b"iface",
            self.BytesSentRole: b"bytesSent",
            self.BytesRecvRole: b"bytesRecv",
            self.PacketsSentRole: b"packetsSent",
            self.PacketsRecvRole: b"packetsRecv",
            self.SpeedUpRole: b"speedUp",
            self.SpeedDownRole: b"speedDown",
            self.IpAddressRole: b"ipAddress",
            self.Ipv6AddressRole: b"ipv6Address",
            self.MacAddressRole: b"macAddress",
            self.NetmaskRole: b"netmask",
            self.BroadcastRole: b"broadcast",
            self.MtuRole: b"mtu",
            self.IsUpRole: b"isUp",
            self.LinkSpeedRole: b"linkSpeed",
            self.DuplexRole: b"duplex",
        }

    @pyqtSlot(list)
    def update_interfaces(self, interface_list: list[dict]) -> None:
        """네트워크 인터페이스 목록을 새 데이터로 전체 교체합니다.

        beginResetModel/endResetModel을 사용하여 뷰에 변경을 알립니다.

        Args:
            interface_list: 새로운 네트워크 인터페이스 딕셔너리 목록.
        """
        self.beginResetModel()
        self._interfaces = list(interface_list)
        self.endResetModel()
