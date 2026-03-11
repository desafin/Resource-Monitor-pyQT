import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "tabs" as Tabs
import "components" as Components

/**
 * 메인 윈도우 - TabBar와 StackLayout으로 구성.
 * 시스템 개요, 프로세스, 디스크, 네트워크 탭을 제공합니다.
 * ThemeManager로 다크/라이트 테마를 지원합니다.
 */
ApplicationWindow {
    id: root
    visible: true
    width: 1280
    height: 800
    title: "System Resource Monitor"

    // 테마 매니저
    QtObject {
        id: theme
        property bool isDarkTheme: true

        // 배경색
        property color background: isDarkTheme ? "#1e1e1e" : "#ffffff"
        property color foreground: isDarkTheme ? "#e0e0e0" : "#333333"
        property color accent: isDarkTheme ? "#4fc3f7" : "#1976d2"
        property color surface: isDarkTheme ? "#2d2d2d" : "#f5f5f5"
        property color cardBackground: isDarkTheme ? "#333333" : "#ffffff"
        property color headerBackground: isDarkTheme ? "#252525" : "#e8e8e8"
        property color textColor: isDarkTheme ? "#e0e0e0" : "#333333"
        property color textSecondary: isDarkTheme ? "#aaaaaa" : "#666666"
        property color borderColor: isDarkTheme ? "#444444" : "#e0e0e0"
    }

    // 업데이트 간격 (초)
    property int _updateInterval: 1

    color: theme.background

    Component.onCompleted: {
        console.log("Window loaded")
        console.log("monitorViewModel exists:", monitorViewModel !== undefined)
        console.log("processViewModel exists:", processViewModel !== undefined)
        console.log("diskViewModel exists:", diskViewModel !== undefined)
        console.log("networkViewModel exists:", networkViewModel !== undefined)
        console.log("hardwareViewModel exists:", hardwareViewModel !== undefined)

        // 저장된 설정 적용
        if (typeof savedWidth !== "undefined") {
            root.width = savedWidth
            root.height = savedHeight
        }
        if (typeof savedDarkTheme !== "undefined") {
            theme.isDarkTheme = savedDarkTheme
        }
        if (typeof savedInterval !== "undefined") {
            root._updateInterval = savedInterval
        }
    }

    // 설정 다이얼로그
    Components.SettingsDialog {
        id: settingsDialog
        onSettingsSaved: function(isDark, interval) {
            theme.isDarkTheme = isDark
            root._updateInterval = interval
            console.log("Settings saved - theme:", isDark ? "dark" : "light", "interval:", interval)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // 탭 바
        Rectangle {
            Layout.fillWidth: true
            height: 40
            color: theme.headerBackground

            RowLayout {
                anchors.fill: parent
                spacing: 0

                TabBar {
                    id: tabBar
                    Layout.fillWidth: true
                    background: Rectangle { color: "transparent" }

                    TabButton {
                        text: "시스템 개요"
                        width: implicitWidth
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: 13
                            color: tabBar.currentIndex === 0 ? theme.accent : theme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: tabBar.currentIndex === 0 ? theme.surface : "transparent"
                            border.width: tabBar.currentIndex === 0 ? 0 : 0
                            Rectangle {
                                width: parent.width
                                height: 2
                                anchors.bottom: parent.bottom
                                color: tabBar.currentIndex === 0 ? theme.accent : "transparent"
                            }
                        }
                    }

                    TabButton {
                        text: "프로세스"
                        width: implicitWidth
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: 13
                            color: tabBar.currentIndex === 1 ? theme.accent : theme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: tabBar.currentIndex === 1 ? theme.surface : "transparent"
                            Rectangle {
                                width: parent.width
                                height: 2
                                anchors.bottom: parent.bottom
                                color: tabBar.currentIndex === 1 ? theme.accent : "transparent"
                            }
                        }
                    }

                    TabButton {
                        text: "디스크"
                        width: implicitWidth
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: 13
                            color: tabBar.currentIndex === 2 ? theme.accent : theme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: tabBar.currentIndex === 2 ? theme.surface : "transparent"
                            Rectangle {
                                width: parent.width
                                height: 2
                                anchors.bottom: parent.bottom
                                color: tabBar.currentIndex === 2 ? theme.accent : "transparent"
                            }
                        }
                    }

                    TabButton {
                        text: "네트워크"
                        width: implicitWidth
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: 13
                            color: tabBar.currentIndex === 3 ? theme.accent : theme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: tabBar.currentIndex === 3 ? theme.surface : "transparent"
                            Rectangle {
                                width: parent.width
                                height: 2
                                anchors.bottom: parent.bottom
                                color: tabBar.currentIndex === 3 ? theme.accent : "transparent"
                            }
                        }
                    }

                    TabButton {
                        text: "하드웨어"
                        width: implicitWidth
                        contentItem: Text {
                            text: parent.text
                            font.pixelSize: 13
                            color: tabBar.currentIndex === 4 ? theme.accent : theme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: tabBar.currentIndex === 4 ? theme.surface : "transparent"
                            Rectangle {
                                width: parent.width
                                height: 2
                                anchors.bottom: parent.bottom
                                color: tabBar.currentIndex === 4 ? theme.accent : "transparent"
                            }
                        }
                    }
                }

                // 테마 토글 버튼
                Button {
                    Layout.preferredWidth: 36
                    Layout.preferredHeight: 36
                    flat: true

                    contentItem: Text {
                        text: theme.isDarkTheme ? "\u2600" : "\u263D"
                        font.pixelSize: 18
                        color: theme.textColor
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        color: parent.hovered ? theme.surface : "transparent"
                        radius: 4
                    }

                    ToolTip.visible: hovered
                    ToolTip.text: theme.isDarkTheme ? "라이트 모드" : "다크 모드"

                    onClicked: theme.isDarkTheme = !theme.isDarkTheme
                }

                // 설정 버튼
                Button {
                    Layout.preferredWidth: 36
                    Layout.preferredHeight: 36
                    Layout.rightMargin: 10
                    flat: true

                    contentItem: Text {
                        text: "\u2699"
                        font.pixelSize: 18
                        color: theme.textColor
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        color: parent.hovered ? theme.surface : "transparent"
                        radius: 4
                    }

                    ToolTip.visible: hovered
                    ToolTip.text: "설정"

                    onClicked: {
                        settingsDialog.currentDarkTheme = theme.isDarkTheme
                        settingsDialog.currentInterval = root._updateInterval
                        settingsDialog.open()
                    }
                }
            }
        }

        // 탭 콘텐츠
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex

            // 시스템 개요 탭
            Tabs.SystemOverviewTab {
                id: systemOverviewTab
            }

            // 프로세스 탭
            Tabs.ProcessesTab {
                id: processesTab
            }

            // 디스크 탭
            Tabs.DiskTab {
                id: diskTab
            }

            // 네트워크 탭
            Tabs.NetworkTab {
                id: networkTab
            }

            // 하드웨어 탭
            Tabs.HardwareTab {
                id: hardwareTab
            }
        }

        // 하단 상태 바
        Rectangle {
            Layout.fillWidth: true
            height: 30
            color: theme.isDarkTheme ? "#1a1a1a" : "#2c2c2c"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 10
                spacing: 20

                Text {
                    text: "CPU: " + (monitorViewModel ? monitorViewModel.cpuUsage : "N/A")
                    color: "white"
                    font.pixelSize: 12
                }

                Text {
                    text: "Memory: " + (monitorViewModel ? monitorViewModel.memoryUsage : "N/A")
                    color: "white"
                    font.pixelSize: 12
                }

                Item {
                    Layout.fillWidth: true
                }

                Text {
                    text: "Resource Monitor v2.0"
                    color: "#aaa"
                    font.pixelSize: 11
                }
            }
        }
    }
}
