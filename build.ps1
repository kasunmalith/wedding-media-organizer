param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    & $Python -c "import sys; assert sys.platform == 'win32' and sys.version_info >= (3,12), 'Use Windows with Python 3.12 or later'"
    if ($LASTEXITCODE -ne 0) { throw "Unsupported build environment" }
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Could not create build environment" }
    $BuildPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    & $BuildPython -m pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed" }
    & $BuildPython -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw "Tests failed; build stopped" }
    & $BuildPython -m PyInstaller --noconfirm WeddingMediaOrganizer.spec
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }
    $ExePath = Join-Path $PSScriptRoot 'dist\WeddingMediaOrganizer\WeddingMediaOrganizer.exe'
    $SmokePath = Join-Path $PSScriptRoot 'dist\smoke-test.json'
    $SmokeProcess = Start-Process -FilePath $ExePath -ArgumentList @('--smoke-test', ('"' + $SmokePath + '"')) -WindowStyle Hidden -PassThru
    if (-not $SmokeProcess.WaitForExit(60000)) {
        $SmokeProcess.Kill()
        throw "Packaged verification timed out; distribution is not verified."
    }
    if ($SmokeProcess.ExitCode -ne 0) { throw "Packaged application verification failed: $SmokePath" }
    Write-Host "Built and verified: $ExePath"
    Write-Host "Distribute the entire dist\WeddingMediaOrganizer folder, including _internal."
} finally {
    Pop-Location
}
