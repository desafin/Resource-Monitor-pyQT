"""MonitorModel의 동작에 대한 특성화 테스트.

models/monitor_model.py의 현재 동작을 포착합니다:
- 초기 상태 검증
- 프로퍼티 반환값 확인
- 모니터링 시작/중지 상태 전환
- measure() 호출 동작
- 외부 모니터 예외 처리
- GPUMonitor ImportError 처리
"""
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class TestMonitorModelInit:
    """MonitorModel 초기화 동작을 검증합니다."""

    @pytest.fixture
    def patched_model(self, qapp: Any) -> Any:
        """모든 모니터를 패치한 MonitorModel 인스턴스를 반환합니다."""
        with (
            patch("models.monitor_model.CPUMonitor") as mock_cpu,
            patch("models.monitor_model.MemoryMonitor") as mock_mem,
            patch("models.monitor_model.FPSMonitor") as mock_fps,
            patch("models.monitor_model.GPUMonitor") as mock_gpu,
        ):
            from models.monitor_model import MonitorModel
            model = MonitorModel()
            yield model

    def test_initial_cpu_is_zero(self, patched_model: Any) -> None:
        """초기 _cpu 값은 0.0이어야 합니다."""
        assert patched_model._cpu == 0.0

    def test_initial_memory_is_empty_dict(self, patched_model: Any) -> None:
        """초기 _memory 값은 빈 딕셔너리여야 합니다."""
        assert patched_model._memory == {}

    def test_initial_gpu_is_empty_list(self, patched_model: Any) -> None:
        """초기 _gpu 값은 빈 리스트여야 합니다."""
        assert patched_model._gpu == []

    def test_initial_fps_is_zero(self, patched_model: Any) -> None:
        """초기 _fps 값은 0.0이어야 합니다."""
        assert patched_model._fps == 0.0

    def test_initial_is_monitoring_is_false(self, patched_model: Any) -> None:
        """초기 _is_monitoring 값은 False여야 합니다."""
        assert patched_model._is_monitoring is False

    def test_monitors_dict_contains_expected_keys(self, patched_model: Any) -> None:
        """_monitors 딕셔너리는 cpu, memory, fps, gpu 키를 포함해야 합니다."""
        assert "cpu" in patched_model._monitors
        assert "memory" in patched_model._monitors
        assert "fps" in patched_model._monitors
        assert "gpu" in patched_model._monitors

    def test_gpu_monitor_import_error_handled_gracefully(self, qapp: object) -> None:
        """GPUMonitor ImportError 발생 시 gpu 키가 _monitors에 없어야 합니다."""
        with (
            patch("models.monitor_model.CPUMonitor"),
            patch("models.monitor_model.MemoryMonitor"),
            patch("models.monitor_model.FPSMonitor"),
            patch("models.monitor_model.GPUMonitor", side_effect=ImportError),
        ):
            from models.monitor_model import MonitorModel
            model = MonitorModel()
            assert "gpu" not in model._monitors

    def test_gpu_monitor_import_error_does_not_raise(self, qapp: object) -> None:
        """GPUMonitor ImportError 발생 시 예외를 전파하지 않아야 합니다."""
        with (
            patch("models.monitor_model.CPUMonitor"),
            patch("models.monitor_model.MemoryMonitor"),
            patch("models.monitor_model.FPSMonitor"),
            patch("models.monitor_model.GPUMonitor", side_effect=ImportError),
        ):
            from models.monitor_model import MonitorModel
            # 예외 없이 생성되어야 함
            model = MonitorModel()
            assert model is not None


