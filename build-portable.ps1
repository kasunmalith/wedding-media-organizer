param([string]$Python = "python")
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    & $Python -c "import sys; assert sys.platform == 'win32' and sys.version_info >= (3,12)"
    if ($LASTEXITCODE -ne 0) { throw 'Windows and Python 3.12+ required' }
    & $Python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
    & $Python -m PyInstaller --noconfirm --distpath portable-dist WeddingMediaOrganizer-portable.spec
    if ($LASTEXITCODE -ne 0) { throw 'Portable build failed' }
    $PortableExe = Join-Path $PSScriptRoot 'portable-dist\WeddingMediaOrganizer.exe'
    $ResultPath = Join-Path $PSScriptRoot 'portable-dist\verification.json'
    $CheckProcess = Start-Process -FilePath $PortableExe -ArgumentList @('--smoke-test', ('"' + $ResultPath + '"')) -WindowStyle Hidden -PassThru
    if (-not $CheckProcess.WaitForExit(120000)) { $CheckProcess.Kill(); throw 'Verification timed out' }
    if ($CheckProcess.ExitCode -ne 0) { throw 'Portable verification failed' }
    Write-Host "Verified single-file portable application: $PortableExe"
} finally { Pop-Location }
