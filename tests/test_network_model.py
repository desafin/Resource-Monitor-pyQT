"""models/network_model.py에 대한 사양 테스트.

NetworkModel(QAbstractListModel)의 data(), rowCount(), roleNames(),
update_interfaces() 메서드를 검증합니다.
"""
import pytest
from PyQt5.QtCore import Qt, QModelIndex

from models.network_model import NetworkModel


@pytest.fixture
def sample_network_data() -> list[dict]:
    """테스트용 네트워크 데이터 목록을 반환하는 fixture."""
    return [
        {
            "interface": "eth0",
            "bytes_sent": 1_000_000,
            "bytes_recv": 5_000_000,
            "packets_sent": 1000,
            "packets_recv": 5000,
            "speed_up": 500.0,
            "speed_down": 2500.0,
            "ip_address": "192.168.1.10",
            "ipv6_address": "fe80::1",
            "mac_address": "aa:bb:cc:dd:ee:ff",
            "netmask": "255.255.255.0",
            "broadcast": "192.168.1.255",
            "mtu": 1500,
            "is_up": True,
            "link_speed": 1000,
            "duplex": "full",
        },
        {
            "interface": "wlan0",
            "bytes_sent": 500_000,
            "bytes_recv": 2_000_000,
            "packets_sent": 500,
            "packets_recv": 2000,
            "speed_up": 250.0,
            "speed_down": 1000.0,
            "ip_address": "10.0.0.5",
            "ipv6_address": "N/A",
            "mac_address": "11:22:33:44:55:66",
            "netmask": "255.0.0.0",
            "broadcast": "10.255.255.255",
            "mtu": 1500,
            "is_up": True,
            "link_speed": 300,
            "duplex": "unknown",
        },
    ]


