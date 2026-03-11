import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * Ping 테스트 섹션 컴포넌트.
 * 호스트명 또는 IP를 입력하고 ping 테스트를 실행합니다.
 */
ColumnLayout {
    id: pingSection
    spacing: 10

    // 헤더
    Text {
        text: "Ping 테스트"
        font.pixelSize: 15
        font.bold: true
        color: theme.textColor
    }

    // 입력 + 버튼
    RowLayout {
        Layout.fillWidth: true
        spacing: 10

        TextField {
            id: pingInput
            Layout.fillWidth: true
            placeholderText: "호스트명 또는 IP 입력"
            color: theme.textColor
            font.pixelSize: 14

            background: Rectangle {
                color: theme.surface
                border.color: pingInput.activeFocus ? theme.accentColor : theme.borderColor
                border.width: 1
                radius: 4
            }

            onAccepted: {
                if (text.length > 0 && networkViewModel && !networkViewModel.isPinging) {
                    networkViewModel.executePing(text)
                }
            }
        }

        Button {
            text: "Ping"
            enabled: pingInput.text.length > 0 && networkViewModel && !networkViewModel.isPinging

            contentItem: Text {
                text: parent.text
                font.pixelSize: 14
                color: parent.enabled ? "white" : theme.textSecondary
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            background: Rectangle {
                color: parent.enabled ? theme.accentColor : theme.surface
                border.color: theme.borderColor
                radius: 4
            }

            onClicked: {
                if (networkViewModel) {
                    networkViewModel.executePing(pingInput.text)
                }
            }
        }

        BusyIndicator {
            visible: networkViewModel ? networkViewModel.isPinging : false
            running: visible
            implicitWidth: 24
            implicitHeight: 24
        }
    }

    // 결과 표시
    Rectangle {
        Layout.fillWidth: true
        height: resultText.implicitHeight + 20
        visible: networkViewModel && networkViewModel.pingResult.length > 0
        color: theme.surface
        border.color: theme.borderColor
        radius: 4

        Text {
            id: resultText
            anchors.fill: parent
            anchors.margins: 10
            text: networkViewModel ? networkViewModel.pingResult : ""
            font.pixelSize: 13
            font.family: "monospace"
            color: theme.textColor
            wrapMode: Text.WordWrap
        }
    }

    // 에러 표시
    Rectangle {
        Layout.fillWidth: true
        height: errorText.implicitHeight + 20
        visible: networkViewModel && networkViewModel.pingError.length > 0
        color: "#1af44336"
        border.color: "#f44336"
        radius: 4

        Text {
            id: errorText
            anchors.fill: parent
            anchors.margins: 10
            text: networkViewModel ? networkViewModel.pingError : ""
            font.pixelSize: 13
            color: "#f44336"
            wrapMode: Text.WordWrap
        }
    }
}
