"""프로세스 트리 구조 기능에 대한 사양 테스트.

트리 모드 토글, ppid 기반 트리 구성, 들여쓰기 레벨 계산을 검증합니다.
"""
import sys
from typing import Any

import pytest


class TestProcessTreeBuilding:
    """프로세스 트리 구성 로직을 검증합니다."""

    @pytest.fixture
    def tree_processes(self) -> list[dict]:
        """트리 테스트용 프로세스 데이터를 반환합니다."""
        return [
            {"pid": 1, "name": "systemd", "username": "root",
             "cpu_percent": 0.0, "memory_percent": 0.1,
             "status": "sleeping", "num_threads": 1, "ppid": 0},
            {"pid": 100, "name": "sshd", "username": "root",
             "cpu_percent": 0.0, "memory_percent": 0.2,
             "status": "sleeping", "num_threads": 1, "ppid": 1},
            {"pid": 200, "name": "bash", "username": "oscar",
             "cpu_percent": 0.5, "memory_percent": 0.3,
             "status": "sleeping", "num_threads": 1, "ppid": 100},
            {"pid": 300, "name": "python3", "username": "oscar",
             "cpu_percent": 25.0, "memory_percent": 3.0,
             "status": "running", "num_threads": 4, "ppid": 200},
            {"pid": 101, "name": "cron", "username": "root",
             "cpu_percent": 0.0, "memory_percent": 0.1,
             "status": "sleeping", "num_threads": 1, "ppid": 1},
        ]

    @pytest.fixture
    def process_model(self, qapp: Any) -> Any:
        """테스트용 ProcessModel 인스턴스를 생성합니다."""
        from models.process_model import ProcessModel
        return ProcessModel()

    def test_ppid_role_exists(self, process_model: Any) -> None:
        """ProcessModel에 PpidRole이 정의되어 있어야 합니다."""
        assert hasattr(process_model, "PpidRole")

    def test_indent_level_role_exists(self, process_model: Any) -> None:
        """ProcessModel에 IndentLevelRole이 정의되어 있어야 합니다."""
        assert hasattr(process_model, "IndentLevelRole")

    def test_ppid_role_in_role_names(self, process_model: Any) -> None:
        """PpidRole이 roleNames에 포함되어야 합니다."""
        roles = process_model.roleNames()
        assert process_model.PpidRole in roles
        assert roles[process_model.PpidRole] == b"ppid"

    def test_indent_level_role_in_role_names(self, process_model: Any) -> None:
        """IndentLevelRole이 roleNames에 포함되어야 합니다."""
        roles = process_model.roleNames()
        assert process_model.IndentLevelRole in roles
        assert roles[process_model.IndentLevelRole] == b"indentLevel"

    def test_ppid_data_returned(
        self, process_model: Any, tree_processes: list[dict]
    ) -> None:
        """PpidRole로 data()를 호출하면 ppid 값을 반환해야 합니다."""
        process_model.update_processes(tree_processes)
        index = process_model.index(1, 0)  # sshd (ppid=1)
        ppid = process_model.data(index, process_model.PpidRole)
        assert ppid == 1

    def test_indent_level_default_zero(
        self, process_model: Any, tree_processes: list[dict]
    ) -> None:
        """트리 모드 비활성화 시 indentLevel은 0이어야 합니다."""
        process_model.update_processes(tree_processes)
        index = process_model.index(0, 0)
        indent = process_model.data(index, process_model.IndentLevelRole)
        assert indent == 0


class TestProcessViewModelTreeMode:
    """ProcessViewModel의 트리 모드 토글 기능을 검증합니다."""

    @pytest.fixture
    def viewmodel(self, qapp: Any) -> Any:
        """테스트용 ProcessViewModel 인스턴스를 생성합니다."""
        from views.process_viewmodel import ProcessViewModel
        vm = ProcessViewModel()
        yield vm
        vm.cleanup()

    def test_tree_mode_default_false(self, viewmodel: Any) -> None:
        """트리 모드는 기본적으로 비활성화되어야 합니다."""
        assert viewmodel.isTreeMode is False

    def test_toggle_tree_mode(self, viewmodel: Any) -> None:
        """toggleTreeMode() 호출 시 트리 모드가 토글되어야 합니다."""
        viewmodel.toggleTreeMode()
        assert viewmodel.isTreeMode is True
        viewmodel.toggleTreeMode()
        assert viewmodel.isTreeMode is False

    def test_tree_mode_signal_emitted(self, viewmodel: Any) -> None:
        """트리 모드 변경 시 isTreeModeChanged 시그널이 방출되어야 합니다."""
        signal_count = []
        viewmodel.isTreeModeChanged.connect(lambda: signal_count.append(1))
        viewmodel.toggleTreeMode()
        assert len(signal_count) == 1


