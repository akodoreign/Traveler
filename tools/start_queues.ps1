# Resume every GPU art queue after a restart (user 2026-11-15: "setup a resume on restart of machine for this and the
# last que" / "were going to have a forced windows update sometime this week"). Run at logon by the scheduled task
# "Rokugan GPU queues" (tools/install_queue_task.ps1); safe to run by hand any time - each queue starts only if it isn't
# already running and isn't finished, and every runner skips the work it already finished. ComfyUI itself comes back
# through its own "ComfyUI Headless" logon task; the runners wait for it.
#   1. gen_pixeldrive    the AI sprite-sheet runner (tools/start_pixeldrive.ps1; a second copy exits at once)
#   2. pixelai_redo      the redraw queue: keys in _art/preview/agents/pixelai/redo_queue.txt without a
#                        sheets/<key>/complete marker
#   3. gen_envart        the environment art (waits for 1 and 2 to finish; done when _art/envart/ALL_DONE exists)
$root = Split-Path -Parent $PSScriptRoot
$pyw = Join-Path $root ".venv\Scripts\pythonw.exe"
$px = Join-Path $root "_art\preview\agents\pixelai"
$log = Join-Path $px "start_queues.log"
function Note($s) { Add-Content -Path $log -Value ((Get-Date -Format "MM-dd HH:mm") + " " + $s) -Encoding utf8 }
function Running($script) {
    @(Get-CimInstance Win32_Process -Filter "name='pythonw.exe' or name='python.exe'" |
      Where-Object { $_.CommandLine -like "*$script*" }).Count -gt 0
}
function Start-Detached($argline) {
    $cmd = "`"$pyw`" -E $argline"
    $r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $root }
    return $r.ProcessId
}

# 1. the sprite-sheet runner
if (Running "gen_pixeldrive.py") { Note "pixeldrive already running" }
else { $o = & (Join-Path $PSScriptRoot "start_pixeldrive.ps1"); Note "pixeldrive: $o" }

# 2. the redraw queue (only the sheets not finished yet)
$qf = Join-Path $px "redo_queue.txt"
if (Running "pixelai_redo.py") { Note "redo already running" }
elseif (Test-Path $qf) {
    $left = @((Get-Content $qf -Raw) -split '\s+' | Where-Object { $_ -and -not (Test-Path (Join-Path $px "sheets\$_\complete")) })
    if ($left.Count -gt 0) {
        $id = Start-Detached ("`"" + (Join-Path $root "tools\pixelai_redo.py") + "`" " + ($left -join " ") + " --log `"" + (Join-Path $px "redo.log") + "`"")
        Note "redo started pid $id for $($left -join ', ')"
    } else { Note "redo queue finished" }
}

# 3. the environment art (waits for 1 and 2 by itself)
if (Running "gen_envart.py") { Note "envart already running" }
elseif (Test-Path (Join-Path $root "_art\envart\ALL_DONE")) { Note "envart finished" }
else {
    $id = Start-Detached ("`"" + (Join-Path $root "tools\gen_envart.py") + "`" run --log `"" + (Join-Path $root "_art\envart\envart.log") + "`"")
    Note "envart started pid $id"
}
