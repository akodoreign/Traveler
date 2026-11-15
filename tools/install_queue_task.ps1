# Registers the logon task "Rokugan GPU queues": 2 minutes after logon (ComfyUI's own logon task starts first) it runs
# tools/start_queues.ps1 hidden. Run once: powershell -ExecutionPolicy Bypass -File tools\install_queue_task.ps1
$script = Join-Path $PSScriptRoot "start_queues.ps1"
$action = New-ScheduledTaskAction -Execute "C:\Windows\System32\conhost.exe" `
    -Argument "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$script`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$trigger.Delay = "PT2M"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -StartWhenAvailable
Register-ScheduledTask -TaskName "Rokugan GPU queues" -Action $action -Trigger $trigger -Settings $settings `
    -Description "Resume the Rokugan Traveler GPU art queues (pixeldrive, redo, envart) after a restart" -Force |
    Select-Object TaskName, State
