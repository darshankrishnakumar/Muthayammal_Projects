import puppeteer from 'puppeteer-core';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_02_network_intrusion_anomaly/docs/screenshots';

async function run() {
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('http://127.0.0.1:5002', { waitUntil: 'networkidle0' });

    console.log('Capturing 01_soc_landing_inspector.png...');
    await page.screenshot({ path: path.join(outDir, '01_soc_landing_inspector.png') });

    console.log('Capturing 02_neptune_syn_flood.png...');
    await page.evaluate(() => {
        loadPreset('syn_flood_dos', document.querySelector('.chip:nth-child(1)'));
        executeInspection();
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '02_neptune_syn_flood.png') });

    console.log('Capturing 03_portsweep_probe.png...');
    await page.evaluate(() => {
        loadPreset('port_scan_probe', document.querySelector('.chip:nth-child(2)'));
        executeInspection();
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '03_portsweep_probe.png') });

    console.log('Capturing 04_zero_day_anomaly.png...');
    await page.evaluate(() => {
        loadPreset('zero_day_anomaly', document.querySelector('.chip:nth-child(6)'));
        executeInspection();
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '04_zero_day_anomaly.png') });

    console.log('Capturing 05_model_benchmarks_tab.png...');
    await page.evaluate(() => {
        switchTab('tab-benchmarks', document.querySelectorAll('.tab-btn')[1]);
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '05_model_benchmarks_tab.png') });

    console.log('Capturing 06_security_event_log_tab.png...');
    await page.evaluate(() => {
        switchTab('tab-history', document.querySelectorAll('.tab-btn')[2]);
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '06_security_event_log_tab.png') });

    console.log('Capturing 07_threat_analytics_tab.png...');
    await page.evaluate(() => {
        switchTab('tab-analytics', document.querySelectorAll('.tab-btn')[3]);
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '07_threat_analytics_tab.png') });

    await browser.close();
    console.log('All screenshots captured successfully.');
}

run().catch(console.error);
