# Starts the AI sprite sheet runner detached (hidden, no console; it keeps going after this window closes).
# Safe to run again at any time: a second copy exits at once, and finished frames and sheets are skipped.
# ComfyUI must be up, or the runner waits for it. Stop it: Stop-Process on the pythonw.exe running gen_pixeldrive.
$root = Split-Path -Parent $PSScriptRoot
$py = Join-Path $root ".venv\Scripts\pythonw.exe"
$script = Join-Path $root "tools\gen_pixeldrive.py"
$log = Join-Path $root "_art\preview\agents\pixelai\drive_base.log"
$cmd = "`"$py`" -E `"$script`" run --workers 3 --looks --busts --log `"$log`""
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $root }
"runner started, pid $($r.ProcessId) (return code $($r.ReturnValue)); log: $log"
