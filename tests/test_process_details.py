"""프로세스 상세 정보 조회 기능에 대한 사양 테스트.

get_process_details(pid) 함수를 검증합니다.
- 정상 프로세스 정보 조회
- 존재하지 않는 프로세스 처리
- 접근 거부된 프로세스 처리
- 반환 딕셔너리 구조 검증
"""
import os
from unittest.mock import MagicMock, patch, PropertyMock

import psutil
import pytest

from utils.process_monitor import get_process_details


class TestGetProcessDetails:
    """get_process_details() 함수의 동작을 검증합니다."""

    def test_returns_dict(self) -> None:
        """반환 타입이 dict여야 합니다."""
        result = get_process_details(os.getpid())
        assert isinstance(result, dict)

    def test_current_process_has_required_keys(self) -> None:
        """현재 프로세스 조회 시 필수 키가 포함되어야 합니다."""
        required_keys = {
            "cmdline", "open_files", "connections",
            "environ", "create_time", "exe", "cwd",
        }
        result = get_process_details(os.getpid())
        assert "error" not in result, f"오류 발생: {result.get('error')}"
        assert required_keys.issubset(result.keys()), (
            f"필수 키 누락: {required_keys - result.keys()}"
        )

    def test_cmdline_is_list(self) -> None:
        """cmdline 값은 리스트여야 합니다."""
        result = get_process_details(os.getpid())
        assert isinstance(result.get("cmdline"), list)

    def test_environ_is_dict(self) -> None:
        """environ 값은 딕셔너리여야 합니다."""
        result = get_process_details(os.getpid())
        assert isinstance(result.get("environ"), dict)

    def test_create_time_is_float(self) -> None:
        """create_time 값은 float여야 합니다."""
        result = get_process_details(os.getpid())
        assert isinstance(result.get("create_time"), float)

    def test_open_files_is_list(self) -> None:
        """open_files 값은 리스트여야 합니다."""
        result = get_process_details(os.getpid())
        assert isinstance(result.get("open_files"), list)

    def test_connections_is_list(self) -> None:
        """connections 값은 리스트여야 합니다."""
        result = get_process_details(os.getpid())
        assert isinstance(result.get("connections"), list)

    @patch("utils.process_monitor.psutil.Process")
    def test_no_such_process_returns_error_dict(self, mock_cls: MagicMock) -> None:
        """존재하지 않는 PID 조회 시 error 키를 포함한 dict를 반환해야 합니다."""
        mock_cls.side_effect = psutil.NoSuchProcess(pid=99999)
        result = get_process_details(99999)
        assert isinstance(result, dict)
        assert "error" in result

    @patch("utils.process_monitor.psutil.Process")
    def test_access_denied_returns_error_dict(self, mock_cls: MagicMock) -> None:
        """접근 거부된 프로세스 조회 시 error 키를 포함한 dict를 반환해야 합니다."""
        mock_cls.side_effect = psutil.AccessDenied(pid=1)
        result = get_process_details(1)
        assert isinstance(result, dict)
        assert "error" in result

    @patch("utils.process_monitor.psutil.Process")
    def test_partial_access_denied_returns_available_data(
        self, mock_cls: MagicMock
    ) -> None:
        """일부 속성에 접근 거부 시 접근 가능한 데이터는 반환해야 합니다."""
        mock_proc = MagicMock()
        mock_proc.cmdline.return_value = ["/usr/bin/test"]
        mock_proc.open_files.side_effect = psutil.AccessDenied(pid=1)
        mock_proc.net_connections.side_effect = psutil.AccessDenied(pid=1)
        mock_proc.environ.side_effect = psutil.AccessDenied(pid=1)
        mock_proc.create_time.return_value = 1000000.0
        mock_proc.exe.return_value = "/usr/bin/test"
        mock_proc.cwd.return_value = "/home/test"
        mock_cls.return_value = mock_proc

        result = get_process_details(1)
        assert "error" not in result
        assert result["cmdline"] == ["/usr/bin/test"]
        # 접근 거부된 필드는 빈 리스트/딕셔너리로 반환
        assert result["open_files"] == []
        assert result["connections"] == []
        assert result["environ"] == {}
