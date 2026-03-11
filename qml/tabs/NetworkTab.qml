import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "../components"

/**
 * 네트워크 탭 - 인터페이스별 상세 정보, 전송량, 속도 표시 및 Ping 테스트.
 * ListView를 사용하여 각 인터페이스의 IP, MAC, MTU, 업로드/다운로드 속도를 표시합니다.
 */
Item {
    id: networkTab

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
                    text: "네트워크 모니터"
                    font.pixelSize: 16
                    font.bold: true
                    color: theme.textColor
                }

                Item { Layout.fillWidth: true }
            }
        }

        // 구분선
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: theme.borderColor
        }

        // 네트워크 인터페이스 목록
        ListView {
            id: networkListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: networkViewModel ? networkViewModel.networkModel : null
            boundsBehavior: Flickable.StopAtBounds
            spacing: 1

            ScrollBar.vertical: ScrollBar {
                active: true
                policy: ScrollBar.AsNeeded
            }

            delegate: Rectangle {
                width: networkListView.width
                height: 200
                color: index % 2 === 0 ? theme.background : theme.surface

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 6

                    // 인터페이스 이름 + 상태 표시
                    RowLayout {
                        spacing: 8

                        // 상태 표시 (초록/회색 원)
                        Rectangle {
                            width: 10
                            height: 10
                            radius: 5
                            color: isUp ? "#4caf50" : "#9e9e9e"
                        }

                        Text {
                            text: iface
                            font.pixelSize: 15
                            font.bold: true
                            color: theme.textColor
                        }

                        Item { Layout.fillWidth: true }
                    }

                    // 속도 표시
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 30

                        // 업로드 속도
                        RowLayout {
                            spacing: 6

                            Text {
                                text: "\u2191"
                                font.pixelSize: 16
                                color: "#f44336"
                            }

                            Text {
                                text: networkViewModel ? networkViewModel.formatSpeed(speedUp) : "0 B/s"
                                font.pixelSize: 14
                                color: theme.textColor
                            }
                        }

                        // 다운로드 속도
                        RowLayout {
                            spacing: 6

                            Text {
                                text: "\u2193"
                                font.pixelSize: 16
                                color: "#4caf50"
                            }

                            Text {
                                text: networkViewModel ? networkViewModel.formatSpeed(speedDown) : "0 B/s"
                                font.pixelSize: 14
                                color: theme.textColor
                            }
                        }

                        Item { Layout.fillWidth: true }
                    }

                    // 누적 전송량
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20

                        Text {
                            text: "전송: " + (networkViewModel ? networkViewModel.formatBytes(bytesSent) : "0 B")
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Text {
                            text: "수신: " + (networkViewModel ? networkViewModel.formatBytes(bytesRecv) : "0 B")
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Text {
                            text: "PKT 전송: " + packetsSent
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Text {
                            text: "PKT 수신: " + packetsRecv
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Item { Layout.fillWidth: true }
                    }

                    // 상세 정보 Row 1: IP, MAC, MTU
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20

                        Text {
                            text: "IP: " + ipAddress
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Text {
                            text: "MAC: " + macAddress
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Text {
                            text: "MTU: " + mtu
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Item { Layout.fillWidth: true }
                    }

                    // 상세 정보 Row 2: Netmask, Speed, Duplex
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20

                        Text {
                            text: "Netmask: " + netmask
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Text {
                            text: "Speed: " + linkSpeed + " Mbps"
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Text {
                            text: "Duplex: " + duplex
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Item { Layout.fillWidth: true }
                    }

                    // 상세 정보 Row 3: IPv6, Broadcast
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 20

                        Text {
                            text: "IPv6: " + ipv6Address
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Text {
                            text: "Broadcast: " + broadcast
                            font.pixelSize: 12
                            color: theme.textSecondary
                        }

                        Item { Layout.fillWidth: true }
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

        // Ping 테스트 섹션
        Rectangle {
            Layout.fillWidth: true
            height: pingSectionContent.implicitHeight + 24
            color: theme.background

            PingSection {
                id: pingSectionContent
                anchors.fill: parent
                anchors.margins: 12
            }
        }
    }
}
