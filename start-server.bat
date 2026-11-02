@echo off
title Academic Integration Tool - Server Launcher
echo ===================================================
echo   Starting Academic Integration Tool Server Stack
echo ===================================================
echo.

:: 1. Check if MySQL Service is running
echo [1/3] Checking MySQL Service...
sc query MySQL80 | find "RUNNING" >nul
if %ERRORLEVEL% neq 0 (
    echo Starting MySQL80 service...
    net start MySQL80
) else (
    echo MySQL80 service is already running.
)
echo.

:: 2. Start Spring Boot Backend in background
echo [2/3] Starting Spring Boot Backend (Port 8080)...
start "Academic-Backend-Server" /min cmd /c "cd /d %~dp0backend && C:\Users\offic\.m2\wrapper\dists\apache-maven-3.6.3-bin\1iopthnavndlasol9gbrbg6bf2\apache-maven-3.6.3\bin\mvn.cmd spring-boot:run"
echo Backend launch command issued.
echo.

:: 3. Start Public Cloudflare HTTP/2 Gateway
echo [3/3] Starting Public Cloudflare Gateway...
start "Academic-Tunnel-Gateway" /min cmd /c "C:\Users\offic\cloudflared.exe tunnel --protocol http2 --url http://127.0.0.1:8080"
echo Public Cloudflare Tunnel launch command issued.
echo.

echo ===================================================
echo   Server stack successfully started in background!
echo   Backend : http://localhost:8080
echo   Database: MySQL on localhost:3306
echo   Tunnel  : Cloudflare High-Speed Gateway Active
echo ===================================================
timeout /t 5
