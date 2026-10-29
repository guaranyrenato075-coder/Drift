import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Window
import Drift

// ScriptAiTab: Native AI scriptwriting, voiceover synthesis, stock media search, and automatic timeline assembly.
Item {
    id: root

    signal added()

    property bool isBusy: false
    property string statusMessage: ""
    property var scenesList: []
    property string activeProfile: "filosofico"
    property string selectedAspectRatio: "16:9"

    function sendAiRequest(endpoint, payload, callback) {
        root.isBusy = true
        root.statusMessage = qsTr("Processando...")
        const xhr = new XMLHttpRequest()
        xhr.open("POST", "http://127.0.0.1:8765/api/" + endpoint)
        xhr.setRequestHeader("Content-Type", "application/json")
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                root.isBusy = false
                if (xhr.status === 200) {
                    try {
                        const res = JSON.parse(xhr.responseText)
                        callback(true, res)
                    } catch(e) {
                        callback(false, { error: e.toString() })
                    }
                } else {
                    callback(false, { error: xhr.statusText })
                }
            }
        }
        xhr.send(JSON.stringify(payload))
    }

    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: contentCol.height + Theme.spacing3xl
        clip: true
        ScrollBar.vertical: AppScrollBar { }

        Column {
            id: contentCol
            x: Theme.pagePadding
            width: parent.width - Theme.pagePadding * 2
            spacing: Theme.spacingMd
            topPadding: Theme.pagePadding

            // Header Section
            ThemedLabel {
                text: qsTr("Roteiro e Edição com IA")
                font.bold: true
                size: "lg"
            }

            ThemedLabel {
                width: parent.width
                wrapMode: Text.WordWrap
                text: qsTr("Diretor de IA: roteirização semântica, ganchos de retenção, perfis de estilo e montagem protegida por etapas.")
                color: Theme.c.subtitlesTab.foregroundMuted
                size: "xs"
            }

            Rectangle {
                width: parent.width
                height: 1
                color: Theme.c.subtitlesTab.border
            }

            // AI Topic Generator
            ThemedLabel {
                text: qsTr("Gerador de Roteiro & Tema")
                size: "sm"
                font.bold: true
            }

            Row {
                width: parent.width
                spacing: Theme.spacingSm

                ThemedTextField {
                    id: topicInput
                    width: parent.width - generateTopicBtn.width - Theme.spacingSm
                    placeholderText: qsTr("Ex: Estoicismo, Universo, Produtividade...")
                    text: "Estoicismo"
                }

                ThemedButton {
                    id: generateTopicBtn
                    text: qsTr("Criar")
                    variant: "secondary"
                    enabled: !root.isBusy && topicInput.text.trim().length > 0
                    onClicked: {
                        root.sendAiRequest("generate_script", { topic: topicInput.text }, function(ok, res) {
                            if (ok && res.script) {
                                scriptArea.text = res.script
                                root.statusMessage = qsTr("Roteiro gerado com sucesso!")
                            } else {
                                root.statusMessage = qsTr("Erro: ") + (res.error || "")
                            }
                        })
                    }
                }
            }

            // Retention Hooks Generator
            ThemedButton {
                width: parent.width
                text: qsTr("🎣 Laboratório de Ganchos de Retenção")
                variant: "secondary"
                enabled: !root.isBusy && topicInput.text.trim().length > 0
                onClicked: {
                    root.sendAiRequest("hooks", { topic: topicInput.text }, function(ok, res) {
                        if (ok && res.hooks && res.hooks.length > 0) {
                            const h = res.hooks[0]
                            scriptArea.text = "CENA 01 (GANCHO DE RETENÇÃO)\nNARRAÇÃO: " + h.text + "\nDESCRIÇÃO VISUAL: " + h.visual_direction + "\n\n" + scriptArea.text
                            root.statusMessage = qsTr("Gancho de retenção inserido no topo do roteiro!")
                        } else {
                            root.statusMessage = qsTr("Falha ao gerar ganchos.")
                        }
                    })
                }
            }

            // Style Profiles & Aspect Ratio
            ThemedLabel {
                text: qsTr("Perfil Visual & Formato")
                size: "sm"
                font.bold: true
            }

            Row {
                width: parent.width
                spacing: Theme.spacingSm

                ThemedButton {
                    width: (parent.width - Theme.spacingSm) / 2
                    text: root.selectedAspectRatio === "16:9" ? qsTr("16:9 YouTube (Ativo)") : qsTr("16:9 YouTube")
                    variant: root.selectedAspectRatio === "16:9" ? "primary" : "secondary"
                    onClicked: root.selectedAspectRatio = "16:9"
                }

                ThemedButton {
                    width: (parent.width - Theme.spacingSm) / 2
                    text: root.selectedAspectRatio === "9:16" ? qsTr("9:16 Shorts (Ativo)") : qsTr("9:16 Shorts")
                    variant: root.selectedAspectRatio === "9:16" ? "primary" : "secondary"
                    onClicked: root.selectedAspectRatio = "9:16"
                }
            }

            // Script TextArea
            ThemedLabel {
                text: qsTr("Roteiro Completo (Texto ou Cenas)")
                size: "sm"
                font.bold: true
            }

            ScrollView {
                width: parent.width
                height: 140
                clip: true

                TextArea {
                    id: scriptArea
                    wrapMode: Text.WordWrap
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSm
                    color: "#ffffff"
                    placeholderText: qsTr("Digite ou cole seu roteiro aqui...")
                    text: "CENA 01\nNARRAÇÃO: Você não controla tudo o que acontece.\nDESCRIÇÃO VISUAL: Um homem observa uma tempestade pela janela.\n\nCENA 02\nNARRAÇÃO: Mas pode controlar a maneira como reage.\nDESCRIÇÃO VISUAL: Uma pessoa meditando ao amanhecer."
                    background: Rectangle {
                        color: Theme.c.panelBackgroundDarker || "#1c1e22"
                        radius: 4
                        border.color: Theme.c.subtitlesTab.border
                        border.width: 1
                    }
                }
            }

            // Action Buttons
            ThemedButton {
                width: parent.width
                text: qsTr("1. Analisar Roteiro Semântico")
                variant: "primary"
                enabled: !root.isBusy && scriptArea.text.trim().length > 0
                onClicked: {
                    root.sendAiRequest("plan", {
                        script: scriptArea.text,
                        title: topicInput.text || "Vídeo IA",
                        aspect_ratio: root.selectedAspectRatio,
                        language: "pt",
                        exaggeration: 0.5
                    }, function(ok, res) {
                        if (ok && res.plan) {
                            root.scenesList = res.plan.scenes || []
                            root.statusMessage = qsTr("%1 cenas analisadas semântica e visualmente.").arg(root.scenesList.length)
                        } else {
                            root.statusMessage = qsTr("Falha na análise: ") + (res.error || "")
                        }
                    })
                }
            }

            Row {
                width: parent.width
                spacing: Theme.spacingSm

                ThemedButton {
                    width: (parent.width - Theme.spacingSm) / 2
                    text: qsTr("2. Voz & Áudio Real")
                    variant: "secondary"
                    enabled: !root.isBusy && root.scenesList.length > 0
                    onClicked: {
                        root.sendAiRequest("voice", { project_id: "" }, function(ok, res) {
                            if (ok) {
                                root.statusMessage = qsTr("Voz gerada e alinhada temporalmente!")
                            } else {
                                root.statusMessage = qsTr("Erro de voz: ") + (res.error || "")
                            }
                        })
                    }
                }

                ThemedButton {
                    width: (parent.width - Theme.spacingSm) / 2
                    text: qsTr("3. Galeria de Mídias")
                    variant: "secondary"
                    enabled: !root.isBusy && root.scenesList.length > 0
                    onClicked: {
                        root.sendAiRequest("search", { project_id: "" }, function(ok, res) {
                            if (ok) {
                                root.statusMessage = qsTr("Vídeos e imagens ranqueados com alternativas!")
                            } else {
                                root.statusMessage = qsTr("Erro de busca: ") + (res.error || "")
                            }
                        })
                    }
                }
            }

            // Pre-export Quality Control Audit
            ThemedButton {
                width: parent.width
                text: qsTr("🛡️ Auditoria de Qualidade Pré-Montagem")
                variant: "secondary"
                enabled: !root.isBusy
                onClicked: {
                    root.sendAiRequest("audit", { project_id: "" }, function(ok, res) {
                        if (ok) {
                            root.statusMessage = qsTr("Nota de Qualidade: %1/100 - %2").arg(res.score).arg(res.summary)
                        } else {
                            root.statusMessage = qsTr("Falha na auditoria.")
                        }
                    })
                }
            }

            ThemedButton {
                width: parent.width
                text: qsTr("4. Montar na Timeline Drift (Por Etapas)")
                variant: "primary"
                enabled: !root.isBusy
                onClicked: {
                    root.sendAiRequest("build", { project_id: "" }, function(ok, res) {
                        if (ok) {
                            root.statusMessage = qsTr("Timeline montada com sucesso em etapas seguras!")
                            root.added()
                        } else {
                            root.statusMessage = qsTr("Erro de montagem: ") + (res.error || "")
                        }
                    })
                }
            }

            // Status feedback banner
            Rectangle {
                width: parent.width
                height: 40
                visible: root.statusMessage.length > 0
                radius: 4
                color: "#1e3a8a"

                ThemedLabel {
                    anchors.centerIn: parent
                    width: parent.width - 16
                    wrapMode: Text.WordWrap
                    text: root.statusMessage
                    size: "xs"
                    color: "#93c5fd"
                }
            }
        }
    }
}
