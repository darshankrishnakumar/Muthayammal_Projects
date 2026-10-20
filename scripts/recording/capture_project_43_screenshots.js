import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_43_document_forgery_detection/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-043 ===');
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

    // 1. Forensic Command Dashboard
    console.log('Capturing 01_forensic_command_dashboard.png...');
    await page.goto('http://127.0.0.1:5043/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_forensic_command_dashboard.png') });

    // 2. Dual-Domain ELA & DCT Canvas
    console.log('Capturing 02_dual_domain_ela_dct_canvas.png...');
    await page.evaluate(() => {
        const el = document.getElementById('forensicCanvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_dual_domain_ela_dct_canvas.png') });

    // 3. Forensic Telemetry Chart
    console.log('Capturing 03_forensic_telemetry_chart.png...');
    await page.evaluate(() => {
        const el = document.getElementById('telemetryChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_forensic_telemetry_chart.png') });

    // 4. Authentic Invoice Inspection
    console.log('Capturing 04_authentic_invoice_inspection.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-doc-title').value = 'Commercial Tax Invoice #9841';
        document.getElementById('sel-doc-type').value = 'INVOICE';
        document.getElementById('sel-forgery-mode').value = 'AUTHENTIC';
        document.getElementById('btn-audit').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_authentic_invoice_inspection.png') });

    // 5. Splicing Forgery Detected (Degree Certificate)
    console.log('Capturing 05_splicing_forgery_detected.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-doc-title').value = 'Degree Certificate Stanford #2024';
        document.getElementById('sel-doc-type').value = 'ACADEMIC_CERTIFICATE';
        document.getElementById('sel-forgery-mode').value = 'SPLICING';
        document.getElementById('btn-audit').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_splicing_forgery_detected.png') });

    // 6. Copy-Move Forgery Detected (Real Estate Contract)
    console.log('Capturing 06_copy_move_forgery_detected.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-doc-title').value = 'Real Estate Agreement Clause 4';
        document.getElementById('sel-doc-type').value = 'CONTRACT';
        document.getElementById('sel-forgery-mode').value = 'COPY_MOVE';
        document.getElementById('btn-audit').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_copy_move_forgery_detected.png') });

    // 7. Questioned Document Audit Records
    console.log('Capturing 07_questioned_document_audit_table.png...');
    await page.evaluate(() => {
        const el = document.getElementById('tbl-audits');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_questioned_document_audit_table.png') });

    // 8. Cryptographic SHA-256 Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('tbl-audit');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully for PROJECT-043! ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
