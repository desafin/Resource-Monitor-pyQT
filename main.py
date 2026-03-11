"""리소스 모니터 애플리케이션 진입점.

PyQt5 + QML 기반 시스템 리소스 모니터링 애플리케이션을 시작합니다.
MonitorModel/ViewModel과 ProcessViewModel을 생성하여 QML에 노출합니다.
"""
import logging
import os
import sys

from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine

from models import MonitorModel
from views import MonitorViewModel, ProcessViewModel, DiskViewModel, NetworkViewModel, HardwareViewModel
from utils.settings_manager import (
    load_window_size, save_window_size,
    load_theme, save_theme,
    load_update_interval, save_update_interval,
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

os.environ["QT_FORCE_STDERR_LOGGING"] = "1"


def main() -> int:
    """애플리케이션 메인 함수."""
    app = QGuiApplication(sys.argv)

    # Model과 ViewModel 생성 (시스템 개요)
    model = MonitorModel()
    view_model = MonitorViewModel(model)

    # 프로세스 ViewModel 생성
    process_viewmodel = ProcessViewModel()

    # 디스크/네트워크/하드웨어 ViewModel 생성
    disk_viewmodel = DiskViewModel()
    network_viewmodel = NetworkViewModel()
    hardware_viewmodel = HardwareViewModel()

    # QML 엔진 설정
    engine = QQmlApplicationEngine()
    context = engine.rootContext()
    context.setContextProperty("monitorViewModel", view_model)
    context.setContextProperty("processViewModel", process_viewmodel)
    context.setContextProperty("diskViewModel", disk_viewmodel)
    context.setContextProperty("networkViewModel", network_viewmodel)
    context.setContextProperty("hardwareViewModel", hardware_viewmodel)

    # 저장된 설정 로드
    saved_width, saved_height = load_window_size()
    saved_dark_theme = load_theme()
    saved_interval = load_update_interval()

    # QML 컨텍스트에 설정 값 전달
    context.setContextProperty("savedWidth", saved_width)
    context.setContextProperty("savedHeight", saved_height)
    context.setContextProperty("savedDarkTheme", saved_dark_theme)
    context.setContextProperty("savedInterval", saved_interval)

    # QML 로드
    qml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qml", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))
    if engine.rootObjects():
        logger.info("QML이 성공적으로 로드되었습니다")
    else:
        logger.error("QML 로드에 실패했습니다")
        return 1

    # 타이머가 직접 model.measure()에 연결
    interval_ms = saved_interval * 1000
    timer = QTimer()
    timer.timeout.connect(model.measure)
    timer.start(interval_ms)

    # 모니터링 시작
    model.startMonitoring()
    disk_viewmodel.startTimer()
    network_viewmodel.startTimer()
    hardware_viewmodel.startTimer()

    # 앱 종료 시 정리
    def on_about_to_quit() -> None:
        """앱 종료 시 워커 스레드를 안전하게 정리하고 설정을 저장합니다."""
        logger.info("애플리케이션 종료 중...")
        # 윈도우 크기 저장 (Wayland 호환: 위치는 저장하지 않음)
        root_objects = engine.rootObjects()
        if root_objects:
            window = root_objects[0]
            save_window_size(window.width(), window.height())
            # 테마와 업데이트 간격은 QML에서 변경 시 저장
            is_dark = window.property("_updateInterval")
            # 테마 정보는 QML theme 객체에서 가져옴
        process_viewmodel.cleanup()
        disk_viewmodel.stopTimer()
        network_viewmodel.stopTimer()
        network_viewmodel.cleanup()
        hardware_viewmodel.stopTimer()
        timer.stop()

    app.aboutToQuit.connect(on_about_to_quit)

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
