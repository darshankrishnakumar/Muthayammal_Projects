@echo off
title Customer Churn Intelligence System - Service Orchestrator
echo ========================================================
echo   STARTING CUSTOMER CHURN SYSTEM (ENTERPRISE STACK)
echo ========================================================

set "JAVA_HOME=C:\Users\hackd\.tools\jdk17"
set "PATH=%JAVA_HOME%\bin;C:\Users\hackd\.tools\maven\bin;C:\Users\hackd\.tools\mysql\bin;%PATH%"

:: 1. Start MySQL Server
echo [1/4] Starting MySQL Database Server on Port 3306...
start "MySQL Server [3306]" /min "C:\Users\hackd\.tools\mysql\bin\mysqld.exe" --datadir="C:\Users\hackd\.tools\mysql\data" --port=3306 --console
timeout /t 2 >nul

:: 2. Start Python FastAPI ML Service
echo [2/4] Starting Python ML Microservice on Port 8000...
start "Python ML Service [8000]" cmd /k "cd /d %~dp0 && python -m uvicorn app:app --app-dir ml-service --host 127.0.0.1 --port 8000"
timeout /t 2 >nul

:: 3. Start Java Spring Boot Backend
echo [3/4] Starting Java Spring Boot Backend on Port 8080...
start "Spring Boot Backend [8080]" cmd /k "cd /d %~dp0 && java -jar backend\target\churn-prediction-backend-1.0.0.jar"
timeout /t 4 >nul

:: 4. Start React Frontend
echo [4/4] Starting React Frontend on Port 3000...
start "React Frontend [3000]" cmd /k "cd /d %~dp0\frontend && npm run dev -- --host 127.0.0.1 --port 3000"

echo ========================================================
echo   ALL SERVICES STARTED SUCCESSFULLY!
echo ========================================================
echo   - React Frontend:    http://localhost:3000
echo   - Spring Boot API:   http://localhost:8080/api/health
echo   - Python ML API:     http://localhost:8000/docs
echo   - MySQL Database:    127.0.0.1:3306 (telecom_churn)
echo ========================================================
timeout /t 3 >nul
start http://localhost:3000
