$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Backend = Join-Path $Root "backend"
Set-Location $Backend

if (-not (Test-Path ".env")) {
  Write-Host "[INFO] Creating .env from .env.example"
  Copy-Item ".env.example" ".env"
}

# Avoid broken inherited Python runtime roots. Some Anaconda installs can
# otherwise treat the project folder as sys.prefix and fail to import encodings.
Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue

$pythonCandidates = @()
$envPython = $env:FENGSHUI_GIS_PYTHON
if ($envPython) {
  $pythonCandidates += $envPython
}

$wherePython = where.exe python 2>$null
if ($LASTEXITCODE -eq 0) {
  $pythonCandidates += $wherePython
}

$Python = $null
foreach ($candidate in ($pythonCandidates | Select-Object -Unique)) {
  if (-not (Test-Path $candidate)) {
    continue
  }

  $probe = New-Object System.Diagnostics.ProcessStartInfo
  $probe.FileName = $candidate
  $probe.UseShellExecute = $false
  $probe.RedirectStandardOutput = $true
  $probe.RedirectStandardError = $true
  $probe.Arguments = '-c "import sys, encodings; print(sys.executable)"'

  try {
    $process = [System.Diagnostics.Process]::Start($probe)
    $process.WaitForExit()
  } catch {
    continue
  }

  if ($process.ExitCode -eq 0) {
    $Python = $candidate
    break
  }
}

if (-not $Python) {
  Write-Host "[ERROR] No healthy Python interpreter was found."
  Write-Host "Please check Anaconda/Python installation. Python must be able to run: import encodings"
  Read-Host "Press Enter to exit"
  exit 1
}

Write-Host "[INFO] Using Python: $Python"

& $Python -c "import fastapi, uvicorn, shapely, pyproj, pydantic_settings" *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Host "[INFO] Backend dependencies are missing. Installing from requirements.txt..."
  & $Python -m pip install -r requirements.txt
  if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Backend dependency installation failed."
    Write-Host "If rasterio/geopandas fail on Windows, install GIS dependencies with conda or keep USE_MOCK_DATA=true and install the remaining packages manually."
    Read-Host "Press Enter to exit"
    exit 1
  }
}

Write-Host "[INFO] Backend is starting at http://127.0.0.1:8000"
& $Python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

Write-Host ""
Write-Host "[ERROR] Backend service stopped."
Read-Host "Press Enter to exit"
