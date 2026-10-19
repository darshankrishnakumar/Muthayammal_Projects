const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function captureScreenshots() {
  const screenshotDir = path.resolve(__dirname, '../../project_33_aircraft_rul/docs/screenshots');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  const sleep = ms => new Promise(r => setTimeout(r, ms));

  console.log('Navigating to http://127.0.0.1:5033/...');
  await page.goto('http://127.0.0.1:5033/', { waitUntil: 'networkidle0' });
  await sleep(1500);

  // 1. Dashboard Fleet Overview
  console.log('Capturing 01_dashboard_fleet_overview.png...');
  await page.screenshot({ path: path.join(screenshotDir, '01_dashboard_fleet_overview.png') });

  // 2. Component Subsystem Selection
  console.log('Selecting High-Pressure Compressor (HPC) Rotor...');
  await page.evaluate(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
    window.selectComponent('High-Pressure Compressor (HPC) Rotor');
  });
  await sleep(1200);
  console.log('Capturing 02_component_subsystem_selection.png...');
  await page.screenshot({ path: path.join(screenshotDir, '02_component_subsystem_selection.png') });

  // 3. C-MAPSS Sensor Telemetry Grid
  console.log('Capturing 03_c_mapss_sensor_telemetry.png...');
  await page.evaluate(() => {
    const el = document.querySelector('.cmapss-grid');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '03_c_mapss_sensor_telemetry.png') });

  // 4. Degradation Decay Curve
  console.log('Capturing 04_degradation_decay_curve.png...');
  await page.evaluate(() => {
    const el = document.getElementById('decayChart');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '04_degradation_decay_curve.png') });

  // 5. Sensor Deviation Metrics
  console.log('Capturing 05_sensor_deviation_metrics.png...');
  await page.evaluate(() => {
    const el = document.getElementById('sensorBarChart');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '05_sensor_deviation_metrics.png') });

  // 6. Critical Wear Simulation (Worn Scenario)
  console.log('Triggering high stress worn scenario on Mainshaft Roller Bearings...');
  await page.evaluate(async () => {
    window.selectComponent('Mainshaft Roller Bearings (#4 Bearing)');
    await new Promise(r => setTimeout(r, 600));
    await window.runPrediction('worn');
  });
  await sleep(1500);
  console.log('Capturing 06_critical_wear_simulation.png...');
  await page.screenshot({ path: path.join(screenshotDir, '06_critical_wear_simulation.png') });

  // 7. Active Maintenance Shop Orders
  console.log('Capturing 07_maintenance_shop_orders.png...');
  await page.evaluate(() => {
    const el = document.getElementById('shopOrdersList');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '07_maintenance_shop_orders.png') });

  // 8. FAA Audit Trail & Historical Ledger
  console.log('Capturing 08_faa_audit_trail_ledger.png...');
  await page.evaluate(() => {
    const el = document.getElementById('historyList');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '08_faa_audit_trail_ledger.png') });

  await browser.close();
  console.log('All 8 Project 33 screenshots captured successfully!');
}

captureScreenshots().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
