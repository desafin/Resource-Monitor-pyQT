"""views/process_viewmodel.py에 대한 사양 테스트.

ProcessViewModel의 프로퍼티, 시그널, 슬롯, 워커 스레드 관리를 검증합니다.
"""
import signal
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtCore import Qt

from views.process_viewmodel import ProcessViewModel
from models.process_model import ProcessModel
from models.process_sort_filter_model import ProcessSortFilterModel


class TestProcessViewModelInit:
    """ProcessViewModel 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """인스턴스를 생성할 수 있어야 합니다."""
        vm = ProcessViewModel()
        assert vm is not None
        vm.cleanup()

    def test_has_process_model(self, qapp) -> None:
        """processModel 프로퍼티가 존재해야 합니다."""
        vm = ProcessViewModel()
        model = vm.processModel
        assert model is not None
        vm.cleanup()

    def test_process_model_is_sort_filter_proxy(self, qapp) -> None:
        """processModel은 ProcessSortFilterModel이어야 합니다."""
        vm = ProcessViewModel()
        model = vm.processModel
        assert isinstance(model, ProcessSortFilterModel)
        vm.cleanup()


class TestProcessViewModelProperties:
    """ProcessViewModel의 Q_PROPERTY를 검증합니다."""

    def test_initial_search_text_empty(self, qapp) -> None:
        """초기 searchText는 빈 문자열이어야 합니다."""
        vm = ProcessViewModel()
        assert vm.searchText == ""
        vm.cleanup()

    def test_set_search_text(self, qapp) -> None:
        """searchText를 설정할 수 있어야 합니다."""
        vm = ProcessViewModel()
        vm.searchText = "firefox"
        assert vm.searchText == "firefox"
        vm.cleanup()

    def test_initial_sort_column(self, qapp) -> None:
        """초기 sortColumn은 'cpu'여야 합니다."""
        vm = ProcessViewModel()
        assert vm.sortColumn == "cpu"
        vm.cleanup()

    def test_set_sort_column(self, qapp) -> None:
        """sortColumn을 설정할 수 있어야 합니다."""
        vm = ProcessViewModel()
        vm.sortColumn = "name"
        assert vm.sortColumn == "name"
        vm.cleanup()

    def test_initial_sort_order(self, qapp) -> None:
        """초기 sortOrder는 Qt.DescendingOrder여야 합니다."""
        vm = ProcessViewModel()
        assert vm.sortOrder == Qt.DescendingOrder
        vm.cleanup()

    def test_set_sort_order(self, qapp) -> None:
        """sortOrder를 설정할 수 있어야 합니다."""
        vm = ProcessViewModel()
        vm.sortOrder = Qt.AscendingOrder
        assert vm.sortOrder == Qt.AscendingOrder
        vm.cleanup()


class TestProcessViewModelSlots:
    """ProcessViewModel의 프로세스 제어 슬롯을 검증합니다."""

    @patch("views.process_viewmodel.send_signal")
    def test_kill_process(self, mock_send: MagicMock, qapp) -> None:
        """killProcess()는 SIGKILL을 전송해야 합니다."""
        mock_send.return_value = (True, "성공")
        vm = ProcessViewModel()
        vm.killProcess(1000)
        mock_send.assert_called_once_with(1000, signal.SIGKILL)
        vm.cleanup()

    @patch("views.process_viewmodel.send_signal")
    def test_terminate_process(self, mock_send: MagicMock, qapp) -> None:
        """terminateProcess()는 SIGTERM을 전송해야 합니다."""
        mock_send.return_value = (True, "성공")
        vm = ProcessViewModel()
        vm.terminateProcess(1000)
        mock_send.assert_called_once_with(1000, signal.SIGTERM)
        vm.cleanup()

    @patch("views.process_viewmodel.send_signal")
    def test_suspend_process(self, mock_send: MagicMock, qapp) -> None:
        """suspendProcess()는 SIGSTOP을 전송해야 합니다."""
        mock_send.return_value = (True, "성공")
        vm = ProcessViewModel()
        vm.suspendProcess(1000)
        mock_send.assert_called_once_with(1000, signal.SIGSTOP)
        vm.cleanup()

    @patch("views.process_viewmodel.send_signal")
    def test_resume_process(self, mock_send: MagicMock, qapp) -> None:
        """resumeProcess()는 SIGCONT를 전송해야 합니다."""
        mock_send.return_value = (True, "성공")
        vm = ProcessViewModel()
        vm.resumeProcess(1000)
        mock_send.assert_called_once_with(1000, signal.SIGCONT)
        vm.cleanup()

    @patch("views.process_viewmodel.change_nice")
    def test_change_nice(self, mock_nice: MagicMock, qapp) -> None:
        """changeNice()는 change_nice()를 호출해야 합니다."""
        mock_nice.return_value = (True, "성공")
        vm = ProcessViewModel()
        vm.changeNice(1000, 10)
        mock_nice.assert_called_once_with(1000, 10)
        vm.cleanup()


class TestProcessViewModelErrorSignal:
    """ProcessViewModel의 에러 시그널을 검증합니다."""

    @patch("views.process_viewmodel.send_signal")
    def test_error_signal_on_failure(self, mock_send: MagicMock, qapp) -> None:
        """프로세스 제어 실패 시 errorOccurred 시그널이 발생해야 합니다."""
        mock_send.return_value = (False, "권한 없음")
        vm = ProcessViewModel()

        errors: list[str] = []
        vm.errorOccurred.connect(lambda msg: errors.append(msg))

        vm.killProcess(1)
        assert len(errors) == 1
        assert "권한 없음" in errors[0]
        vm.cleanup()

    @patch("views.process_viewmodel.change_nice")
    def test_error_signal_on_nice_failure(self, mock_nice: MagicMock, qapp) -> None:
        """우선순위 변경 실패 시 errorOccurred 시그널이 발생해야 합니다."""
        mock_nice.return_value = (False, "권한 없음")
        vm = ProcessViewModel()

        errors: list[str] = []
        vm.errorOccurred.connect(lambda msg: errors.append(msg))

        vm.changeNice(1, -5)
        assert len(errors) == 1
        vm.cleanup()
