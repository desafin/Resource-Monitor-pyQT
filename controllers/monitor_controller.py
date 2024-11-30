# controllers/monitor_controller.py
from PyQt5.QtCore import QObject, pyqtSignal
from utils import CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor


class MonitorController(QObject):
    dataChanged = pyqtSignal(dict)
    monitoringStarted = pyqtSignal()
    monitoringStopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.monitors = {
            'cpu': CPUMonitor(),
            'memory': MemoryMonitor(),
            'fps': FPSMonitor()
        }

        try:
            self.monitors['gpu'] = GPUMonitor()
        except ImportError:
            print(f"[{self.__class__.__name__}] GPU 모니터링을 사용할 수 없습니다.")

        self._is_monitoring = False

    def start_monitoring(self):
        if not self._is_monitoring:
            self._is_monitoring = True
            self.monitoringStarted.emit()
            print(f"[{self.__class__.__name__}] 모니터링이 시작되었습니다.")

    def stop_monitoring(self):
        if self._is_monitoring:
            self._is_monitoring = False
            self.monitoringStopped.emit()
            print(f"[{self.__class__.__name__}] 모니터링이 중지되었습니다.")

    def measure_all(self):
        if not self._is_monitoring:
            return

        results = {}
        for name, monitor in self.monitors.items():
            try:
                results[name] = monitor.measure()
            except Exception as e:
                print(f"[{self.__class__.__name__}] {name} 측정 중 오류 발생: {str(e)}")

        print(f"[{self.__class__.__name__}] 데이터 업데이트: {results}")
        self.dataChanged.emit(results)
        return results

    def get_monitor(self, resource_type):
        if resource_type not in self.monitors:
            print(f"[{self.__class__.__name__}] 존재하지 않는 모니터: {resource_type}")
        return self.monitors.get(resource_type)


    def cleanup(self):
        print(f"[{self.__class__.__name__}] 리소스 정리를 시작합니다.")
        self.stop_monitoring()
        for monitor in self.monitors.values():
            if hasattr(monitor, 'cleanup'):
                monitor.cleanup()