"""utils/serial_monitor.py에 대한 사양 테스트.

시리얼 포트를 /dev/ttyUSB*, /dev/ttyACM*, /dev/ttyS*에서 탐색하는 기능을 검증합니다.
collect_serial_ports()와 is_serial_available() 함수를 테스트합니다.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestIsSerialAvailable:
    """is_serial_available() 함수를 검증합니다."""

    @patch("utils.serial_monitor.glob.glob")
    def test_returns_true_when_serial_ports_exist(
        self, mock_glob: MagicMock
    ) -> None:
        """시리얼 포트가 존재하면 True를 반환해야 합니다."""
        mock_glob.side_effect = [["/dev/ttyUSB0"], [], []]
        from utils.serial_monitor import is_serial_available
        assert is_serial_available() is True

    @patch("utils.serial_monitor.glob.glob")
    def test_returns_false_when_no_serial_ports(
        self, mock_glob: MagicMock
    ) -> None:
        """시리얼 포트가 없으면 False를 반환해야 합니다."""
        mock_glob.return_value = []
        from utils.serial_monitor import is_serial_available
        assert is_serial_available() is False


class TestCollectSerialPorts:
    """collect_serial_ports() 함수를 검증합니다."""

    @patch("utils.serial_monitor.os.access")
    @patch("utils.serial_monitor.os.path.exists")
    @patch("utils.serial_monitor.glob.glob")
    def test_returns_usb_serial_port(
        self, mock_glob: MagicMock, mock_exists: MagicMock,
        mock_access: MagicMock
    ) -> None:
        """USB 시리얼 포트를 올바르게 반환해야 합니다."""
        mock_glob.side_effect = [["/dev/ttyUSB0"], [], []]
        mock_exists.return_value = True
        mock_access.return_value = True

        from utils.serial_monitor import collect_serial_ports
        result = collect_serial_ports()

        assert len(result) == 1
        assert result[0]["path"] == "/dev/ttyUSB0"
        assert result[0]["type"] == "USB"
        assert result[0]["exists"] is True

    @patch("utils.serial_monitor.os.access")
    @patch("utils.serial_monitor.os.path.exists")
    @patch("utils.serial_monitor.glob.glob")
    def test_returns_acm_serial_port(
        self, mock_glob: MagicMock, mock_exists: MagicMock,
        mock_access: MagicMock
    ) -> None:
        """ACM 시리얼 포트를 올바르게 반환해야 합니다."""
        mock_glob.side_effect = [[], ["/dev/ttyACM0"], []]
        mock_exists.return_value = True
        mock_access.return_value = True

        from utils.serial_monitor import collect_serial_ports
        result = collect_serial_ports()

        assert len(result) == 1
        assert result[0]["path"] == "/dev/ttyACM0"
        assert result[0]["type"] == "ACM"

    @patch("utils.serial_monitor.os.access")
    @patch("utils.serial_monitor.os.path.exists")
    @patch("utils.serial_monitor.glob.glob")
    def test_returns_standard_serial_port(
        self, mock_glob: MagicMock, mock_exists: MagicMock,
        mock_access: MagicMock
    ) -> None:
        """표준 시리얼 포트를 올바르게 반환해야 합니다."""
        mock_glob.side_effect = [[], [], ["/dev/ttyS0"]]
        mock_exists.return_value = True
        mock_access.return_value = True

        from utils.serial_monitor import collect_serial_ports
        result = collect_serial_ports()

        assert len(result) == 1
        assert result[0]["path"] == "/dev/ttyS0"
        assert result[0]["type"] == "Standard"

    @patch("utils.serial_monitor.os.access")
    @patch("utils.serial_monitor.os.path.exists")
    @patch("utils.serial_monitor.glob.glob")
    def test_returns_multiple_ports(
        self, mock_glob: MagicMock, mock_exists: MagicMock,
        mock_access: MagicMock
    ) -> None:
        """여러 시리얼 포트가 있으면 모두 반환해야 합니다."""
        mock_glob.side_effect = [
            ["/dev/ttyUSB0", "/dev/ttyUSB1"],
            ["/dev/ttyACM0"],
            [],
        ]
        mock_exists.return_value = True
        mock_access.return_value = True

        from utils.serial_monitor import collect_serial_ports
        result = collect_serial_ports()

        assert len(result) == 3
        paths = {r["path"] for r in result}
        assert paths == {"/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0"}

    @patch("utils.serial_monitor.glob.glob")
    def test_returns_empty_when_no_ports(
        self, mock_glob: MagicMock
    ) -> None:
        """시리얼 포트가 없으면 빈 리스트를 반환해야 합니다."""
        mock_glob.return_value = []
        from utils.serial_monitor import collect_serial_ports
        result = collect_serial_ports()
        assert result == []

    @patch("utils.serial_monitor.os.access")
    @patch("utils.serial_monitor.os.path.exists")
    @patch("utils.serial_monitor.glob.glob")
    def test_marks_nonexistent_port(
        self, mock_glob: MagicMock, mock_exists: MagicMock,
        mock_access: MagicMock
    ) -> None:
        """존재하지 않는 포트는 exists=False로 표시해야 합니다."""
        mock_glob.side_effect = [["/dev/ttyUSB0"], [], []]
        mock_exists.return_value = False
        mock_access.return_value = False

        from utils.serial_monitor import collect_serial_ports
        result = collect_serial_ports()

        assert len(result) == 1
        assert result[0]["exists"] is False

    @patch("utils.serial_monitor.glob.glob")
    def test_return_type_is_list_of_dicts(
        self, mock_glob: MagicMock
    ) -> None:
        """반환 타입이 list[dict]여야 합니다."""
        mock_glob.return_value = []
        from utils.serial_monitor import collect_serial_ports
        result = collect_serial_ports()
        assert isinstance(result, list)

    @patch("utils.serial_monitor.os.access")
    @patch("utils.serial_monitor.os.path.exists")
    @patch("utils.serial_monitor.glob.glob")
    def test_result_has_required_fields(
        self, mock_glob: MagicMock, mock_exists: MagicMock,
        mock_access: MagicMock
    ) -> None:
        """결과에 필수 필드가 모두 포함되어야 합니다."""
        mock_glob.side_effect = [["/dev/ttyUSB0"], [], []]
        mock_exists.return_value = True
        mock_access.return_value = True

        from utils.serial_monitor import collect_serial_ports
        result = collect_serial_ports()

        assert len(result) == 1
        required_fields = {"path", "type", "exists"}
        assert required_fields.issubset(set(result[0].keys()))
