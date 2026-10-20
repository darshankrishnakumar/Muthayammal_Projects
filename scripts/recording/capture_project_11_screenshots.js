import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_11_parkinsons_disease_diagnosis/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-011 ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Executive Dashboard
    console.log('Capturing 01_executive_dashboard.png...');
    await page.goto('http://127.0.0.1:5011/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '01_executive_dashboard.png') });

    // 2. Clinical Intake Workspace
    console.log('Capturing 02_clinical_intake_workspace.png...');
    await page.screenshot({ path: path.join(outDir, '02_clinical_intake_workspace.png') });

    // 3. Healthy Control Clearance
    console.log('Running analysis on Healthy Control and capturing 03_healthy_control_clearance.png...');
    await page.click('#evalBtn');
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '03_healthy_control_clearance.png') });

    // 4. UPDRS Motor Staging & Dysphonia Metrics
    console.log('Capturing 04_updrs_motor_staging.png...');
    await page.evaluate(() => {
        const el = document.getElementById('updrsVal');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '04_updrs_motor_staging.png') });

    // 5. Parkinson's Disease Detection
    console.log('Selecting Early Stage PD preset and capturing 05_parkinsons_disease_detection.png...');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('.btn-preset'));
        const pdBtn = btns.find(b => b.textContent.includes('Early Stage'));
        if (pdBtn) pdBtn.click();
    });
    await new Promise(r => setTimeout(r, 600));
    await page.click('#evalBtn');
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '05_parkinsons_disease_detection.png') });

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
    console.log('=== All 7 Screenshots Captured Successfully for PROJECT-011 ===');
}

run().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
