import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_20_weapon_detection/docs/screenshots';
const altOutDir = '/Users/eash/Documents/antigravity/excited-borg/project_20_weapon_detection/screenshots';

for (const d of [outDir, altOutDir]) {
    if (!fs.existsSync(d)) {
        fs.mkdirSync(d, { recursive: true });
    }
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-020 (Port 5020) ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    const saveScreenshot = async (filename) => {
        const p1 = path.join(outDir, filename);
        const p2 = path.join(altOutDir, filename);
        await page.screenshot({ path: p1 });
        fs.copyFileSync(p1, p2);
        console.log(`Saved ${filename}`);
    };

    // 1. Landing View: Live Detection Console
    console.log('Capturing 01_live_detection_console.png...');
    await page.goto('http://127.0.0.1:5020/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await saveScreenshot('01_live_detection_console.png');

    // 2. Active Weapon Detection with Bounding Box
    console.log('Capturing 02_weapon_detection_bounding_boxes.png...');
    await page.evaluate(() => {
        if (typeof loadPreset === 'function') loadPreset('handgun');
    });
    await new Promise(r => setTimeout(r, 1500));
    await saveScreenshot('02_weapon_detection_bounding_boxes.png');

    // 3. Dual Compare Surveillance View
    console.log('Capturing 03_dual_compare_surveillance.png...');
    await page.evaluate(() => switchTab('dual'));
    await new Promise(r => setTimeout(r, 1000));
    await saveScreenshot('03_dual_compare_surveillance.png');

    // 4. Threat Density Heatmap
    console.log('Capturing 04_threat_density_heatmap.png...');
    await page.evaluate(() => switchTab('heatmap'));
    await new Promise(r => setTimeout(r, 1000));
    await saveScreenshot('04_threat_density_heatmap.png');

    // 5. CCTV Wall Monitoring
    console.log('Capturing 05_cctv_wall_monitoring.png...');
    await page.evaluate(() => switchTab('cctv'));
    await new Promise(r => setTimeout(r, 1000));
    await saveScreenshot('05_cctv_wall_monitoring.png');

    // 6. YOLOv8 Neural Architecture & Metrics
    console.log('Capturing 06_yolov8_neural_architecture.png...');
    await page.evaluate(() => switchTab('model'));
    await new Promise(r => setTimeout(r, 1200));
    await saveScreenshot('06_yolov8_neural_architecture.png');

    // 7. SQLite Audit Incident Ledger
    console.log('Capturing 07_sqlite_audit_incident_ledger.png...');
    await page.evaluate(() => switchTab('logs'));
    await new Promise(r => setTimeout(r, 1000));
    await saveScreenshot('07_sqlite_audit_incident_ledger.png');

    // 8. Forensic Analytics Reporting
    console.log('Capturing 08_forensic_analytics_reporting.png...');
    await page.evaluate(() => switchTab('analytics'));
    await new Promise(r => setTimeout(r, 1200));
    await saveScreenshot('08_forensic_analytics_reporting.png');

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully! ===');
}

run().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
