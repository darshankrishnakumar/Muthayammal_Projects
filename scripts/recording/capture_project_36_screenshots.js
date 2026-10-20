import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputDir = '/Users/eash/Documents/antigravity/excited-borg/project_36_waste_classification/docs/screenshots';

async function capture() {
    console.log('=== Starting Screenshot Capture for PROJECT-036 ===');
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
    console.log('Capturing 01_sorting_dashboard_overview.png...');
    await page.goto('http://127.0.0.1:5036/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outputDir, '01_sorting_dashboard_overview.png') });

    // 2. Optical Conveyor Canvas
    console.log('Capturing 02_optical_conveyor_canvas.png...');
    await page.evaluate(() => {
        const el = document.querySelector('.conveyor-viewport');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '02_optical_conveyor_canvas.png') });

    // 3. Conveyor Line Selection
    console.log('Capturing 03_conveyor_line_selection.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectConveyor === 'function') {
            await window.selectConveyor('CONV-B2');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outputDir, '03_conveyor_line_selection.png') });

    // 4. Plastic Item Classification
    console.log('Capturing 04_plastic_item_classification.png...');
    await page.evaluate(async () => {
        if (typeof window.classifyItem === 'function') {
            await window.classifyItem('plastic_bottle');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '04_plastic_item_classification.png') });

    // 5. Metal Can Eddy Diverter
    console.log('Capturing 05_metal_can_eddy_diverter.png...');
    await page.evaluate(async () => {
        if (typeof window.classifyItem === 'function') {
            await window.classifyItem('aluminum_can');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '05_metal_can_eddy_diverter.png') });

    // 6. Cardboard Rotary Separation
    console.log('Capturing 06_cardboard_rotary_separation.png...');
    await page.evaluate(async () => {
        if (typeof window.classifyItem === 'function') {
            await window.classifyItem('corrugated_box');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '06_cardboard_rotary_separation.png') });

    // 7. Dispatched Recycling Batches
    console.log('Capturing 07_dispatched_recycling_batches.png...');
    await page.evaluate(() => {
        const el = document.getElementById('batchesTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '07_dispatched_recycling_batches.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('auditTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('All 8 screenshots successfully captured in:', outputDir);
}

capture().catch(err => {
    console.error('Screenshot capture error:', err);
    process.exit(1);
});
