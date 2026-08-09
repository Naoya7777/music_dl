$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$venvDirectory = Join-Path $projectRoot ".venv"
$pythonExecutable = Join-Path $venvDirectory "Scripts\python.exe"
$requirementsFile = Join-Path $projectRoot "requirements.txt"

if (-not (Get-Command "py" -ErrorAction SilentlyContinue)) {
    throw "Python Launcher (py) was not found. Install Python 3.14."
}

if (-not (Get-Command "ffmpeg" -ErrorAction SilentlyContinue)) {
    throw "FFmpeg was not found. Install FFmpeg and add it to PATH."
}

if (-not (Test-Path -LiteralPath $pythonExecutable)) {
    Write-Host "Creating the virtual environment..."
    & py -3.14 -m venv $venvDirectory
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create the Python 3.14 virtual environment."
    }
}

& $pythonExecutable -c "import customtkinter, yt_dlp" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing required Python packages..."
    & $pythonExecutable -m pip install -r $requirementsFile
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install the required Python packages."
    }
}

Push-Location $projectRoot
try {
    & $pythonExecutable -m src.main
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start Music DL."
    }
}
finally {
    Pop-Location
}
