import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * 디스크 탭 - 파티션별 사용량 및 I/O 통계 표시.
 * ListView를 사용하여 각 파티션의 사용률 바와 상세 정보를 표시합니다.
 */
Item {
    id: diskTab

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 헤더
        Rectangle {
            Layout.fillWidth: true
            height: 40
            color: theme.headerBackground

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 15
                anchors.rightMargin: 15

                Text {
                    text: "디스크 사용량"
                    font.pixelSize: 16
                    font.bold: true
                    color: theme.textColor
                }

                Item { Layout.fillWidth: true }

                Button {
                    text: "새로고침"
                    flat: true
                    font.pixelSize: 12
                    onClicked: {
                        if (diskViewModel) diskViewModel.refresh()
                    }

                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: theme.accent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        color: "transparent"
                    }
                }
            }
        }

        // 구분선
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: theme.borderColor
        }

        // 디스크 목록
        ListView {
            id: diskListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: diskViewModel ? diskViewModel.diskModel : null
            boundsBehavior: Flickable.StopAtBounds
            spacing: 1

            ScrollBar.vertical: ScrollBar {
                active: true
                policy: ScrollBar.AsNeeded
            }

            delegate: Rectangle {
                width: diskListView.width
                height: 100
                color: index % 2 === 0 ? theme.background : theme.surface

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 6

                    // 장치명과 마운트 포인트
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Text {
                            text: device
                            font.pixelSize: 14
                            font.bold: true
                            color: theme.textColor
                        }

                        Text {
                            text: mountpoint
                            font.pixelSize: 13
                            color: theme.textSecondary
                        }

                        Text {
                            text: "(" + fstype + ")"
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: percent.toFixed(1) + "%"
                            font.pixelSize: 14
                            font.bold: true
                            color: percent > 90 ? "#d32f2f" : (percent > 70 ? "#f57c00" : theme.accent)
                        }
                    }

                    // 사용량 프로그레스 바
                    ProgressBar {
                        id: usageBar
                        Layout.fillWidth: true
                        value: percent / 100.0
                        height: 8

                        background: Rectangle {
                            implicitHeight: 8
                            color: theme.borderColor
                            radius: 4
                        }

                        contentItem: Item {
                            implicitHeight: 8

                            Rectangle {
                                width: usageBar.visualPosition * parent.width
                                height: parent.height
                                radius: 4
                                color: percent > 90 ? "#d32f2f" : (percent > 70 ? "#f57c00" : theme.accent)
                            }
                        }
                    }

                    // 사용량 상세
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20

                        Text {
                            text: "사용: " + (diskViewModel ? diskViewModel.formatBytes(used) : "N/A")
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Text {
                            text: "여유: " + (diskViewModel ? diskViewModel.formatBytes(free) : "N/A")
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Text {
                            text: "전체: " + (diskViewModel ? diskViewModel.formatBytes(total) : "N/A")
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: "R: " + (diskViewModel ? diskViewModel.formatBytes(readBytes) : "N/A")
                            font.pixelSize: 12
                            color: "#4caf50"
                        }

                        Text {
                            text: "W: " + (diskViewModel ? diskViewModel.formatBytes(writeBytes) : "N/A")
                            font.pixelSize: 12
                            color: "#2196f3"
                        }
                    }
                }
            }
        }
    }
}
