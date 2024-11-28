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

        # 컨트롤러의 데이터 변경 시그널 연결
        self._controller.dataChanged.connect(self._update_data)

    def _update_data(self, new_data):
        """새로운 모니터링 데이터로 업데이트"""
        self._data = new_data
        # 모델이 변경되었음을 알림
        self.dataChanged.emit()

    @property
    def data(self):
        return self._data
