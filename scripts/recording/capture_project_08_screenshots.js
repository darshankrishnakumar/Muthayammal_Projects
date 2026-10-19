import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_08_customer_churn_prediction/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-008 ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Executive Dashboard
    console.log('Capturing 01_executive_dashboard.png...');
    await page.goto('http://127.0.0.1:5008/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '01_executive_dashboard.png') });

    // 2. Prediction Input Form
    console.log('Capturing 02_prediction_input_form.png...');
    await page.goto('http://127.0.0.1:5008/predict', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '02_prediction_input_form.png') });

    // 3. Submit prediction and capture results gauge
    console.log('Submitting prediction form and capturing 03_prediction_results_gauge.png...');
    await page.click('#predictBtn');
    await page.waitForNavigation({ waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => {
        const el = document.getElementById('predictionResultSection');
        if (el) el.scrollIntoView({ behavior: 'instant' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_prediction_results_gauge.png') });

    // 4. Survival & Cumulative Hazard Curves
    console.log('Capturing 04_survival_and_hazard_curves.png...');
    await page.evaluate(() => {
        window.scrollBy({ top: 400, behavior: 'instant' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '04_survival_and_hazard_curves.png') });

    // 5. SHAP Feature Importance
    console.log('Capturing 05_shap_feature_importance.png...');
    await page.evaluate(() => {
        window.scrollBy({ top: 450, behavior: 'instant' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '05_shap_feature_importance.png') });

    // 6. Model Performance Benchmarks
    console.log('Capturing 06_model_performance_benchmarks.png...');
    await page.goto('http://127.0.0.1:5008/model-performance', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_model_performance_benchmarks.png') });

    // 7. Transaction History & Audit Ledger
    console.log('Capturing 07_transaction_history_audit.png...');
    await page.goto('http://127.0.0.1:5008/history', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '07_transaction_history_audit.png') });

    await browser.close();
    console.log('=== All 7 Screenshots Successfully Captured for PROJECT-008 ===');
}

run().catch(err => {
    console.error('Screenshot capture error:', err);
    process.exit(1);
});