class TestBuildProcessTree:
    """build_process_tree() 유틸리티 함수를 검증합니다."""

    @pytest.fixture
    def flat_processes(self) -> list[dict]:
        """평탄한 프로세스 목록을 반환합니다."""
        return [
            {"pid": 1, "name": "systemd", "ppid": 0,
             "username": "root", "cpu_percent": 0.0,
             "memory_percent": 0.1, "status": "sleeping", "num_threads": 1},
            {"pid": 100, "name": "sshd", "ppid": 1,
             "username": "root", "cpu_percent": 0.0,
             "memory_percent": 0.2, "status": "sleeping", "num_threads": 1},
            {"pid": 200, "name": "bash", "ppid": 100,
             "username": "oscar", "cpu_percent": 0.5,
             "memory_percent": 0.3, "status": "sleeping", "num_threads": 1},
            {"pid": 300, "name": "python3", "ppid": 200,
             "username": "oscar", "cpu_percent": 25.0,
             "memory_percent": 3.0, "status": "running", "num_threads": 4},
            {"pid": 101, "name": "cron", "ppid": 1,
             "username": "root", "cpu_percent": 0.0,
             "memory_percent": 0.1, "status": "sleeping", "num_threads": 1},
        ]

    def test_build_tree_returns_list(self, flat_processes: list[dict]) -> None:
        """build_process_tree()가 리스트를 반환해야 합니다."""
        from utils.process_tree import build_process_tree
        result = build_process_tree(flat_processes)
        assert isinstance(result, list)

    def test_build_tree_preserves_all_processes(
        self, flat_processes: list[dict]
    ) -> None:
        """트리 빌드 후에도 모든 프로세스가 보존되어야 합니다."""
        from utils.process_tree import build_process_tree
        result = build_process_tree(flat_processes)
        assert len(result) == len(flat_processes)

    def test_build_tree_assigns_indent_levels(
        self, flat_processes: list[dict]
    ) -> None:
        """트리 빌드 시 각 프로세스에 indent_level이 할당되어야 합니다."""
        from utils.process_tree import build_process_tree
        result = build_process_tree(flat_processes)
        for proc in result:
            assert "indent_level" in proc

    def test_root_process_indent_zero(
        self, flat_processes: list[dict]
    ) -> None:
        """루트 프로세스(ppid=0)의 indent_level은 0이어야 합니다."""
        from utils.process_tree import build_process_tree
        result = build_process_tree(flat_processes)
        root = next(p for p in result if p["pid"] == 1)
        assert root["indent_level"] == 0

    def test_child_indent_greater_than_parent(
        self, flat_processes: list[dict]
    ) -> None:
        """자식 프로세스의 indent_level은 부모보다 커야 합니다."""
        from utils.process_tree import build_process_tree
        result = build_process_tree(flat_processes)
        # pid=100(sshd)의 부모는 pid=1(systemd)
        systemd = next(p for p in result if p["pid"] == 1)
        sshd = next(p for p in result if p["pid"] == 100)
        assert sshd["indent_level"] > systemd["indent_level"]

    def test_deep_nesting_indent_levels(
        self, flat_processes: list[dict]
    ) -> None:
        """깊은 중첩 구조에서 indent_level이 순차적으로 증가해야 합니다."""
        from utils.process_tree import build_process_tree
        result = build_process_tree(flat_processes)
        # systemd(0) -> sshd(1) -> bash(2) -> python3(3)
        systemd = next(p for p in result if p["pid"] == 1)
        sshd = next(p for p in result if p["pid"] == 100)
        bash = next(p for p in result if p["pid"] == 200)
        python3 = next(p for p in result if p["pid"] == 300)
        assert systemd["indent_level"] == 0
        assert sshd["indent_level"] == 1
        assert bash["indent_level"] == 2
        assert python3["indent_level"] == 3

    def test_siblings_same_indent_level(
        self, flat_processes: list[dict]
    ) -> None:
        """형제 프로세스들은 같은 indent_level을 가져야 합니다."""
        from utils.process_tree import build_process_tree
        result = build_process_tree(flat_processes)
        # sshd(ppid=1)와 cron(ppid=1)은 형제
        sshd = next(p for p in result if p["pid"] == 100)
        cron = next(p for p in result if p["pid"] == 101)
        assert sshd["indent_level"] == cron["indent_level"]

    def test_tree_order_parent_before_children(
        self, flat_processes: list[dict]
    ) -> None:
        """트리 순서에서 부모가 자식보다 먼저 나와야 합니다."""
        from utils.process_tree import build_process_tree
        result = build_process_tree(flat_processes)
        pid_order = [p["pid"] for p in result]
        # systemd는 sshd보다 먼저 나와야 함
        assert pid_order.index(1) < pid_order.index(100)
        # sshd는 bash보다 먼저 나와야 함
        assert pid_order.index(100) < pid_order.index(200)

    def test_empty_list_returns_empty(self) -> None:
        """빈 리스트 입력 시 빈 리스트를 반환해야 합니다."""
        from utils.process_tree import build_process_tree
        result = build_process_tree([])
        assert result == []

    def test_orphan_processes_handled(self) -> None:
        """부모가 없는(고아) 프로세스도 포함되어야 합니다."""
        from utils.process_tree import build_process_tree
        processes = [
            {"pid": 500, "name": "orphan", "ppid": 99999,
             "username": "root", "cpu_percent": 0.0,
             "memory_percent": 0.0, "status": "running", "num_threads": 1},
        ]
        result = build_process_tree(processes)
        assert len(result) == 1
        assert result[0]["indent_level"] == 0
