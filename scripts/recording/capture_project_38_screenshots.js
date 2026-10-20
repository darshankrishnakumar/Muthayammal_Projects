import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputDir = '/Users/eash/Documents/antigravity/excited-borg/project_38_pavement_crack_detection/docs/screenshots';

async function capture() {
    console.log('=== Starting Screenshot Capture for PROJECT-038 ===');
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

    // 1. Dashboard Overview
    console.log('Capturing 01_pavement_inspection_dashboard.png...');
    await page.goto('http://127.0.0.1:5038/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outputDir, '01_pavement_inspection_dashboard.png') });

    // 2. Optical Scan Canvas
    console.log('Capturing 02_optical_scan_canvas.png...');
    await page.evaluate(() => {
        const el = document.getElementById('pavementCanvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '02_optical_scan_canvas.png') });

    // 3. Corridor Selection Highway
    console.log('Capturing 03_corridor_selection_highway.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectRoadSegment === 'function') {
            await window.selectRoadSegment('Interstate 80 Westbound', 114.2);
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outputDir, '03_corridor_selection_highway.png') });

    // 4. Alligator Fatigue Distress
    console.log('Capturing 04_alligator_fatigue_distress.png...');
    await page.evaluate(async () => {
        if (typeof window.runCrackAnalysis === 'function') {
            await window.runCrackAnalysis('ALLIGATOR', 'HIGH');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '04_alligator_fatigue_distress.png') });

    // 5. Transverse Thermal Crack
    console.log('Capturing 05_transverse_thermal_crack.png...');
    await page.evaluate(async () => {
        if (typeof window.runCrackAnalysis === 'function') {
            await window.runCrackAnalysis('TRANSVERSE', 'MEDIUM');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '05_transverse_thermal_crack.png') });

    // 6. Pothole Distress
    console.log('Capturing 06_pothole_emergency_distress.png...');
    await page.evaluate(async () => {
        if (typeof window.runCrackAnalysis === 'function') {
            await window.runCrackAnalysis('POTHOLE', 'HIGH');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '06_pothole_emergency_distress.png') });

    // 7. Dispatched Work Orders
    console.log('Capturing 07_dispatched_work_orders.png...');
    await page.evaluate(() => {
        const el = document.getElementById('workOrdersSection');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '07_dispatched_work_orders.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('auditLedgerSection');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('All 8 screenshots successfully captured in:', outputDir);
}

capture().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
