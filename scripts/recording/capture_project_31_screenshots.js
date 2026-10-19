const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function captureScreenshots() {
  const screenshotDir = path.resolve(__dirname, '../../project_31_flood_risk/docs/screenshots');
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

  console.log('Navigating to http://127.0.0.1:5031/...');
  await page.goto('http://127.0.0.1:5031/', { waitUntil: 'networkidle0' });
  await sleep(1500);

  // 1. Dashboard Overview
  console.log('Capturing 01_flood_risk_overview.png...');
  await page.screenshot({ path: path.join(screenshotDir, '01_flood_risk_overview.png') });

  // 2. Hydrological Gauges Chart
  console.log('Capturing 02_hydrological_gauges.png...');
  await page.evaluate(() => {
    const el = document.getElementById('gaugeChart');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '02_hydrological_gauges.png') });

  // 3. Inundation Water Contour Simulation
  console.log('Capturing 03_inundation_depth_simulation.png...');
  await page.evaluate(() => {
    const el = document.getElementById('inundationCanvas');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '03_inundation_depth_simulation.png') });

  // 4. Basin Topography Selection (Bay Coastal Lowlands)
  console.log('Selecting Bay Coastal Lowlands...');
  await page.evaluate(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
    window.selectZone('Bay Coastal Lowlands');
  });
  await sleep(1200);
  console.log('Capturing 04_basin_topography_selection.png...');
  await page.screenshot({ path: path.join(screenshotDir, '04_basin_topography_selection.png') });

  // 5. Critical Flood Alert (Simulate Deluge Scenario)
  console.log('Simulating Deluge scenario on Bay Coastal Lowlands...');
  await page.evaluate(async () => {
    await window.simulateEvent('deluge');
  });
  await sleep(1500);
  console.log('Capturing 05_critical_flood_alert.png...');
  await page.screenshot({ path: path.join(screenshotDir, '05_critical_flood_alert.png') });

  // 6. Lead Time Forecasting & Evacuation Protocol
  console.log('Capturing 06_lead_time_forecasting.png...');
  await page.evaluate(() => {
    const el = document.getElementById('leadTimeChart');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '06_lead_time_forecasting.png') });

  // 7. Historical Flood Warning Broadcast Ledger
  console.log('Scrolling down to historical broadcast ledger...');
  await page.evaluate(() => {
    const el = document.getElementById('historyList');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  console.log('Capturing 07_historical_flood_ledger.png...');
  await page.screenshot({ path: path.join(screenshotDir, '07_historical_flood_ledger.png') });

  // 8. Upland Ridge Buffer Normal Hydrological Equilibrium
  console.log('Selecting Upland Ridge Buffer and testing benign state...');
  await page.evaluate(async () => {
    window.scrollTo({ top: 0, behavior: 'instant' });
    window.selectZone('Upland Ridge Buffer');
    await window.simulateEvent('clear');
  });
  await sleep(1200);
  console.log('Capturing 08_neural_network_diagnostics.png...');
  await page.screenshot({ path: path.join(screenshotDir, '08_neural_network_diagnostics.png') });

  await browser.close();
  console.log('All 8 Project 31 screenshots captured successfully!');
}

captureScreenshots().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
