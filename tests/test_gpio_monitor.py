"""utils/gpio_monitor.py에 대한 사양 테스트.

GPIO 핀 상태를 /sys/class/gpio/에서 읽어오는 기능을 검증합니다.
collect_gpio_pins()와 is_gpio_available() 함수를 테스트합니다.
"""
import os
import pytest
from unittest.mock import patch, MagicMock


class TestIsGpioAvailable:
    """is_gpio_available() 함수를 검증합니다."""

    @patch("utils.gpio_monitor.os.path.isdir")
    @patch("utils.gpio_monitor.os.access")
    def test_returns_true_when_gpio_dir_exists_and_readable(
        self, mock_access: MagicMock, mock_isdir: MagicMock
    ) -> None:
        """GPIO 디렉터리가 존재하고 읽기 가능하면 True를 반환해야 합니다."""
        mock_isdir.return_value = True
        mock_access.return_value = True
        from utils.gpio_monitor import is_gpio_available
        assert is_gpio_available() is True

    @patch("utils.gpio_monitor.os.path.isdir")
    def test_returns_false_when_gpio_dir_missing(
        self, mock_isdir: MagicMock
    ) -> None:
        """GPIO 디렉터리가 없으면 False를 반환해야 합니다."""
        mock_isdir.return_value = False
        from utils.gpio_monitor import is_gpio_available
        assert is_gpio_available() is False

    @patch("utils.gpio_monitor.os.path.isdir")
    @patch("utils.gpio_monitor.os.access")
    def test_returns_false_when_gpio_dir_not_readable(
        self, mock_access: MagicMock, mock_isdir: MagicMock
    ) -> None:
        """GPIO 디렉터리가 읽기 불가하면 False를 반환해야 합니다."""
        mock_isdir.return_value = True
        mock_access.return_value = False
        from utils.gpio_monitor import is_gpio_available
        assert is_gpio_available() is False


class TestCollectGpioPins:
    """collect_gpio_pins() 함수를 검증합니다."""

    @patch("utils.gpio_monitor.os.listdir")
    @patch("utils.gpio_monitor.os.path.isdir")
    def test_returns_empty_list_when_no_gpio_dirs(
        self, mock_isdir: MagicMock, mock_listdir: MagicMock
    ) -> None:
        """GPIO 핀이 없으면 빈 리스트를 반환해야 합니다."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["export", "unexport"]
        from utils.gpio_monitor import collect_gpio_pins
        result = collect_gpio_pins()
        assert result == []

    @patch("builtins.open")
    @patch("utils.gpio_monitor.os.listdir")
    @patch("utils.gpio_monitor.os.path.isdir")
    def test_returns_pin_data_for_exported_gpio(
        self, mock_isdir: MagicMock, mock_listdir: MagicMock,
        mock_open: MagicMock
    ) -> None:
        """내보낸 GPIO 핀의 데이터를 올바르게 반환해야 합니다."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["gpio17", "export", "unexport"]

        # open() 호출 시 direction과 value 파일 읽기 모의
        def open_side_effect(path: str, *args, **kwargs):
            m = MagicMock()
            if "direction" in path:
                m.__enter__ = MagicMock(return_value=MagicMock(read=MagicMock(return_value="in\n")))
            elif "value" in path:
                m.__enter__ = MagicMock(return_value=MagicMock(read=MagicMock(return_value="1\n")))
            m.__exit__ = MagicMock(return_value=False)
            return m

        mock_open.side_effect = open_side_effect

        from utils.gpio_monitor import collect_gpio_pins
        result = collect_gpio_pins()

        assert len(result) == 1
        assert result[0]["pin"] == 17
        assert result[0]["direction"] == "in"
        assert result[0]["value"] == 1

    @patch("builtins.open")
    @patch("utils.gpio_monitor.os.listdir")
    @patch("utils.gpio_monitor.os.path.isdir")
    def test_returns_multiple_pins(
        self, mock_isdir: MagicMock, mock_listdir: MagicMock,
        mock_open: MagicMock
    ) -> None:
        """여러 GPIO 핀이 있으면 모두 반환해야 합니다."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["gpio4", "gpio17", "export"]

        def open_side_effect(path: str, *args, **kwargs):
            m = MagicMock()
            if "direction" in path:
                m.__enter__ = MagicMock(return_value=MagicMock(read=MagicMock(return_value="out\n")))
            elif "value" in path:
                m.__enter__ = MagicMock(return_value=MagicMock(read=MagicMock(return_value="0\n")))
            m.__exit__ = MagicMock(return_value=False)
            return m

        mock_open.side_effect = open_side_effect

        from utils.gpio_monitor import collect_gpio_pins
        result = collect_gpio_pins()

        assert len(result) == 2
        pins = {r["pin"] for r in result}
        assert pins == {4, 17}

    @patch("builtins.open")
    @patch("utils.gpio_monitor.os.listdir")
    @patch("utils.gpio_monitor.os.path.isdir")
    def test_handles_file_not_found_error(
        self, mock_isdir: MagicMock, mock_listdir: MagicMock,
        mock_open: MagicMock
    ) -> None:
        """파일을 읽을 수 없으면 해당 핀을 건너뛰어야 합니다."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["gpio5"]
        mock_open.side_effect = FileNotFoundError("파일 없음")

        from utils.gpio_monitor import collect_gpio_pins
        result = collect_gpio_pins()
        assert result == []

    @patch("builtins.open")
    @patch("utils.gpio_monitor.os.listdir")
    @patch("utils.gpio_monitor.os.path.isdir")
    def test_handles_permission_error(
        self, mock_isdir: MagicMock, mock_listdir: MagicMock,
        mock_open: MagicMock
    ) -> None:
        """권한 오류 시 해당 핀을 건너뛰어야 합니다."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["gpio10"]
        mock_open.side_effect = PermissionError("권한 없음")

        from utils.gpio_monitor import collect_gpio_pins
        result = collect_gpio_pins()
        assert result == []

    @patch("utils.gpio_monitor.os.path.isdir")
    def test_returns_empty_when_gpio_dir_missing(
        self, mock_isdir: MagicMock
    ) -> None:
        """GPIO 디렉터리가 없으면 빈 리스트를 반환해야 합니다."""
        mock_isdir.return_value = False
        from utils.gpio_monitor import collect_gpio_pins
        result = collect_gpio_pins()
        assert result == []

    def test_return_type_is_list_of_dicts(self) -> None:
        """반환 타입이 list[dict]여야 합니다."""
        with patch("utils.gpio_monitor.os.path.isdir", return_value=True), \
             patch("utils.gpio_monitor.os.listdir", return_value=[]):
            from utils.gpio_monitor import collect_gpio_pins
            result = collect_gpio_pins()
            assert isinstance(result, list)
