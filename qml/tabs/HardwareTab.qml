import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * 하드웨어 탭 - GPIO, USB, 시리얼 인터페이스 모니터링.
 * 접이식 섹션으로 각 하드웨어 인터페이스의 상태를 표시합니다.
 */
Item {
    id: hardwareTab

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
                    text: "하드웨어 인터페이스"
                    font.pixelSize: 16
                    font.bold: true
                    color: theme.textColor
                }

                Item { Layout.fillWidth: true }

                // 새로고침 버튼
                Button {
                    Layout.preferredWidth: 32
                    Layout.preferredHeight: 32
                    flat: true

                    contentItem: Text {
                        text: "\u21BB"
                        font.pixelSize: 16
                        color: theme.textColor
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        color: parent.hovered ? theme.surface : "transparent"
                        radius: 4
                    }

                    ToolTip.visible: hovered
                    ToolTip.text: "새로고침"

                    onClicked: {
                        if (hardwareViewModel) {
                            hardwareViewModel.refresh()
                        }
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

        // 스크롤 가능한 콘텐츠
        Flickable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentHeight: contentColumn.height
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            ScrollBar.vertical: ScrollBar {
                active: true
                policy: ScrollBar.AsNeeded
            }

            ColumnLayout {
                id: contentColumn
                width: parent.width
                spacing: 0

                // ============================================
                // GPIO 섹션
                // ============================================
                Rectangle {
                    Layout.fillWidth: true
                    height: gpioHeader.height
                    color: theme.headerBackground

                    RowLayout {
                        id: gpioHeader
                        width: parent.width
                        height: 36

                        anchors.leftMargin: 15
                        anchors.rightMargin: 15
                        anchors.left: parent.left
                        anchors.right: parent.right

                        Text {
                            text: gpioSection.visible ? "\u25BC" : "\u25B6"
                            font.pixelSize: 10
                            color: theme.textSecondary
                        }

                        Text {
                            text: "GPIO"
                            font.pixelSize: 14
                            font.bold: true
                            color: theme.textColor
                        }

                        Text {
                            text: hardwareViewModel ? "(" + hardwareViewModel.gpioCount + ")" : "(0)"
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Item { Layout.fillWidth: true }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: gpioSection.visible = !gpioSection.visible
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: theme.borderColor
                }

                // GPIO 콘텐츠
                ColumnLayout {
                    id: gpioSection
                    Layout.fillWidth: true
                    visible: true
                    spacing: 0

                    // GPIO 사용 불가 메시지
                    Rectangle {
                        Layout.fillWidth: true
                        height: 50
                        color: theme.background
                        visible: hardwareViewModel ? !hardwareViewModel.gpioAvailable : true

                        Text {
                            anchors.centerIn: parent
                            text: "GPIO sysfs 인터페이스를 사용할 수 없습니다"
                            font.pixelSize: 13
                            color: theme.textSecondary
                        }
                    }

                    // GPIO 테이블 헤더
                    Rectangle {
                        Layout.fillWidth: true
                        height: 30
                        color: theme.surface
                        visible: hardwareViewModel ? (hardwareViewModel.gpioAvailable && hardwareViewModel.gpioCount > 0) : false

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 15
                            anchors.rightMargin: 15
                            spacing: 10

                            Text {
                                Layout.preferredWidth: 80
                                text: "Pin #"
                                font.pixelSize: 12
                                font.bold: true
                                color: theme.textSecondary
                            }

                            Text {
                                Layout.preferredWidth: 120
                                text: "Direction"
                                font.pixelSize: 12
                                font.bold: true
                                color: theme.textSecondary
                            }

                            Text {
                                Layout.fillWidth: true
                                text: "Value"
                                font.pixelSize: 12
                                font.bold: true
                                color: theme.textSecondary
                            }
                        }
                    }

                    // GPIO 핀 목록
                    Repeater {
                        model: hardwareViewModel ? hardwareViewModel.gpioData : []

                        Rectangle {
                            Layout.fillWidth: true
                            height: 36
                            color: index % 2 === 0 ? theme.background : theme.surface

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 15
                                anchors.rightMargin: 15
                                spacing: 10

                                Text {
                                    Layout.preferredWidth: 80
                                    text: modelData.pin
                                    font.pixelSize: 13
                                    color: theme.textColor
                                }

                                RowLayout {
                                    Layout.preferredWidth: 120
                                    spacing: 6

                                    // 방향 인디케이터
                                    Rectangle {
                                        width: 8
                                        height: 8
                                        radius: 4
                                        color: modelData.direction === "in" ? "#4caf50" : "#ff9800"
                                    }

                                    Text {
                                        text: modelData.direction
                                        font.pixelSize: 13
                                        color: theme.textColor
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 6

                                    // LED 인디케이터
                                    Rectangle {
                                        width: 10
                                        height: 10
                                        radius: 5
                                        color: modelData.value === 1 ? "#4fc3f7" : "#555555"
                                        border.width: 1
                                        border.color: theme.borderColor
                                    }

                                    Text {
                                        text: modelData.value
                                        font.pixelSize: 13
                                        color: theme.textColor
                                    }
                                }
                            }
                        }
                    }

                    // GPIO 사용 가능하지만 핀이 없는 경우
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        color: theme.background
                        visible: hardwareViewModel ? (hardwareViewModel.gpioAvailable && hardwareViewModel.gpioCount === 0) : false

                        Text {
                            anchors.centerIn: parent
                            text: "내보낸 GPIO 핀이 없습니다"
                            font.pixelSize: 13
                            color: theme.textSecondary
                        }
                    }
                }

                // ============================================
                // USB 섹션
                // ============================================
                Rectangle {
                    Layout.fillWidth: true
                    height: usbHeader.height
                    color: theme.headerBackground

                    RowLayout {
                        id: usbHeader
                        width: parent.width
                        height: 36

                        anchors.leftMargin: 15
                        anchors.rightMargin: 15
                        anchors.left: parent.left
                        anchors.right: parent.right

                        Text {
                            text: usbSection.visible ? "\u25BC" : "\u25B6"
                            font.pixelSize: 10
                            color: theme.textSecondary
                        }

                        Text {
                            text: "USB"
                            font.pixelSize: 14
                            font.bold: true
                            color: theme.textColor
                        }

                        Text {
                            text: hardwareViewModel ? "(" + hardwareViewModel.usbCount + ")" : "(0)"
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Item { Layout.fillWidth: true }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: usbSection.visible = !usbSection.visible
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: theme.borderColor
                }

                // USB 콘텐츠
                ColumnLayout {
                    id: usbSection
                    Layout.fillWidth: true
                    visible: true
                    spacing: 0

                    // USB 사용 불가 메시지
                    Rectangle {
                        Layout.fillWidth: true
                        height: 50
                        color: theme.background
                        visible: hardwareViewModel ? !hardwareViewModel.usbAvailable : true

                        Text {
                            anchors.centerIn: parent
                            text: "USB 정보를 읽을 수 없습니다"
                            font.pixelSize: 13
                            color: theme.textSecondary
                        }
                    }

                    // USB 장치 목록
                    Repeater {
                        model: hardwareViewModel ? hardwareViewModel.usbData : []

                        Rectangle {
                            Layout.fillWidth: true
                            height: 70
                            color: index % 2 === 0 ? theme.background : theme.surface

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 4

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 15

                                    Text {
                                        text: "Bus " + modelData.bus + " : Device " + modelData.device
                                        font.pixelSize: 13
                                        font.bold: true
                                        color: theme.textColor
                                    }

                                    Text {
                                        text: modelData.vendor_id + ":" + modelData.product_id
                                        font.pixelSize: 12
                                        font.family: "monospace"
                                        color: theme.accent
                                    }

                                    Item { Layout.fillWidth: true }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 15

                                    Text {
                                        text: modelData.manufacturer
                                        font.pixelSize: 12
                                        color: theme.textSecondary
                                    }

                                    Text {
                                        text: modelData.product
                                        font.pixelSize: 12
                                        color: theme.textSecondary
                                    }

                                    Item { Layout.fillWidth: true }
                                }
                            }
                        }
                    }

                    // USB 장치가 없는 경우
                    Rectangle {
                        Layout.fillWidth: true
                        height: 40
                        color: theme.background
                        visible: hardwareViewModel ? (hardwareViewModel.usbAvailable && hardwareViewModel.usbCount === 0) : false

                        Text {
                            anchors.centerIn: parent
                            text: "연결된 USB 장치가 없습니다"
                            font.pixelSize: 13
                            color: theme.textSecondary
                        }
                    }
                }

                // ============================================
                // 시리얼 섹션
                // ============================================
                Rectangle {
                    Layout.fillWidth: true
                    height: serialHeader.height
                    color: theme.headerBackground

                    RowLayout {
                        id: serialHeader
                        width: parent.width
                        height: 36

                        anchors.leftMargin: 15
                        anchors.rightMargin: 15
                        anchors.left: parent.left
                        anchors.right: parent.right

                        Text {
                            text: serialSection.visible ? "\u25BC" : "\u25B6"
                            font.pixelSize: 10
                            color: theme.textSecondary
                        }

                        Text {
                            text: "시리얼"
                            font.pixelSize: 14
                            font.bold: true
                            color: theme.textColor
                        }

                        Text {
                            text: hardwareViewModel ? "(" + hardwareViewModel.serialCount + ")" : "(0)"
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Item { Layout.fillWidth: true }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: serialSection.visible = !serialSection.visible
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: theme.borderColor
                }

                // 시리얼 콘텐츠
                ColumnLayout {
                    id: serialSection
                    Layout.fillWidth: true
                    visible: true
                    spacing: 0

                    // 시리얼 장치가 없는 경우
                    Rectangle {
                        Layout.fillWidth: true
                        height: 50
                        color: theme.background
                        visible: hardwareViewModel ? hardwareViewModel.serialCount === 0 : true

                        Text {
                            anchors.centerIn: parent
                            text: "연결된 시리얼 장치 없음"
                            font.pixelSize: 13
                            color: theme.textSecondary
                        }
                    }

                    // 시리얼 포트 목록
                    Repeater {
                        model: hardwareViewModel ? hardwareViewModel.serialData : []

                        Rectangle {
                            Layout.fillWidth: true
                            height: 40
                            color: index % 2 === 0 ? theme.background : theme.surface

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 15
                                anchors.rightMargin: 15
                                spacing: 15

                                Text {
                                    Layout.preferredWidth: 200
                                    text: modelData.path
                                    font.pixelSize: 13
                                    font.family: "monospace"
                                    color: theme.textColor
                                }

                                // 타입 배지
                                Rectangle {
                                    width: typeBadgeText.width + 16
                                    height: 22
                                    radius: 4
                                    color: modelData.type === "USB" ? "#1b5e20"
                                         : modelData.type === "ACM" ? "#0d47a1"
                                         : "#424242"

                                    Text {
                                        id: typeBadgeText
                                        anchors.centerIn: parent
                                        text: modelData.type
                                        font.pixelSize: 11
                                        color: "white"
                                    }
                                }

                                // 상태 인디케이터
                                RowLayout {
                                    spacing: 6

                                    Rectangle {
                                        width: 8
                                        height: 8
                                        radius: 4
                                        color: modelData.exists ? "#4caf50" : "#f44336"
                                    }

                                    Text {
                                        text: modelData.exists ? "접근 가능" : "접근 불가"
                                        font.pixelSize: 12
                                        color: theme.textSecondary
                                    }
                                }

                                Item { Layout.fillWidth: true }
                            }
                        }
                    }
                }

                // 하단 여백
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 20
                }
            }
        }
    }
}
