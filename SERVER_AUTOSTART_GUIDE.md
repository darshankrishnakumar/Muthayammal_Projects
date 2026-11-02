# 🔄 Auto-Restart & Auto-Host Workflow Guide

This document explains how your laptop automatically resumes hosting the backend and database whenever you turn on or restart your laptop.

---

## ⚡ Method 1: Automatic on Laptop Boot (100% Zero-Click)

Whenever you power on your laptop and log into Windows, your server and tunnel can start automatically in the background.

### Setup Instructions (Do this once):
1. Press `Win + R` on your keyboard to open the **Run** dialog.
2. Type `shell:startup` and press **Enter**. (This opens your Windows Startup folder).
3. Right-click on [`start-server.bat`](file:///e:/ACADEMIC_INTEGRATION_TOOL/start-server.bat) in `E:\ACADEMIC_INTEGRATION_TOOL\`.
4. Click **"Show more options"** ➡️ **"Create shortcut"**.
5. Move/paste that shortcut into the **Startup folder** you opened in step 2.

**Done!** Every time you start or restart your laptop, Windows will automatically start MySQL, Spring Boot, and your public tunnel gateway in the background.

---

## 🖱️ Method 2: 1-Click Desktop Shortcut

If you prefer to start the server only when you want to test:
1. Right-click on [`start-server.bat`](file:///e:/ACADEMIC_INTEGRATION_TOOL/start-server.bat) in `E:\ACADEMIC_INTEGRATION_TOOL\`.
2. Click **"Send to"** ➡️ **"Desktop (create shortcut)"**.
3. Whenever you open your laptop, simply **double-click the desktop shortcut**, and your entire backend server + tunnel will spin up in 5 seconds!

---

## 🛑 How to Stop the Server Anytime

Whenever you want to pause hosting:
- Double-click [`stop-server.bat`](file:///e:/ACADEMIC_INTEGRATION_TOOL/stop-server.bat) in your project directory.
- It will cleanly terminate Spring Boot, free port `8080`, and close all active tunnels.

---

## 🌐 Fixed Public URL (No Reconfiguration Needed on Vercel)

The startup script uses the fixed subdomain:
👉 **`https://academic-integration-backend.loca.lt`**

Because this subdomain is permanent, you **never have to update your Vercel environment variables** again after a restart.

| Service | Address |
| :--- | :--- |
| **Vercel Frontend** | `https://academic-integration-tool.vercel.app` |
| **Public Gateway URL** | `https://academic-integration-backend.loca.lt` |
| **Backend REST API** | `http://localhost:8080` |
| **MySQL Database** | `localhost:3306` (`academic_db`) |
