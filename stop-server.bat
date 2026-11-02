@echo off
title Academic Integration Tool - Server Stopper
echo ===================================================
echo   Stopping Academic Integration Tool Server Stack
echo ===================================================
echo.

echo Stopping Java / Spring Boot and Node / Tunnel processes...
taskkill /F /FI "WINDOWTITLE eq Academic-Backend-Server*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Academic-Tunnel-Gateway*" >nul 2>&1

:: Free port 8080 if needed
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

echo.
echo All backend and tunnel services have been stopped.
echo ===================================================
timeout /t 3
