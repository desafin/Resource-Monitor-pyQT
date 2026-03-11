# views/monitor_viewmodel.py
import logging
from collections import deque

from PyQt5.QtCore import QObject, QVariant, pyqtSignal, pyqtSlot, pyqtProperty

logger = logging.getLogger(__name__)


class MonitorViewModel(QObject):
    """모니터링 뷰모델 - Model의 원시 데이터를 표시용 문자열로 포맷팅"""

    # 포맷된 문자열 변경 시그널
    cpuUsageChanged = pyqtSignal()
    memoryUsageChanged = pyqtSignal()
    gpuUsageChanged = pyqtSignal()
    fpsDisplayChanged = pyqtSignal()
    isMonitoringChanged = pyqtSignal()

    # 히스토리 변경 시그널
    cpuHistoryChanged = pyqtSignal()
    memoryHistoryChanged = pyqtSignal()

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self._model = model

        # 포맷된 표시 문자열
        self._cpu_usage = "0.0%"
        self._memory_usage = "0.0 GB / 0.0 GB (0.0%)"
        self._gpu_usage = "N/A"
        self._fps_display = "0.0 FPS"

        # CPU/메모리 히스토리 (최근 60개 값 유지)
        self._cpu_history: deque[float] = deque(maxlen=60)
        self._memory_history: deque[float] = deque(maxlen=60)

        # Model 시그널 연결 - 선언적 데이터 흐름
        self._model.cpuChanged.connect(self._on_cpu_changed)
        self._model.memoryChanged.connect(self._on_memory_changed)
        self._model.gpuChanged.connect(self._on_gpu_changed)
        self._model.fpsChanged.connect(self._on_fps_changed)
        self._model.isMonitoringChanged.connect(self.isMonitoringChanged)

        logger.info("뷰모델이 초기화되었습니다.")

    # --- Q_PROPERTY 정의 (QML 바인딩용) ---

    @pyqtProperty(str, notify=cpuUsageChanged)
    def cpuUsage(self):
        return self._cpu_usage

    @pyqtProperty(str, notify=memoryUsageChanged)
    def memoryUsage(self):
        return self._memory_usage

    @pyqtProperty(str, notify=gpuUsageChanged)
    def gpuUsage(self):
        return self._gpu_usage

    @pyqtProperty(str, notify=fpsDisplayChanged)
    def fpsDisplay(self):
        return self._fps_display

    @pyqtProperty(bool, notify=isMonitoringChanged)
    def isMonitoring(self):
        return self._model.isMonitoring

    @pyqtProperty(list, notify=cpuHistoryChanged)
    def cpuHistory(self):
        """CPU 사용률 히스토리 (최근 60개 값)를 반환합니다."""
        return list(self._cpu_history)

    @pyqtProperty(list, notify=memoryHistoryChanged)
    def memoryHistory(self):
        """메모리 사용률 히스토리 (최근 60개 값)를 반환합니다."""
        return list(self._memory_history)

    # --- 모니터링 제어 슬롯 ---

    @pyqtSlot()
    def startMonitoring(self):
        """모니터링 시작"""
        self._model.startMonitoring()

    @pyqtSlot()
    def stopMonitoring(self):
        """모니터링 중지"""
        self._model.stopMonitoring()

    # --- Model 시그널 핸들러 (데이터 포맷팅) ---

    def _on_cpu_changed(self):
        """CPU 데이터를 표시용 문자열로 포맷팅하고 히스토리에 추가"""
        cpu_val = self._model.cpu
        self._cpu_usage = f"{cpu_val:.1f}%"
        self._cpu_history.append(cpu_val)
        self.cpuUsageChanged.emit()
        self.cpuHistoryChanged.emit()

    def _on_memory_changed(self):
        """메모리 데이터를 표시용 문자열로 포맷팅하고 히스토리에 추가 (bytes -> GB 변환)"""
        mem = self._model.memory
        if mem:
            used_gb = mem.get('used', 0) / 1024 / 1024 / 1024
            total_gb = mem.get('total', 0) / 1024 / 1024 / 1024
            percent = mem.get('percent', 0)
            self._memory_usage = f"{used_gb:.1f} GB / {total_gb:.1f} GB ({percent:.1f}%)"
            self._memory_history.append(percent)
        else:
            self._memory_usage = "0.0 GB / 0.0 GB (0.0%)"
            self._memory_history.append(0.0)
        self.memoryUsageChanged.emit()
        self.memoryHistoryChanged.emit()

    def _on_gpu_changed(self):
        """GPU 데이터를 표시용 문자열로 포맷팅"""
        gpu_data = self._model.gpu
        if gpu_data and isinstance(gpu_data, list) and len(gpu_data) > 0:
            self._gpu_usage = f"{gpu_data[0].get('load', 0):.1f}%"
        else:
            self._gpu_usage = "N/A"
        self.gpuUsageChanged.emit()

    def _on_fps_changed(self):
        """FPS 데이터를 표시용 문자열로 포맷팅"""
        self._fps_display = f"{self._model.fps:.1f} FPS"
        self.fpsDisplayChanged.emit()
