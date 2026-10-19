const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function captureScreenshots() {
  const screenshotDir = path.resolve(__dirname, '../../project_34_road_damage/docs/screenshots');
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

  console.log('Navigating to http://127.0.0.1:5034/...');
  await page.goto('http://127.0.0.1:5034/', { waitUntil: 'networkidle0' });
  await sleep(1500);

  // 1. Dashboard Survey Overview
  console.log('Capturing 01_dashboard_survey_overview.png...');
  await page.screenshot({ path: path.join(screenshotDir, '01_dashboard_survey_overview.png') });

  // 2. YOLO Bounding Box Canvas
  console.log('Capturing 02_yolo_bounding_box_canvas.png...');
  await page.evaluate(() => {
    const el = document.getElementById('roadCanvas');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '02_yolo_bounding_box_canvas.png') });

  // 3. Sector Corridor Selection
  console.log('Selecting Urban Arterial Road 12...');
  await page.evaluate(() => {
    window.scrollTo({ top: 0, behavior: 'instant' });
    window.selectSector('SEC-URBAN-02');
  });
  await sleep(1200);
  console.log('Capturing 03_sector_corridor_selection.png...');
  await page.screenshot({ path: path.join(screenshotDir, '03_sector_corridor_selection.png') });

  // 4. PCI Condition Gauge Rating
  console.log('Capturing 04_pci_condition_gauge_rating.png...');
  await page.evaluate(() => {
    const el = document.querySelector('.hero-pci');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '04_pci_condition_gauge_rating.png') });

  // 5. Defect Distribution Donut Chart
  console.log('Capturing 05_defect_distribution_donut.png...');
  await page.evaluate(() => {
    const el = document.getElementById('defectChart');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '05_defect_distribution_donut.png') });

  // 6. Damaged Area Bar Chart
  console.log('Capturing 06_damaged_area_bar_chart.png...');
  await page.evaluate(() => {
    const el = document.getElementById('areaChart');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '06_damaged_area_bar_chart.png') });

  // 7. Severe Damage Simulation
  console.log('Triggering severe road damage scenario...');
  await page.evaluate(async () => {
    window.selectSector('SEC-IND-03');
    await new Promise(r => setTimeout(r, 600));
    await window.runInspection('severe');
  });
  await sleep(1500);
  console.log('Capturing 07_severe_damage_simulation.png...');
  await page.screenshot({ path: path.join(screenshotDir, '07_severe_damage_simulation.png') });

  // 8. Municipal Work Orders & Audit Trail
  console.log('Capturing 08_municipal_work_orders_audit.png...');
  await page.evaluate(() => {
    const el = document.getElementById('workOrdersList');
    if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
  });
  await sleep(800);
  await page.screenshot({ path: path.join(screenshotDir, '08_municipal_work_orders_audit.png') });

  await browser.close();
  console.log('All 8 Project 34 screenshots captured successfully!');
}

captureScreenshots().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
