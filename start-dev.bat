@echo off
setlocal

REM One-click local dev launcher for the Fengshui GIS MVP.
REM It starts backend FastAPI and frontend Vite in two separate windows.

cd /d "%~dp0"

if not exist "backend" (
  echo [ERROR] backend directory not found.
  pause
  exit /b 1
)

if not exist "frontend" (
  echo [ERROR] frontend directory not found.
  pause
  exit /b 1
)

if not exist "backend\.env" (
  echo [INFO] Creating backend\.env from backend\.env.example
  copy "backend\.env.example" "backend\.env" >nul
)

if not exist "frontend\.env" (
  echo [INFO] Creating frontend\.env from frontend\.env.example
  copy "frontend\.env.example" "frontend\.env" >nul
)

call "%~dp0scripts\stop-dev.bat"

echo [INFO] Starting backend at http://127.0.0.1:8000
start "Fengshui GIS Backend" cmd /k ""%~dp0scripts\start-backend.bat""

echo [INFO] Starting frontend at http://127.0.0.1:5173
start "Fengshui GIS Frontend" cmd /k ""%~dp0scripts\start-frontend.bat""

echo.
echo [OK] Dev services are launching in separate windows.
echo Backend:  http://127.0.0.1:8000/api/health
echo Frontend: http://127.0.0.1:5173
echo.
pause
