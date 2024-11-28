# controllers/monitor_controller.py
from PyQt5.QtCore import QObject, pyqtSignal
from utils import CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor


class MonitorController(QObject):
    """시스템 모니터링 컨트롤러"""

    # 모니터링 데이터 변경 시그널
    dataChanged = pyqtSignal(dict)
    monitoringStarted = pyqtSignal()
    monitoringStopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        # 모니터링 컴포넌트들 초기화
        self.monitors = {
            'cpu': CPUMonitor(),
            'memory': MemoryMonitor(),
            'fps': FPSMonitor()
        }

        try:
            self.monitors['gpu'] = GPUMonitor()
        except ImportError:
            print("GPU 모니터링을 사용할 수 없습니다.")

        self._is_monitoring = False

    def start_monitoring(self):
        """모니터링 시작"""
        if not self._is_monitoring:
            self._is_monitoring = True
            self.monitoringStarted.emit()
            print("Monitoring started")

    def stop_monitoring(self):
        """모니터링 중지"""
        if self._is_monitoring:
            self._is_monitoring = False
            self.monitoringStopped.emit()
            print("Monitoring stopped")

    def measure_all(self):
        """모든 리소스 측정 및 데이터 전파"""
        if not self._is_monitoring:
            return

        results = {}
        for name, monitor in self.monitors.items():
            results[name] = monitor.measure()

        # 데이터 변경을 알림
        self.dataChanged.emit(results)
        return results

    def get_monitor(self, resource_type):
        """특정 리소스 모니터 반환"""
        return self.monitors.get(resource_type)

    @property
    def is_monitoring(self):
        """모니터링 상태 반환"""
        return self._is_monitoring

    def cleanup(self):
        """리소스 정리"""
        self.stop_monitoring()
        # 필요한 경우 각 모니터의 cleanup 메서드 호출
        for monitor in self.monitors.values():
            if hasattr(monitor, 'cleanup'):
                monitor.cleanup()