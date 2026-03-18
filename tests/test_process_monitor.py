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

    @patch("utils.process_monitor.psutil.Process")
    def test_change_nice_generic_exception(self, mock_process_cls: MagicMock) -> None:
        """기타 예외가 발생하면 (False, 에러 메시지)를 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.nice.side_effect = OSError("OS 오류 발생")
        mock_process_cls.return_value = mock_proc

        success, message = change_nice(1234, 5)
        assert success is False
        assert isinstance(message, str)


class TestSendSignalGenericException:
    """send_signal() 기타 예외 경로를 검증합니다."""

    @patch("utils.process_monitor.psutil.Process")
    def test_send_signal_generic_exception(self, mock_process_cls: MagicMock) -> None:
        """기타 예외가 발생하면 (False, 에러 메시지)를 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.send_signal.side_effect = OSError("OS 오류 발생")
        mock_process_cls.return_value = mock_proc

        success, message = send_signal(1234, 15)
        assert success is False
        assert isinstance(message, str)


class TestCollectProcessesInnerException:
    """collect_processes() 내부 루프 예외 경로를 검증합니다."""

    @patch("utils.process_monitor.psutil.process_iter")
    def test_inner_no_such_process_continues(self, mock_iter: MagicMock) -> None:
        """내부 루프에서 NoSuchProcess 발생 시 해당 프로세스를 건너뛰어야 합니다."""
        good_proc = MagicMock()
        good_proc.info = {
            "pid": 1,
            "name": "systemd",
            "username": "root",
            "cpu_percent": 0.0,
            "memory_percent": 0.1,
            "status": "sleeping",
            "num_threads": 1,
            "ppid": 0,
        }
        bad_proc = MagicMock()
        # info 속성 접근 시 예외 발생
        type(bad_proc).info = property(
            lambda self: (_ for _ in ()).throw(psutil.NoSuchProcess(pid=999))
        )
        mock_iter.return_value = iter([bad_proc, good_proc])
        result = collect_processes()
        # bad_proc은 건너뛰고 good_proc은 포함
        assert len(result) == 1
        assert result[0]["pid"] == 1


