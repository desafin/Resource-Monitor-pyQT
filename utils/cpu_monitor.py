from monitor_base import ResourceMonitor
import psutil

class CPUMonitor(ResourceMonitor):
    """CPU 사용량 모니터링"""

    def measure(self):
        self.last_measurement = self.current_measurement
        self.current_measurement = psutil.cpu_percent(interval=0.1)
        return self.current_measurement