@echo off
setlocal

REM Stop only the local dev processes used by this project.
REM This avoids stale Vite/Uvicorn windows occupying ports 5173/8000.

echo [INFO] Stopping stale Fengshui GIS dev services...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$root = (Resolve-Path '%~dp0..').Path; " ^
  "$items = Get-CimInstance Win32_Process | Where-Object { " ^
  "  ($_.CommandLine -like '*uvicorn*main:app*--port*8000*') -or " ^
  "  ($_.CommandLine -like ('*' + $root + '*frontend*node_modules*vite*')) -or " ^
  "  ($_.CommandLine -like ('*' + $root + '*frontend*') -and $_.CommandLine -like '*npm*run*dev*') " ^
  "}; " ^
  "foreach ($item in $items) { try { Stop-Process -Id $item.ProcessId -Force -ErrorAction Stop; Write-Host ('[STOPPED] ' + $item.ProcessId + ' ' + $item.Name) } catch {} }"

exit /b 0
