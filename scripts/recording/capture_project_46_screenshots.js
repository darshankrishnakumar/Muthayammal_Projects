import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_46_manufacturing_defect_detection/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-046 ===');
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
    console.log('Capturing 01_industrial_defect_dashboard.png...');
    await page.goto('http://127.0.0.1:5046/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_industrial_defect_dashboard.png') });

    // 2. Optical Laser HUD View
    console.log('Capturing 02_optical_laser_hud_view.png...');
    await page.evaluate(() => {
        const el = document.getElementById('component-graphic');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_optical_laser_hud_view.png') });

    // 3. PCB Board Nominal Scan (PASS)
    console.log('Capturing 03_pcb_board_nominal_scan.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('part-type').value = 'PCB_BOARD';
        document.getElementById('part-type').dispatchEvent(new Event('change'));
        document.getElementById('assembly-line').value = 'Line-1 SMT PCB Assembly';
        document.getElementById('defect-sim').value = 'NONE';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_pcb_board_nominal_scan.png') });

    // 4. Machined Gear Crack Rejection (REJECT)
    console.log('Capturing 04_machined_gear_crack_rejection.png...');
    await page.evaluate(async () => {
        document.getElementById('part-type').value = 'MACHINED_GEAR';
        document.getElementById('part-type').dispatchEvent(new Event('change'));
        document.getElementById('assembly-line').value = 'Line-2 CNC Gear Milling';
        document.getElementById('defect-sim').value = 'CRACK';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_machined_gear_crack_rejection.png') });

    // 5. Metallic Casing Dent Defect
    console.log('Capturing 05_metallic_casing_dent_defect.png...');
    await page.evaluate(async () => {
        document.getElementById('part-type').value = 'METALLIC_CASING';
        document.getElementById('part-type').dispatchEvent(new Event('change'));
        document.getElementById('assembly-line').value = 'Line-3 Casing Foundry';
        document.getElementById('defect-sim').value = 'DENT';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_metallic_casing_dent_defect.png') });

    // 6. Turbine Blade Precision Aerospace Inspection
    console.log('Capturing 06_turbine_blade_aerospace_inspection.png...');
    await page.evaluate(async () => {
        document.getElementById('part-type').value = 'TURBINE_BLADE';
        document.getElementById('part-type').dispatchEvent(new Event('change'));
        document.getElementById('assembly-line').value = 'Line-4 Precision Aerospace';
        document.getElementById('defect-sim').value = 'MISSING_COMPONENT';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_turbine_blade_aerospace_inspection.png') });

    // 7. Calibrated Inspection Templates
    console.log('Capturing 07_calibrated_templates_registry.png...');
    await page.evaluate(() => {
        const el = document.getElementById('templates-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_calibrated_templates_registry.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('audit-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 screenshots captured successfully for PROJECT-046 ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
