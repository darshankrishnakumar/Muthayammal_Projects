import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_55_accident_emergency_alert/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-055 (Port 5055) ===');
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

    // 1. Full Dashboard Overview
    console.log('Capturing 01_accident_detection_dashboard.png...');
    await page.goto('http://127.0.0.1:5055/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_accident_detection_dashboard.png') });

    // 2. Multi-Cue Attention Diagnostics
    console.log('Capturing 02_multicue_attention_diagnostics.png...');
    await page.evaluate(() => {
        const el = document.getElementById('cad-banner');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_multicue_attention_diagnostics.png') });

    // 3. HWY 101 Rollover Critical Alert
    console.log('Capturing 03_hwy101_rollover_critical_alert.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        const sel = document.getElementById('preset-select');
        sel.value = 'PRESET-HWY101-ROLLOVER';
        sel.dispatchEvent(new Event('change'));
        document.getElementById('btn-trigger').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_hwy101_rollover_critical_alert.png') });

    // 4. Urban T-Bone Collision Dispatch
    console.log('Capturing 04_urban_tbone_collision_dispatch.png...');
    await page.evaluate(async () => {
        const sel = document.getElementById('preset-select');
        sel.value = 'PRESET-URBAN-TBONE';
        sel.dispatchEvent(new Event('change'));
        document.getElementById('btn-trigger').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_urban_tbone_collision_dispatch.png') });

    // 5. Rural Guardrail Spinout Impact
    console.log('Capturing 05_rural_guardrail_spinout_impact.png...');
    await page.evaluate(async () => {
        const sel = document.getElementById('preset-select');
        sel.value = 'PRESET-RURAL-GUARDRAIL';
        sel.dispatchEvent(new Event('change'));
        document.getElementById('btn-trigger').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_rural_guardrail_spinout_impact.png') });

    // 6. False Alarm Suppression (Safe Braking Non-Crash)
    console.log('Capturing 06_false_alarm_suppression_braking.png...');
    await page.evaluate(async () => {
        const sel = document.getElementById('preset-select');
        sel.value = 'PRESET-SAFE-BRAKING';
        sel.dispatchEvent(new Event('change'));
        document.getElementById('btn-trigger').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_false_alarm_suppression_braking.png') });

    // 7. Cryptographic Audit Ledger
    console.log('Capturing 07_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('ledger-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_cryptographic_audit_ledger.png') });

    // 8. CAD Incident Registry
    console.log('Capturing 08_cad_incident_registry.png...');
    await page.evaluate(() => {
        const el = document.getElementById('incidents-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cad_incident_registry.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Successfully Captured for PROJECT-055! ===');
}

captureScreenshots().catch(err => {
    console.error('Error capturing screenshots:', err);
    process.exit(1);
});
