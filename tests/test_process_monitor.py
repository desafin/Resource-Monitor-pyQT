"""utils/process_monitor.py에 대한 사양 테스트.

collect_processes(), send_signal(), change_nice() 함수를 검증합니다.
"""
import signal
from unittest.mock import MagicMock, patch, PropertyMock

import psutil
import pytest

from utils.process_monitor import collect_processes, send_signal, change_nice


class TestCollectProcesses:
    """collect_processes() 함수의 동작을 검증합니다."""

    def test_returns_list(self) -> None:
        """프로세스 목록이 list 타입으로 반환되어야 합니다."""
        result = collect_processes()
        assert isinstance(result, list)

    def test_returns_non_empty_list(self) -> None:
        """실행 중인 시스템에서 비어있지 않은 목록을 반환해야 합니다."""
        result = collect_processes()
        assert len(result) > 0

    def test_process_dict_has_required_keys(self) -> None:
        """각 프로세스 딕셔너리는 필수 키를 포함해야 합니다."""
        required_keys = {
            "pid", "name", "username", "cpu_percent",
            "memory_percent", "status", "num_threads",
        }
        result = collect_processes()
        assert len(result) > 0
        for proc in result:
            assert required_keys.issubset(proc.keys()), (
                f"프로세스에 필수 키가 누락됨: {required_keys - proc.keys()}"
            )

    def test_pid_is_integer(self) -> None:
        """PID 값은 정수여야 합니다."""
        result = collect_processes()
        for proc in result:
            assert isinstance(proc["pid"], int)

    def test_cpu_percent_is_numeric(self) -> None:
        """cpu_percent 값은 숫자(float 또는 int)여야 합니다."""
        result = collect_processes()
        for proc in result:
            assert isinstance(proc["cpu_percent"], (int, float))

    def test_memory_percent_is_numeric(self) -> None:
        """memory_percent 값은 숫자(float 또는 int)여야 합니다."""
        result = collect_processes()
        for proc in result:
            assert isinstance(proc["memory_percent"], (int, float))

    @patch("utils.process_monitor.psutil.process_iter")
    def test_handles_no_such_process(self, mock_iter: MagicMock) -> None:
        """NoSuchProcess 예외가 발생해도 정상적으로 처리해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.info = {"pid": 999, "name": "gone"}
        mock_proc.__getitem__ = lambda self, key: self.info[key]

        def side_effect(*args, **kwargs):
            raise psutil.NoSuchProcess(pid=999)

        mock_iter.side_effect = side_effect
        result = collect_processes()
        assert isinstance(result, list)

    @patch("utils.process_monitor.psutil.process_iter")
    def test_handles_access_denied(self, mock_iter: MagicMock) -> None:
        """AccessDenied 예외가 발생해도 정상적으로 처리해야 합니다."""
        mock_iter.side_effect = psutil.AccessDenied(pid=1)
        result = collect_processes()
        assert isinstance(result, list)

    @patch("utils.process_monitor.psutil.process_iter")
    def test_handles_zombie_process(self, mock_iter: MagicMock) -> None:
        """ZombieProcess 예외가 발생해도 정상적으로 처리해야 합니다."""
        mock_iter.side_effect = psutil.ZombieProcess(pid=666)
        result = collect_processes()
        assert isinstance(result, list)


class TestSendSignal:
    """send_signal() 함수의 동작을 검증합니다."""

    @patch("utils.process_monitor.psutil.Process")
    def test_send_signal_success(self, mock_process_cls: MagicMock) -> None:
        """유효한 PID에 시그널을 보내면 (True, 성공 메시지)를 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_process_cls.return_value = mock_proc

        success, message = send_signal(1000, signal.SIGTERM)
        assert success is True
        assert isinstance(message, str)
        mock_proc.send_signal.assert_called_once_with(signal.SIGTERM)

    @patch("utils.process_monitor.psutil.Process")
    def test_send_signal_no_such_process(self, mock_process_cls: MagicMock) -> None:
        """존재하지 않는 PID에 시그널을 보내면 (False, 에러 메시지)를 반환해야 합니다."""
        mock_process_cls.side_effect = psutil.NoSuchProcess(pid=99999)

        success, message = send_signal(99999, signal.SIGTERM)
        assert success is False
        assert isinstance(message, str)

    @patch("utils.process_monitor.psutil.Process")
    def test_send_signal_access_denied(self, mock_process_cls: MagicMock) -> None:
        """권한이 없는 프로세스에 시그널을 보내면 (False, 에러 메시지)를 반환해야 합니다."""
        mock_process_cls.side_effect = psutil.AccessDenied(pid=1)

        success, message = send_signal(1, signal.SIGKILL)
        assert success is False
        assert isinstance(message, str)

    def test_send_signal_returns_tuple(self) -> None:
        """반환 타입이 tuple[bool, str]이어야 합니다."""
        result = send_signal(99999, signal.SIGTERM)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)


class TestChangeNice:
    """change_nice() 함수의 동작을 검증합니다."""

    @patch("utils.process_monitor.psutil.Process")
    def test_change_nice_success(self, mock_process_cls: MagicMock) -> None:
        """유효한 PID와 nice 값으로 호출하면 (True, 성공 메시지)를 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_process_cls.return_value = mock_proc

        success, message = change_nice(1000, 10)
        assert success is True
        assert isinstance(message, str)
        mock_proc.nice.assert_called_once_with(10)

    @patch("utils.process_monitor.psutil.Process")
    def test_change_nice_no_such_process(self, mock_process_cls: MagicMock) -> None:
        """존재하지 않는 PID의 nice 값을 변경하면 (False, 에러 메시지)를 반환해야 합니다."""
        mock_process_cls.side_effect = psutil.NoSuchProcess(pid=99999)

        success, message = change_nice(99999, 10)
        assert success is False
        assert isinstance(message, str)

    @patch("utils.process_monitor.psutil.Process")
    def test_change_nice_access_denied(self, mock_process_cls: MagicMock) -> None:
        """권한이 없는 프로세스의 nice 값을 변경하면 (False, 에러 메시지)를 반환해야 합니다."""
        mock_process_cls.side_effect = psutil.AccessDenied(pid=1)

        success, message = change_nice(1, -5)
        assert success is False
        assert isinstance(message, str)

    def test_change_nice_returns_tuple(self) -> None:
        """반환 타입이 tuple[bool, str]이어야 합니다."""
        result = change_nice(99999, 10)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)
