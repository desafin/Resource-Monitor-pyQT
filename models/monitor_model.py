# models/monitor_model.py
import logging

from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot, QVariant
from utils import CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor

logger = logging.getLogger(__name__)


class MonitorModel(QObject):
    """모니터링 데이터 모델 - 모든 모니터를 소유하고 Q_PROPERTY로 데이터 노출"""

    # 각 리소스별 변경 시그널
    cpuChanged = pyqtSignal()
    memoryChanged = pyqtSignal()
    gpuChanged = pyqtSignal()
    fpsChanged = pyqtSignal()
    isMonitoringChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 모니터 인스턴스 생성
        self._monitors = {
            'cpu': CPUMonitor(),
            'memory': MemoryMonitor(),
            'fps': FPSMonitor()
        }

        # GPU 모니터는 GPUtil 미설치 시 우아하게 처리
        try:
            self._monitors['gpu'] = GPUMonitor()
        except ImportError:
            logger.warning("GPU 모니터링을 사용할 수 없습니다.")

        # 내부 상태
        self._cpu = 0.0
        self._memory = {}
        self._gpu = []
        self._fps = 0.0
        self._is_monitoring = False

        logger.info("모델이 초기화되었습니다.")

    # --- Q_PROPERTY 정의 ---

    @pyqtProperty(float, notify=cpuChanged)
    def cpu(self):
        return self._cpu

    @pyqtProperty(QVariant, notify=memoryChanged)
    def memory(self):
        return self._memory

    @pyqtProperty(QVariant, notify=gpuChanged)
    def gpu(self):
        return self._gpu

    @pyqtProperty(float, notify=fpsChanged)
    def fps(self):
        return self._fps

    @pyqtProperty(bool, notify=isMonitoringChanged)
    def isMonitoring(self):
        return self._is_monitoring

    # --- 모니터링 제어 ---

    @pyqtSlot()
    def startMonitoring(self):
        """모니터링 시작"""
        if not self._is_monitoring:
            self._is_monitoring = True
            self.isMonitoringChanged.emit()
            logger.info("모니터링이 시작되었습니다.")

    @pyqtSlot()
    def stopMonitoring(self):
        """모니터링 중지"""
        if self._is_monitoring:
            self._is_monitoring = False
            self.isMonitoringChanged.emit()
            logger.info("모니터링이 중지되었습니다.")

    def _measure_and_emit(self, key: str, attr: str, signal) -> None:
        """단일 모니터를 측정하고 값이 변경된 경우 시그널을 발행합니다."""
        if key not in self._monitors:
            return
        try:
            new_val = self._monitors[key].measure()
            if getattr(self, attr) != new_val:
                setattr(self, attr, new_val)
                signal.emit()
        except Exception as e:
            logger.error("%s 측정 오류: %s", key.upper(), e)

    @pyqtSlot()
    def measure(self):
        """모든 모니터를 측정하고 프로퍼티 업데이트"""
        if not self._is_monitoring:
            return
        self._measure_and_emit('cpu', '_cpu', self.cpuChanged)
        self._measure_and_emit('memory', '_memory', self.memoryChanged)
        self._measure_and_emit('gpu', '_gpu', self.gpuChanged)
        self._measure_and_emit('fps', '_fps', self.fpsChanged)
