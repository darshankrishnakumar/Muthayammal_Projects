import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_17_phishing_email_detection/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-017 (Port 5017) ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Landing Scanner View
    console.log('Capturing 01_landing_scanner_view.png...');
    await page.goto('http://127.0.0.1:5017/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_landing_scanner_view.png') });

    // 2. Click preset 1 (Bank Header Spoofing) and Run Scan
    console.log('Capturing 02_phishing_bank_detection.png...');
    await page.click('button[data-sample="sample-phish-rcnn-1"]');
    await new Promise(r => setTimeout(r, 400));
    await page.click('#scanBtn');
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '02_phishing_bank_detection.png') });

    // 3. Scroll to Attention Heatmap
    console.log('Capturing 03_attention_heatmap_xai.png...');
    await page.evaluate(() => {
        const el = document.getElementById('attentionContainer');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '03_attention_heatmap_xai.png') });

    // 4. Scroll to Multi-Model Consensus Grid
    console.log('Capturing 04_multi_model_consensus.png...');
    await page.evaluate(() => {
        const el = document.getElementById('allModelsGrid');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '04_multi_model_consensus.png') });

    // 5. Click Safe Preset (Legitimate Standup Sync) and Scan
    console.log('Capturing 05_legitimate_email_scan.png...');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.click('button[data-sample="sample-safe-rcnn-1"]');
    await new Promise(r => setTimeout(r, 400));
    await page.click('#scanBtn');
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '05_legitimate_email_scan.png') });

    // 6. Switch to Benchmarks Tab
    console.log('Capturing 06_academic_benchmarks.png...');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.click('.nav-tab[data-tab="benchmarks"]');
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '06_academic_benchmarks.png') });

    // 7. Switch to SQLite Scan History Tab
    console.log('Capturing 07_sqlite_scan_history.png...');
    await page.click('.nav-tab[data-tab="history"]');
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '07_sqlite_scan_history.png') });

    // 8. Switch to Architecture Tab
    console.log('Capturing 08_rcnn_deep_architecture.png...');
    await page.click('.nav-tab[data-tab="architecture"]');
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '08_rcnn_deep_architecture.png') });

    await browser.close();
    console.log('All 8 high-res screenshots captured successfully in:', outDir);
}

run().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
