import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_13_crime_prediction_forecasting/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-013 ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Executive Dashboard
    console.log('Capturing 01_executive_dashboard.png...');
    await page.goto('http://127.0.0.1:5013/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_executive_dashboard.png') });

    // 2. Spatial & Temporal Simulator
    console.log('Capturing 02_spatial_temporal_simulator.png...');
    await page.evaluate(() => {
        const el = document.getElementById('selDistrict');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '02_spatial_temporal_simulator.png') });

    // 3. Critical Threat Prediction
    console.log('Simulating Late-Night Downtown and capturing 03_critical_threat_prediction.png...');
    await page.evaluate(() => {
        loadPreset('late_night_downtown');
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.evaluate(() => {
        const el = document.getElementById('resultCard');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '03_critical_threat_prediction.png') });

    // 4. Low Threat Suburban Prediction
    console.log('Simulating Suburban Quiet and capturing 04_low_threat_suburban_prediction.png...');
    await page.evaluate(() => {
        loadPreset('suburban_quiet');
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.evaluate(() => {
        const el = document.getElementById('resultCard');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '04_low_threat_suburban_prediction.png') });

    // 5. 24-Hour Temporal Crime Risk Curve
    console.log('Capturing 05_hourly_crime_risk_curve.png...');
    await page.evaluate(() => {
        loadPreset('late_night_downtown');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => {
        const el = document.getElementById('hourlyBarsContainer');
        if (el) el.parentElement.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '05_hourly_crime_risk_curve.png') });

    // 6. Patrol Dispatch Action
    console.log('Capturing 06_patrol_dispatch_action.png...');
    await page.evaluate(() => {
        switchTab('dispatches');
        const el = document.getElementById('dispatchesTableContainer');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '06_patrol_dispatch_action.png') });

    // 7. SQLite Relational Audit Ledger
    console.log('Capturing 07_sqlite_audit_ledger.png...');
    await page.evaluate(() => {
        switchTab('incidents');
        window.scrollTo(0, document.body.scrollHeight);
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_sqlite_audit_ledger.png') });

    await browser.close();
    console.log('=== All 7 Screenshots Captured Successfully for PROJECT-013 ===');
}

run().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
