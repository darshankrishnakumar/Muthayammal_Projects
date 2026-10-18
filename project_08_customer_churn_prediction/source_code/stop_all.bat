@echo off
title Customer Churn Intelligence System - Stop Services
echo ========================================================
echo   STOPPING ALL SERVICES
echo ========================================================

echo Stopping Java Spring Boot...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do taskkill /f /pid %%a 2>nul

echo Stopping Python ML Service...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /f /pid %%a 2>nul

echo Stopping React Frontend...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %%a 2>nul

echo Stopping MySQL Server...
"C:\Users\hackd\.tools\mysql\bin\mysqladmin.exe" -u root shutdown 2>nul

echo All services stopped cleanly.
pause
