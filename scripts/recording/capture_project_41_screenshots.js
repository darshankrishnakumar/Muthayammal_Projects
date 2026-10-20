import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_41_fruit_quality_grading/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-041 ===');
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

    // 1. Command Dashboard
    console.log('Capturing 01_command_dashboard.png...');
    await page.goto('http://127.0.0.1:5041/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_command_dashboard.png') });

    // 2. Optical Conveyor Tunnel Canvas
    console.log('Capturing 02_optical_conveyor_tunnel_canvas.png...');
    await page.evaluate(() => {
        const el = document.getElementById('conveyorCanvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_optical_conveyor_tunnel_canvas.png') });

    // 3. Grade & Freshness Charts
    console.log('Capturing 03_grade_and_freshness_charts.png...');
    await page.evaluate(() => {
        const el = document.getElementById('gradeChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_grade_and_freshness_charts.png') });

    // 4. Apple Grade A Export Inspection
    console.log('Capturing 04_apple_grade_a_export_inspection.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectLane === 'function') {
            window.selectLane(1, 'Lane 1: High-Speed Apple Optical Sorter', 'APPLE', 'NONE');
            await new Promise(r => setTimeout(r, 300));
            await window.triggerFruitInspection();
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_apple_grade_a_export_inspection.png') });

    // 5. Orange Skin Rot Defect Reject
    console.log('Capturing 05_orange_skin_rot_defect_reject.png...');
    await page.evaluate(async () => {
        if (typeof window.selectLane === 'function') {
            window.selectLane(2, 'Lane 2: Citrus / Orange Surface Defect Sorter', 'ORANGE', 'SKIN_ROT');
            await new Promise(r => setTimeout(r, 300));
            await window.triggerFruitInspection();
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_orange_skin_rot_defect_reject.png') });

    // 6. Mango Premium Export Grader
    console.log('Capturing 06_mango_premium_export_grader.png...');
    await page.evaluate(async () => {
        if (typeof window.selectLane === 'function') {
            window.selectLane(4, 'Lane 4: Premium Mango Export Inspection Line', 'MANGO', 'NONE');
            await new Promise(r => setTimeout(r, 300));
            await window.triggerFruitInspection();
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_mango_premium_export_grader.png') });

    // 7. Conveyor Inspection Telemetry Table
    console.log('Capturing 07_conveyor_inspection_telemetry_table.png...');
    await page.evaluate(() => {
        const el = document.getElementById('itemsTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_conveyor_inspection_telemetry_table.png') });

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
