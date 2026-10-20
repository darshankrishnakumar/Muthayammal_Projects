import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_53_railway_track_defect_detection/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-053 (Port 5053) ===');
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
    console.log('Capturing 01_railway_defect_dashboard.png...');
    await page.goto('http://127.0.0.1:5053/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_railway_defect_dashboard.png') });

    // 2. ResUNet Segmentation Visualizer
    console.log('Capturing 02_resunet_segmentation_visualizer.png...');
    await page.evaluate(() => {
        const el = document.getElementById('vis-box');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_resunet_segmentation_visualizer.png') });

    // 3. High-Speed Corridor Nominal Inspection
    console.log('Capturing 03_high_speed_corridor_nominal.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('segment-select').value = 'Line 1 Main Westbound';
        document.getElementById('chainage-input').value = 'KM 144.200';
        document.getElementById('cond-select').value = 'nominal';
        document.getElementById('btn-inspect').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_high_speed_corridor_nominal.png') });

    // 4. Heavy Freight Corridor Surface Crack
    console.log('Capturing 04_freight_corridor_surface_crack.png...');
    await page.evaluate(async () => {
        document.getElementById('segment-select').value = 'Line 2 Freight Northbound';
        document.getElementById('chainage-input').value = 'KM 082.450';
        document.getElementById('cond-select').value = 'crack';
        document.getElementById('btn-inspect').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_freight_corridor_surface_crack.png') });

    // 5. Mountain Switch Missing Fastener
    console.log('Capturing 05_mountain_switch_missing_fastener.png...');
    await page.evaluate(async () => {
        document.getElementById('segment-select').value = 'Mountain Switch & Turnout';
        document.getElementById('chainage-input').value = 'KM 210.800';
        document.getElementById('cond-select').value = 'fastener';
        document.getElementById('btn-inspect').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_mountain_switch_missing_fastener.png') });

    // 6. Metro Suburban Abnormal Joint
    console.log('Capturing 06_metro_suburban_abnormal_joint.png...');
    await page.evaluate(async () => {
        document.getElementById('segment-select').value = 'Metro Suburban Southbound';
        document.getElementById('chainage-input').value = 'KM 018.150';
        document.getElementById('cond-select').value = 'joint';
        document.getElementById('btn-inspect').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_metro_suburban_abnormal_joint.png') });

    // 7. Geotagged Defect Registry
    console.log('Capturing 07_geotagged_defect_registry.png...');
    await page.evaluate(() => {
        const el = document.getElementById('records-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_geotagged_defect_registry.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('audit-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully for PROJECT-053! ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
