Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Configura o backend gráfico para OpenGL compativel com a GPU
Set oEnv = WshShell.Environment("PROCESS")
oEnv("QSG_RHI_BACKEND") = "opengl"

curDir = fso.GetParentFolderName(WScript.ScriptFullName)
sidecarScript = curDir & "\drift-ai-editor\sidecar_launcher.py"

cmd = "python """ & sidecarScript & """"
WshShell.Run cmd, 0, False
