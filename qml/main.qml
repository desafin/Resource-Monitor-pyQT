import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: root
    visible: true
    width: 400
    height: 600
    title: "System Monitor"
    Component.onCompleted: {
        console.log("Window loaded")
        console.log("monitorViewModel exists:", monitorViewModel !== undefined)
        if (monitorViewModel) {
            console.log("monitorViewModel type:", typeof monitorViewModel)
        }
    }

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


    Connections {
        target: monitorViewModel

        function onUpdateUI(data) {
            console.log("data recv:", JSON.stringify(data))

            if (data.cpu !== undefined) {
                monitorModel.setProperty(0, "value", data.cpu.toFixed(1) + "%")
            }
            if (data.memory !== undefined) {
                // Convert bytes to GB
                let usedGB = (data.memory.used / 1024 / 1024 / 1024).toFixed(1)
                let totalGB = (data.memory.total / 1024 / 1024 / 1024).toFixed(1)
                monitorModel.setProperty(1, "value",
                    usedGB + " GB / " + totalGB + " GB (" +
                    data.memory.percent.toFixed(1) + "%)")
            }
            if (data.fps !== undefined) {
                monitorModel.setProperty(2, "value", data.fps.toFixed(1) + " FPS")
            }
            if (data.gpu !== undefined && data.gpu.length > 0) {
                monitorModel.setProperty(3, "value", data.gpu[0].load.toFixed(1) + "%")
            }
        }
    }
}

