# viewmodels/monitor_viewmodel.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from utils import CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor

class MonitorViewModel(QObject):
    """모니터링 뷰모델"""

    # updateUI 시그널 추가
    updateUI = pyqtSignal(dict)  # dict 타입의 데이터를 전달하는 시그널
    
    def __init__(self, model, controller):
        super().__init__()
        self._model = model
        self._controller = controller

        # 모델 데이터 변경 감지
        self._model.dataChanged.connect(self._on_data_changed)

    @pyqtSlot()
    def startMonitoring(self):
        """모니터링 시작"""
        self._controller.start_monitoring()

    @pyqtSlot()
    def stopMonitoring(self):
        """모니터링 중지"""
        self._controller.stop_monitoring()
    def _on_data_changed(self):
        """모델 데이터 변경 시 처리"""
        data = self._model.data
        # QML에 데이터 전달을 위한 처리
        self.updateUI.emit(data)