class TestMonitorModelProperties:
    """MonitorModel 프로퍼티 반환값을 검증합니다."""

    @pytest.fixture
    def model(self, qapp: Any) -> Any:
        """테스트용 MonitorModel 인스턴스를 반환합니다."""
        with (
            patch("models.monitor_model.CPUMonitor"),
            patch("models.monitor_model.MemoryMonitor"),
            patch("models.monitor_model.FPSMonitor"),
            patch("models.monitor_model.GPUMonitor"),
        ):
            from models.monitor_model import MonitorModel
            return MonitorModel()

    def test_cpu_property_returns_cpu_value(self, model: Any) -> None:
        """cpu 프로퍼티는 _cpu 값을 반환해야 합니다."""
        model._cpu = 55.5
        assert model.cpu == 55.5

    def test_memory_property_returns_memory_value(self, model: Any) -> None:
        """memory 프로퍼티는 _memory 딕셔너리를 반환해야 합니다."""
        mem_data = {"used": 1024, "total": 4096, "percent": 25.0}
        model._memory = mem_data
        assert model.memory == mem_data

    def test_gpu_property_returns_gpu_value(self, model: Any) -> None:
        """gpu 프로퍼티는 _gpu 리스트를 반환해야 합니다."""
        gpu_data = [{"load": 80.0}]
        model._gpu = gpu_data
        assert model.gpu == gpu_data

    def test_fps_property_returns_fps_value(self, model: Any) -> None:
        """fps 프로퍼티는 _fps 값을 반환해야 합니다."""
        model._fps = 60.0
        assert model.fps == 60.0

    def test_is_monitoring_property_returns_monitoring_state(self, model: Any) -> None:
        """isMonitoring 프로퍼티는 _is_monitoring 값을 반환해야 합니다."""
        model._is_monitoring = True
        assert model.isMonitoring is True


class TestMonitorModelStartStop:
    """MonitorModel startMonitoring/stopMonitoring 슬롯을 검증합니다."""

    @pytest.fixture
    def model(self, qapp: Any) -> Any:
        """테스트용 MonitorModel 인스턴스를 반환합니다."""
        with (
            patch("models.monitor_model.CPUMonitor"),
            patch("models.monitor_model.MemoryMonitor"),
            patch("models.monitor_model.FPSMonitor"),
            patch("models.monitor_model.GPUMonitor"),
        ):
            from models.monitor_model import MonitorModel
            return MonitorModel()

    def test_start_monitoring_sets_is_monitoring_true(self, model: Any) -> None:
        """startMonitoring() 호출 후 _is_monitoring이 True여야 합니다."""
        model.startMonitoring()
        assert model._is_monitoring is True

    def test_start_monitoring_emits_is_monitoring_changed(self, model: Any) -> None:
        """startMonitoring() 호출 시 isMonitoringChanged 시그널이 방출되어야 합니다."""
        signal_count: list = []
        model.isMonitoringChanged.connect(lambda: signal_count.append(1))
        model.startMonitoring()
        assert len(signal_count) == 1

    def test_start_monitoring_is_idempotent(self, model: Any) -> None:
        """startMonitoring()을 두 번 호출해도 시그널은 한 번만 방출되어야 합니다."""
        signal_count: list = []
        model.isMonitoringChanged.connect(lambda: signal_count.append(1))
        model.startMonitoring()
        model.startMonitoring()
        assert len(signal_count) == 1

    def test_stop_monitoring_sets_is_monitoring_false(self, model: Any) -> None:
        """stopMonitoring() 호출 후 _is_monitoring이 False여야 합니다."""
        model.startMonitoring()
        model.stopMonitoring()
        assert model._is_monitoring is False

    def test_stop_monitoring_emits_is_monitoring_changed(self, model: Any) -> None:
        """stopMonitoring() 호출 시 isMonitoringChanged 시그널이 방출되어야 합니다."""
        model.startMonitoring()
        signal_count: list = []
        model.isMonitoringChanged.connect(lambda: signal_count.append(1))
        model.stopMonitoring()
        assert len(signal_count) == 1

    def test_stop_monitoring_is_idempotent(self, model: Any) -> None:
        """stopMonitoring()을 두 번 호출해도 시그널은 한 번만 방출되어야 합니다."""
        model.startMonitoring()
        signal_count: list = []
        model.isMonitoringChanged.connect(lambda: signal_count.append(1))
        model.stopMonitoring()
        model.stopMonitoring()
        assert len(signal_count) == 1


