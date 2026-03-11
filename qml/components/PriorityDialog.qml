import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * 프로세스 우선순위 변경 다이얼로그.
 * SpinBox로 nice 값(-20~19)을 선택하여 우선순위를 변경합니다.
 * ThemeManager 색상을 사용합니다.
 */
Dialog {
    id: priorityDialog

    // 대상 프로세스 PID
    property int targetPid: -1
    // 대상 프로세스 이름
    property string targetName: ""

    title: "우선순위 변경 - " + targetName
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel

    width: 350
    height: 200

    // 다이얼로그를 화면 중앙에 배치
    anchors.centerIn: parent

    background: Rectangle {
        color: theme.cardBackground
        border.color: theme.borderColor
        radius: 6
    }

    header: Rectangle {
        color: theme.headerBackground
        height: 40
        radius: 6

        // 하단 모서리를 직각으로
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 6
            color: theme.headerBackground
        }

        Text {
            anchors.centerIn: parent
            text: priorityDialog.title
            font.pixelSize: 14
            font.bold: true
            color: theme.textColor
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 15

        Label {
            text: "PID: " + targetPid + " (" + targetName + ")"
            font.pixelSize: 14
            Layout.fillWidth: true
            color: theme.textColor
        }

        Label {
            text: "Nice 값 (-20: 최고 우선순위, 19: 최저 우선순위)"
            font.pixelSize: 12
            color: theme.textSecondary
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Label {
                text: "Nice 값:"
                font.pixelSize: 14
                color: theme.textColor
            }

            SpinBox {
                id: niceSpinBox
                from: -20
                to: 19
                value: 0
                editable: true
                Layout.fillWidth: true
            }
        }

        Label {
            text: "참고: 음수 값은 root 권한이 필요합니다"
            font.pixelSize: 11
            color: theme.textSecondary
            Layout.fillWidth: true
        }
    }

    onAccepted: {
        if (processViewModel && targetPid > 0) {
            processViewModel.changeNice(targetPid, niceSpinBox.value)
        }
    }

    onOpened: {
        niceSpinBox.value = 0
    }
}