class TestGetProcessDetails:
    """get_process_details() 함수의 동작을 검증합니다."""

    @patch("utils.process_monitor.psutil.Process")
    def test_returns_error_when_no_such_process(self, mock_process_cls: MagicMock) -> None:
        """존재하지 않는 PID면 error 키를 포함한 딕셔너리를 반환해야 합니다."""
        mock_process_cls.side_effect = psutil.NoSuchProcess(pid=99999)
        from utils.process_monitor import get_process_details
        result = get_process_details(99999)
        assert "error" in result

    @patch("utils.process_monitor.psutil.Process")
    def test_returns_error_when_access_denied(self, mock_process_cls: MagicMock) -> None:
        """접근 거부 시 error 키를 포함한 딕셔너리를 반환해야 합니다."""
        mock_process_cls.side_effect = psutil.AccessDenied(pid=1)
        from utils.process_monitor import get_process_details
        result = get_process_details(1)
        assert "error" in result

    @patch("utils.process_monitor.psutil.Process")
    def test_returns_dict_with_required_keys(self, mock_process_cls: MagicMock) -> None:
        """정상 프로세스면 필수 키들을 포함한 딕셔너리를 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.cmdline.return_value = ["/usr/bin/python3"]
        mock_proc.open_files.return_value = []
        mock_proc.net_connections.return_value = []
        mock_proc.environ.return_value = {"PATH": "/usr/bin"}
        mock_proc.create_time.return_value = 1700000000.0
        mock_proc.exe.return_value = "/usr/bin/python3"
        mock_proc.cwd.return_value = "/home/oscar"
        mock_process_cls.return_value = mock_proc

        from utils.process_monitor import get_process_details
        result = get_process_details(1000)

        required_keys = {"cmdline", "open_files", "connections", "environ", "create_time", "exe", "cwd"}
        assert required_keys.issubset(result.keys())

    @patch("utils.process_monitor.psutil.Process")
    def test_cmdline_fallback_on_access_denied(self, mock_process_cls: MagicMock) -> None:
        """cmdline() 접근 거부 시 빈 리스트를 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.cmdline.side_effect = psutil.AccessDenied(pid=1)
        mock_proc.open_files.return_value = []
        mock_proc.net_connections.return_value = []
        mock_proc.environ.return_value = {}
        mock_proc.create_time.return_value = 0.0
        mock_proc.exe.return_value = ""
        mock_proc.cwd.return_value = ""
        mock_process_cls.return_value = mock_proc

        from utils.process_monitor import get_process_details
        result = get_process_details(1)
        assert result["cmdline"] == []

    @patch("utils.process_monitor.psutil.Process")
    def test_open_files_fallback_on_access_denied(self, mock_process_cls: MagicMock) -> None:
        """open_files() 접근 거부 시 빈 리스트를 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.cmdline.return_value = []
        mock_proc.open_files.side_effect = psutil.AccessDenied(pid=1)
        mock_proc.net_connections.return_value = []
        mock_proc.environ.return_value = {}
        mock_proc.create_time.return_value = 0.0
        mock_proc.exe.return_value = ""
        mock_proc.cwd.return_value = ""
        mock_process_cls.return_value = mock_proc

        from utils.process_monitor import get_process_details
        result = get_process_details(1)
        assert result["open_files"] == []

    @patch("utils.process_monitor.psutil.Process")
    def test_connections_fallback_on_access_denied(self, mock_process_cls: MagicMock) -> None:
        """net_connections() 접근 거부 시 빈 리스트를 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.cmdline.return_value = []
        mock_proc.open_files.return_value = []
        mock_proc.net_connections.side_effect = psutil.AccessDenied(pid=1)
        mock_proc.environ.return_value = {}
        mock_proc.create_time.return_value = 0.0
        mock_proc.exe.return_value = ""
        mock_proc.cwd.return_value = ""
        mock_process_cls.return_value = mock_proc

        from utils.process_monitor import get_process_details
        result = get_process_details(1)
        assert result["connections"] == []

    @patch("utils.process_monitor.psutil.Process")
    def test_environ_fallback_on_access_denied(self, mock_process_cls: MagicMock) -> None:
        """environ() 접근 거부 시 빈 딕셔너리를 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.cmdline.return_value = []
        mock_proc.open_files.return_value = []
        mock_proc.net_connections.return_value = []
        mock_proc.environ.side_effect = psutil.AccessDenied(pid=1)
        mock_proc.create_time.return_value = 0.0
        mock_proc.exe.return_value = ""
        mock_proc.cwd.return_value = ""
        mock_process_cls.return_value = mock_proc

        from utils.process_monitor import get_process_details
        result = get_process_details(1)
        assert result["environ"] == {}

    @patch("utils.process_monitor.psutil.Process")
    def test_exe_fallback_on_access_denied(self, mock_process_cls: MagicMock) -> None:
        """exe() 접근 거부 시 빈 문자열을 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.cmdline.return_value = []
        mock_proc.open_files.return_value = []
        mock_proc.net_connections.return_value = []
        mock_proc.environ.return_value = {}
        mock_proc.create_time.return_value = 0.0
        mock_proc.exe.side_effect = psutil.AccessDenied(pid=1)
        mock_proc.cwd.return_value = ""
        mock_process_cls.return_value = mock_proc

        from utils.process_monitor import get_process_details
        result = get_process_details(1)
        assert result["exe"] == ""

    @patch("utils.process_monitor.psutil.Process")
    def test_cwd_fallback_on_access_denied(self, mock_process_cls: MagicMock) -> None:
        """cwd() 접근 거부 시 빈 문자열을 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.cmdline.return_value = []
        mock_proc.open_files.return_value = []
        mock_proc.net_connections.return_value = []
        mock_proc.environ.return_value = {}
        mock_proc.create_time.return_value = 0.0
        mock_proc.exe.return_value = ""
        mock_proc.cwd.side_effect = psutil.AccessDenied(pid=1)
        mock_process_cls.return_value = mock_proc

        from utils.process_monitor import get_process_details
        result = get_process_details(1)
        assert result["cwd"] == ""

    @patch("utils.process_monitor.psutil.Process")
    def test_create_time_fallback_on_access_denied(self, mock_process_cls: MagicMock) -> None:
        """create_time() 접근 거부 시 0.0을 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.cmdline.return_value = []
        mock_proc.open_files.return_value = []
        mock_proc.net_connections.return_value = []
        mock_proc.environ.return_value = {}
        mock_proc.create_time.side_effect = psutil.AccessDenied(pid=1)
        mock_proc.exe.return_value = ""
        mock_proc.cwd.return_value = ""
        mock_process_cls.return_value = mock_proc

        from utils.process_monitor import get_process_details
        result = get_process_details(1)
        assert result["create_time"] == 0.0
