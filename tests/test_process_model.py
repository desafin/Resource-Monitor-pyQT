"""models/process_model.py에 대한 사양 테스트.

ProcessModel(QAbstractListModel)의 data(), rowCount(), roleNames(),
update_processes() 메서드를 검증합니다.
"""
import pytest
from PyQt5.QtCore import Qt, QModelIndex

from models.process_model import ProcessModel


class TestProcessModelInit:
    """ProcessModel 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """ProcessModel 인스턴스를 생성할 수 있어야 합니다."""
        model = ProcessModel()
        assert model is not None

    def test_initial_row_count_is_zero(self, qapp) -> None:
        """초기 상태에서 행 수는 0이어야 합니다."""
        model = ProcessModel()
        assert model.rowCount() == 0


class TestProcessModelRoleNames:
    """ProcessModel의 roleNames()를 검증합니다."""

    def test_role_names_not_empty(self, qapp) -> None:
        """roleNames()는 비어있지 않아야 합니다."""
        model = ProcessModel()
        roles = model.roleNames()
        assert len(roles) > 0

    def test_role_names_has_pid(self, qapp) -> None:
        """roleNames()에 'pid' 역할이 포함되어야 합니다."""
        model = ProcessModel()
        roles = model.roleNames()
        role_values = [bytes(v).decode() for v in roles.values()]
        assert "pid" in role_values

    def test_role_names_has_all_required(self, qapp) -> None:
        """roleNames()에 모든 필수 역할이 포함되어야 합니다."""
        model = ProcessModel()
        roles = model.roleNames()
        role_values = {bytes(v).decode() for v in roles.values()}
        required = {"pid", "name", "cpuPercent", "memPercent", "status", "user", "threads"}
        assert required.issubset(role_values), (
            f"누락된 역할: {required - role_values}"
        )


class TestProcessModelUpdateProcesses:
    """ProcessModel.update_processes() 메서드를 검증합니다."""

    def test_update_sets_row_count(self, qapp, sample_process_data) -> None:
        """update_processes() 후 rowCount()가 데이터 수와 일치해야 합니다."""
        model = ProcessModel()
        model.update_processes(sample_process_data)
        assert model.rowCount() == len(sample_process_data)

    def test_update_with_empty_list(self, qapp) -> None:
        """빈 목록으로 업데이트하면 rowCount()가 0이어야 합니다."""
        model = ProcessModel()
        model.update_processes([{"pid": 1, "name": "test", "username": "u",
                                 "cpu_percent": 0.0, "memory_percent": 0.0,
                                 "status": "running", "num_threads": 1}])
        assert model.rowCount() == 1
        model.update_processes([])
        assert model.rowCount() == 0

    def test_update_replaces_previous_data(self, qapp) -> None:
        """update_processes()는 이전 데이터를 완전히 교체해야 합니다."""
        model = ProcessModel()
        model.update_processes([{"pid": 1, "name": "a", "username": "u",
                                 "cpu_percent": 0.0, "memory_percent": 0.0,
                                 "status": "running", "num_threads": 1}])
        model.update_processes([{"pid": 2, "name": "b", "username": "u",
                                 "cpu_percent": 0.0, "memory_percent": 0.0,
                                 "status": "running", "num_threads": 1},
                                {"pid": 3, "name": "c", "username": "u",
                                 "cpu_percent": 0.0, "memory_percent": 0.0,
                                 "status": "running", "num_threads": 1}])
        assert model.rowCount() == 2


class TestProcessModelData:
    """ProcessModel.data() 메서드를 검증합니다."""

    @pytest.fixture
    def loaded_model(self, qapp, sample_process_data) -> ProcessModel:
        """데이터가 로드된 ProcessModel을 반환합니다."""
        model = ProcessModel()
        model.update_processes(sample_process_data)
        return model

    def test_data_returns_pid(self, loaded_model, sample_process_data) -> None:
        """PidRole로 data()를 호출하면 올바른 PID를 반환해야 합니다."""
        roles = loaded_model.roleNames()
        pid_role = None
        for role_id, role_name in roles.items():
            if bytes(role_name).decode() == "pid":
                pid_role = role_id
                break
        assert pid_role is not None

        index = loaded_model.index(0, 0)
        value = loaded_model.data(index, pid_role)
        assert value == sample_process_data[0]["pid"]

    def test_data_returns_name(self, loaded_model, sample_process_data) -> None:
        """NameRole로 data()를 호출하면 올바른 이름을 반환해야 합니다."""
        roles = loaded_model.roleNames()
        name_role = None
        for role_id, role_name in roles.items():
            if bytes(role_name).decode() == "name":
                name_role = role_id
                break
        assert name_role is not None

        index = loaded_model.index(1, 0)
        value = loaded_model.data(index, name_role)
        assert value == sample_process_data[1]["name"]

    def test_data_invalid_index_returns_none(self, loaded_model) -> None:
        """유효하지 않은 인덱스로 data()를 호출하면 None을 반환해야 합니다."""
        index = loaded_model.index(999, 0)
        roles = loaded_model.roleNames()
        first_role = list(roles.keys())[0]
        value = loaded_model.data(index, first_role)
        assert value is None

    def test_data_returns_cpu_percent(self, loaded_model, sample_process_data) -> None:
        """CpuRole로 data()를 호출하면 올바른 CPU 사용률을 반환해야 합니다."""
        roles = loaded_model.roleNames()
        cpu_role = None
        for role_id, role_name in roles.items():
            if bytes(role_name).decode() == "cpuPercent":
                cpu_role = role_id
                break
        assert cpu_role is not None

        index = loaded_model.index(1, 0)
        value = loaded_model.data(index, cpu_role)
        assert value == sample_process_data[1]["cpu_percent"]
