import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_54_weather_event_prediction/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-054 (Port 5054) ===');
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
    console.log('Capturing 01_weather_nowcasting_dashboard.png...');
    await page.goto('http://127.0.0.1:5054/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_weather_nowcasting_dashboard.png') });

    // 2. BiGRU Temporal Attention HUD
    console.log('Capturing 02_bigru_temporal_attention_hud.png...');
    await page.evaluate(() => {
        const el = document.getElementById('radar-vis-box');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_bigru_temporal_attention_hud.png') });

    // 3. Coastal Radar Station Nominal Nowcast
    console.log('Capturing 03_coastal_radar_station_nominal.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('station-select').value = 'Coastal Maritime Radar Station 01';
        document.getElementById('cond-select').value = 'nominal';
        document.getElementById('lead-select').value = '3';
        document.getElementById('btn-nowcast').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_coastal_radar_station_nominal.png') });

    // 4. Plains Supercell Severe Thunderstorm Warning
    console.log('Capturing 04_plains_supercell_severe_storm.png...');
    await page.evaluate(async () => {
        document.getElementById('station-select').value = 'Plains Supercell Radar Station 02';
        document.getElementById('cond-select').value = 'severe_storm';
        document.getElementById('lead-select').value = '2';
        document.getElementById('btn-nowcast').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_plains_supercell_severe_storm.png') });

    // 5. Mountain Alpine Gale Wind Warning
    console.log('Capturing 05_mountain_alpine_gale_wind.png...');
    await page.evaluate(async () => {
        document.getElementById('station-select').value = 'Mountain Alpine Pass Radar Station 03';
        document.getElementById('cond-select').value = 'gale';
        document.getElementById('lead-select').value = '1';
        document.getElementById('btn-nowcast').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_mountain_alpine_gale_wind.png') });

    // 6. Urban Convective Basin Heavy Rainfall Alert
    console.log('Capturing 06_urban_heat_basin_convective.png...');
    await page.evaluate(async () => {
        document.getElementById('station-select').value = 'Urban Convective Basin Radar Station 04';
        document.getElementById('cond-select').value = 'heavy_rain';
        document.getElementById('lead-select').value = '3';
        document.getElementById('btn-nowcast').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_urban_heat_basin_convective.png') });

    // 7. Meteorological Nowcast Records Table
    console.log('Capturing 07_meteorological_nowcast_registry.png...');
    await page.evaluate(() => {
        const el = document.getElementById('records-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_meteorological_nowcast_registry.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('audit-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully for PROJECT-054! ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
