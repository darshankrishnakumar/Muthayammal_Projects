import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_52_crowd_density_estimation/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-052 (Port 5052) ===');
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
    console.log('Capturing 01_crowd_monitoring_dashboard.png...');
    await page.goto('http://127.0.0.1:5052/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_crowd_monitoring_dashboard.png') });

    // 2. CSRNet Spatial Density Heatmap Grid
    console.log('Capturing 02_csrnet_density_heatmap_grid.png...');
    await page.evaluate(() => {
        const el = document.getElementById('heatmap-grid');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_csrnet_density_heatmap_grid.png') });

    // 3. Central Plaza Concourse Surge Alert
    console.log('Capturing 03_central_plaza_concourse_surge.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('zone-select').value = 'Central Plaza Concourse';
        document.getElementById('sim-level').value = 'high';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_central_plaza_concourse_surge.png') });

    // 4. North Gate Turnstiles Bottleneck
    console.log('Capturing 04_north_gate_turnstiles_bottleneck.png...');
    await page.evaluate(async () => {
        document.getElementById('zone-select').value = 'North Gate Turnstiles';
        document.getElementById('sim-level').value = 'high';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_north_gate_turnstiles_bottleneck.png') });

    // 5. Transit Station Platform Monitoring
    console.log('Capturing 05_transit_station_platform_monitoring.png...');
    await page.evaluate(async () => {
        document.getElementById('zone-select').value = 'Transit Station Platform 2';
        document.getElementById('sim-level').value = 'moderate';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_transit_station_platform_monitoring.png') });

    // 6. Stadium Emergency Exit Corridor
    console.log('Capturing 06_stadium_emergency_exit_corridor.png...');
    await page.evaluate(async () => {
        document.getElementById('zone-select').value = 'Stadium Emergency Exit Corridor';
        document.getElementById('sim-level').value = 'high';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_stadium_emergency_exit_corridor.png') });

    // 7. Live Crowd Telemetry Log Table
    console.log('Capturing 07_live_crowd_telemetry_registry.png...');
    await page.evaluate(() => {
        const el = document.getElementById('events-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_live_crowd_telemetry_registry.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('audit-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully for PROJECT-052! ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
