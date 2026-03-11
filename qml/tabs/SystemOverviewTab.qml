import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * 시스템 개요 탭 - CPU, 메모리, FPS, GPU 모니터링 표시.
 * Canvas 기반 실시간 CPU/메모리 히스토리 그래프 포함.
 * ThemeManager 색상을 사용합니다.
 */
Item {
    id: systemOverviewTab

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 0

        // CPU
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: theme.background

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Text {
                    text: "CPU"
                    font.pixelSize: 18
                    font.bold: true
                    Layout.preferredWidth: 100
                    color: theme.textColor
                }

                Text {
                    text: monitorViewModel ? monitorViewModel.cpuUsage : "N/A"
                    font.pixelSize: 18
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignRight
                    color: theme.textColor
                }
            }
        }

        // CPU 히스토리 그래프
        Rectangle {
            Layout.fillWidth: true
            height: 120
            color: theme.surface
            radius: 4

            Canvas {
                id: cpuCanvas
                anchors.fill: parent
                anchors.margins: 8

                property var historyData: monitorViewModel ? monitorViewModel.cpuHistory : []
                property color lineColor: "#4fc3f7"
                property color fillColor: "#334fc3f7"

                onHistoryDataChanged: requestPaint()

                // 테마 변경 시 다시 그리기
                Connections {
                    target: theme
                    function onIsDarkThemeChanged() { cpuCanvas.requestPaint() }
                }

                onPaint: {
                    var ctx = getContext("2d")
                    var w = width
                    var h = height
                    ctx.clearRect(0, 0, w, h)

                    // 배경 그리드
                    ctx.strokeStyle = theme.borderColor
                    ctx.lineWidth = 0.5
                    for (var i = 0; i <= 4; i++) {
                        var y = (h / 4) * i
                        ctx.beginPath()
                        ctx.moveTo(0, y)
                        ctx.lineTo(w, y)
                        ctx.stroke()
                    }

                    // Y축 레이블
                    ctx.fillStyle = theme.textSecondary
                    ctx.font = "10px sans-serif"
                    ctx.fillText("100%", 2, 12)
                    ctx.fillText("50%", 2, h / 2 + 4)
                    ctx.fillText("0%", 2, h - 2)

                    var data = historyData
                    if (!data || data.length < 2) return

                    var maxPoints = 60
                    var step = w / (maxPoints - 1)
                    var startX = w - (data.length - 1) * step

                    // 그라디언트 채우기
                    ctx.beginPath()
                    ctx.moveTo(startX, h - (data[0] / 100) * h)
                    for (var j = 1; j < data.length; j++) {
                        var x = startX + j * step
                        var yVal = h - (data[j] / 100) * h
                        ctx.lineTo(x, yVal)
                    }
                    ctx.lineTo(startX + (data.length - 1) * step, h)
                    ctx.lineTo(startX, h)
                    ctx.closePath()
                    ctx.fillStyle = fillColor
                    ctx.fill()

                    // 라인 그리기
                    ctx.beginPath()
                    ctx.strokeStyle = lineColor
                    ctx.lineWidth = 2
                    ctx.moveTo(startX, h - (data[0] / 100) * h)
                    for (var k = 1; k < data.length; k++) {
                        var xp = startX + k * step
                        var yp = h - (data[k] / 100) * h
                        ctx.lineTo(xp, yp)
                    }
                    ctx.stroke()
                }
            }

            // 그래프 라벨
            Text {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 8
                text: "CPU History (60s)"
                font.pixelSize: 10
                color: theme.textSecondary
            }
        }

        // 구분선
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: theme.borderColor
        }

        // Memory
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: theme.background

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Text {
                    text: "Memory"
                    font.pixelSize: 18
                    font.bold: true
                    Layout.preferredWidth: 100
                    color: theme.textColor
                }

                Text {
                    text: monitorViewModel ? monitorViewModel.memoryUsage : "N/A"
                    font.pixelSize: 18
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignRight
                    color: theme.textColor
                }
            }
        }

        // 메모리 히스토리 그래프
        Rectangle {
            Layout.fillWidth: true
            height: 120
            color: theme.surface
            radius: 4

            Canvas {
                id: memoryCanvas
                anchors.fill: parent
                anchors.margins: 8

                property var historyData: monitorViewModel ? monitorViewModel.memoryHistory : []
                property color lineColor: "#81c784"
                property color fillColor: "#3381c784"

                onHistoryDataChanged: requestPaint()

                Connections {
                    target: theme
                    function onIsDarkThemeChanged() { memoryCanvas.requestPaint() }
                }

                onPaint: {
                    var ctx = getContext("2d")
                    var w = width
                    var h = height
                    ctx.clearRect(0, 0, w, h)

                    // 배경 그리드
                    ctx.strokeStyle = theme.borderColor
                    ctx.lineWidth = 0.5
                    for (var i = 0; i <= 4; i++) {
                        var y = (h / 4) * i
                        ctx.beginPath()
                        ctx.moveTo(0, y)
                        ctx.lineTo(w, y)
                        ctx.stroke()
                    }

                    // Y축 레이블
                    ctx.fillStyle = theme.textSecondary
                    ctx.font = "10px sans-serif"
                    ctx.fillText("100%", 2, 12)
                    ctx.fillText("50%", 2, h / 2 + 4)
                    ctx.fillText("0%", 2, h - 2)

                    var data = historyData
                    if (!data || data.length < 2) return

                    var maxPoints = 60
                    var step = w / (maxPoints - 1)
                    var startX = w - (data.length - 1) * step

                    // 그라디언트 채우기
                    ctx.beginPath()
                    ctx.moveTo(startX, h - (data[0] / 100) * h)
                    for (var j = 1; j < data.length; j++) {
                        var x = startX + j * step
                        var yVal = h - (data[j] / 100) * h
                        ctx.lineTo(x, yVal)
                    }
                    ctx.lineTo(startX + (data.length - 1) * step, h)
                    ctx.lineTo(startX, h)
                    ctx.closePath()
                    ctx.fillStyle = fillColor
                    ctx.fill()

                    // 라인 그리기
                    ctx.beginPath()
                    ctx.strokeStyle = lineColor
                    ctx.lineWidth = 2
                    ctx.moveTo(startX, h - (data[0] / 100) * h)
                    for (var k = 1; k < data.length; k++) {
                        var xp = startX + k * step
                        var yp = h - (data[k] / 100) * h
                        ctx.lineTo(xp, yp)
                    }
                    ctx.stroke()
                }
            }

            Text {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 8
                text: "Memory History (60s)"
                font.pixelSize: 10
                color: theme.textSecondary
            }
        }

        // 구분선
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: theme.borderColor
        }

        // FPS
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: theme.background

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Text {
                    text: "FPS"
                    font.pixelSize: 18
                    font.bold: true
                    Layout.preferredWidth: 100
                    color: theme.textColor
                }

                Text {
                    text: monitorViewModel ? monitorViewModel.fpsDisplay : "N/A"
                    font.pixelSize: 18
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignRight
                    color: theme.textColor
                }
            }
        }

        // 구분선
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: theme.borderColor
        }

        // GPU
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: theme.surface

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Text {
                    text: "GPU"
                    font.pixelSize: 18
                    font.bold: true
                    Layout.preferredWidth: 100
                    color: theme.textColor
                }

                Text {
                    text: monitorViewModel ? monitorViewModel.gpuUsage : "N/A"
                    font.pixelSize: 18
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignRight
                    color: theme.textColor
                }
            }
        }

        // 나머지 공간 채우기
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
