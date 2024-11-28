from utils import CPUMonitor, MemoryMonitor, GPUMonitor, FPSMonitor

class SystemMonitor:
#전체 시스템 모니터링 관리 클래스

    def __init__(self):
        self.monitors = {
            'cpu': CPUMonitor(),
            'memory': MemoryMonitor(),
            'fps': FPSMonitor()
        }
        try:
            self.monitors['gpu'] = GPUMonitor()
        except ImportError:
            print("GPU 모니터링을 사용할 수 없습니다.")

    def measure_all(self):
        """모든 리소스 측정"""
        results = {}
        for name, monitor in self.monitors.items():
            results[name] = monitor.measure()
        return results

    def get_monitor(self, resource_type):
        """특정 리소스 모니터 반환"""
        return self.monitors.get(resource_type)


