// NebulaOS boot splash for Plasma: softly pulsing logo over the nebula, thin progress bar.
import QtQuick

Rectangle {
    id: root
    color: "#07060d"
    property int stage

    Image {
        anchors.fill: parent
        source: "images/background.png"
        fillMode: Image.PreserveAspectCrop
        opacity: 0.85
    }

    Image {
        id: logo
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -24
        source: "images/logo.png"
        width: 132
        height: 132
        smooth: true
        mipmap: true
        SequentialAnimation on opacity {
            loops: Animation.Infinite
            NumberAnimation { from: 0.78; to: 1.0; duration: 900; easing.type: Easing.InOutQuad }
            NumberAnimation { from: 1.0; to: 0.78; duration: 900; easing.type: Easing.InOutQuad }
        }
    }

    Rectangle {
        id: track
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: logo.bottom
        anchors.topMargin: 44
        width: 200
        height: 4
        radius: 2
        color: "#26ffffff"

        Rectangle {
            height: parent.height
            radius: 2
            width: parent.width * Math.min(1, Math.max(0.08, root.stage / 6))
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: "#8b5cf6" }
                GradientStop { position: 1.0; color: "#06b6d4" }
            }
            Behavior on width { NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: track.bottom
        anchors.topMargin: 18
        text: "NebulaOS"
        color: "#b3ffffff"
        font.pixelSize: 15
        font.family: "Inter"
        font.letterSpacing: 3
    }
}
