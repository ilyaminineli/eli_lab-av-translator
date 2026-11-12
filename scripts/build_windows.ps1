[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ProjectPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$BuildScript = Join-Path $PSScriptRoot "build_pyinstaller.py"

if (-not (Test-Path $ProjectPython)) {
    throw "The repository-local .venv was not found. Create it with 64-bit CPython 3.12, 3.13 or 3.14, then run: .\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py"
}

# Compatibility wrapper for older instructions/tools. The only supported
# build implementation is scripts/build_pyinstaller.py.
& $ProjectPython $BuildScript @args
if ($LASTEXITCODE -ne 0) {
    throw "The PyInstaller build failed with exit code $LASTEXITCODE."
}
