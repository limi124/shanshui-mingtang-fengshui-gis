@echo off
setlocal

cd /d "%~dp0..\frontend"

if not exist ".env" (
  echo [INFO] Creating .env from .env.example
  copy ".env.example" ".env" >nul
)

where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js was not found. Please install Node.js 20+.
  pause
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm was not found. Please install Node.js 20+ with npm.
  pause
  exit /b 1
)

if not exist "node_modules" (
  echo [INFO] node_modules not found. Installing frontend dependencies...
  call npm install
  if errorlevel 1 (
    echo [ERROR] npm install failed.
    pause
    exit /b 1
  )
)

echo [INFO] Frontend is starting at http://127.0.0.1:5173
call npm run dev -- --force

echo.
echo [ERROR] Frontend service stopped.
pause
