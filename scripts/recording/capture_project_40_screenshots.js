import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_40_fire_smoke_detection/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-040 ===');
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    page.on('dialog', async d => { await d.dismiss(); });

    // 1. Command Dashboard
    console.log('Capturing 01_command_dashboard.png...');
    await page.goto('http://127.0.0.1:5040/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_command_dashboard.png') });

    // 2. CCTV Flame/Smoke Particle Feed
    console.log('Capturing 02_cctv_flame_smoke_particle_feed.png...');
    await page.evaluate(() => {
        const el = document.getElementById('cctvCanvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_cctv_flame_smoke_particle_feed.png') });

    // 3. FFT Flicker Spectrum Analyzer
    console.log('Capturing 03_fft_flicker_spectrum_analyzer.png...');
    await page.evaluate(() => {
        const el = document.getElementById('fftChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_fft_flicker_spectrum_analyzer.png') });

    // 4. Dual Hazard Fire Smoke Incident
    console.log('Capturing 04_dual_hazard_fire_smoke_incident.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectZone === 'function') {
            window.selectZone('Warehouse Sector B Chemical Storage', 'CCTV-CHE-02', 'DUAL_HAZARD');
            await new Promise(r => setTimeout(r, 300));
            await window.triggerIncidentAnalysis();
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_dual_hazard_fire_smoke_incident.png') });

    // 5. Boiler Room Flame Detection
    console.log('Capturing 05_boiler_room_flame_detection.png...');
    await page.evaluate(async () => {
        if (typeof window.selectZone === 'function') {
            window.selectZone('Industrial Plant Boiler Room', 'CCTV-BOI-01', 'FLAME');
            await new Promise(r => setTimeout(r, 300));
            await window.triggerIncidentAnalysis();
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_boiler_room_flame_detection.png') });

    // 6. Server Hall Clean Agent Suppression
    console.log('Capturing 06_server_hall_clean_agent_suppression.png...');
    await page.evaluate(async () => {
        if (typeof window.selectZone === 'function') {
            window.selectZone('Data Center Server Hall 3', 'CCTV-SRV-02', 'SMOKE');
            await new Promise(r => setTimeout(r, 300));
            await window.triggerIncidentAnalysis();
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_server_hall_clean_agent_suppression.png') });

    // 7. Facility Incident History Register
    console.log('Capturing 07_facility_incident_history_register.png...');
    await page.evaluate(() => {
        const el = document.getElementById('incidentsTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_facility_incident_history_register.png') });

    // 8. Cryptographic Audit Ledger Table
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('auditLedgerSection');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('All 8 screenshots successfully captured in:', outDir);
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
