import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_10_deepfake_detector/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-010 ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Executive Dashboard
    console.log('Capturing 01_executive_dashboard.png...');
    await page.goto('http://127.0.0.1:5010/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '01_executive_dashboard.png') });

    // 2. Face Intake Workspace
    console.log('Capturing 02_face_intake_workspace.png...');
    await page.screenshot({ path: path.join(outDir, '02_face_intake_workspace.png') });

    // 3. Deepfake Detection Result (Authentic Face Scan)
    console.log('Running analysis on Authentic Face and capturing 03_deepfake_detection_result.png...');
    await page.click('#analyzeBtn');
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '03_deepfake_detection_result.png') });

    // 4. Multi-Modal Forensics Breakdown
    console.log('Capturing 04_forensics_breakdown.png...');
    await page.evaluate(() => {
        const el = document.getElementById('indFft');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '04_forensics_breakdown.png') });

    // 5. FaceSwap Manipulation Scan
    console.log('Selecting FaceSwap preset and capturing 05_faceswap_manipulation_scan.png...');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('.btn-preset'));
        const swapBtn = btns.find(b => b.textContent.includes('FaceSwap'));
        if (swapBtn) swapBtn.click();
    });
    await new Promise(r => setTimeout(r, 600));
    await page.click('#analyzeBtn');
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '05_faceswap_manipulation_scan.png') });

    // 6. Model Architecture & Benchmarks
    console.log('Capturing 06_model_architecture_benchmarks.png...');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'instant' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '06_model_architecture_benchmarks.png') });

    // 7. Transaction History & SQLite Audit Ledger
    console.log('Capturing 07_transaction_history_audit.png...');
    await page.evaluate(() => {
        const el = document.getElementById('historyTableBody');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'end' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_transaction_history_audit.png') });

    await browser.close();
    console.log('=== All 7 Screenshots Captured Successfully for PROJECT-010 ===');
}

run().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
