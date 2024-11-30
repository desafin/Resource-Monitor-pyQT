# models/monitor_model.py
from PyQt5.QtCore import QObject, pyqtSignal
from utils import CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor


class MonitorModel(QObject):
    """모니터링 데이터 모델"""

    dataChanged = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self._controller = controller
        self._data = {}
        self._controller.dataChanged.connect(self._update_data)
        print(f"[{self.__class__.__name__}] 모델이 초기화되었습니다.")

    def _update_data(self, new_data):
        """새로운 모니터링 데이터로 업데이트"""
        self._data = new_data
        print(f"[{self.__class__.__name__}] 데이터 업데이트: {new_data}")
        self.dataChanged.emit()

    @property
    def data(self):
        return self._data