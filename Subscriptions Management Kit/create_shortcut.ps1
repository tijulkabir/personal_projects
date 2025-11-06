# create_shortcut.ps1
param(
    [string]$TargetPath = "$PSScriptRoot\run.cmd",    # path to run.cmd
    [string]$LinkName = "Subscription Manager.lnk",
    [string]$IconPath = "$PSScriptRoot\bytefroster.ico", # path to your icon
    [string]$ShortcutFolder = "$env:USERPROFILE\Desktop"  # Desktop by default
)

# Prefer packaged EXE if it exists
$DistExe = Join-Path $PSScriptRoot "dist\subscription_manager\subscription_manager.exe"
if (Test-Path $DistExe) {
    $TargetPath = $DistExe
}

$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = Join-Path -Path $ShortcutFolder -ChildPath $LinkName
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = Split-Path $TargetPath
$Shortcut.IconLocation = $IconPath
$Shortcut.Save()

Write-Output "Shortcut created: $ShortcutPath"
