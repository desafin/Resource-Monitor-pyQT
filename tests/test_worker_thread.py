"""ProcessWorker의 동작에 대한 특성화 테스트.

services/worker_thread.py의 현재 동작을 포착합니다:
- start_collecting() 상태 전환 및 멱등성
- stop_collecting() 타이머 정리 동작
- _collect() 프로세스 수집 및 시그널 방출
- 예외 처리 동작
"""
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class TestProcessWorkerInit:
    """ProcessWorker 초기화 동작을 검증합니다."""

    @pytest.fixture
    def worker(self, qapp: Any) -> Any:
        """테스트용 ProcessWorker 인스턴스를 반환합니다."""
        from services.worker_thread import ProcessWorker
        return ProcessWorker()

    def test_initial_running_is_false(self, worker: Any) -> None:
        """초기 _running 값은 False여야 합니다."""
        assert worker._running is False

    def test_initial_timer_is_none(self, worker: Any) -> None:
        """초기 _timer 값은 None이어야 합니다."""
        assert worker._timer is None


class TestProcessWorkerStartCollecting:
    """ProcessWorker.start_collecting() 동작을 검증합니다."""

    @pytest.fixture
    def worker(self, qapp: Any) -> Any:
        """테스트용 ProcessWorker 인스턴스를 반환합니다."""
        from services.worker_thread import ProcessWorker
        return ProcessWorker()

    def test_start_collecting_sets_running_true(self, worker: Any) -> None:
        """start_collecting() 호출 후 _running이 True여야 합니다."""
        with patch("services.worker_thread.collect_processes", return_value=[]):
            with patch("services.worker_thread.QTimer") as mock_timer_cls:
                mock_timer_cls.return_value = MagicMock()
                worker.start_collecting()
        assert worker._running is True

    def test_start_collecting_creates_timer(self, worker: Any) -> None:
        """start_collecting() 호출 시 QTimer가 생성되어야 합니다."""
        with patch("services.worker_thread.collect_processes", return_value=[]):
            with patch("services.worker_thread.QTimer") as mock_timer_cls:
                mock_instance = MagicMock()
                mock_timer_cls.return_value = mock_instance
                worker.start_collecting()
                mock_timer_cls.assert_called_once()

    def test_start_collecting_starts_timer(self, worker: Any) -> None:
        """start_collecting() 호출 시 타이머가 시작되어야 합니다."""
        with patch("services.worker_thread.collect_processes", return_value=[]):
            with patch("services.worker_thread.QTimer") as mock_timer_cls:
                mock_instance = MagicMock()
                mock_timer_cls.return_value = mock_instance
                worker.start_collecting()
                mock_instance.start.assert_called_once_with(2000)

    def test_start_collecting_calls_collect_immediately(self, worker: Any) -> None:
        """start_collecting() 호출 시 즉시 _collect()가 한 번 실행되어야 합니다."""
        collected_signals: list = []
        worker.finished.connect(lambda procs: collected_signals.append(procs))

        with patch("services.worker_thread.collect_processes", return_value=[{"pid": 1}]):
            with patch("services.worker_thread.QTimer") as mock_timer_cls:
                mock_timer_cls.return_value = MagicMock()
                worker.start_collecting()

        assert len(collected_signals) == 1
        assert collected_signals[0] == [{"pid": 1}]

    def test_start_collecting_is_idempotent(self, worker: Any) -> None:
        """start_collecting()을 두 번 호출해도 타이머는 한 번만 생성되어야 합니다."""
        with patch("services.worker_thread.collect_processes", return_value=[]):
            with patch("services.worker_thread.QTimer") as mock_timer_cls:
                mock_instance = MagicMock()
                mock_timer_cls.return_value = mock_instance
                worker.start_collecting()
                worker.start_collecting()
                # QTimer는 한 번만 생성되어야 함
                assert mock_timer_cls.call_count == 1

    def test_start_collecting_idempotent_collect_once(self, worker: Any) -> None:
        """start_collecting()을 두 번 호출해도 collect는 한 번만 실행되어야 합니다."""
        collected_signals: list = []
        worker.finished.connect(lambda procs: collected_signals.append(procs))

        with patch("services.worker_thread.collect_processes", return_value=[]) as mock_collect:
            with patch("services.worker_thread.QTimer") as mock_timer_cls:
                mock_timer_cls.return_value = MagicMock()
                worker.start_collecting()
                worker.start_collecting()

        assert mock_collect.call_count == 1


