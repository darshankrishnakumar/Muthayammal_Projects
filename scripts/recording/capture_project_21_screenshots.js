import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_21_credit_card_fraud/docs/screenshots';
const altOutDir = '/Users/eash/Documents/antigravity/excited-borg/project_21_credit_card_fraud/screenshots';

for (const d of [outDir, altOutDir]) {
    if (!fs.existsSync(d)) {
        fs.mkdirSync(d, { recursive: true });
    }
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-021 (Port 5021) ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    const saveScreenshot = async (filename) => {
        const p1 = path.join(outDir, filename);
        const p2 = path.join(altOutDir, filename);
        await page.screenshot({ path: p1 });
        fs.copyFileSync(p1, p2);
        console.log(`Saved ${filename}`);
    };

    // 1. Landing View: Tab 0 (Real-Time Telematics Stream)
    console.log('Capturing 01_realtime_telematics_stream.png...');
    await page.goto('http://127.0.0.1:5021/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await saveScreenshot('01_realtime_telematics_stream.png');

    // 2. Critical Fraud Interdiction Alert
    console.log('Capturing 02_fraud_alert_critical_interdiction.png...');
    await page.evaluate(() => {
        if (typeof injectInstantFraud === 'function') injectInstantFraud();
    });
    await new Promise(r => setTimeout(r, 1200));
    await saveScreenshot('02_fraud_alert_critical_interdiction.png');

    // 3. Tab 1: Forensic Inspector & SHAP Explainability
    console.log('Capturing 03_forensic_inspector_shap_explainability.png...');
    await page.evaluate(() => {
        const btns = document.querySelectorAll('.tab-btn');
        if (btns[1]) switchTab(1, btns[1]);
    });
    await new Promise(r => setTimeout(r, 800));
    // Load fraud preset and run evaluation
    await page.evaluate(() => {
        if (typeof loadPreset === 'function') loadPreset('fraud1');
    });
    await new Promise(r => setTimeout(r, 600));
    await page.evaluate(() => {
        if (typeof runInspectorEvaluation === 'function') runInspectorEvaluation();
    });
    await new Promise(r => setTimeout(r, 1200));
    await saveScreenshot('03_forensic_inspector_shap_explainability.png');

    // 4. Tab 2: Model Benchmarks & ROC Curves
    console.log('Capturing 04_model_benchmarks_roc_curves.png...');
    await page.evaluate(() => {
        const btns = document.querySelectorAll('.tab-btn');
        if (btns[2]) switchTab(2, btns[2]);
    });
    await new Promise(r => setTimeout(r, 1200));
    await saveScreenshot('04_model_benchmarks_roc_curves.png');

    // 5. Tab 2 Scrolled: Threshold Tuning Studio & Cost-Benefit Analysis
    console.log('Capturing 05_threshold_tuning_studio.png...');
    await page.evaluate(() => {
        const slider = document.getElementById('decisionThreshold');
        if (slider) {
            slider.value = '0.65';
            if (typeof onThresholdChange === 'function') onThresholdChange(0.65);
        }
        window.scrollTo(0, 350);
    });
    await new Promise(r => setTimeout(r, 800));
    await saveScreenshot('05_threshold_tuning_studio.png');

    // 6. Tab 3: Batch Evaluation Matrix
    console.log('Capturing 06_batch_evaluation_matrix.png...');
    await page.evaluate(() => {
        window.scrollTo(0, 0);
        const btns = document.querySelectorAll('.tab-btn');
        if (btns[3]) switchTab(3, btns[3]);
    });
    await new Promise(r => setTimeout(r, 800));
    await page.evaluate(() => {
        if (typeof runBatchSimulation === 'function') runBatchSimulation();
    });
    await new Promise(r => setTimeout(r, 1500));
    await saveScreenshot('06_batch_evaluation_matrix.png');

    // 7. Tab 3 Scrolled: Card Sanctions & Blacklist Ledger
    console.log('Capturing 07_card_sanctions_blacklist_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('blockedCardsTableBody');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await saveScreenshot('07_card_sanctions_blacklist_ledger.png');

    // 8. Forensic Audit Dossier Ledger
    console.log('Capturing 08_sqlite_forensic_audit_dossier.png...');
    await page.evaluate(() => {
        const btns = document.querySelectorAll('.tab-btn');
        if (btns[0]) switchTab(0, btns[0]);
        window.scrollTo(0, 200);
    });
    await new Promise(r => setTimeout(r, 1000));
    await saveScreenshot('08_sqlite_forensic_audit_dossier.png');

    await browser.close();
    console.log('=== All 8 Screenshots for PROJECT-021 Captured Successfully! ===');
}

run().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
