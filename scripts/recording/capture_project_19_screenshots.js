import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_19_stock_management/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-019 (Port 5019) ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Landing View: Tab 0 (Inventory & POS Sales)
    console.log('Capturing 01_inventory_dashboard_ledger.png...');
    await page.goto('http://127.0.0.1:5019/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_inventory_dashboard_ledger.png') });

    // 2. Tab 1: Barcode & RFID Scanner
    console.log('Capturing 02_hardware_barcode_rfid_terminal.png...');
    await page.evaluate(() => switchTab(1));
    await new Promise(r => setTimeout(r, 800));
    // Trigger a hardware scan to populate the result box
    await page.evaluate(() => triggerHardwareScan());
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_hardware_barcode_rfid_terminal.png') });

    // 3. Tab 2: Wholesaler Orders & Shipments
    console.log('Capturing 03_wholesaler_orders_and_shipments.png...');
    await page.evaluate(() => switchTab(2));
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '03_wholesaler_orders_and_shipments.png') });

    // 4. Tab 3: AI Demand Forecast with Model Benchmarks
    console.log('Capturing 04_ai_demand_forecasting_models.png...');
    await page.evaluate(() => switchTab(3));
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_ai_demand_forecasting_models.png') });

    // 5. Tab 3 Scrolled: ROP & EOQ Optimization Table
    console.log('Capturing 05_reorder_point_eoq_alerts.png...');
    await page.evaluate(() => {
        const el = document.getElementById('ropAlertsBody');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '05_reorder_point_eoq_alerts.png') });

    // 6. Tab 4: Compliance & Management Reports
    console.log('Capturing 06_management_reports_csv_export.png...');
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab(4); });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '06_management_reports_csv_export.png') });

    // 7. Tab 5: Neural Architecture & Feature Importance
    console.log('Capturing 07_neural_architecture_forensics.png...');
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab(5); });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_neural_architecture_forensics.png') });

    // 8. Tab 5 Scrolled: Relational Database Schema Ledger
    console.log('Capturing 08_relational_schema_ledger.png...');
    await page.evaluate(() => window.scrollTo(0, 450));
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '08_relational_schema_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully for PROJECT-019 ===');
}

run().catch(err => {
    console.error('Error capturing screenshots:', err);
    process.exit(1);
});
