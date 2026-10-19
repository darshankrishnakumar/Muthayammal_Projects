const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function captureScreenshots() {
  const screenshotDir = path.resolve(__dirname, '../../project_32_predictive_maintenance/docs/screenshots');
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

  console.log('Navigating to http://127.0.0.1:5032/...');
  await page.goto('http://127.0.0.1:5032/', { waitUntil: 'networkidle0' });
  await sleep(1500);

  // 1. Dashboard Overview
  console.log('Capturing 01_pdm_dashboard_overview.png...');
  await page.screenshot({ path: path.join(screenshotDir, '01_pdm_dashboard_overview.png') });

  // 2. FFT Vibration Spectrum Chart
  console.log('Capturing 02_fft_vibration_spectrum.png...');
  await page.evaluate(() => {
    const el = document.getElementById('fftChart');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '02_fft_vibration_spectrum.png') });

  // 3. Health Radar Diagnostics
  console.log('Capturing 03_health_radar_diagnostics.png...');
  await page.evaluate(() => {
    const el = document.getElementById('healthRadar');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '03_health_radar_diagnostics.png') });

  // 4. Machine Fleet Selection (Gas Turbine Generator D-401)
  console.log('Selecting Gas Turbine Generator D-401...');
  await page.evaluate(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
    window.selectMachine('Gas Turbine Generator D-401');
  });
  await sleep(1200);
  console.log('Capturing 04_machine_fleet_selection.png...');
  await page.screenshot({ path: path.join(screenshotDir, '04_machine_fleet_selection.png') });

  // 5. Bearing Spall Critical Fault Simulation
  console.log('Triggering fault diagnostics scenario on Gas Turbine Generator D-401...');
  await page.evaluate(async () => {
    await window.runDiagnostics('fault');
  });
  await sleep(1500);
  console.log('Capturing 05_bearing_spall_critical_fault.png...');
  await page.screenshot({ path: path.join(screenshotDir, '05_bearing_spall_critical_fault.png') });

  // 6. Remaining Useful Life (RUL) Readout
  console.log('Capturing 06_rul_remaining_useful_life.png...');
  await page.evaluate(() => {
    const el = document.getElementById('heroRul');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '06_rul_remaining_useful_life.png') });

  // 7. Work Order Action Box & Dispatch
  console.log('Capturing 07_work_order_dispatch_action.png...');
  await page.evaluate(() => {
    const el = document.getElementById('woBox');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '07_work_order_dispatch_action.png') });

  // 8. Historical Asset Maintenance Inspection Ledger
  console.log('Scrolling down to historical inspection ledger...');
  await page.evaluate(() => {
    const el = document.getElementById('historyList');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  console.log('Capturing 08_historical_telemetry_ledger.png...');
  await page.screenshot({ path: path.join(screenshotDir, '08_historical_telemetry_ledger.png') });

  await browser.close();
  console.log('All 8 Project 32 screenshots captured successfully!');
}

captureScreenshots().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
