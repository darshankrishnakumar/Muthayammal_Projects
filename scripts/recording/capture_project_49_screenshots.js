import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_49_healthcare_risk_assessment/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-049 (Port 5049) ===');
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
    console.log('Capturing 01_healthcare_risk_dashboard.png...');
    await page.goto('http://127.0.0.1:5049/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_healthcare_risk_dashboard.png') });

    // 2. SHAP Feature Contribution Importance HUD
    console.log('Capturing 02_shap_feature_importance_hud.png...');
    await page.evaluate(() => {
        const el = document.getElementById('shapChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_shap_feature_importance_hud.png') });

    // 3. Robert Vance (Hypertensive CVD High Risk)
    console.log('Capturing 03_robert_vance_hypertension_cvd_scan.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-preset').value = 'vance_htn';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-assess').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_robert_vance_hypertension_cvd_scan.png') });

    // 4. Linda Sterling (Normotensive Control Low Risk)
    console.log('Capturing 04_linda_sterling_normotensive_control.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'sterling_norm';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-assess').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_linda_sterling_normotensive_control.png') });

    // 5. Arthur Pendelton (Renal CKD Critical Risk)
    console.log('Capturing 05_arthur_pendelton_renal_ckd_critical.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'pendelton_ckd';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-assess').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_arthur_pendelton_renal_ckd_critical.png') });

    // 6. Jennifer Montgomery (Diabetic Metabolic High Risk)
    console.log('Capturing 06_jennifer_montgomery_diabetic_metabolic.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'montgomery_t2d';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-assess').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_jennifer_montgomery_diabetic_metabolic.png') });

    // 7. Patient Clinical Risk Ledger Table
    console.log('Capturing 07_patient_clinical_risk_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('records-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_patient_clinical_risk_ledger.png') });

    // 8. Cryptographic Audit Ledger Table
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
