Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strDesktop = WshShell.SpecialFolders("Desktop")
curDir = fso.GetParentFolderName(WScript.ScriptFullName)

shortcutPath = strDesktop & "\CutWire Drift AI.lnk"
Set oShortcut = WshShell.CreateShortcut(shortcutPath)

' Target is wscript running Iniciar_Drift_IA.vbs
oShortcut.TargetPath = "wscript.exe"
oShortcut.Arguments = """" & curDir & "\Iniciar_Drift_IA.vbs"""
oShortcut.WorkingDirectory = curDir
oShortcut.IconLocation = curDir & "\Drift\drift.exe, 0"
oShortcut.Description = "CutWire Drift - Editor de Vídeo com Inteligência Artificial Integrada"
oShortcut.Save

WScript.Echo "Atalho criado com sucesso na sua Area de Trabalho: CutWire Drift AI"

