import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_42_face_attendance_antispoofing/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-042 ===');
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1280,800'
        ]
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    page.on('dialog', async d => { await d.dismiss(); });

    // 1. Biometric Command Dashboard
    console.log('Capturing 01_biometric_command_dashboard.png...');
    await page.goto('http://127.0.0.1:5042/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_biometric_command_dashboard.png') });

    // 2. Face Mesh & Optical Flow HUD
    console.log('Capturing 02_face_mesh_optical_flow_hud.png...');
    await page.evaluate(() => {
        const el = document.getElementById('hud-canvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_face_mesh_optical_flow_hud.png') });

    // 3. Liveness Telemetry Chart
    console.log('Capturing 03_liveness_telemetry_chart.png...');
    await page.evaluate(() => {
        const el = document.getElementById('telemetryChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_liveness_telemetry_chart.png') });

    // 4. Genuine Student Face Verification (Alex Chen)
    console.log('Capturing 04_genuine_alex_chen_verification.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-student').value = '0';
        document.getElementById('sel-attack').value = 'LIVE';
        document.getElementById('btn-verify').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_genuine_alex_chen_verification.png') });

    // 5. 2D Print Photo Attack Interception
    console.log('Capturing 05_print_attack_2d_blocked.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-student').value = '1';
        document.getElementById('sel-attack').value = 'PRINT_ATTACK_2D';
        document.getElementById('btn-verify').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_print_attack_2d_blocked.png') });

    // 6. 4K Screen Replay Attack Interception
    console.log('Capturing 06_screen_replay_attack_blocked.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-student').value = '2';
        document.getElementById('sel-attack').value = 'SCREEN_REPLAY_ATTACK';
        document.getElementById('btn-verify').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_screen_replay_attack_blocked.png') });

    // 7. Verified Attendance Records Table
    console.log('Capturing 07_verified_attendance_records.png...');
    await page.evaluate(() => {
        const el = document.getElementById('tbl-attendance');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_verified_attendance_records.png') });

    // 8. Cryptographic SHA-256 Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('tbl-audit');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully for PROJECT-042! ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
