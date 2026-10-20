import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_48_food_quality_freshness/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-048 (Port 5048) ===');
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
    console.log('Capturing 01_food_freshness_dashboard.png...');
    await page.goto('http://127.0.0.1:5048/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_food_freshness_dashboard.png') });

    // 2. Spectrophotometer Absorbance Spectrum HUD
    console.log('Capturing 02_spectrophotometer_absorbance_hud.png...');
    await page.evaluate(() => {
        const el = document.getElementById('specChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_spectrophotometer_absorbance_hud.png') });

    // 3. Prime Ribeye Beef Cut (Fresh Prime Quality)
    console.log('Capturing 03_prime_ribeye_optimal_quality.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('food-cat').value = 'Prime Ribeye Beef Cut';
        document.getElementById('food-cond').value = 'fresh';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_prime_ribeye_optimal_quality.png') });

    // 4. Fresh Atlantic Salmon Freshness Scan
    console.log('Capturing 04_atlantic_salmon_freshness_scan.png...');
    await page.evaluate(async () => {
        document.getElementById('food-cat').value = 'Fresh Atlantic Salmon';
        document.getElementById('food-cond').value = 'fresh';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_atlantic_salmon_freshness_scan.png') });

    // 5. Hass Avocado Marginal Degradation
    console.log('Capturing 05_avocado_marginal_degradation.png...');
    await page.evaluate(async () => {
        document.getElementById('food-cat').value = 'Hass Avocado Pack';
        document.getElementById('food-cond').value = 'moderate';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_avocado_marginal_degradation.png') });

    // 6. Artisan Sourdough Spoilage Alert
    console.log('Capturing 06_sourdough_spoilage_alert.png...');
    await page.evaluate(async () => {
        document.getElementById('food-cat').value = 'Artisan Sourdough Loaves';
        document.getElementById('food-cond').value = 'spoiled';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_sourdough_spoilage_alert.png') });

    // 7. Food Safety Inspection Registry Table
    console.log('Capturing 07_food_safety_inspection_registry.png...');
    await page.evaluate(() => {
        const el = document.getElementById('records-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_food_safety_inspection_registry.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('audit-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== Screenshot Capture Complete (8/8) ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot error:', err);
    process.exit(1);
});
