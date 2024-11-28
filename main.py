import sys
import time
from PyQt5.QtCore import QObject, QUrl, pyqtSlot, QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from system_monitor import SystemMonitor
from controllers import MonitorController
from models import MonitorModel
from views import MonitorViewModel
def main():
    app = QGuiApplication(sys.argv)

    # 컨트롤러 생성
    controller = MonitorController()

    # 모델 생성 및 컨트롤러 연결
    model = MonitorModel(controller)

    # 뷰모델 생성
    viewmodel = MonitorViewModel(model, controller)

    # QML 엔진 설정
    engine = QQmlApplicationEngine()
    context = engine.rootContext()
    context.setContextProperty("monitorViewModel", viewmodel)

    # QML 로드
    engine.load(QUrl.fromLocalFile("qml/main.qml"))

    if not engine.rootObjects():
        return -1

    # 타이머 생성 및 시작 (1초 간격)
    timer = QTimer()
    timer.timeout.connect(controller.measure_all)
    timer.start(1000)  # 1000ms = 1초

    # 모니터링 시작
    controller.start_monitoring()

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())