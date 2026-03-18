"""MonitorViewModel의 CPU/메모리 히스토리 추적 기능에 대한 사양 테스트.

cpuHistory, memoryHistory Q_PROPERTY가 올바르게 동작하는지 검증합니다.
- deque(maxlen=60) 기반 히스토리 저장
- 데이터 변경 시 히스토리 자동 추가
- 히스토리 시그널 방출
"""
import sys
from typing import Any
from unittest.mock import MagicMock, PropertyMock

import pytest


class TestMonitorViewModelHistory:
    """MonitorViewModel의 히스토리 추적 동작을 검증합니다."""

    @pytest.fixture
    def mock_model(self) -> Any:
        """시그널을 가진 모의 MonitorModel을 생성합니다."""
        from PyQt5.QtCore import QObject, pyqtSignal

        class MockModel(QObject):
            cpuChanged = pyqtSignal()
            memoryChanged = pyqtSignal()
            gpuChanged = pyqtSignal()
            fpsChanged = pyqtSignal()
            isMonitoringChanged = pyqtSignal()

            def __init__(self) -> None:
                super().__init__()
                self._cpu = 0.0
                self._memory: dict = {}
                self._gpu: list = []
                self._fps = 0.0
                self._is_monitoring = False

            @property
            def cpu(self) -> float:
                return self._cpu

            @property
            def memory(self) -> dict:
                return self._memory

            @property
            def gpu(self) -> list:
                return self._gpu

            @property
            def fps(self) -> float:
                return self._fps

            @property
            def isMonitoring(self) -> bool:
                return self._is_monitoring

        return MockModel()

    @pytest.fixture
    def viewmodel(self, qapp: Any, mock_model: Any) -> Any:
        """테스트용 MonitorViewModel 인스턴스를 생성합니다."""
        from views.monitor_viewmodel import MonitorViewModel
        return MonitorViewModel(mock_model)

    def test_cpu_history_initially_empty(self, viewmodel: Any) -> None:
        """초기 cpuHistory는 빈 리스트여야 합니다."""
        assert viewmodel.cpuHistory == []

    def test_memory_history_initially_empty(self, viewmodel: Any) -> None:
        """초기 memoryHistory는 빈 리스트여야 합니다."""
        assert viewmodel.memoryHistory == []

    def test_cpu_history_updates_on_cpu_change(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """CPU 값이 변경되면 cpuHistory에 추가되어야 합니다."""
        mock_model._cpu = 45.0
        mock_model.cpuChanged.emit()
        assert len(viewmodel.cpuHistory) == 1
        assert viewmodel.cpuHistory[0] == 45.0

    def test_memory_history_updates_on_memory_change(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """메모리 값이 변경되면 memoryHistory에 추가되어야 합니다."""
        mock_model._memory = {
            "used": 4 * 1024 * 1024 * 1024,
            "total": 16 * 1024 * 1024 * 1024,
            "percent": 25.0,
        }
        mock_model.memoryChanged.emit()
        assert len(viewmodel.memoryHistory) == 1
        assert viewmodel.memoryHistory[0] == 25.0

    def test_cpu_history_max_length_60(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """cpuHistory는 최대 60개 값만 유지해야 합니다."""
        for i in range(70):
            mock_model._cpu = float(i)
            mock_model.cpuChanged.emit()
        assert len(viewmodel.cpuHistory) == 60
        # 가장 오래된 값(0~9)은 제거되고 10~69가 남아야 함
        assert viewmodel.cpuHistory[0] == 10.0
        assert viewmodel.cpuHistory[-1] == 69.0

    def test_memory_history_max_length_60(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """memoryHistory는 최대 60개 값만 유지해야 합니다."""
        for i in range(70):
            mock_model._memory = {
                "used": 0,
                "total": 1,
                "percent": float(i),
            }
            mock_model.memoryChanged.emit()
        assert len(viewmodel.memoryHistory) == 60

    def test_cpu_history_signal_emitted(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """cpuHistory가 변경되면 cpuHistoryChanged 시그널이 방출되어야 합니다."""
        signal_count = []
        viewmodel.cpuHistoryChanged.connect(lambda: signal_count.append(1))
        mock_model._cpu = 50.0
        mock_model.cpuChanged.emit()
        assert len(signal_count) >= 1

    def test_memory_history_signal_emitted(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """memoryHistory가 변경되면 memoryHistoryChanged 시그널이 방출되어야 합니다."""
        signal_count = []
        viewmodel.memoryHistoryChanged.connect(lambda: signal_count.append(1))
        mock_model._memory = {"used": 0, "total": 1, "percent": 30.0}
        mock_model.memoryChanged.emit()
        assert len(signal_count) >= 1

    def test_cpu_history_returns_list(self, viewmodel: Any) -> None:
        """cpuHistory 프로퍼티가 list를 반환해야 합니다."""
        assert isinstance(viewmodel.cpuHistory, list)

    def test_memory_history_returns_list(self, viewmodel: Any) -> None:
        """memoryHistory 프로퍼티가 list를 반환해야 합니다."""
        assert isinstance(viewmodel.memoryHistory, list)

    # --- 포맷된 문자열 프로퍼티 초기값 검증 ---

    def test_cpu_usage_initial_value(self, viewmodel: Any) -> None:
        """초기 cpuUsage는 '0.0%'여야 합니다."""
        assert viewmodel.cpuUsage == "0.0%"

    def test_memory_usage_initial_value(self, viewmodel: Any) -> None:
        """초기 memoryUsage는 '0.0 GB / 0.0 GB (0.0%)'여야 합니다."""
        assert viewmodel.memoryUsage == "0.0 GB / 0.0 GB (0.0%)"

    def test_gpu_usage_initial_value(self, viewmodel: Any) -> None:
        """초기 gpuUsage는 'N/A'여야 합니다."""
        assert viewmodel.gpuUsage == "N/A"

    def test_fps_display_initial_value(self, viewmodel: Any) -> None:
        """초기 fpsDisplay는 '0.0 FPS'여야 합니다."""
        assert viewmodel.fpsDisplay == "0.0 FPS"

    def test_is_monitoring_delegates_to_model(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """isMonitoring 프로퍼티는 model.isMonitoring 값을 반환해야 합니다."""
        assert viewmodel.isMonitoring == mock_model.isMonitoring

    # --- 모니터링 제어 슬롯 위임 검증 ---

    def test_start_monitoring_calls_model(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """startMonitoring() 호출 시 model.startMonitoring()이 호출되어야 합니다."""
        from unittest.mock import MagicMock
        mock_model.startMonitoring = MagicMock()
        viewmodel.startMonitoring()
        mock_model.startMonitoring.assert_called_once()

    def test_stop_monitoring_calls_model(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """stopMonitoring() 호출 시 model.stopMonitoring()이 호출되어야 합니다."""
        from unittest.mock import MagicMock
        mock_model.stopMonitoring = MagicMock()
        viewmodel.stopMonitoring()
        mock_model.stopMonitoring.assert_called_once()

    # --- CPU 포맷 문자열 갱신 검증 ---

    def test_cpu_usage_formatted_string(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """cpuChanged 시그널 발생 후 cpuUsage가 올바르게 포맷되어야 합니다."""
        mock_model._cpu = 45.5
        mock_model.cpuChanged.emit()
        assert viewmodel.cpuUsage == "45.5%"

    # --- 메모리 포맷 문자열 갱신 검증 ---

    def test_memory_usage_formatted_on_change(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """memoryChanged 시그널 발생 후 memoryUsage가 올바르게 포맷되어야 합니다."""
        mock_model._memory = {
            "used": 4 * 1024 * 1024 * 1024,   # 4 GB
            "total": 16 * 1024 * 1024 * 1024,  # 16 GB
            "percent": 25.0,
        }
        mock_model.memoryChanged.emit()
        assert viewmodel.memoryUsage == "4.0 GB / 16.0 GB (25.0%)"

    def test_memory_usage_empty_memory(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """memoryChanged 시그널 발생 시 메모리 딕셔너리가 비어있으면 기본 문자열을 표시해야 합니다."""
        mock_model._memory = {}
        mock_model.memoryChanged.emit()
        assert viewmodel.memoryUsage == "0.0 GB / 0.0 GB (0.0%)"

    # --- GPU 포맷 문자열 갱신 검증 ---

    def test_gpu_usage_with_data(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """gpuChanged 시그널 발생 후 GPU 데이터가 있으면 부하율이 포맷되어야 합니다."""
        mock_model._gpu = [{"load": 75.0}]
        mock_model.gpuChanged.emit()
        assert viewmodel.gpuUsage == "75.0%"

    def test_gpu_usage_no_data(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """gpuChanged 시그널 발생 후 GPU 데이터가 없으면 'N/A'를 표시해야 합니다."""
        mock_model._gpu = []
        mock_model.gpuChanged.emit()
        assert viewmodel.gpuUsage == "N/A"

    # --- FPS 포맷 문자열 갱신 검증 ---

    def test_fps_display_formatted(
        self, viewmodel: Any, mock_model: Any
    ) -> None:
        """fpsChanged 시그널 발생 후 fpsDisplay가 올바르게 포맷되어야 합니다."""
        mock_model._fps = 60.0
        mock_model.fpsChanged.emit()
        assert viewmodel.fpsDisplay == "60.0 FPS"
