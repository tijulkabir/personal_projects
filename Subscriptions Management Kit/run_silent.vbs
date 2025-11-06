' run_silent.vbs — fully silent launcher for Subscription Manager
Option Explicit
Dim fso, scriptFolder, pythonwPath, appPath, objShell, cmd, distExePath

Set fso = CreateObject("Scripting.FileSystemObject")
scriptFolder = fso.GetParentFolderName(WScript.ScriptFullName)
pythonwPath = scriptFolder & "\.venv\Scripts\pythonw.exe"
appPath = scriptFolder & "\subscription_manager.py"
distExePath = scriptFolder & "\dist\subscription_manager\subscription_manager.exe"

Set objShell = CreateObject("WScript.Shell")

' Change working dir to project folder (prevents Explorer from opening)
objShell.CurrentDirectory = scriptFolder

' Prefer packaged EXE (has embedded icon for Task Manager)
If fso.FileExists(distExePath) Then
    cmd = """" & distExePath & """"
    objShell.Run cmd, 0, False
    WScript.Quit 0
End If

If fso.FileExists(pythonwPath) Then
    cmd = """" & pythonwPath & """ """ & appPath & """"
    objShell.Run cmd, 0, False
Else
    ' fallback to system pythonw
    cmd = "pythonw.exe """ & appPath & """"
    objShell.Run cmd, 0, False
End If
