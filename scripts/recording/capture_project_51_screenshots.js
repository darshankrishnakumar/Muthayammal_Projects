import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_51_energy_consumption_forecasting/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-051 (Port 5051) ===');
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
    console.log('Capturing 01_energy_dispatch_dashboard.png...');
    await page.goto('http://127.0.0.1:5051/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_energy_dispatch_dashboard.png') });

    // 2. 24-Hour Load Demand Forecast Chart
    console.log('Capturing 02_load_demand_forecast_chart.png...');
    await page.evaluate(() => {
        const el = document.getElementById('energyChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_load_demand_forecast_chart.png') });

    // 3. Tech Campus Optimization Plan
    console.log('Capturing 03_tech_campus_optimization_plan.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-preset').value = 'tech_campus';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-optimize').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_tech_campus_optimization_plan.png') });

    // 4. Industrial Plant Load Shift
    console.log('Capturing 04_industrial_plant_load_shift.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'auto_assembly';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-optimize').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_industrial_plant_load_shift.png') });

    // 5. Hyperscale Data Center Dispatch
    console.log('Capturing 05_hyperscale_datacenter_dispatch.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'cloud_datacenter';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-optimize').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_hyperscale_datacenter_dispatch.png') });

    // 6. Metro Hospital Complex Resilience
    console.log('Capturing 06_metro_hospital_critical_resilience.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'metro_hospital';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-optimize').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_metro_hospital_critical_resilience.png') });

    // 7. Active Optimization Plans Table
    console.log('Capturing 07_active_optimization_plans_registry.png...');
    await page.evaluate(() => {
        const el = document.getElementById('plans-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_active_optimization_plans_registry.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('audit-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully for PROJECT-051! ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
