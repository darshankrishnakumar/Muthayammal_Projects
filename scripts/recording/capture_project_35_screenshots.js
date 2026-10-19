import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputDir = '/Users/eash/Documents/antigravity/excited-borg/project_35_driver_drowsiness/docs/screenshots';

async function capture() {
    console.log('=== Starting Screenshot Capture for PROJECT-035 ===');
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    page.on('dialog', async d => { await d.dismiss(); });

    // 1. Dashboard Fleet Overview
    console.log('Capturing 01_dashboard_fleet_overview.png...');
    await page.goto('http://127.0.0.1:5035/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outputDir, '01_dashboard_fleet_overview.png') });

    // 2. Infrared Facemesh HUD
    console.log('Capturing 02_infrared_facemesh_hud.png...');
    await page.evaluate(() => {
        const el = document.querySelector('.feed-container');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '02_infrared_facemesh_hud.png') });

    // 3. Driver Profile Selection
    console.log('Capturing 03_driver_profile_selection.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectDriver === 'function') {
            await window.selectDriver('DRV-804');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outputDir, '03_driver_profile_selection.png') });

    // 4. Alert State Telemetry
    console.log('Capturing 04_alert_state_telemetry.png...');
    await page.evaluate(async () => {
        if (typeof window.runAnalysis === 'function') {
            await window.runAnalysis('alert');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '04_alert_state_telemetry.png') });

    // 5. Drowsiness Advisory Mode
    console.log('Capturing 05_drowsiness_advisory_mode.png...');
    await page.evaluate(async () => {
        if (typeof window.runAnalysis === 'function') {
            await window.runAnalysis('drowsy');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '05_drowsiness_advisory_mode.png') });

    // 6. Critical Microsleep Intervention
    console.log('Capturing 06_critical_microsleep_intervention.png...');
    await page.evaluate(async () => {
        if (typeof window.simulateFatigueSpike === 'function') {
            await window.simulateFatigueSpike();
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outputDir, '06_critical_microsleep_intervention.png') });

    // 7. Fleet Trip Sessions Table
    console.log('Capturing 07_fleet_trip_sessions_table.png...');
    await page.evaluate(() => {
        const el = document.getElementById('tripsTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '07_fleet_trip_sessions_table.png') });

    // 8. Safety Alerts and Audit Ledger
    console.log('Capturing 08_safety_alerts_and_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('alertsTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '08_safety_alerts_and_audit_ledger.png') });

    await browser.close();
    console.log('All 8 screenshots successfully captured in:', outputDir);
}

capture().catch(err => {
    console.error('Screenshot capture error:', err);
    process.exit(1);
});
