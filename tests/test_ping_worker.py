"""services/ping_worker.py에 대한 사양 테스트.

PingWorker(QObject)의 시그널 발신, 에러 처리를 검증합니다.
"""
import pytest
from unittest.mock import patch, MagicMock

from PyQt5.QtCore import QObject


class TestPingWorkerInit:
    """PingWorker 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """PingWorker 인스턴스를 생성할 수 있어야 합니다."""
        from services.ping_worker import PingWorker
        worker = PingWorker()
        assert worker is not None

    def test_is_qobject(self, qapp) -> None:
        """QObject를 상속해야 합니다."""
        from services.ping_worker import PingWorker
        worker = PingWorker()
        assert isinstance(worker, QObject)

    def test_has_ping_started_signal(self, qapp) -> None:
        """pingStarted 시그널이 있어야 합니다."""
        from services.ping_worker import PingWorker
        worker = PingWorker()
        assert hasattr(worker, "pingStarted")

    def test_has_ping_finished_signal(self, qapp) -> None:
        """pingFinished 시그널이 있어야 합니다."""
        from services.ping_worker import PingWorker
        worker = PingWorker()
        assert hasattr(worker, "pingFinished")

    def test_has_ping_error_signal(self, qapp) -> None:
        """pingError 시그널이 있어야 합니다."""
        from services.ping_worker import PingWorker
        worker = PingWorker()
        assert hasattr(worker, "pingError")


class TestPingWorkerExecutePing:
    """PingWorker.execute_ping() 메서드를 검증합니다."""

    @patch("services.ping_worker.run_ping")
    def test_emits_ping_started(self, mock_run_ping: MagicMock, qapp) -> None:
        """ping 시작 시 pingStarted 시그널을 발신해야 합니다."""
        mock_run_ping.return_value = {
            "target": "8.8.8.8",
            "packets_transmitted": 4,
            "packets_received": 4,
            "packet_loss": 0.0,
            "rtt_min": 1.0, "rtt_avg": 2.0,
            "rtt_max": 3.0, "rtt_mdev": 0.5,
        }

        from services.ping_worker import PingWorker
        worker = PingWorker()

        started_called = []
        worker.pingStarted.connect(lambda: started_called.append(True))
        worker.execute_ping("8.8.8.8")

        assert len(started_called) == 1

    @patch("services.ping_worker.run_ping")
    def test_emits_ping_finished_on_success(self, mock_run_ping: MagicMock, qapp) -> None:
        """성공 시 pingFinished 시그널을 발신해야 합니다."""
        expected = {
            "target": "8.8.8.8",
            "packets_transmitted": 4,
            "packets_received": 4,
            "packet_loss": 0.0,
            "rtt_min": 1.0, "rtt_avg": 2.0,
            "rtt_max": 3.0, "rtt_mdev": 0.5,
        }
        mock_run_ping.return_value = expected

        from services.ping_worker import PingWorker
        worker = PingWorker()

        results = []
        worker.pingFinished.connect(lambda r: results.append(r))
        worker.execute_ping("8.8.8.8")

        assert len(results) == 1
        assert results[0]["target"] == "8.8.8.8"

    @patch("services.ping_worker.run_ping")
    def test_emits_ping_error_on_failure(self, mock_run_ping: MagicMock, qapp) -> None:
        """에러 발생 시 pingError 시그널을 발신해야 합니다."""
        mock_run_ping.return_value = {"error": "호스트를 찾을 수 없습니다"}

        from services.ping_worker import PingWorker
        worker = PingWorker()

        errors = []
        worker.pingError.connect(lambda e: errors.append(e))
        worker.execute_ping("nonexistent.invalid")

        assert len(errors) == 1
        assert "호스트를 찾을 수 없습니다" in errors[0]

    @patch("services.ping_worker.run_ping")
    def test_does_not_emit_finished_on_error(self, mock_run_ping: MagicMock, qapp) -> None:
        """에러 발생 시 pingFinished를 발신하지 않아야 합니다."""
        mock_run_ping.return_value = {"error": "에러 발생"}

        from services.ping_worker import PingWorker
        worker = PingWorker()

        results = []
        worker.pingFinished.connect(lambda r: results.append(r))
        worker.execute_ping("bad.target")

        assert len(results) == 0

    @patch("services.ping_worker.run_ping")
    def test_handles_exception(self, mock_run_ping: MagicMock, qapp) -> None:
        """run_ping에서 예외 발생 시 pingError를 발신해야 합니다."""
        mock_run_ping.side_effect = RuntimeError("예상치 못한 오류")

        from services.ping_worker import PingWorker
        worker = PingWorker()

        errors = []
        worker.pingError.connect(lambda e: errors.append(e))
        worker.execute_ping("8.8.8.8")

        assert len(errors) == 1
