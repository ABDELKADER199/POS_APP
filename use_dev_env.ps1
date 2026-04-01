$pythonRoot = "C:\Users\Master\AppData\Local\Programs\Python\Python312"
$venvScripts = Join-Path $PSScriptRoot ".venv\Scripts"
$tmpDir = Join-Path $PSScriptRoot ".tmp"

if (-not (Test-Path $pythonRoot)) {
    Write-Error "Python 3.12 not found at: $pythonRoot"
    return
}

if (-not (Test-Path $tmpDir)) {
    New-Item -ItemType Directory -Path $tmpDir | Out-Null
}

$env:Path = "$pythonRoot;$pythonRoot\Scripts;$venvScripts;$env:Path"
$env:TEMP = $tmpDir
$env:TMP = $tmpDir

Write-Output "Development environment activated for this shell session."
Write-Output "python path: $pythonRoot"
python --version
if (Test-Path (Join-Path $venvScripts "python.exe")) {
    & (Join-Path $venvScripts "python.exe") --version
}
