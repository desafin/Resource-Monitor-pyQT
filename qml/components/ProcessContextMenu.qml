import QtQuick 2.15
import QtQuick.Controls 2.15

/**
 * 프로세스 우클릭 컨텍스트 메뉴.
 * 종료, 강제 종료, 일시 중지, 재개, 우선순위 변경 메뉴 항목을 제공합니다.
 */
Menu {
    id: contextMenu

    // 선택된 프로세스의 PID
    property int selectedPid: -1
    // 선택된 프로세스의 이름
    property string selectedName: ""

    title: selectedName + " (PID: " + selectedPid + ")"

    background: Rectangle {
        implicitWidth: 200
        color: theme.cardBackground
        border.color: theme.borderColor
        radius: 4
    }

    MenuItem {
        text: "종료 (SIGTERM)"
        contentItem: Text {
            text: parent.text
            color: theme.textColor
            font.pixelSize: 13
        }
        background: Rectangle {
            color: parent.highlighted ? theme.surface : "transparent"
        }
        onTriggered: {
            if (processViewModel && selectedPid > 0) {
                processViewModel.terminateProcess(selectedPid)
            }
        }
    }

    MenuItem {
        text: "강제 종료 (SIGKILL)"
        contentItem: Text {
            text: parent.text
            color: "#d32f2f"
            font.pixelSize: 13
        }
        background: Rectangle {
            color: parent.highlighted ? theme.surface : "transparent"
        }
        onTriggered: {
            if (processViewModel && selectedPid > 0) {
                processViewModel.killProcess(selectedPid)
            }
        }
    }

    MenuSeparator {
        contentItem: Rectangle {
            implicitHeight: 1
            color: theme.borderColor
        }
    }

    MenuItem {
        text: "일시 중지 (SIGSTOP)"
        contentItem: Text {
            text: parent.text
            color: theme.textColor
            font.pixelSize: 13
        }
        background: Rectangle {
            color: parent.highlighted ? theme.surface : "transparent"
        }
        onTriggered: {
            if (processViewModel && selectedPid > 0) {
                processViewModel.suspendProcess(selectedPid)
            }
        }
    }

    MenuItem {
        text: "재개 (SIGCONT)"
        contentItem: Text {
            text: parent.text
            color: theme.textColor
            font.pixelSize: 13
        }
        background: Rectangle {
            color: parent.highlighted ? theme.surface : "transparent"
        }
        onTriggered: {
            if (processViewModel && selectedPid > 0) {
                processViewModel.resumeProcess(selectedPid)
            }
        }
    }

    MenuSeparator {
        contentItem: Rectangle {
            implicitHeight: 1
            color: theme.borderColor
        }
    }

    MenuItem {
        text: "우선순위 변경..."
        contentItem: Text {
            text: parent.text
            color: theme.textColor
            font.pixelSize: 13
        }
        background: Rectangle {
            color: parent.highlighted ? theme.surface : "transparent"
        }
        onTriggered: {
            priorityDialog.targetPid = selectedPid
            priorityDialog.targetName = selectedName
            priorityDialog.open()
        }
    }

    MenuSeparator {
        contentItem: Rectangle {
            implicitHeight: 1
            color: theme.borderColor
        }
    }

    MenuItem {
        text: "상세 정보..."
        contentItem: Text {
            text: parent.text
            color: theme.accent
            font.pixelSize: 13
        }
        background: Rectangle {
            color: parent.highlighted ? theme.surface : "transparent"
        }
        onTriggered: {
            if (processViewModel && selectedPid > 0) {
                processViewModel.getProcessDetails(selectedPid)
            }
        }
    }
}
