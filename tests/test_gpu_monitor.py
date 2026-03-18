"""utils/gpu_monitor.py에 대한 특성화 테스트.

GPUMonitor.__init__() 및 measure() 동작을 검증합니다.
GPUtil이 None인 경우(ImportError)와 정상 동작을 모두 커버합니다.
"""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_gpu(
    gpu_id: int = 0,
    load: float = 0.5,
    memory_used: int = 2048,
    memory_total: int = 8192,
) -> MagicMock:
    """GPU 객체를 모의하는 헬퍼 함수."""
    gpu = MagicMock()
    gpu.id = gpu_id
    gpu.load = load
    gpu.memoryUsed = memory_used
    gpu.memoryTotal = memory_total
    return gpu


class TestGPUMonitorInit:
    """GPUMonitor 초기화를 검증합니다."""

    def test_creates_instance_when_gputil_available(self) -> None:
        """GPUtil이 사용 가능하면 인스턴스를 생성할 수 있어야 합니다."""
        with patch.dict("sys.modules", {"GPUtil": MagicMock()}):
            # gpu_monitor 모듈을 재로드하여 패치된 GPUtil 사용
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            assert monitor is not None

    def test_raises_import_error_when_gputil_is_none(self) -> None:
        """GPUtil이 None이면 ImportError를 발생시켜야 합니다."""
        with patch.dict("sys.modules", {"GPUtil": None}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            # GPUtil을 None으로 강제 설정
            original_gputil = gpu_mod.GPUtil
            gpu_mod.GPUtil = None  # type: ignore[assignment]
            try:
                with pytest.raises(ImportError):
                    gpu_mod.GPUMonitor()
            finally:
                gpu_mod.GPUtil = original_gputil

    def test_initial_current_measurement_is_zero(self) -> None:
        """초기 current_measurement는 0이어야 합니다."""
        mock_gputil = MagicMock()
        with patch.dict("sys.modules", {"GPUtil": mock_gputil}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            assert monitor.current_measurement == 0

    def test_initial_last_measurement_is_zero(self) -> None:
        """초기 last_measurement는 0이어야 합니다."""
        mock_gputil = MagicMock()
        with patch.dict("sys.modules", {"GPUtil": mock_gputil}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            assert monitor.last_measurement == 0


class TestGPUMonitorMeasure:
    """GPUMonitor.measure() 동작을 검증합니다."""

    def test_measure_returns_list_of_gpu_dicts(self) -> None:
        """measure()는 GPU 정보 딕셔너리 목록을 반환해야 합니다."""
        mock_gputil = MagicMock()
        mock_gpu = _make_gpu(gpu_id=0, load=0.75, memory_used=4096, memory_total=8192)
        mock_gputil.getGPUs.return_value = [mock_gpu]

        with patch.dict("sys.modules", {"GPUtil": mock_gputil}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            result = monitor.measure()

        assert isinstance(result, list)
        assert len(result) == 1

    def test_measure_gpu_dict_has_required_keys(self) -> None:
        """각 GPU 딕셔너리는 id, load, memory_used, memory_total 키를 가져야 합니다."""
        mock_gputil = MagicMock()
        mock_gpu = _make_gpu()
        mock_gputil.getGPUs.return_value = [mock_gpu]

        with patch.dict("sys.modules", {"GPUtil": mock_gputil}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            result = monitor.measure()

        gpu_info = result[0]
        assert "id" in gpu_info
        assert "load" in gpu_info
        assert "memory_used" in gpu_info
        assert "memory_total" in gpu_info

    def test_measure_load_is_multiplied_by_100(self) -> None:
        """GPU load는 GPUtil 값에 100을 곱한 값이어야 합니다."""
        mock_gputil = MagicMock()
        mock_gpu = _make_gpu(load=0.5)
        mock_gputil.getGPUs.return_value = [mock_gpu]

        with patch.dict("sys.modules", {"GPUtil": mock_gputil}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            result = monitor.measure()

        assert result[0]["load"] == 50.0

    def test_measure_updates_current_measurement(self) -> None:
        """measure() 호출 후 current_measurement가 갱신되어야 합니다."""
        mock_gputil = MagicMock()
        mock_gpu = _make_gpu(gpu_id=0)
        mock_gputil.getGPUs.return_value = [mock_gpu]

        with patch.dict("sys.modules", {"GPUtil": mock_gputil}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            monitor.measure()

        assert isinstance(monitor.current_measurement, list)

    def test_measure_moves_current_to_last(self) -> None:
        """두 번째 measure() 호출 시 이전 current_measurement가 last_measurement로 이동해야 합니다."""
        mock_gputil = MagicMock()
        first_gpu = _make_gpu(load=0.2)
        second_gpu = _make_gpu(load=0.8)
        mock_gputil.getGPUs.side_effect = [[first_gpu], [second_gpu]]

        with patch.dict("sys.modules", {"GPUtil": mock_gputil}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            monitor.measure()
            first_result = monitor.current_measurement
            monitor.measure()

        assert monitor.last_measurement == first_result

    def test_measure_returns_error_string_on_exception(self) -> None:
        """getGPUs()가 예외를 발생시키면 에러 문자열을 반환해야 합니다."""
        mock_gputil = MagicMock()
        mock_gputil.getGPUs.side_effect = RuntimeError("GPU 접근 오류")

        with patch.dict("sys.modules", {"GPUtil": mock_gputil}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            result = monitor.measure()

        assert isinstance(result, str)
        assert "GPU 측정 실패" in result

    def test_measure_multiple_gpus(self) -> None:
        """다중 GPU 환경에서 모든 GPU 정보를 반환해야 합니다."""
        mock_gputil = MagicMock()
        gpu0 = _make_gpu(gpu_id=0, load=0.3)
        gpu1 = _make_gpu(gpu_id=1, load=0.7)
        mock_gputil.getGPUs.return_value = [gpu0, gpu1]

        with patch.dict("sys.modules", {"GPUtil": mock_gputil}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            result = monitor.measure()

        assert len(result) == 2
        assert result[0]["id"] == 0
        assert result[1]["id"] == 1

    def test_measure_empty_gpu_list(self) -> None:
        """GPU가 없을 때 빈 리스트를 반환해야 합니다."""
        mock_gputil = MagicMock()
        mock_gputil.getGPUs.return_value = []

        with patch.dict("sys.modules", {"GPUtil": mock_gputil}):
            import importlib
            import utils.gpu_monitor as gpu_mod
            importlib.reload(gpu_mod)
            monitor = gpu_mod.GPUMonitor()
            result = monitor.measure()

        assert result == []
