import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * 검색 바 컴포넌트.
 * 300ms 디바운스 타이머로 processViewModel.searchText에 바인딩합니다.
 * ThemeManager 색상을 사용합니다.
 */
Item {
    id: searchBar
    height: 40
    Layout.fillWidth: true

    // 디바운스 타이머 (300ms 딜레이)
    Timer {
        id: debounceTimer
        interval: 300
        repeat: false
        onTriggered: {
            if (processViewModel) {
                processViewModel.searchText = searchField.text
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 5
        spacing: 8

        // 검색 아이콘 (텍스트로 대체)
        Text {
            text: "\u{1F50D}"
            font.pixelSize: 16
            verticalAlignment: Text.AlignVCenter
            color: theme.textSecondary
        }

        TextField {
            id: searchField
            Layout.fillWidth: true
            placeholderText: "프로세스 검색..."
            font.pixelSize: 14
            color: theme.textColor
            placeholderTextColor: theme.textSecondary

            background: Rectangle {
                color: theme.surface
                border.color: searchField.activeFocus ? theme.accent : theme.borderColor
                border.width: 1
                radius: 4
            }

            onTextChanged: {
                debounceTimer.restart()
            }

            // 검색 지우기 버튼
            Button {
                anchors.right: parent.right
                anchors.rightMargin: 5
                anchors.verticalCenter: parent.verticalCenter
                width: 20
                height: 20
                flat: true
                text: "X"
                font.pixelSize: 10
                visible: searchField.text.length > 0

                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: theme.textSecondary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    color: parent.hovered ? theme.borderColor : "transparent"
                    radius: 2
                }

                onClicked: {
                    searchField.text = ""
                }
            }
        }
    }
}
