"""테스트 공통 fixture 정의."""
import sys
import os
import pytest

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_process_data() -> list[dict]:
    """테스트용 프로세스 데이터 목록을 반환하는 fixture."""
    return [
        {
            "pid": 1,
            "name": "systemd",
            "username": "root",
            "cpu_percent": 0.0,
            "memory_percent": 0.1,
            "status": "sleeping",
            "num_threads": 1,
        },
        {
            "pid": 1000,
            "name": "python3",
            "username": "oscar",
            "cpu_percent": 25.5,
            "memory_percent": 3.2,
            "status": "running",
            "num_threads": 4,
        },
        {
            "pid": 2000,
            "name": "firefox",
            "username": "oscar",
            "cpu_percent": 12.3,
            "memory_percent": 8.7,
            "status": "sleeping",
            "num_threads": 45,
        },
        {
            "pid": 3000,
            "name": "code",
            "username": "oscar",
            "cpu_percent": 5.0,
            "memory_percent": 4.5,
            "status": "running",
            "num_threads": 20,
        },
    ]


@pytest.fixture
def qapp():
    """PyQt5 QApplication fixture (테스트 세션에서 한 번만 생성)."""
    from PyQt5.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app
