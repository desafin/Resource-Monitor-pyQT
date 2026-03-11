import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "../components" as Components

/**
 * 프로세스 탭 - 프로세스 목록 테이블 표시.
 * 검색 바, 정렬 가능한 헤더, 프로세스 목록 ListView를 포함합니다.
 * ThemeManager 색상을 사용합니다.
 */
Item {
    id: processesTab

    // 현재 선택된 프로세스 인덱스
    property int selectedIndex: -1

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 검색 바 + 트리 모드 토글
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            Layout.margins: 5
            spacing: 5

            Components.SearchBar {
                Layout.fillWidth: true
                Layout.preferredHeight: 40
            }

            Button {
                id: treeModeButton
                Layout.preferredWidth: 90
                Layout.preferredHeight: 32
                flat: true

                contentItem: Text {
                    text: (processViewModel && processViewModel.isTreeMode) ? "\u25BC 트리 보기" : "\u25B6 트리 보기"
                    font.pixelSize: 12
                    color: (processViewModel && processViewModel.isTreeMode) ? theme.accent : theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    color: (processViewModel && processViewModel.isTreeMode) ? theme.surface : "transparent"
                    border.color: theme.borderColor
                    border.width: 1
                    radius: 4
                }

                ToolTip.visible: hovered
                ToolTip.text: "프로세스 트리 모드 토글"

                onClicked: {
                    if (processViewModel) {
                        processViewModel.toggleTreeMode()
                    }
                }
            }
        }

        // 테이블 헤더 (클릭으로 정렬)
        Rectangle {
            Layout.fillWidth: true
            height: 35
            color: theme.headerBackground

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 10
                spacing: 0

                // PID 헤더
                HeaderButton {
                    text: "PID"
                    Layout.preferredWidth: 80
                    columnName: "pid"
                }

                // 이름 헤더
                HeaderButton {
                    text: "이름"
                    Layout.fillWidth: true
                    Layout.minimumWidth: 150
                    columnName: "name"
                }

                // 사용자 헤더
                HeaderButton {
                    text: "사용자"
                    Layout.preferredWidth: 100
                    columnName: "user"
                }

                // CPU 헤더
                HeaderButton {
                    text: "CPU %"
                    Layout.preferredWidth: 80
                    columnName: "cpu"
                }

                // 메모리 헤더
                HeaderButton {
                    text: "메모리 %"
                    Layout.preferredWidth: 80
                    columnName: "memory"
                }

                // 상태 헤더
                HeaderButton {
                    text: "상태"
                    Layout.preferredWidth: 80
                    columnName: "status"
                }

                // 스레드 헤더
                HeaderButton {
                    text: "스레드"
                    Layout.preferredWidth: 60
                    columnName: "threads"
                }
            }
        }

        // 프로세스 목록
        ListView {
            id: processListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: processViewModel ? processViewModel.processModel : null
            boundsBehavior: Flickable.StopAtBounds

            // 스크롤바
            ScrollBar.vertical: ScrollBar {
                active: true
                policy: ScrollBar.AsNeeded
            }

            delegate: Rectangle {
                width: processListView.width
                height: 32
                color: {
                    if (index === processesTab.selectedIndex)
                        return theme.isDarkTheme ? "#1a3a5c" : "#cce5ff"
                    return index % 2 === 0 ? theme.background : theme.surface
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 10
                    anchors.rightMargin: 10
                    spacing: 0

                    // PID
                    Text {
                        text: pid
                        font.pixelSize: 13
                        Layout.preferredWidth: 80
                        elide: Text.ElideRight
                        color: theme.textColor
                    }

                    // 이름 (트리 모드에서 들여쓰기 표시)
                    Text {
                        text: {
                            if (processViewModel && processViewModel.isTreeMode && indentLevel > 0) {
                                var indent = ""
                                for (var i = 0; i < indentLevel - 1; i++) {
                                    indent += "    "
                                }
                                indent += "\u2514\u2500\u2500 "
                                return indent + name
                            }
                            return name
                        }
                        font.pixelSize: 13
                        Layout.fillWidth: true
                        Layout.minimumWidth: 150
                        elide: Text.ElideRight
                        color: theme.textColor
                    }

                    // 사용자
                    Text {
                        text: user
                        font.pixelSize: 13
                        Layout.preferredWidth: 100
                        elide: Text.ElideRight
                        color: theme.textSecondary
                    }

                    // CPU %
                    Text {
                        text: cpuPercent.toFixed(1)
                        font.pixelSize: 13
                        Layout.preferredWidth: 80
                        horizontalAlignment: Text.AlignRight
                        color: cpuPercent > 50 ? "#d32f2f" : (cpuPercent > 20 ? "#f57c00" : theme.textColor)
                    }

                    // 메모리 %
                    Text {
                        text: memPercent.toFixed(1)
                        font.pixelSize: 13
                        Layout.preferredWidth: 80
                        horizontalAlignment: Text.AlignRight
                        color: memPercent > 50 ? "#d32f2f" : (memPercent > 20 ? "#f57c00" : theme.textColor)
                    }

                    // 상태
                    Text {
                        text: status
                        font.pixelSize: 13
                        Layout.preferredWidth: 80
                        color: status === "running" ? "#4caf50" : (status === "zombie" ? "#d32f2f" : theme.textSecondary)
                    }

                    // 스레드
                    Text {
                        text: threads
                        font.pixelSize: 13
                        Layout.preferredWidth: 60
                        horizontalAlignment: Text.AlignRight
                        color: theme.textColor
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton | Qt.RightButton

                    onClicked: {
                        processesTab.selectedIndex = index
                        if (mouse.button === Qt.RightButton) {
                            contextMenu.selectedPid = pid
                            contextMenu.selectedName = name
                            contextMenu.popup()
                        }
                    }
                }
            }
        }
    }

    // 컨텍스트 메뉴
    Components.ProcessContextMenu {
        id: contextMenu
    }

    // 우선순위 변경 다이얼로그
    Components.PriorityDialog {
        id: priorityDialog
    }

    // 프로세스 상세 정보 다이얼로그
    Components.ProcessDetailsDialog {
        id: processDetailsDialog
    }

    // processDetailsReady 시그널 수신하여 다이얼로그 표시
    Connections {
        target: processViewModel
        function onProcessDetailsReady(details) {
            if (details.error) {
                console.warn("프로세스 상세 정보 조회 실패:", details.error)
                return
            }
            processDetailsDialog.processData = details
            processDetailsDialog.processPid = contextMenu.selectedPid
            processDetailsDialog.processName = contextMenu.selectedName
            processDetailsDialog.open()
        }
    }

    // 정렬 헤더 버튼 컴포넌트
    component HeaderButton: Item {
        property string text: ""
        property string columnName: ""

        height: parent.height

        Text {
            anchors.fill: parent
            anchors.leftMargin: 4
            text: {
                var arrow = ""
                if (processViewModel && processViewModel.sortColumn === parent.columnName) {
                    arrow = processViewModel.sortOrder === Qt.AscendingOrder ? " \u25B2" : " \u25BC"
                }
                return parent.text + arrow
            }
            font.pixelSize: 13
            font.bold: true
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
            color: theme.textColor
        }

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                if (!processViewModel) return
                if (processViewModel.sortColumn === columnName) {
                    // 같은 컬럼 클릭 시 정렬 순서 토글
                    processViewModel.sortOrder =
                        processViewModel.sortOrder === Qt.AscendingOrder
                            ? Qt.DescendingOrder : Qt.AscendingOrder
                } else {
                    processViewModel.sortColumn = columnName
                    processViewModel.sortOrder = Qt.DescendingOrder
                }
            }
        }
    }
}
