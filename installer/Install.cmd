@echo off
setlocal
title Garmin Assistant Setup
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install.ps1"
if errorlevel 1 (
  echo.
  echo Installation failed. Please read the message above and the installation guide.
  pause
  exit /b 1
)
