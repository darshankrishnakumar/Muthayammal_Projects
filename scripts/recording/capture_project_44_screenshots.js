import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_44_resume_screening_nlp/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-044 ===');
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

    // 1. Full ATS Screening Dashboard
    console.log('Capturing 01_ats_screening_dashboard.png...');
    await page.goto('http://127.0.0.1:5044/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_ats_screening_dashboard.png') });

    // 2. Cross-Attention Radar Canvas
    console.log('Capturing 02_cross_attention_radar_canvas.png...');
    await page.evaluate(() => {
        const el = document.getElementById('radarCanvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_cross_attention_radar_canvas.png') });

    // 3. Competency Dimension Chart
    console.log('Capturing 03_competency_regressor_chart.png...');
    await page.evaluate(() => {
        const el = document.getElementById('competencyChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_competency_regressor_chart.png') });

    // 4. Senior AI Candidate Shortlisted (Dr. Sarah Connor)
    console.log('Capturing 04_senior_ai_candidate_shortlisted.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-preset').value = 'lead_ai';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-run').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_senior_ai_candidate_shortlisted.png') });

    // 5. Cloud Platform Candidate Screened (Aria Stark)
    console.log('Capturing 05_cloud_platform_candidate_screened.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'cloud_arch';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-run').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_cloud_platform_candidate_screened.png') });

    // 6. Junior Candidate Rejected (Marcus Vance)
    console.log('Capturing 06_junior_candidate_rejected.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'junior_dev';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-run').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_junior_candidate_rejected.png') });

    // 7. ATS Candidate Ranking Table
    console.log('Capturing 07_ats_candidate_ranking_table.png...');
    await page.evaluate(() => {
        const el = document.getElementById('tbl-matches');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_ats_candidate_ranking_table.png') });

    // 8. Cryptographic SHA-256 Audit Ledger Table
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('tbl-audit');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully for PROJECT-044 ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
