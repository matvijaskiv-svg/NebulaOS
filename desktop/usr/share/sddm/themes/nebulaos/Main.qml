// NebulaOS login screen (SDDM, Qt 6), in the spirit of the macOS lock screen:
// blurred wallpaper, date + large clock at the top, round avatar, name and a pill
// password field at the bottom; small session and power controls in the corner.
import QtQuick
import QtQuick.Controls
import QtQuick.Effects

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#07060d"

    property color accent: config.accent || "#a855f7"
    property int userIndex: Math.max(0, userModel.lastIndex)
    property int sessionIndex: Math.max(0, sessionModel.lastIndex)
    property string userName: ""
    property string realName: ""
    property string userIcon: ""

    readonly property string lang: Qt.locale().name.substring(0, 2)
    readonly property var tr: ({
        "ru": { "Enter password": "Введите пароль", "Restart": "Перезагрузка", "Shut down": "Выключить",
                "Sleep": "Сон", "Wrong password": "Неверный пароль", "Other user": "Другой пользователь" },
        "uk": { "Enter password": "Введіть пароль", "Restart": "Перезавантажити", "Shut down": "Вимкнути",
                "Sleep": "Сон", "Wrong password": "Невірний пароль", "Other user": "Інший користувач" },
        "it": { "Enter password": "Inserisci la password", "Restart": "Riavvia", "Shut down": "Spegni",
                "Sleep": "Sospendi", "Wrong password": "Password errata", "Other user": "Altro utente" }
    })
    function t(s) { return (tr[lang] && tr[lang][s]) || s }

    // ---------- background: wallpaper, softly blurred and dimmed ----------
    Image {
        id: wallpaper
        anchors.fill: parent
        source: config.background
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }
    // Blur on top; without GPU effects (safe graphics) the plain wallpaper stays visible.
    MultiEffect {
        anchors.fill: parent
        source: wallpaper
        blurEnabled: true
        blur: 0.55
        blurMax: 48
        saturation: 0.15
        brightness: -0.08
    }
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#40000000" }
            GradientStop { position: 0.55; color: "#10000000" }
            GradientStop { position: 1.0; color: "#80000000" }
        }
    }

    // ---------- date and clock ----------
    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: root.height * 0.08
        spacing: 0
        Text {
            id: date
            anchors.horizontalCenter: parent.horizontalCenter
            color: "#f2ffffff"
            font.pixelSize: Math.round(root.height * 0.024)
            font.family: "Inter"
            font.weight: Font.DemiBold
            text: Qt.locale().toString(new Date(), "dddd d MMMM")
        }
        Text {
            id: clock
            anchors.horizontalCenter: parent.horizontalCenter
            color: "#f2ffffff"
            font.pixelSize: Math.round(root.height * 0.135)
            font.family: "Inter"
            font.weight: Font.Bold
            font.letterSpacing: -2
            text: Qt.formatTime(new Date(), "HH:mm")
        }
        Timer {
            interval: 1000; running: true; repeat: true
            onTriggered: {
                clock.text = Qt.formatTime(new Date(), "HH:mm")
                date.text = Qt.locale().toString(new Date(), "dddd d MMMM")
            }
        }
    }

    // Users: read the chosen one from the model (role names come from SDDM).
    Repeater {
        model: userModel
        delegate: Item {
            Component.onCompleted: if (index === root.userIndex) {
                root.userName = model.name
                root.realName = model.realName || model.name
                root.userIcon = model.icon || ""
            }
        }
    }

    // ---------- avatar, name, password ----------
    Column {
        id: login
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: root.height * 0.11
        spacing: 14

        Item {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 96; height: 96
            Rectangle {
                id: avatarBg
                anchors.fill: parent
                radius: width / 2
                color: "#33ffffff"
                border.color: "#55ffffff"
                border.width: 1
                Text {
                    anchors.centerIn: parent
                    visible: !face.visible
                    text: (root.realName || "?").charAt(0).toUpperCase()
                    color: "white"
                    font.pixelSize: 42
                    font.family: "Inter"
                    font.weight: Font.DemiBold
                }
            }
            Image {
                id: face
                anchors.fill: parent
                source: root.userIcon
                visible: status === Image.Ready
                fillMode: Image.PreserveAspectCrop
                layer.enabled: true
                layer.effect: MultiEffect {
                    maskEnabled: true
                    maskSource: ShaderEffectSource { sourceItem: avatarBg; hideSource: false }
                }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.realName
            color: "white"
            font.pixelSize: 20
            font.family: "Inter"
            font.weight: Font.DemiBold
        }

        Rectangle {
            id: field
            anchors.horizontalCenter: parent.horizontalCenter
            width: 260; height: 38
            radius: height / 2
            color: "#2effffff"
            border.color: password.activeFocus ? "#88ffffff" : "#40ffffff"
            border.width: 1

            TextInput {
                id: password
                anchors.left: parent.left
                anchors.right: go.left
                anchors.leftMargin: 16
                anchors.rightMargin: 6
                anchors.verticalCenter: parent.verticalCenter
                echoMode: TextInput.Password
                passwordCharacter: "●"
                color: "white"
                font.pixelSize: 15
                font.family: "Inter"
                focus: true
                clip: true
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    visible: !password.text.length
                    text: root.t("Enter password")
                    color: "#b3ffffff"
                    font: password.font
                }
                Keys.onReturnPressed: root.doLogin()
                Keys.onEnterPressed: root.doLogin()
            }
            Rectangle {
                id: go
                anchors.right: parent.right
                anchors.rightMargin: 5
                anchors.verticalCenter: parent.verticalCenter
                width: 28; height: 28
                radius: 14
                visible: password.text.length > 0
                color: root.accent
                Text {
                    anchors.centerIn: parent
                    text: "→"
                    color: "white"
                    font.pixelSize: 16
                    font.weight: Font.Bold
                }
                MouseArea { anchors.fill: parent; onClicked: root.doLogin() }
            }
            // macOS-style shake on a wrong password
            SequentialAnimation {
                id: shake
                property real base: 0
                NumberAnimation { target: field; property: "anchors.horizontalCenterOffset"; to: -14; duration: 50 }
                NumberAnimation { target: field; property: "anchors.horizontalCenterOffset"; to: 14; duration: 70 }
                NumberAnimation { target: field; property: "anchors.horizontalCenterOffset"; to: -9; duration: 70 }
                NumberAnimation { target: field; property: "anchors.horizontalCenterOffset"; to: 6; duration: 60 }
                NumberAnimation { target: field; property: "anchors.horizontalCenterOffset"; to: 0; duration: 50 }
            }
        }

        Text {
            id: message
            anchors.horizontalCenter: parent.horizontalCenter
            text: ""
            color: "#ffd0d0"
            font.pixelSize: 13
            font.family: "Inter"
            height: 16
        }
    }

    function doLogin() {
        if (!password.text.length) return
        message.text = ""
        sddm.login(root.userName, password.text, root.sessionIndex)
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            password.text = ""
            message.text = root.t("Wrong password")
            shake.start()
            password.forceActiveFocus()
        }
    }

    // ---------- bottom corner: power ----------
    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 28
        spacing: 22
        Repeater {
            model: [
                { label: root.t("Sleep"), glyph: "☾", act: "suspend", ok: sddm.canSuspend },
                { label: root.t("Restart"), glyph: "↻", act: "reboot", ok: sddm.canReboot },
                { label: root.t("Shut down"), glyph: "⏻", act: "powerOff", ok: sddm.canPowerOff }
            ]
            delegate: Column {
                visible: modelData.ok
                spacing: 4
                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 40; height: 40; radius: 20
                    color: hover.containsMouse ? "#40ffffff" : "#26ffffff"
                    Text {
                        anchors.centerIn: parent
                        visible: modelData.act !== "powerOff"
                        text: modelData.glyph; color: "white"; font.pixelSize: 18
                    }
                    Canvas {      // power symbol, drawn (fonts often lack it)
                        anchors.centerIn: parent
                        width: 18; height: 18
                        visible: modelData.act === "powerOff"
                        onPaint: {
                            var c = getContext("2d")
                            c.strokeStyle = "white"; c.lineWidth = 2; c.lineCap = "round"
                            c.beginPath(); c.arc(9, 10, 7, -Math.PI * 0.32, Math.PI * 1.32); c.stroke()
                            c.beginPath(); c.moveTo(9, 1.5); c.lineTo(9, 9); c.stroke()
                        }
                    }
                    MouseArea {
                        id: hover
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: sddm[modelData.act]()
                    }
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: modelData.label
                    color: "#ccffffff"
                    font.pixelSize: 11
                    font.family: "Inter"
                }
            }
        }
    }

    // ---------- bottom left: keyboard layout ----------
    Text {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 32
        visible: keyboard && keyboard.layouts && keyboard.layouts.length > 1
        text: keyboard && keyboard.layouts && keyboard.layouts.length
              ? keyboard.layouts[keyboard.currentLayout].shortName.toUpperCase() : ""
        color: "#ccffffff"
        font.pixelSize: 13
        font.family: "Inter"
        font.weight: Font.DemiBold
        MouseArea {
            anchors.fill: parent
            onClicked: keyboard.currentLayout = (keyboard.currentLayout + 1) % keyboard.layouts.length
        }
    }

    Component.onCompleted: password.forceActiveFocus()
}
