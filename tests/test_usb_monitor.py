"""utils/usb_monitor.py에 대한 사양 테스트.

USB 장치 목록을 /sys/bus/usb/devices/에서 읽어오는 기능을 검증합니다.
collect_usb_devices()와 is_usb_available() 함수를 테스트합니다.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestIsUsbAvailable:
    """is_usb_available() 함수를 검증합니다."""

    @patch("utils.usb_monitor.os.path.isdir")
    def test_returns_true_when_usb_dir_exists(
        self, mock_isdir: MagicMock
    ) -> None:
        """USB 디렉터리가 존재하면 True를 반환해야 합니다."""
        mock_isdir.return_value = True
        from utils.usb_monitor import is_usb_available
        assert is_usb_available() is True

    @patch("utils.usb_monitor.os.path.isdir")
    def test_returns_false_when_usb_dir_missing(
        self, mock_isdir: MagicMock
    ) -> None:
        """USB 디렉터리가 없으면 False를 반환해야 합니다."""
        mock_isdir.return_value = False
        from utils.usb_monitor import is_usb_available
        assert is_usb_available() is False


class TestCollectUsbDevices:
    """collect_usb_devices() 함수를 검증합니다."""

    @patch("utils.usb_monitor.os.path.isdir")
    def test_returns_empty_when_usb_dir_missing(
        self, mock_isdir: MagicMock
    ) -> None:
        """USB 디렉터리가 없으면 빈 리스트를 반환해야 합니다."""
        mock_isdir.return_value = False
        from utils.usb_monitor import collect_usb_devices
        result = collect_usb_devices()
        assert result == []

    @patch("builtins.open")
    @patch("utils.usb_monitor.os.listdir")
    @patch("utils.usb_monitor.os.path.isfile")
    @patch("utils.usb_monitor.os.path.isdir")
    def test_returns_usb_device_data(
        self, mock_isdir: MagicMock, mock_isfile: MagicMock,
        mock_listdir: MagicMock, mock_open: MagicMock
    ) -> None:
        """USB 장치 정보를 올바르게 반환해야 합니다."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["1-1"]
        mock_isfile.return_value = True

        file_contents = {
            "idVendor": "046d",
            "idProduct": "c077",
            "manufacturer": "Logitech",
            "product": "USB Mouse",
            "busnum": "1",
            "devnum": "3",
        }

        def open_side_effect(path: str, *args, **kwargs):
            m = MagicMock()
            for key, value in file_contents.items():
                if key in path:
                    m.__enter__ = MagicMock(
                        return_value=MagicMock(read=MagicMock(return_value=f"{value}\n"))
                    )
                    m.__exit__ = MagicMock(return_value=False)
                    return m
            m.__enter__ = MagicMock(
                return_value=MagicMock(read=MagicMock(return_value="N/A\n"))
            )
            m.__exit__ = MagicMock(return_value=False)
            return m

        mock_open.side_effect = open_side_effect

        from utils.usb_monitor import collect_usb_devices
        result = collect_usb_devices()

        assert len(result) == 1
        device = result[0]
        assert device["vendor_id"] == "046d"
        assert device["product_id"] == "c077"
        assert device["manufacturer"] == "Logitech"
        assert device["product"] == "USB Mouse"

    @patch("builtins.open")
    @patch("utils.usb_monitor.os.listdir")
    @patch("utils.usb_monitor.os.path.isfile")
    @patch("utils.usb_monitor.os.path.isdir")
    def test_skips_entries_without_idvendor(
        self, mock_isdir: MagicMock, mock_isfile: MagicMock,
        mock_listdir: MagicMock, mock_open: MagicMock
    ) -> None:
        """idVendor 파일이 없는 항목은 건너뛰어야 합니다."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["usb1"]

        def isfile_side_effect(path: str) -> bool:
            # idVendor 파일이 없는 경우
            if "idVendor" in path:
                return False
            return True

        mock_isfile.side_effect = isfile_side_effect

        from utils.usb_monitor import collect_usb_devices
        result = collect_usb_devices()
        assert result == []

    @patch("builtins.open")
    @patch("utils.usb_monitor.os.listdir")
    @patch("utils.usb_monitor.os.path.isfile")
    @patch("utils.usb_monitor.os.path.isdir")
    def test_handles_permission_error_gracefully(
        self, mock_isdir: MagicMock, mock_isfile: MagicMock,
        mock_listdir: MagicMock, mock_open: MagicMock
    ) -> None:
        """읽기 권한이 없는 필드는 'N/A'로 처리해야 합니다."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["2-1"]
        mock_isfile.return_value = True

        call_count = 0

        def open_side_effect(path: str, *args, **kwargs):
            nonlocal call_count
            m = MagicMock()
            if "idVendor" in path:
                m.__enter__ = MagicMock(
                    return_value=MagicMock(read=MagicMock(return_value="1234\n"))
                )
                m.__exit__ = MagicMock(return_value=False)
                return m
            elif "idProduct" in path:
                m.__enter__ = MagicMock(
                    return_value=MagicMock(read=MagicMock(return_value="5678\n"))
                )
                m.__exit__ = MagicMock(return_value=False)
                return m
            elif "busnum" in path:
                m.__enter__ = MagicMock(
                    return_value=MagicMock(read=MagicMock(return_value="2\n"))
                )
                m.__exit__ = MagicMock(return_value=False)
                return m
            elif "devnum" in path:
                m.__enter__ = MagicMock(
                    return_value=MagicMock(read=MagicMock(return_value="1\n"))
                )
                m.__exit__ = MagicMock(return_value=False)
                return m
            else:
                raise PermissionError("권한 없음")

        mock_open.side_effect = open_side_effect

        from utils.usb_monitor import collect_usb_devices
        result = collect_usb_devices()

        assert len(result) == 1
        assert result[0]["manufacturer"] == "N/A"
        assert result[0]["product"] == "N/A"

    @patch("utils.usb_monitor.os.listdir")
    @patch("utils.usb_monitor.os.path.isdir")
    def test_returns_empty_when_no_devices(
        self, mock_isdir: MagicMock, mock_listdir: MagicMock
    ) -> None:
        """장치가 없으면 빈 리스트를 반환해야 합니다."""
        mock_isdir.return_value = True
        mock_listdir.return_value = []
        from utils.usb_monitor import collect_usb_devices
        result = collect_usb_devices()
        assert result == []

    def test_return_type_is_list(self) -> None:
        """반환 타입이 list여야 합니다."""
        with patch("utils.usb_monitor.os.path.isdir", return_value=False):
            from utils.usb_monitor import collect_usb_devices
            result = collect_usb_devices()
            assert isinstance(result, list)

    @patch("builtins.open")
    @patch("utils.usb_monitor.os.listdir")
    @patch("utils.usb_monitor.os.path.isfile")
    @patch("utils.usb_monitor.os.path.isdir")
    def test_result_has_required_fields(
        self, mock_isdir: MagicMock, mock_isfile: MagicMock,
        mock_listdir: MagicMock, mock_open: MagicMock
    ) -> None:
        """결과에 필수 필드가 모두 포함되어야 합니다."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ["1-1"]
        mock_isfile.return_value = True

        def open_side_effect(path: str, *args, **kwargs):
            m = MagicMock()
            m.__enter__ = MagicMock(
                return_value=MagicMock(read=MagicMock(return_value="test\n"))
            )
            m.__exit__ = MagicMock(return_value=False)
            return m

        mock_open.side_effect = open_side_effect

        from utils.usb_monitor import collect_usb_devices
        result = collect_usb_devices()

        assert len(result) == 1
        required_fields = {"bus", "device", "vendor_id", "product_id",
                           "manufacturer", "product", "path"}
        assert required_fields.issubset(set(result[0].keys()))
