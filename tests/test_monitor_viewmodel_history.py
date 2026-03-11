"""MonitorViewModel의 CPU/메모리 히스토리 추적 기능에 대한 사양 테스트.

cpuHistory, memoryHistory Q_PROPERTY가 올바르게 동작하는지 검증합니다.
- deque(maxlen=60) 기반 히스토리 저장
- 데이터 변경 시 히스토리 자동 추가
- 히스토리 시그널 방출
"""
import sys
from unittest.mock import MagicMock, PropertyMock

import pytest


class TestMonitorViewModelHistory:
    """MonitorViewModel의 히스토리 추적 동작을 검증합니다."""

    @pytest.fixture
    def mock_model(self) -> MagicMock:
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
    def viewmodel(self, qapp: object, mock_model: MagicMock) -> object:
        """테스트용 MonitorViewModel 인스턴스를 생성합니다."""
        from views.monitor_viewmodel import MonitorViewModel
        return MonitorViewModel(mock_model)

    def test_cpu_history_initially_empty(self, viewmodel: object) -> None:
        """초기 cpuHistory는 빈 리스트여야 합니다."""
        assert viewmodel.cpuHistory == []

    def test_memory_history_initially_empty(self, viewmodel: object) -> None:
        """초기 memoryHistory는 빈 리스트여야 합니다."""
        assert viewmodel.memoryHistory == []

    def test_cpu_history_updates_on_cpu_change(
        self, viewmodel: object, mock_model: MagicMock
    ) -> None:
        """CPU 값이 변경되면 cpuHistory에 추가되어야 합니다."""
        mock_model._cpu = 45.0
        mock_model.cpuChanged.emit()
        assert len(viewmodel.cpuHistory) == 1
        assert viewmodel.cpuHistory[0] == 45.0

    def test_memory_history_updates_on_memory_change(
        self, viewmodel: object, mock_model: MagicMock
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
        self, viewmodel: object, mock_model: MagicMock
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
        self, viewmodel: object, mock_model: MagicMock
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
        self, viewmodel: object, mock_model: MagicMock
    ) -> None:
        """cpuHistory가 변경되면 cpuHistoryChanged 시그널이 방출되어야 합니다."""
        signal_count = []
        viewmodel.cpuHistoryChanged.connect(lambda: signal_count.append(1))
        mock_model._cpu = 50.0
        mock_model.cpuChanged.emit()
        assert len(signal_count) >= 1

    def test_memory_history_signal_emitted(
        self, viewmodel: object, mock_model: MagicMock
    ) -> None:
        """memoryHistory가 변경되면 memoryHistoryChanged 시그널이 방출되어야 합니다."""
        signal_count = []
        viewmodel.memoryHistoryChanged.connect(lambda: signal_count.append(1))
        mock_model._memory = {"used": 0, "total": 1, "percent": 30.0}
        mock_model.memoryChanged.emit()
        assert len(signal_count) >= 1

    def test_cpu_history_returns_list(self, viewmodel: object) -> None:
        """cpuHistory 프로퍼티가 list를 반환해야 합니다."""
        assert isinstance(viewmodel.cpuHistory, list)

    def test_memory_history_returns_list(self, viewmodel: object) -> None:
        """memoryHistory 프로퍼티가 list를 반환해야 합니다."""
        assert isinstance(viewmodel.memoryHistory, list)
