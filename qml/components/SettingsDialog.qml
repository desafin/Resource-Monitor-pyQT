import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * 설정 다이얼로그.
 * 테마 선택, 업데이트 간격 조절 기능을 제공합니다.
 */
Dialog {
    id: settingsDialog
    title: "설정"
    width: 400
    height: 300
    modal: true
    anchors.centerIn: parent

    // 현재 설정 값 (열릴 때 외부에서 설정)
    property bool currentDarkTheme: true
    property int currentInterval: 1

    // 설정 저장 시그널
    signal settingsSaved(bool isDark, int interval)

    background: Rectangle {
        color: theme.cardBackground
        border.color: theme.borderColor
        radius: 8
    }

    header: Rectangle {
        height: 40
        color: theme.headerBackground
        radius: 8

        Text {
            anchors.centerIn: parent
            text: "설정"
            font.pixelSize: 15
            font.bold: true
            color: theme.textColor
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 8
            color: theme.headerBackground
        }
    }

    contentItem: ColumnLayout {
        spacing: 20

        // 테마 설정
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "테마"
                font.pixelSize: 14
                font.bold: true
                color: theme.textColor
            }

            RowLayout {
                spacing: 15

                RadioButton {
                    id: darkRadio
                    text: "다크"
                    checked: currentDarkTheme

                    contentItem: Text {
                        text: parent.text
                        font.pixelSize: 13
                        color: theme.textColor
                        leftPadding: parent.indicator.width + parent.spacing
                    }
                }

                RadioButton {
                    id: lightRadio
                    text: "라이트"
                    checked: !currentDarkTheme

                    contentItem: Text {
                        text: parent.text
                        font.pixelSize: 13
                        color: theme.textColor
                        leftPadding: parent.indicator.width + parent.spacing
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

        // 업데이트 간격
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "업데이트 간격"
                font.pixelSize: 14
                font.bold: true
                color: theme.textColor
            }

            RowLayout {
                spacing: 10

                Slider {
                    id: intervalSlider
                    Layout.fillWidth: true
                    from: 1
                    to: 10
                    stepSize: 1
                    value: currentInterval
                }

                Text {
                    text: intervalSlider.value + "초"
                    font.pixelSize: 13
                    Layout.preferredWidth: 40
                    color: theme.textColor
                }
            }
        }

        Item { Layout.fillHeight: true }
    }

    footer: Rectangle {
        height: 50
        color: theme.cardBackground

        Rectangle {
            anchors.top: parent.top
            width: parent.width
            height: 1
            color: theme.borderColor
        }

        RowLayout {
            anchors.centerIn: parent
            spacing: 15

            Button {
                text: "취소"
                contentItem: Text {
                    text: parent.text
                    font.pixelSize: 13
                    color: theme.textColor
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    implicitWidth: 80
                    implicitHeight: 32
                    color: parent.hovered ? theme.surface : "transparent"
                    border.color: theme.borderColor
                    border.width: 1
                    radius: 4
                }
                onClicked: settingsDialog.close()
            }

            Button {
                text: "저장"
                contentItem: Text {
                    text: parent.text
                    font.pixelSize: 13
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    implicitWidth: 80
                    implicitHeight: 32
                    color: parent.hovered ? Qt.lighter(theme.accent, 1.2) : theme.accent
                    radius: 4
                }
                onClicked: {
                    settingsDialog.settingsSaved(darkRadio.checked, intervalSlider.value)
                    settingsDialog.close()
                }
            }
        }
    }
}
