import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    visible: true
    width: 400
    height: 600
    title: "System Monitor"

    // 모니터링 데이터 모델
    ListModel {
        id: monitorModel
        ListElement {
            name: "CPU"
            value: "0%"
        }
        ListElement {
            name: "Memory"
            value: "0 GB / 0 GB"
        }
        ListElement {
            name: "FPS"
            value: "0"
        }
        ListElement {
            name: "GPU"
            value: "0%"
        }
    }

    // 델리게이트 정의
    Component {
        id: monitorDelegate
        Rectangle {
            width: parent.width
            height: 60
            color: index % 2 ? "#f0f0f0" : "white"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Text {
                    text: name
                    font.pixelSize: 18
                    font.bold: true
                    Layout.preferredWidth: 100
                }

                Text {
                    text: value
                    font.pixelSize: 18
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignRight
                }
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: monitorModel
            delegate: monitorDelegate
        }
    }

    // 데이터 연결
    Connections {
        target: systemMonitor

        function onCpuDataChanged(value) {
            monitorModel.setProperty(0, "value", value.toFixed(1) + "%")
        }

        function onMemoryDataChanged(used, total, percent) {
            monitorModel.setProperty(1, "value",
                used.toFixed(1) + " GB / " + total.toFixed(1) + " GB (" + percent.toFixed(1) + "%)")
        }

        function onFpsDataChanged(value) {
            monitorModel.setProperty(2, "value", value.toFixed(1) + " FPS")
        }
    }
}