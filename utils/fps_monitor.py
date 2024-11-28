from monitor_base import ResourceMonitor
import time

class FPSMonitor(ResourceMonitor):
    """FPS 모니터링"""

    def __init__(self):
        super().__init__()
        self.frame_count = 0
        self.last_time = time.time()

    def measure(self):
        self.frame_count += 1
        current_time = time.time()
        time_diff = current_time - self.last_time

        if time_diff >= 1.0:  # 1초마다 FPS 계산
            self.last_measurement = self.current_measurement
            self.current_measurement = self.frame_count / time_diff
            self.frame_count = 0
            self.last_time = current_time

        return self.current_measurement
