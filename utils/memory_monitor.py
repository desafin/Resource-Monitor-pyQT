from monitor_base import ResourceMonitor
import psutil

class MemoryMonitor(ResourceMonitor):
    """메모리 사용량 모니터링"""

    def measure(self):
        self.last_measurement = self.current_measurement
        memory = psutil.virtual_memory()
        self.current_measurement = {
            'total': memory.total,
            'used': memory.used,
            'percent': memory.percent
        }
        return self.current_measurement
