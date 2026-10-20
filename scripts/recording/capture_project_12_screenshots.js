import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_12_egg_gender_prediction/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-012 ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Executive Dashboard
    console.log('Capturing 01_executive_dashboard.png...');
    await page.goto('http://127.0.0.1:5012/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_executive_dashboard.png') });

    // 2. Specimen Selection Workspace
    console.log('Capturing 02_specimen_selection_workspace.png...');
    await page.evaluate(() => {
        const el = document.getElementById('samplesList');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '02_specimen_selection_workspace.png') });

    // 3. Female Egg Morphology Analysis
    console.log('Testing Female egg sample and capturing 03_female_egg_morphology_analysis.png...');
    await page.evaluate(() => {
        const sampleCards = document.querySelectorAll('#samplesList > div');
        if (sampleCards.length > 0) {
            sampleCards[0].click(); // F01
        }
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.evaluate(() => {
        const el = document.getElementById('predictionResultCard');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '03_female_egg_morphology_analysis.png') });

    // 4. Male Egg Morphology Analysis
    console.log('Testing Male egg sample and capturing 04_male_egg_morphology_analysis.png...');
    await page.evaluate(() => {
        const sampleCards = Array.from(document.querySelectorAll('#samplesList > div'));
        const maleCard = sampleCards.find(c => c.textContent.includes('M01') || c.textContent.includes('Male'));
        if (maleCard) maleCard.click();
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.evaluate(() => {
        const el = document.getElementById('predictionResultCard');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '04_male_egg_morphology_analysis.png') });

    // 5. Batch Dataset Evaluation Modal
    console.log('Submitting all for batch evaluation and capturing 05_batch_dataset_evaluation_modal.png...');
    await page.evaluate(() => {
        window.scrollTo(0, 0);
    });
    await new Promise(r => setTimeout(r, 400));
    await page.click('#submitAllBtn');
    await new Promise(r => setTimeout(r, 2000));
    await page.screenshot({ path: path.join(outDir, '05_batch_dataset_evaluation_modal.png') });

    // 6. Morphology Gauge & Neural Breakdown
    console.log('Capturing 06_morphology_gauge_and_neural_breakdown.png...');
    await page.evaluate(() => {
        // Close modal if open
        const closeBtn = document.querySelector('#batchModal button') || document.querySelector('[onclick*="closeModal"]');
        if (closeBtn) closeBtn.click();
        const predCard = document.getElementById('predictionResultCard');
        if (predCard) predCard.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '06_morphology_gauge_and_neural_breakdown.png') });

    // 7. SQLite Audit Ledger
    console.log('Capturing 07_sqlite_audit_ledger.png...');
    await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_sqlite_audit_ledger.png') });

    await browser.close();
    console.log('=== All 7 Screenshots Captured Successfully for PROJECT-012 ===');
}

run().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