class TestMonitorModelMeasure:
    """MonitorModel measure() 슬롯 동작을 검증합니다."""

    @pytest.fixture
    def model_with_mocks(self, qapp: Any) -> Any:
        """모니터 인스턴스가 MagicMock인 MonitorModel을 반환합니다."""
        with (
            patch("models.monitor_model.CPUMonitor") as mock_cpu_cls,
            patch("models.monitor_model.MemoryMonitor") as mock_mem_cls,
            patch("models.monitor_model.FPSMonitor") as mock_fps_cls,
            patch("models.monitor_model.GPUMonitor") as mock_gpu_cls,
        ):
            from models.monitor_model import MonitorModel
            model = MonitorModel()
            # 인스턴스를 직접 교체하여 measure 반환값 제어
            model._monitors["cpu"] = mock_cpu_cls.return_value
            model._monitors["memory"] = mock_mem_cls.return_value
            model._monitors["fps"] = mock_fps_cls.return_value
            model._monitors["gpu"] = mock_gpu_cls.return_value
            yield model

    def test_measure_does_nothing_when_not_monitoring(self, model_with_mocks: Any) -> None:
        """모니터링 중이 아닐 때 measure()는 모니터를 호출하지 않아야 합니다."""
        assert model_with_mocks._is_monitoring is False
        model_with_mocks.measure()
        model_with_mocks._monitors["cpu"].measure.assert_not_called()
        model_with_mocks._monitors["memory"].measure.assert_not_called()

    def test_measure_calls_all_monitors_when_monitoring(self, model_with_mocks: Any) -> None:
        """모니터링 중일 때 measure()는 모든 모니터의 measure()를 호출해야 합니다."""
        model_with_mocks._monitors["cpu"].measure.return_value = 10.0
        model_with_mocks._monitors["memory"].measure.return_value = {"used": 1, "total": 2, "percent": 50.0}
        model_with_mocks._monitors["fps"].measure.return_value = 30.0
        model_with_mocks._monitors["gpu"].measure.return_value = [{"load": 70.0}]

        model_with_mocks.startMonitoring()
        model_with_mocks.measure()

        model_with_mocks._monitors["cpu"].measure.assert_called_once()
        model_with_mocks._monitors["memory"].measure.assert_called_once()
        model_with_mocks._monitors["fps"].measure.assert_called_once()

    def test_measure_emits_signal_on_value_change(self, model_with_mocks: Any) -> None:
        """값이 변경될 때 해당 시그널이 방출되어야 합니다."""
        model_with_mocks._monitors["cpu"].measure.return_value = 75.0
        model_with_mocks._monitors["memory"].measure.return_value = {}
        model_with_mocks._monitors["fps"].measure.return_value = 0.0
        model_with_mocks._monitors["gpu"].measure.return_value = []

        cpu_signals: list = []
        model_with_mocks.cpuChanged.connect(lambda: cpu_signals.append(1))

        model_with_mocks.startMonitoring()
        model_with_mocks.measure()

        assert len(cpu_signals) >= 1

    def test_measure_does_not_emit_signal_when_value_unchanged(self, model_with_mocks: Any) -> None:
        """값이 변경되지 않으면 시그널이 방출되지 않아야 합니다."""
        # 초기값과 동일한 값 반환
        model_with_mocks._monitors["cpu"].measure.return_value = 0.0
        model_with_mocks._monitors["memory"].measure.return_value = {}
        model_with_mocks._monitors["fps"].measure.return_value = 0.0
        model_with_mocks._monitors["gpu"].measure.return_value = []

        cpu_signals: list = []
        model_with_mocks.cpuChanged.connect(lambda: cpu_signals.append(1))

        model_with_mocks.startMonitoring()
        model_with_mocks.measure()

        assert len(cpu_signals) == 0


class TestMonitorModelMeasureAndEmit:
    """MonitorModel _measure_and_emit() 내부 메서드를 검증합니다."""

    @pytest.fixture
    def model(self, qapp: Any) -> Any:
        """테스트용 MonitorModel 인스턴스를 반환합니다."""
        with (
            patch("models.monitor_model.CPUMonitor"),
            patch("models.monitor_model.MemoryMonitor"),
            patch("models.monitor_model.FPSMonitor"),
            patch("models.monitor_model.GPUMonitor"),
        ):
            from models.monitor_model import MonitorModel
            return MonitorModel()

    def test_measure_and_emit_skips_missing_key(self, model: Any) -> None:
        """존재하지 않는 키로 _measure_and_emit() 호출 시 아무 동작도 하지 않아야 합니다."""
        mock_signal = MagicMock()
        # 예외 없이 반환되어야 함
        model._measure_and_emit("nonexistent_key", "_cpu", mock_signal)
        mock_signal.emit.assert_not_called()

    def test_measure_and_emit_handles_exception(self, model: Any) -> None:
        """모니터 measure()에서 예외 발생 시 로그를 남기고 계속 진행해야 합니다."""
        mock_monitor = MagicMock()
        mock_monitor.measure.side_effect = RuntimeError("측정 실패")
        model._monitors["cpu"] = mock_monitor

        mock_signal = MagicMock()
        # 예외가 전파되지 않아야 함
        model._measure_and_emit("cpu", "_cpu", mock_signal)
        mock_signal.emit.assert_not_called()
