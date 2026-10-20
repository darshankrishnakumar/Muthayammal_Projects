import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_39_sign_language_speech/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-039 ===');
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    page.on('dialog', async d => { await d.dismiss(); });

    // 1. Initial Dashboard
    console.log('Capturing 01_command_dashboard.png...');
    await page.goto('http://127.0.0.1:5039/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '01_command_dashboard.png') });

    // 2. Focus on Spatial Landmark Canvas
    console.log('Capturing 02_spatial_landmark_canvas.png...');
    await page.evaluate(() => {
        const el = document.getElementById('landmarkCanvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_spatial_landmark_canvas.png') });

    // 3. HELLO Greeting Translation
    console.log('Capturing 03_hello_greeting_translation.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectGesture === 'function') {
            await window.selectGesture('HELLO', 0);
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_hello_greeting_translation.png') });

    // 4. EMERGENCY Alert Gesture
    console.log('Capturing 04_emergency_alert_gesture.png...');
    await page.evaluate(async () => {
        if (typeof window.selectGesture === 'function') {
            await window.selectGesture('EMERGENCY', 4);
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '04_emergency_alert_gesture.png') });

    // 5. DOCTOR Medical Translation
    console.log('Capturing 05_doctor_medical_translation.png...');
    await page.evaluate(async () => {
        if (typeof window.selectGesture === 'function') {
            await window.selectGesture('DOCTOR', 5);
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '05_doctor_medical_translation.png') });

    // 6. WATER Essential Need Gesture
    console.log('Capturing 06_water_essential_need.png...');
    await page.evaluate(async () => {
        if (typeof window.selectGesture === 'function') {
            await window.selectGesture('WATER', 6);
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '06_water_essential_need.png') });

    // 7. Translation History Register
    console.log('Capturing 07_translation_history_register.png...');
    await page.evaluate(() => {
        const el = document.getElementById('logsTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_translation_history_register.png') });

    // 8. Cryptographic Audit Ledger Table
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('auditLedgerSection');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('All 8 screenshots successfully captured in:', outDir);
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
