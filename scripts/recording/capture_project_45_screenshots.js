import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_45_skill_gap_career_recommendation/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-045 ===');
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

    // 1. Full Career Dashboard
    console.log('Capturing 01_career_dashboard.png...');
    await page.goto('http://127.0.0.1:5045/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_career_dashboard.png') });

    // 2. Topological Graph Canvas
    console.log('Capturing 02_topological_graph_canvas.png...');
    await page.evaluate(() => {
        const el = document.getElementById('graphCanvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_topological_graph_canvas.png') });

    // 3. Trajectory Regressor Chart
    console.log('Capturing 03_trajectory_regressor_chart.png...');
    await page.evaluate(() => {
        const el = document.getElementById('trajectoryChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_trajectory_regressor_chart.png') });

    // 4. AI Engineer High Readiness (Jordan Bell)
    console.log('Capturing 04_ai_engineer_high_readiness.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-preset').value = 'jordan_ai';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-run').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_ai_engineer_high_readiness.png') });

    // 5. Cloud DevOps Architect Roadmap (Alex Thorne)
    console.log('Capturing 05_cloud_devops_architect_roadmap.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'alex_cloud';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-run').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_cloud_devops_architect_roadmap.png') });

    // 6. Career Switcher Gap Analysis (Morgan Vance)
    console.log('Capturing 06_career_switcher_gap_analysis.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'career_switcher';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-run').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_career_switcher_gap_analysis.png') });

    // 7. Active Roadmaps Table
    console.log('Capturing 07_active_roadmaps_table.png...');
    await page.evaluate(() => {
        const el = document.getElementById('tbl-roadmaps');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_active_roadmaps_table.png') });

    // 8. Cryptographic SHA-256 Audit Ledger Table
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('tbl-audit');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully for PROJECT-045 ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
