import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * 프로세스 상세 정보 다이얼로그.
 * General, Files, Network, Environment 탭으로 구성.
 * processViewModel.processDetailsReady 시그널로 데이터를 수신합니다.
 */
Dialog {
    id: detailsDialog
    title: "프로세스 상세 정보"
    width: 700
    height: 500
    modal: true
    anchors.centerIn: parent

    // 프로세스 상세 데이터
    property var processData: ({})
    property int processPid: 0
    property string processName: ""

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
            text: processName + " (PID: " + processPid + ")"
            font.pixelSize: 15
            font.bold: true
            color: theme.textColor
        }

        // 하단 모서리 둥글기 제거
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 8
            color: theme.headerBackground
        }
    }

    contentItem: ColumnLayout {
        spacing: 0

        // 탭 바
        TabBar {
            id: detailTabBar
            Layout.fillWidth: true
            background: Rectangle { color: theme.surface }

            TabButton {
                text: "일반"
                contentItem: Text {
                    text: parent.text
                    font.pixelSize: 12
                    color: detailTabBar.currentIndex === 0 ? theme.accent : theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: detailTabBar.currentIndex === 0 ? theme.cardBackground : "transparent"
                    Rectangle {
                        width: parent.width; height: 2
                        anchors.bottom: parent.bottom
                        color: detailTabBar.currentIndex === 0 ? theme.accent : "transparent"
                    }
                }
            }

            TabButton {
                text: "파일"
                contentItem: Text {
                    text: parent.text
                    font.pixelSize: 12
                    color: detailTabBar.currentIndex === 1 ? theme.accent : theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: detailTabBar.currentIndex === 1 ? theme.cardBackground : "transparent"
                    Rectangle {
                        width: parent.width; height: 2
                        anchors.bottom: parent.bottom
                        color: detailTabBar.currentIndex === 1 ? theme.accent : "transparent"
                    }
                }
            }

            TabButton {
                text: "네트워크"
                contentItem: Text {
                    text: parent.text
                    font.pixelSize: 12
                    color: detailTabBar.currentIndex === 2 ? theme.accent : theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: detailTabBar.currentIndex === 2 ? theme.cardBackground : "transparent"
                    Rectangle {
                        width: parent.width; height: 2
                        anchors.bottom: parent.bottom
                        color: detailTabBar.currentIndex === 2 ? theme.accent : "transparent"
                    }
                }
            }

            TabButton {
                text: "환경 변수"
                contentItem: Text {
                    text: parent.text
                    font.pixelSize: 12
                    color: detailTabBar.currentIndex === 3 ? theme.accent : theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: detailTabBar.currentIndex === 3 ? theme.cardBackground : "transparent"
                    Rectangle {
                        width: parent.width; height: 2
                        anchors.bottom: parent.bottom
                        color: detailTabBar.currentIndex === 3 ? theme.accent : "transparent"
                    }
                }
            }
        }

        // 탭 콘텐츠
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: detailTabBar.currentIndex

            // 일반 탭
            Flickable {
                contentHeight: generalColumn.height
                clip: true
                ScrollBar.vertical: ScrollBar { active: true }

                ColumnLayout {
                    id: generalColumn
                    width: parent.width
                    spacing: 8

                    Repeater {
                        model: [
                            { label: "PID", value: processPid },
                            { label: "이름", value: processName },
                            { label: "실행 파일", value: processData.exe || "N/A" },
                            { label: "작업 디렉토리", value: processData.cwd || "N/A" },
                            { label: "커맨드 라인", value: (processData.cmdline || []).join(" ") || "N/A" },
                            { label: "생성 시간", value: processData.create_time ? new Date(processData.create_time * 1000).toLocaleString() : "N/A" }
                        ]

                        delegate: Rectangle {
                            Layout.fillWidth: true
                            height: 36
                            color: index % 2 === 0 ? theme.cardBackground : theme.surface

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                anchors.rightMargin: 12

                                Text {
                                    text: modelData.label
                                    font.pixelSize: 13
                                    font.bold: true
                                    Layout.preferredWidth: 120
                                    color: theme.textSecondary
                                }
                                Text {
                                    text: String(modelData.value)
                                    font.pixelSize: 13
                                    Layout.fillWidth: true
                                    elide: Text.ElideMiddle
                                    color: theme.textColor
                                }
                            }
                        }
                    }
                }
            }

            // 파일 탭
            ListView {
                clip: true
                model: processData.open_files || []
                ScrollBar.vertical: ScrollBar { active: true }

                delegate: Rectangle {
                    width: parent ? parent.width : 0
                    height: 30
                    color: index % 2 === 0 ? theme.cardBackground : theme.surface

                    Text {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        text: modelData
                        font.pixelSize: 12
                        font.family: "monospace"
                        elide: Text.ElideMiddle
                        verticalAlignment: Text.AlignVCenter
                        color: theme.textColor
                    }
                }

                // 빈 목록 메시지
                Text {
                    anchors.centerIn: parent
                    text: "열린 파일 없음 (또는 접근 거부)"
                    color: theme.textSecondary
                    font.pixelSize: 13
                    visible: parent.count === 0
                }
            }

            // 네트워크 탭
            ListView {
                clip: true
                model: processData.connections || []
                ScrollBar.vertical: ScrollBar { active: true }

                delegate: Rectangle {
                    width: parent ? parent.width : 0
                    height: 30
                    color: index % 2 === 0 ? theme.cardBackground : theme.surface

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 10

                        Text {
                            text: modelData.laddr || "-"
                            font.pixelSize: 12
                            font.family: "monospace"
                            Layout.preferredWidth: 200
                            elide: Text.ElideRight
                            color: theme.textColor
                        }
                        Text {
                            text: "\u2192"
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }
                        Text {
                            text: modelData.raddr || "-"
                            font.pixelSize: 12
                            font.family: "monospace"
                            Layout.preferredWidth: 200
                            elide: Text.ElideRight
                            color: theme.textColor
                        }
                        Text {
                            text: modelData.status || ""
                            font.pixelSize: 12
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignRight
                            color: theme.accent
                        }
                    }
                }

                Text {
                    anchors.centerIn: parent
                    text: "네트워크 연결 없음 (또는 접근 거부)"
                    color: theme.textSecondary
                    font.pixelSize: 13
                    visible: parent.count === 0
                }
            }

            // 환경 변수 탭
            ListView {
                clip: true
                model: {
                    var env = processData.environ || {}
                    var keys = Object.keys(env)
                    keys.sort()
                    var result = []
                    for (var i = 0; i < keys.length; i++) {
                        result.push({ key: keys[i], value: env[keys[i]] })
                    }
                    return result
                }
                ScrollBar.vertical: ScrollBar { active: true }

                delegate: Rectangle {
                    width: parent ? parent.width : 0
                    height: 30
                    color: index % 2 === 0 ? theme.cardBackground : theme.surface

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12

                        Text {
                            text: modelData.key
                            font.pixelSize: 12
                            font.bold: true
                            font.family: "monospace"
                            Layout.preferredWidth: 250
                            elide: Text.ElideRight
                            color: theme.accent
                        }
                        Text {
                            text: modelData.value
                            font.pixelSize: 12
                            font.family: "monospace"
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                            color: theme.textColor
                        }
                    }
                }

                Text {
                    anchors.centerIn: parent
                    text: "환경 변수 없음 (또는 접근 거부)"
                    color: theme.textSecondary
                    font.pixelSize: 13
                    visible: parent.count === 0
                }
            }
        }
    }

    footer: Rectangle {
        height: 45
        color: theme.cardBackground

        Rectangle {
            anchors.top: parent.top
            width: parent.width
            height: 1
            color: theme.borderColor
        }

        Button {
            anchors.centerIn: parent
            text: "닫기"
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
            onClicked: detailsDialog.close()
        }
    }
}
