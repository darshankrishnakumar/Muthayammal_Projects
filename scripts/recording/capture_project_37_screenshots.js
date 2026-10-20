import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputDir = '/Users/eash/Documents/antigravity/excited-borg/project_37_traffic_violation/docs/screenshots';

async function capture() {
    console.log('=== Starting Screenshot Capture for PROJECT-037 ===');
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    page.on('dialog', async d => { await d.dismiss(); });

    // 1. Traffic Command Dashboard
    console.log('Capturing 01_traffic_command_dashboard.png...');
    await page.goto('http://127.0.0.1:5037/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outputDir, '01_traffic_command_dashboard.png') });

    // 2. CCTV Surveillance Feed
    console.log('Capturing 02_cctv_surveillance_feed.png...');
    await page.evaluate(() => {
        const el = document.querySelector('.cctv-viewport');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '02_cctv_surveillance_feed.png') });

    // 3. Intersection Selection Corridor
    console.log('Capturing 03_intersection_selection_corridor.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectIntersection === 'function') {
            await window.selectIntersection('INT-02');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outputDir, '03_intersection_selection_corridor.png') });

    // 4. Speeding Violation Telemetry
    console.log('Capturing 04_speeding_violation_telemetry.png...');
    await page.evaluate(async () => {
        if (typeof window.runViolationAnalysis === 'function') {
            await window.runViolationAnalysis('speeding');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '04_speeding_violation_telemetry.png') });

    // 5. Red Light Signal Jump
    console.log('Capturing 05_red_light_signal_jump.png...');
    await page.evaluate(async () => {
        if (typeof window.runViolationAnalysis === 'function') {
            await window.runViolationAnalysis('red_light');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '05_red_light_signal_jump.png') });

    // 6. Two-Wheeler No Helmet
    console.log('Capturing 06_two_wheeler_no_helmet.png...');
    await page.evaluate(async () => {
        if (typeof window.runViolationAnalysis === 'function') {
            await window.runViolationAnalysis('no_helmet');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '06_two_wheeler_no_helmet.png') });

    // 7. Automated e-Challan Feed
    console.log('Capturing 07_automated_echallan_feed.png...');
    await page.evaluate(() => {
        const el = document.getElementById('challanList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '07_automated_echallan_feed.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('auditTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outputDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('All 8 screenshots successfully captured in:', outputDir);
}

capture().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
