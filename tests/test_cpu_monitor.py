"""utils/cpu_monitor.py에 대한 특성화 테스트.

CPUMonitor.measure() 동작을 검증합니다.
"""
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cpu_monitor import CPUMonitor


class TestCPUMonitorInit:
    """CPUMonitor 초기화를 검증합니다."""

    def test_creates_instance(self) -> None:
        """CPUMonitor 인스턴스를 생성할 수 있어야 합니다."""
        monitor = CPUMonitor()
        assert monitor is not None

    def test_initial_current_measurement_is_zero(self) -> None:
        """초기 current_measurement는 0이어야 합니다."""
        monitor = CPUMonitor()
        assert monitor.current_measurement == 0

    def test_initial_last_measurement_is_zero(self) -> None:
        """초기 last_measurement는 0이어야 합니다."""
        monitor = CPUMonitor()
        assert monitor.last_measurement == 0


class TestCPUMonitorMeasure:
    """CPUMonitor.measure() 동작을 검증합니다."""

    @patch("utils.cpu_monitor.psutil.cpu_percent")
    def test_measure_returns_cpu_percent_value(
        self, mock_cpu_percent: MagicMock
    ) -> None:
        """measure()는 psutil.cpu_percent 반환값을 돌려줘야 합니다."""
        mock_cpu_percent.return_value = 42.5
        monitor = CPUMonitor()
        result = monitor.measure()
        assert result == 42.5

    @patch("utils.cpu_monitor.psutil.cpu_percent")
    def test_measure_updates_current_measurement(
        self, mock_cpu_percent: MagicMock
    ) -> None:
        """measure() 호출 후 current_measurement가 갱신되어야 합니다."""
        mock_cpu_percent.return_value = 55.0
        monitor = CPUMonitor()
        monitor.measure()
        assert monitor.current_measurement == 55.0

    @patch("utils.cpu_monitor.psutil.cpu_percent")
    def test_measure_moves_current_to_last(
        self, mock_cpu_percent: MagicMock
    ) -> None:
        """두 번째 measure() 호출 시 이전 current_measurement가 last_measurement로 이동해야 합니다."""
        mock_cpu_percent.side_effect = [30.0, 60.0]
        monitor = CPUMonitor()
        monitor.measure()
        monitor.measure()
        assert monitor.last_measurement == 30.0
        assert monitor.current_measurement == 60.0

    @patch("utils.cpu_monitor.psutil.cpu_percent")
    def test_measure_calls_psutil_with_interval(
        self, mock_cpu_percent: MagicMock
    ) -> None:
        """measure()는 interval=0.1을 사용하여 psutil.cpu_percent를 호출해야 합니다."""
        mock_cpu_percent.return_value = 10.0
        monitor = CPUMonitor()
        monitor.measure()
        mock_cpu_percent.assert_called_once_with(interval=0.1)

    @patch("utils.cpu_monitor.psutil.cpu_percent")
    def test_measure_returns_zero_when_cpu_idle(
        self, mock_cpu_percent: MagicMock
    ) -> None:
        """CPU가 유휴 상태일 때 0.0을 반환해야 합니다."""
        mock_cpu_percent.return_value = 0.0
        monitor = CPUMonitor()
        result = monitor.measure()
        assert result == 0.0

    @patch("utils.cpu_monitor.psutil.cpu_percent")
    def test_measure_returns_100_at_full_load(
        self, mock_cpu_percent: MagicMock
    ) -> None:
        """CPU가 최대 부하일 때 100.0을 반환해야 합니다."""
        mock_cpu_percent.return_value = 100.0
        monitor = CPUMonitor()
        result = monitor.measure()
        assert result == 100.0

    @patch("utils.cpu_monitor.psutil.cpu_percent")
    def test_measure_returns_float(
        self, mock_cpu_percent: MagicMock
    ) -> None:
        """measure()는 float 값을 반환해야 합니다."""
        mock_cpu_percent.return_value = 75.3
        monitor = CPUMonitor()
        result = monitor.measure()
        assert isinstance(result, float)

    @patch("utils.cpu_monitor.psutil.cpu_percent")
    def test_get_measurement_returns_last_measured(
        self, mock_cpu_percent: MagicMock
    ) -> None:
        """get_measurement()는 measure() 후 최신값을 반환해야 합니다."""
        mock_cpu_percent.return_value = 88.8
        monitor = CPUMonitor()
        monitor.measure()
        assert monitor.get_measurement() == 88.8
