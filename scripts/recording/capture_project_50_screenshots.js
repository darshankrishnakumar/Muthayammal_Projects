import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_50_handwritten_document_recognition/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-050 (Port 5050) ===');
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
    console.log('Capturing 01_idp_workstation_dashboard.png...');
    await page.goto('http://127.0.0.1:5050/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_idp_workstation_dashboard.png') });

    // 2. LayoutLM Spatial Bounding Box Entity Mapping
    console.log('Capturing 02_layoutlm_spatial_entity_mapping.png...');
    await page.evaluate(() => {
        const el = document.getElementById('bbox-name');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_layoutlm_spatial_entity_mapping.png') });

    // 3. Handwriting Degradation Chart HUD
    console.log('Capturing 03_handwriting_degradation_chart.png...');
    await page.evaluate(() => {
        const el = document.getElementById('featureChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_handwriting_degradation_chart.png') });

    // 4. Dr. Jonathan Hayes (Hospital Clinical Intake — Clean SOTA)
    console.log('Capturing 04_dr_hayes_clinical_intake_scan.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-preset').value = 'hayes_intake';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-parse').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_dr_hayes_clinical_intake_scan.png') });

    // 5. Global Supplies Ltd (Handwritten Commercial Invoice)
    console.log('Capturing 05_global_supplies_invoice_scan.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'global_supplies_invoice';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-parse').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_global_supplies_invoice_scan.png') });

    // 6. Anonymous Respondent #42 (Survey Sheet — Degraded Cursive Escalation)
    console.log('Capturing 06_anonymous_survey_cursive_escalation.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'anonymous_survey';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-parse').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_anonymous_survey_cursive_escalation.png') });

    // 7. Parsed Document Registry
    console.log('Capturing 07_parsed_document_registry.png...');
    await page.evaluate(() => {
        const el = document.getElementById('records-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_parsed_document_registry.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('audit-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully for PROJECT-050 ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
