from abc import ABC, abstractmethod
class ResourceMonitor(ABC):
    """리소스 모니터링을 위한 기본 추상 클래스"""

    def __init__(self):
        self.last_measurement = 0
        self.current_measurement = 0

    @abstractmethod
    def measure(self):
        """리소스 측정을 위한 추상 메서드"""
        pass

    def get_measurement(self):
        """최신 측정값 반환"""
        return self.current_measurement
