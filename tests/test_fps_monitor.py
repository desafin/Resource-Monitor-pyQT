"""utils/fps_monitor.py에 대한 특성화 테스트.

FPSMonitor.__init__() 및 measure() 동작을 검증합니다.
"""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.fps_monitor import FPSMonitor


class TestFPSMonitorInit:
    """FPSMonitor 초기화를 검증합니다."""

    @patch("utils.fps_monitor.time.time")
    def test_creates_instance(self, mock_time: MagicMock) -> None:
        """FPSMonitor 인스턴스를 생성할 수 있어야 합니다."""
        mock_time.return_value = 1000.0
        monitor = FPSMonitor()
        assert monitor is not None

    @patch("utils.fps_monitor.time.time")
    def test_initial_frame_count_is_zero(self, mock_time: MagicMock) -> None:
        """초기 frame_count는 0이어야 합니다."""
        mock_time.return_value = 1000.0
        monitor = FPSMonitor()
        assert monitor.frame_count == 0

    @patch("utils.fps_monitor.time.time")
    def test_initial_last_time_set_from_time(self, mock_time: MagicMock) -> None:
        """초기 last_time은 time.time() 결과여야 합니다."""
        mock_time.return_value = 5000.0
        monitor = FPSMonitor()
        assert monitor.last_time == 5000.0

    @patch("utils.fps_monitor.time.time")
    def test_initial_current_measurement_is_zero(self, mock_time: MagicMock) -> None:
        """초기 current_measurement는 0이어야 합니다."""
        mock_time.return_value = 1000.0
        monitor = FPSMonitor()
        assert monitor.current_measurement == 0

    @patch("utils.fps_monitor.time.time")
    def test_initial_last_measurement_is_zero(self, mock_time: MagicMock) -> None:
        """초기 last_measurement는 0이어야 합니다."""
        mock_time.return_value = 1000.0
        monitor = FPSMonitor()
        assert monitor.last_measurement == 0


class TestFPSMonitorMeasure:
    """FPSMonitor.measure() 동작을 검증합니다."""

    @patch("utils.fps_monitor.time.time")
    def test_measure_increments_frame_count(self, mock_time: MagicMock) -> None:
        """measure() 호출마다 frame_count가 증가해야 합니다."""
        mock_time.return_value = 1000.0
        monitor = FPSMonitor()
        monitor.measure()
        assert monitor.frame_count == 1
        monitor.measure()
        assert monitor.frame_count == 2

    @patch("utils.fps_monitor.time.time")
    def test_measure_returns_zero_when_time_diff_less_than_one_second(
        self, mock_time: MagicMock
    ) -> None:
        """경과 시간이 1초 미만이면 current_measurement(초기값 0)를 반환해야 합니다."""
        mock_time.return_value = 1000.0
        monitor = FPSMonitor()
        # time.time()이 0.5초 경과를 반환 → FPS 계산 없음
        mock_time.return_value = 1000.5
        result = monitor.measure()
        assert result == 0

    @patch("utils.fps_monitor.time.time")
    def test_measure_calculates_fps_when_one_second_passed(
        self, mock_time: MagicMock
    ) -> None:
        """1초 이상 경과 시 FPS를 계산하고 current_measurement를 갱신해야 합니다."""
        mock_time.return_value = 1000.0
        monitor = FPSMonitor()
        # 30번 프레임 누적 후 1초 경과 시뮬레이션
        for _ in range(30):
            mock_time.return_value = 1000.5  # 아직 1초 미만
            monitor.measure()
        # 1초 이상 경과
        mock_time.return_value = 1001.0
        result = monitor.measure()
        # frame_count가 31이고 time_diff가 1.0이므로 31 FPS 근사
        assert result > 0

    @patch("utils.fps_monitor.time.time")
    def test_measure_resets_frame_count_after_fps_calculation(
        self, mock_time: MagicMock
    ) -> None:
        """FPS 계산 후 frame_count가 0으로 리셋되어야 합니다."""
        mock_time.return_value = 1000.0
        monitor = FPSMonitor()
        # 10번 프레임 누적
        for _ in range(10):
            mock_time.return_value = 1000.9
            monitor.measure()
        # 1초 이상 경과로 FPS 계산 트리거
        mock_time.return_value = 1001.1
        monitor.measure()
        assert monitor.frame_count == 0

    @patch("utils.fps_monitor.time.time")
    def test_measure_updates_last_time_after_fps_calculation(
        self, mock_time: MagicMock
    ) -> None:
        """FPS 계산 후 last_time이 current_time으로 갱신되어야 합니다."""
        mock_time.return_value = 1000.0
        monitor = FPSMonitor()
        for _ in range(5):
            mock_time.return_value = 1000.9
            monitor.measure()
        new_time = 1002.0
        mock_time.return_value = new_time
        monitor.measure()
        assert monitor.last_time == new_time

    @patch("utils.fps_monitor.time.time")
    def test_measure_moves_current_to_last_on_fps_calculation(
        self, mock_time: MagicMock
    ) -> None:
        """FPS 계산 시 이전 current_measurement가 last_measurement로 이동해야 합니다."""
        mock_time.return_value = 1000.0
        monitor = FPSMonitor()
        # 첫 번째 FPS 계산 구간
        for _ in range(60):
            mock_time.return_value = 1000.5
            monitor.measure()
        mock_time.return_value = 1001.5
        monitor.measure()
        first_fps = monitor.current_measurement
        # 두 번째 FPS 계산 구간
        for _ in range(30):
            mock_time.return_value = 1002.0
            monitor.measure()
        mock_time.return_value = 1003.0
        monitor.measure()
        assert monitor.last_measurement == first_fps

    @patch("utils.fps_monitor.time.time")
    def test_measure_exact_fps_calculation(
        self, mock_time: MagicMock
    ) -> None:
        """정확한 FPS 계산을 검증합니다: 60프레임 / 1.0초 = 60 FPS."""
        mock_time.return_value = 0.0
        monitor = FPSMonitor()
        # 60번 프레임 누적 (1초 미만)
        for _ in range(60):
            mock_time.return_value = 0.5
            monitor.measure()
        # 정확히 1초 경과
        mock_time.return_value = 1.0
        monitor.measure()
        # 61번째 호출 포함 (61프레임 / 1.0초)
        assert monitor.current_measurement == pytest.approx(61.0, rel=0.01)
