import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_09_cyberbullying_detection_dea_rnn/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-009 ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Executive Dashboard
    console.log('Capturing 01_executive_dashboard.png...');
    await page.goto('http://127.0.0.1:5009/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '01_executive_dashboard.png') });

    // 2. Tweet Intake Workspace
    console.log('Capturing 02_tweet_intake_workspace.png...');
    // Click Gender Harassment preset to load sample text
    await page.evaluate(() => {
        if (typeof loadPreset === 'function') {
            loadPreset('gender');
        }
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '02_tweet_intake_workspace.png') });

    // 3. Cyberbullying Classification Result
    console.log('Running analysis and capturing 03_cyberbullying_classification_result.png...');
    await page.click('#analyzeBtn');
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '03_cyberbullying_classification_result.png') });

    // 4. Token Attention Heatmap (Focus on attention box)
    console.log('Capturing 04_token_attention_heatmap.png...');
    await page.evaluate(() => {
        const el = document.getElementById('attnTokensBox');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '04_token_attention_heatmap.png') });

    // 5. Multi-Class Probability Distribution
    console.log('Capturing 05_multiclass_probability_distribution.png...');
    await page.evaluate(() => {
        const el = document.getElementById('probBarsContainer');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '05_multiclass_probability_distribution.png') });

    // 6. Model Architecture & Benchmarks
    console.log('Capturing 06_model_architecture_benchmarks.png...');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'instant' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '06_model_architecture_benchmarks.png') });

    // 7. Transaction History & Audit Ledger
    console.log('Capturing 07_transaction_history_audit.png...');
    await page.evaluate(() => {
        const el = document.getElementById('historyTableBody');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'end' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_transaction_history_audit.png') });

    await browser.close();
    console.log('=== All 7 Screenshots Captured Successfully for PROJECT-009 ===');
}

run().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