class TestProcessWorkerStopCollecting:
    """ProcessWorker.stop_collecting() 동작을 검증합니다."""

    @pytest.fixture
    def worker(self, qapp: Any) -> Any:
        """테스트용 ProcessWorker 인스턴스를 반환합니다."""
        from services.worker_thread import ProcessWorker
        return ProcessWorker()

    def test_stop_collecting_sets_running_false(self, worker: Any) -> None:
        """stop_collecting() 호출 후 _running이 False여야 합니다."""
        with patch("services.worker_thread.collect_processes", return_value=[]):
            with patch("services.worker_thread.QTimer") as mock_timer_cls:
                mock_timer_cls.return_value = MagicMock()
                worker.start_collecting()
        worker.stop_collecting()
        assert worker._running is False

    def test_stop_collecting_stops_timer(self, worker: Any) -> None:
        """stop_collecting() 호출 시 타이머의 stop()이 호출되어야 합니다."""
        mock_timer = MagicMock()
        with patch("services.worker_thread.collect_processes", return_value=[]):
            with patch("services.worker_thread.QTimer") as mock_timer_cls:
                mock_timer_cls.return_value = mock_timer
                worker.start_collecting()
        worker.stop_collecting()
        mock_timer.stop.assert_called_once()

    def test_stop_collecting_deletes_timer(self, worker: Any) -> None:
        """stop_collecting() 호출 시 타이머의 deleteLater()가 호출되어야 합니다."""
        mock_timer = MagicMock()
        with patch("services.worker_thread.collect_processes", return_value=[]):
            with patch("services.worker_thread.QTimer") as mock_timer_cls:
                mock_timer_cls.return_value = mock_timer
                worker.start_collecting()
        worker.stop_collecting()
        mock_timer.deleteLater.assert_called_once()

    def test_stop_collecting_sets_timer_to_none(self, worker: Any) -> None:
        """stop_collecting() 호출 후 _timer가 None이어야 합니다."""
        with patch("services.worker_thread.collect_processes", return_value=[]):
            with patch("services.worker_thread.QTimer") as mock_timer_cls:
                mock_timer_cls.return_value = MagicMock()
                worker.start_collecting()
        worker.stop_collecting()
        assert worker._timer is None

    def test_stop_collecting_safe_when_timer_is_none(self, worker: Any) -> None:
        """타이머가 None일 때 stop_collecting() 호출 시 예외가 발생하지 않아야 합니다."""
        assert worker._timer is None
        # 예외 없이 실행되어야 함
        worker.stop_collecting()
        assert worker._running is False


class TestProcessWorkerCollect:
    """ProcessWorker._collect() 내부 메서드 동작을 검증합니다."""

    @pytest.fixture
    def worker(self, qapp: Any) -> Any:
        """테스트용 ProcessWorker 인스턴스를 반환합니다."""
        from services.worker_thread import ProcessWorker
        return ProcessWorker()

    def test_collect_emits_finished_with_process_list(self, worker: Any) -> None:
        """_collect()는 collect_processes() 결과를 finished 시그널로 방출해야 합니다."""
        process_data = [{"pid": 100, "name": "python3"}]
        received: list = []
        worker.finished.connect(lambda procs: received.append(procs))

        with patch("services.worker_thread.collect_processes", return_value=process_data):
            worker._collect()

        assert len(received) == 1
        assert received[0] == process_data

    def test_collect_calls_collect_processes(self, worker: Any) -> None:
        """_collect()는 collect_processes()를 호출해야 합니다."""
        with patch("services.worker_thread.collect_processes", return_value=[]) as mock_collect:
            worker._collect()
        mock_collect.assert_called_once()

    def test_collect_emits_empty_list_on_exception(self, worker: Any) -> None:
        """collect_processes()에서 예외 발생 시 finished 시그널에 빈 리스트를 방출해야 합니다."""
        received: list = []
        worker.finished.connect(lambda procs: received.append(procs))

        with patch("services.worker_thread.collect_processes", side_effect=RuntimeError("수집 오류")):
            worker._collect()

        assert len(received) == 1
        assert received[0] == []

    def test_collect_does_not_raise_on_exception(self, worker: Any) -> None:
        """collect_processes() 예외 발생 시 예외가 전파되지 않아야 합니다."""
        with patch("services.worker_thread.collect_processes", side_effect=Exception("예상치 못한 오류")):
            # 예외 없이 실행되어야 함
            worker._collect()
