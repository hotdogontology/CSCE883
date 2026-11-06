param([switch]$SkipInstall)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:Path = "$env:USERPROFILE\.elan\bin;C:\Program Files\Git\cmd;" + $env:Path
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    & py -3.12 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Creating the Python environment failed.' }
}
if (-not $SkipInstall) {
    & $projectPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw 'Updating pip failed.' }
    & $projectPython -m pip install torch --index-url https://download.pytorch.org/whl/cu128
    if ($LASTEXITCODE -ne 0) { throw 'Installing CUDA PyTorch failed.' }
    & $projectPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Installing project dependencies failed.' }
}
& $projectPython scripts/check_gpu.py
if ($LASTEXITCODE -ne 0) { throw 'GPU verification failed.' }
Push-Location lean
try {
    if (-not $SkipInstall) {
        & lake update
        if ($LASTEXITCODE -ne 0) { throw 'Fetching Lean dependencies failed.' }
        & lake exe cache get
        if ($LASTEXITCODE -ne 0) { throw 'Fetching Mathlib cache failed.' }
    }
    & lake build
    if ($LASTEXITCODE -ne 0) { throw 'Lean smoke proof failed.' }
} finally { Pop-Location }
