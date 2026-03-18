"""utils/memory_monitor.py에 대한 특성화 테스트.

MemoryMonitor.measure() 동작을 검증합니다.
"""
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.memory_monitor import MemoryMonitor


def _make_virtual_memory(total: int = 8_000_000_000, used: int = 4_000_000_000, percent: float = 50.0) -> MagicMock:
    """가상 메모리 정보를 모의하는 헬퍼 함수."""
    mem = MagicMock()
    mem.total = total
    mem.used = used
    mem.percent = percent
    return mem


class TestMemoryMonitorInit:
    """MemoryMonitor 초기화를 검증합니다."""

    def test_creates_instance(self) -> None:
        """MemoryMonitor 인스턴스를 생성할 수 있어야 합니다."""
        monitor = MemoryMonitor()
        assert monitor is not None

    def test_initial_current_measurement_is_zero(self) -> None:
        """초기 current_measurement는 0이어야 합니다."""
        monitor = MemoryMonitor()
        assert monitor.current_measurement == 0

    def test_initial_last_measurement_is_zero(self) -> None:
        """초기 last_measurement는 0이어야 합니다."""
        monitor = MemoryMonitor()
        assert monitor.last_measurement == 0


class TestMemoryMonitorMeasure:
    """MemoryMonitor.measure() 동작을 검증합니다."""

    @patch("utils.memory_monitor.psutil.virtual_memory")
    def test_measure_returns_dict(self, mock_virtual_memory: MagicMock) -> None:
        """measure()는 dict를 반환해야 합니다."""
        mock_virtual_memory.return_value = _make_virtual_memory()
        monitor = MemoryMonitor()
        result = monitor.measure()
        assert isinstance(result, dict)

    @patch("utils.memory_monitor.psutil.virtual_memory")
    def test_measure_dict_contains_total(self, mock_virtual_memory: MagicMock) -> None:
        """반환된 딕셔너리는 'total' 키를 포함해야 합니다."""
        mock_virtual_memory.return_value = _make_virtual_memory(total=16_000_000_000)
        monitor = MemoryMonitor()
        result = monitor.measure()
        assert "total" in result
        assert result["total"] == 16_000_000_000

    @patch("utils.memory_monitor.psutil.virtual_memory")
    def test_measure_dict_contains_used(self, mock_virtual_memory: MagicMock) -> None:
        """반환된 딕셔너리는 'used' 키를 포함해야 합니다."""
        mock_virtual_memory.return_value = _make_virtual_memory(used=3_000_000_000)
        monitor = MemoryMonitor()
        result = monitor.measure()
        assert "used" in result
        assert result["used"] == 3_000_000_000

    @patch("utils.memory_monitor.psutil.virtual_memory")
    def test_measure_dict_contains_percent(self, mock_virtual_memory: MagicMock) -> None:
        """반환된 딕셔너리는 'percent' 키를 포함해야 합니다."""
        mock_virtual_memory.return_value = _make_virtual_memory(percent=75.5)
        monitor = MemoryMonitor()
        result = monitor.measure()
        assert "percent" in result
        assert result["percent"] == 75.5

    @patch("utils.memory_monitor.psutil.virtual_memory")
    def test_measure_updates_current_measurement(self, mock_virtual_memory: MagicMock) -> None:
        """measure() 호출 후 current_measurement가 갱신되어야 합니다."""
        mem_info = _make_virtual_memory(total=8_000_000_000, used=4_000_000_000, percent=50.0)
        mock_virtual_memory.return_value = mem_info
        monitor = MemoryMonitor()
        monitor.measure()
        assert monitor.current_measurement["percent"] == 50.0

    @patch("utils.memory_monitor.psutil.virtual_memory")
    def test_measure_moves_current_to_last(self, mock_virtual_memory: MagicMock) -> None:
        """두 번째 measure() 호출 시 이전값이 last_measurement로 이동해야 합니다."""
        first_mem = _make_virtual_memory(percent=40.0)
        second_mem = _make_virtual_memory(percent=80.0)
        mock_virtual_memory.side_effect = [first_mem, second_mem]
        monitor = MemoryMonitor()
        monitor.measure()
        monitor.measure()
        assert monitor.last_measurement["percent"] == 40.0
        assert monitor.current_measurement["percent"] == 80.0

    @patch("utils.memory_monitor.psutil.virtual_memory")
    def test_measure_calls_virtual_memory(self, mock_virtual_memory: MagicMock) -> None:
        """measure()는 psutil.virtual_memory()를 호출해야 합니다."""
        mock_virtual_memory.return_value = _make_virtual_memory()
        monitor = MemoryMonitor()
        monitor.measure()
        mock_virtual_memory.assert_called_once()

    @patch("utils.memory_monitor.psutil.virtual_memory")
    def test_get_measurement_returns_dict_after_measure(self, mock_virtual_memory: MagicMock) -> None:
        """get_measurement()는 measure() 후 최신 딕셔너리를 반환해야 합니다."""
        mock_virtual_memory.return_value = _make_virtual_memory(percent=33.3)
        monitor = MemoryMonitor()
        monitor.measure()
        result = monitor.get_measurement()
        assert isinstance(result, dict)
        assert result["percent"] == 33.3