class TestNetworkModelInit:
    """NetworkModel 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """NetworkModel 인스턴스를 생성할 수 있어야 합니다."""
        model = NetworkModel()
        assert model is not None

    def test_initial_row_count_is_zero(self, qapp) -> None:
        """초기 상태에서 행 수는 0이어야 합니다."""
        model = NetworkModel()
        assert model.rowCount() == 0


class TestNetworkModelRoleNames:
    """NetworkModel의 roleNames()를 검증합니다."""

    def test_role_names_not_empty(self, qapp) -> None:
        """roleNames()는 비어있지 않아야 합니다."""
        model = NetworkModel()
        roles = model.roleNames()
        assert len(roles) > 0

    def test_role_names_has_all_required(self, qapp) -> None:
        """roleNames()에 모든 필수 역할이 포함되어야 합니다."""
        model = NetworkModel()
        roles = model.roleNames()
        role_values = {bytes(v).decode() for v in roles.values()}
        required = {
            "iface", "bytesSent", "bytesRecv",
            "packetsSent", "packetsRecv",
            "speedUp", "speedDown",
            "ipAddress", "ipv6Address", "macAddress",
            "netmask", "broadcast", "mtu",
            "isUp", "linkSpeed", "duplex",
        }
        assert required.issubset(role_values), (
            f"누락된 역할: {required - role_values}"
        )


class TestNetworkModelUpdateInterfaces:
    """NetworkModel.update_interfaces() 메서드를 검증합니다."""

    def test_update_sets_row_count(self, qapp, sample_network_data) -> None:
        """update_interfaces() 후 rowCount()가 데이터 수와 일치해야 합니다."""
        model = NetworkModel()
        model.update_interfaces(sample_network_data)
        assert model.rowCount() == len(sample_network_data)

    def test_update_with_empty_list(self, qapp) -> None:
        """빈 목록으로 업데이트하면 rowCount()가 0이어야 합니다."""
        model = NetworkModel()
        model.update_interfaces([{
            "interface": "eth0", "bytes_sent": 0, "bytes_recv": 0,
            "packets_sent": 0, "packets_recv": 0,
            "speed_up": 0.0, "speed_down": 0.0,
        }])
        assert model.rowCount() == 1
        model.update_interfaces([])
        assert model.rowCount() == 0

    def test_update_replaces_previous_data(self, qapp) -> None:
        """update_interfaces()는 이전 데이터를 완전히 교체해야 합니다."""
        model = NetworkModel()
        model.update_interfaces([{
            "interface": "eth0", "bytes_sent": 0, "bytes_recv": 0,
            "packets_sent": 0, "packets_recv": 0,
            "speed_up": 0.0, "speed_down": 0.0,
        }])
        model.update_interfaces([
            {"interface": "eth0", "bytes_sent": 0, "bytes_recv": 0,
             "packets_sent": 0, "packets_recv": 0,
             "speed_up": 0.0, "speed_down": 0.0},
            {"interface": "wlan0", "bytes_sent": 0, "bytes_recv": 0,
             "packets_sent": 0, "packets_recv": 0,
             "speed_up": 0.0, "speed_down": 0.0},
        ])
        assert model.rowCount() == 2


class TestNetworkModelData:
    """NetworkModel.data() 메서드를 검증합니다."""

    @pytest.fixture
    def loaded_model(self, qapp, sample_network_data) -> NetworkModel:
        """데이터가 로드된 NetworkModel을 반환합니다."""
        model = NetworkModel()
        model.update_interfaces(sample_network_data)
        return model

    def _get_role_id(self, model: NetworkModel, role_name: str) -> int:
        """역할 이름으로 역할 ID를 찾아 반환합니다."""
        roles = model.roleNames()
        for role_id, name in roles.items():
            if bytes(name).decode() == role_name:
                return role_id
        raise ValueError(f"역할 '{role_name}'을 찾을 수 없습니다")

    def test_data_returns_interface(self, loaded_model, sample_network_data) -> None:
        """interface 역할로 data()를 호출하면 올바른 인터페이스명을 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "iface")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["interface"]

    def test_data_returns_bytes_sent(self, loaded_model, sample_network_data) -> None:
        """bytesSent 역할로 data()를 호출하면 올바른 전송 바이트를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "bytesSent")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["bytes_sent"]

    def test_data_returns_speed_down(self, loaded_model, sample_network_data) -> None:
        """speedDown 역할로 data()를 호출하면 올바른 다운로드 속도를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "speedDown")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["speed_down"]

    def test_data_invalid_index_returns_none(self, loaded_model) -> None:
        """유효하지 않은 인덱스로 data()를 호출하면 None을 반환해야 합니다."""
        index = loaded_model.index(999, 0)
        role_id = self._get_role_id(loaded_model, "iface")
        assert loaded_model.data(index, role_id) is None

    def test_data_second_interface(self, loaded_model, sample_network_data) -> None:
        """두 번째 인터페이스의 데이터를 올바르게 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "iface")
        index = loaded_model.index(1, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[1]["interface"]

    def test_data_returns_ip_address(self, loaded_model, sample_network_data) -> None:
        """ipAddress 역할로 data()를 호출하면 올바른 IP 주소를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "ipAddress")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["ip_address"]

    def test_data_returns_ipv6_address(self, loaded_model, sample_network_data) -> None:
        """ipv6Address 역할로 data()를 호출하면 올바른 IPv6 주소를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "ipv6Address")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["ipv6_address"]

    def test_data_returns_mac_address(self, loaded_model, sample_network_data) -> None:
        """macAddress 역할로 data()를 호출하면 올바른 MAC 주소를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "macAddress")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["mac_address"]

    def test_data_returns_mtu(self, loaded_model, sample_network_data) -> None:
        """mtu 역할로 data()를 호출하면 올바른 MTU를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "mtu")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["mtu"]

    def test_data_returns_is_up(self, loaded_model, sample_network_data) -> None:
        """isUp 역할로 data()를 호출하면 올바른 활성화 상태를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "isUp")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["is_up"]

    def test_data_returns_link_speed(self, loaded_model, sample_network_data) -> None:
        """linkSpeed 역할로 data()를 호출하면 올바른 링크 속도를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "linkSpeed")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["link_speed"]

    def test_data_returns_duplex(self, loaded_model, sample_network_data) -> None:
        """duplex 역할로 data()를 호출하면 올바른 듀플렉스 값을 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "duplex")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["duplex"]

    def test_data_returns_netmask(self, loaded_model, sample_network_data) -> None:
        """netmask 역할로 data()를 호출하면 올바른 넷마스크를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "netmask")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["netmask"]

    def test_data_returns_broadcast(self, loaded_model, sample_network_data) -> None:
        """broadcast 역할로 data()를 호출하면 올바른 브로드캐스트를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "broadcast")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_network_data[0]["broadcast"]
