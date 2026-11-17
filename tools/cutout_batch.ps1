# One roster batch: cut, bake, install, test, release, then print the next batch's art rows.
#   tools\cutout_batch.ps1 cast8 <cores image id> <limbs image id> "release message"
param([string]$Name, [string]$Cores, [string]$Limbs, [string]$Message)
$images = "$env:USERPROFILE\.copilot\session-state\5c919086-c3a2-4ea7-ba88-88c0967cb011\images"
Push-Location "$PSScriptRoot"
$keys = (py -3.12 -E cutout_prompt.py next | Select-Object -First 1) -replace '^.*next: ', ''
py -3.12 -E cutout_batch_run.py $Name "$images\image-$Cores.png" "$images\image-$Limbs.png" @($keys -split ' ') 2>&1 | Select-Object -Last 2
$built = $LASTEXITCODE
$unit = py -3.12 -E -W ignore -m unittest test_rig3d 2>&1 | Select-String -Pattern "^(Ran|OK|FAILED)"
Pop-Location
if ($built -ne 0 -or -not ($unit -match "OK")) { "build or invariants failed; not releasing"; $unit; exit 1 }
$battle = py -3.12 -E "$PSScriptRoot\testbattle.py" 3 --lv 60 --rt "party P101;party P132" --wait 150 2>&1 |
    Select-String -Pattern "gid 3|Exception in|ERROR" | Select-Object -Last 2
$battle
if (-not ($battle -match "won/ended") -or ($battle -match "Exception")) { "battle check failed; not releasing"; exit 1 }
py -3.12 -E "$PSScriptRoot\release_here.py" $Message tools/cutout_profiles _art/sources/cutout
Push-Location "$PSScriptRoot"; py -3.12 -E cutout_prompt.py next; Pop-Location
