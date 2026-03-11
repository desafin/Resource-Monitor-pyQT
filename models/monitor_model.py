# models/monitor_model.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot, QVariant
from utils import CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor


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
            print(f"[{self.__class__.__name__}] GPU 모니터링을 사용할 수 없습니다.")

        # 내부 상태
        self._cpu = 0.0
        self._memory = {}
        self._gpu = []
        self._fps = 0.0
        self._is_monitoring = False

        print(f"[{self.__class__.__name__}] 모델이 초기화되었습니다.")

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
            print(f"[{self.__class__.__name__}] 모니터링이 시작되었습니다.")

    @pyqtSlot()
    def stopMonitoring(self):
        """모니터링 중지"""
        if self._is_monitoring:
            self._is_monitoring = False
            self.isMonitoringChanged.emit()
            print(f"[{self.__class__.__name__}] 모니터링이 중지되었습니다.")

    @pyqtSlot()
    def measure(self):
        """모든 모니터를 측정하고 프로퍼티 업데이트"""
        if not self._is_monitoring:
            return

        # CPU 측정
        if 'cpu' in self._monitors:
            try:
                new_cpu = self._monitors['cpu'].measure()
                if self._cpu != new_cpu:
                    self._cpu = new_cpu
                    self.cpuChanged.emit()
            except Exception as e:
                print(f"[{self.__class__.__name__}] CPU 측정 오류: {e}")

        # 메모리 측정
        if 'memory' in self._monitors:
            try:
                new_memory = self._monitors['memory'].measure()
                if self._memory != new_memory:
                    self._memory = new_memory
                    self.memoryChanged.emit()
            except Exception as e:
                print(f"[{self.__class__.__name__}] 메모리 측정 오류: {e}")

        # GPU 측정
        if 'gpu' in self._monitors:
            try:
                new_gpu = self._monitors['gpu'].measure()
                if self._gpu != new_gpu:
                    self._gpu = new_gpu
                    self.gpuChanged.emit()
            except Exception as e:
                print(f"[{self.__class__.__name__}] GPU 측정 오류: {e}")

        # FPS 측정
        if 'fps' in self._monitors:
            try:
                new_fps = self._monitors['fps'].measure()
                if self._fps != new_fps:
                    self._fps = new_fps
                    self.fpsChanged.emit()
            except Exception as e:
                print(f"[{self.__class__.__name__}] FPS 측정 오류: {e}")
