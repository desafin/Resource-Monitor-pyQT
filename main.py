import os
import sys
import time
from PyQt5.QtCore import QObject, QUrl, pyqtSlot, QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication
from system_monitor import SystemMonitor
from controllers import MonitorController
from models import MonitorModel
from views import MonitorViewModel

os.environ["QT_FORCE_STDERR_LOGGING"] = "1"

def main():
    app = QGuiApplication(sys.argv)

    # 모델과 컨트롤러 생성
    controller = MonitorController()
    model = MonitorModel(controller)
    viewmodel = MonitorViewModel(model, controller)
    if viewmodel == None :
        print("viewmodel is null")

    # QML 엔진 설정
    engine = QQmlApplicationEngine()
    context = engine.rootContext()
    context.setContextProperty("monitorViewModel", viewmodel)

    # QML 로드
    engine.load(QUrl.fromLocalFile("qml/main.qml"))
    if engine.rootObjects():
        print("QML loaded successfully")
        print("Root objects:", len(engine.rootObjects()))
    else:
        print("Failed to load QML")


    # 타이머 생성 및 시작 (1초 간격)
    timer = QTimer()
    timer.timeout.connect(controller.measure_all)
    timer.start(1000)  # 1000ms = 1초

    # 모니터링 시작
    controller.start_monitoring()

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())