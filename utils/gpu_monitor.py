from monitor_base import ResourceMonitor
import GPUtil

class GPUMonitor(ResourceMonitor):
    """GPU 사용량 모니터링"""

    def __init__(self):
        super().__init__()
        if GPUtil is None:
            raise ImportError("GPUtil 라이브러리가 설치되지 않았습니다.")

    def measure(self):
        self.last_measurement = self.current_measurement
        try:
            gpus = GPUtil.getGPUs()
            self.current_measurement = [{
                'id': gpu.id,
                'load': gpu.load * 100,
                'memory_used': gpu.memoryUsed,
                'memory_total': gpu.memoryTotal
            } for gpu in gpus]
        except Exception as e:
            self.current_measurement = f"GPU 측정 실패: {str(e)}"
        return self.current_measurement
