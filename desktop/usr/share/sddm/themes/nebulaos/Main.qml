// NebulaOS login screen (Qt 6). Glass card, clock, logo, password field.
import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#07060d"

    property int sessionIndex: sessionModel.lastIndex
    property color accent: config.accent || "#a855f7"

    // Translations: the greeter follows the system language (LANG).
    readonly property string lang: Qt.locale().name.substring(0, 2)
    readonly property var tr: ({
        "ru": { "Username": "Пользователь", "Password": "Пароль", "Restart": "Перезагрузка",
                "Shut down": "Выключить", "Wrong password": "Неверный пароль" },
        "uk": { "Username": "Користувач", "Password": "Пароль", "Restart": "Перезавантажити",
                "Shut down": "Вимкнути", "Wrong password": "Невірний пароль" },
        "it": { "Username": "Utente", "Password": "Password", "Restart": "Riavvia",
                "Shut down": "Spegni", "Wrong password": "Password errata" }
    })
    function t(s) { return (tr[lang] && tr[lang][s]) || s }

    Image {
        anchors.fill: parent
        source: config.background
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }
    Rectangle { anchors.fill: parent; color: "#000000"; opacity: 0.35 }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: parent.height * 0.12
        spacing: 4
        Text {
            id: clock
            anchors.horizontalCenter: parent.horizontalCenter
            color: "white"
            font.pixelSize: 96
            font.weight: Font.Light
            font.family: "Inter"
            text: Qt.formatTime(new Date(), "HH:mm")
        }
        Text {
            id: date
            anchors.horizontalCenter: parent.horizontalCenter
            color: "#e6dcf5"
            font.pixelSize: 22
            font.family: "Inter"
            text: Qt.locale().toString(new Date(), "dddd, d MMMM")
        }
        Timer {
            interval: 1000; running: true; repeat: true
            onTriggered: {
                clock.text = Qt.formatTime(new Date(), "HH:mm")
                date.text = Qt.locale().toString(new Date(), "dddd, d MMMM")
            }
        }
    }

    Rectangle {
        id: card
        width: 380
        height: 300
        radius: 24
        color: "#33150f24"
        border.color: "#40ffffff"
        border.width: 1
        anchors.centerIn: parent
        anchors.verticalCenterOffset: 120

        Column {
            anchors.centerIn: parent
            spacing: 14
            width: 300

            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                source: config.logo
                width: 84; height: 84
                smooth: true
            }
            TextField {
                id: user
                width: parent.width
                text: userModel.lastUser
                placeholderText: root.t("Username")
                color: "white"
                font.pixelSize: 16
                background: Rectangle { radius: 12; color: "#26ffffff" }
            }
            TextField {
                id: password
                width: parent.width
                echoMode: TextInput.Password
                placeholderText: root.t("Password")
                color: "white"
                font.pixelSize: 16
                focus: true
                background: Rectangle { radius: 12; color: "#26ffffff"; border.color: password.activeFocus ? root.accent : "transparent"; border.width: 2 }
                onAccepted: sddm.login(user.text, password.text, root.sessionIndex)
            }
            Text {
                id: message
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                color: "#ffb4c8"
                font.pixelSize: 14
                text: ""
            }
        }
    }

    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 28
        spacing: 12
        Repeater {
            model: [
                { label: root.t("Restart"), act: "reboot", ok: sddm.canReboot },
                { label: root.t("Shut down"), act: "off", ok: sddm.canPowerOff }
            ]
            delegate: Rectangle {
                visible: modelData.ok
                width: label.width + 28; height: 38; radius: 19
                color: area.containsMouse ? "#40ffffff" : "#26ffffff"
                Text { id: label; anchors.centerIn: parent; color: "white"; font.pixelSize: 14; text: modelData.label }
                MouseArea {
                    id: area
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: modelData.act === "reboot" ? sddm.reboot() : sddm.powerOff()
                }
            }
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            message.text = root.t("Wrong password")
            password.text = ""
            password.forceActiveFocus()
        }
    }
}
