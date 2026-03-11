"""models/disk_model.py에 대한 사양 테스트.

DiskModel(QAbstractListModel)의 data(), rowCount(), roleNames(),
update_disks() 메서드를 검증합니다.
"""
import pytest
from PyQt5.QtCore import Qt, QModelIndex

from models.disk_model import DiskModel


@pytest.fixture
def sample_disk_data() -> list[dict]:
    """테스트용 디스크 데이터 목록을 반환하는 fixture."""
    return [
        {
            "device": "/dev/sda1",
            "mountpoint": "/",
            "fstype": "ext4",
            "total": 500_000_000_000,
            "used": 200_000_000_000,
            "free": 300_000_000_000,
            "percent": 40.0,
            "read_bytes": 1_000_000,
            "write_bytes": 2_000_000,
        },
        {
            "device": "/dev/sda2",
            "mountpoint": "/home",
            "fstype": "ext4",
            "total": 1_000_000_000_000,
            "used": 600_000_000_000,
            "free": 400_000_000_000,
            "percent": 60.0,
            "read_bytes": 5_000_000,
            "write_bytes": 3_000_000,
        },
    ]


class TestDiskModelInit:
    """DiskModel 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """DiskModel 인스턴스를 생성할 수 있어야 합니다."""
        model = DiskModel()
        assert model is not None

    def test_initial_row_count_is_zero(self, qapp) -> None:
        """초기 상태에서 행 수는 0이어야 합니다."""
        model = DiskModel()
        assert model.rowCount() == 0


class TestDiskModelRoleNames:
    """DiskModel의 roleNames()를 검증합니다."""

    def test_role_names_not_empty(self, qapp) -> None:
        """roleNames()는 비어있지 않아야 합니다."""
        model = DiskModel()
        roles = model.roleNames()
        assert len(roles) > 0

    def test_role_names_has_all_required(self, qapp) -> None:
        """roleNames()에 모든 필수 역할이 포함되어야 합니다."""
        model = DiskModel()
        roles = model.roleNames()
        role_values = {bytes(v).decode() for v in roles.values()}
        required = {
            "device", "mountpoint", "fstype",
            "total", "used", "free", "percent",
            "readBytes", "writeBytes",
        }
        assert required.issubset(role_values), (
            f"누락된 역할: {required - role_values}"
        )


class TestDiskModelUpdateDisks:
    """DiskModel.update_disks() 메서드를 검증합니다."""

    def test_update_sets_row_count(self, qapp, sample_disk_data) -> None:
        """update_disks() 후 rowCount()가 데이터 수와 일치해야 합니다."""
        model = DiskModel()
        model.update_disks(sample_disk_data)
        assert model.rowCount() == len(sample_disk_data)

    def test_update_with_empty_list(self, qapp) -> None:
        """빈 목록으로 업데이트하면 rowCount()가 0이어야 합니다."""
        model = DiskModel()
        model.update_disks([{"device": "/dev/sda1", "mountpoint": "/",
                             "fstype": "ext4", "total": 100, "used": 50,
                             "free": 50, "percent": 50.0,
                             "read_bytes": 0, "write_bytes": 0}])
        assert model.rowCount() == 1
        model.update_disks([])
        assert model.rowCount() == 0

    def test_update_replaces_previous_data(self, qapp) -> None:
        """update_disks()는 이전 데이터를 완전히 교체해야 합니다."""
        model = DiskModel()
        model.update_disks([{"device": "/dev/sda1", "mountpoint": "/",
                             "fstype": "ext4", "total": 100, "used": 50,
                             "free": 50, "percent": 50.0,
                             "read_bytes": 0, "write_bytes": 0}])
        model.update_disks([
            {"device": "/dev/sda1", "mountpoint": "/", "fstype": "ext4",
             "total": 100, "used": 50, "free": 50, "percent": 50.0,
             "read_bytes": 0, "write_bytes": 0},
            {"device": "/dev/sda2", "mountpoint": "/home", "fstype": "ext4",
             "total": 100, "used": 50, "free": 50, "percent": 50.0,
             "read_bytes": 0, "write_bytes": 0},
        ])
        assert model.rowCount() == 2


class TestDiskModelData:
    """DiskModel.data() 메서드를 검증합니다."""

    @pytest.fixture
    def loaded_model(self, qapp, sample_disk_data) -> DiskModel:
        """데이터가 로드된 DiskModel을 반환합니다."""
        model = DiskModel()
        model.update_disks(sample_disk_data)
        return model

    def _get_role_id(self, model: DiskModel, role_name: str) -> int:
        """역할 이름으로 역할 ID를 찾아 반환합니다."""
        roles = model.roleNames()
        for role_id, name in roles.items():
            if bytes(name).decode() == role_name:
                return role_id
        raise ValueError(f"역할 '{role_name}'을 찾을 수 없습니다")

    def test_data_returns_device(self, loaded_model, sample_disk_data) -> None:
        """device 역할로 data()를 호출하면 올바른 장치명을 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "device")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_disk_data[0]["device"]

    def test_data_returns_mountpoint(self, loaded_model, sample_disk_data) -> None:
        """mountpoint 역할로 data()를 호출하면 올바른 마운트 포인트를 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "mountpoint")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_disk_data[0]["mountpoint"]

    def test_data_returns_percent(self, loaded_model, sample_disk_data) -> None:
        """percent 역할로 data()를 호출하면 올바른 사용률을 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "percent")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_disk_data[0]["percent"]

    def test_data_returns_total(self, loaded_model, sample_disk_data) -> None:
        """total 역할로 data()를 호출하면 올바른 총 용량을 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "total")
        index = loaded_model.index(0, 0)
        assert loaded_model.data(index, role_id) == sample_disk_data[0]["total"]

    def test_data_invalid_index_returns_none(self, loaded_model) -> None:
        """유효하지 않은 인덱스로 data()를 호출하면 None을 반환해야 합니다."""
        index = loaded_model.index(999, 0)
        role_id = self._get_role_id(loaded_model, "device")
        assert loaded_model.data(index, role_id) is None

    def test_data_second_disk(self, loaded_model, sample_disk_data) -> None:
        """두 번째 디스크의 데이터를 올바르게 반환해야 합니다."""
        role_id = self._get_role_id(loaded_model, "device")
        index = loaded_model.index(1, 0)
        assert loaded_model.data(index, role_id) == sample_disk_data[1]["device"]
