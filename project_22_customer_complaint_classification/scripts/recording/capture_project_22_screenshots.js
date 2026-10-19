/**
 * Puppeteer script to capture 8 high-resolution screenshots of PROJECT-022 UI.
 */
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const SCREENSHOTS_DIR = path.resolve(__dirname, '../../docs/screenshots');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  if (!fs.existsSync(SCREENSHOTS_DIR)) {
    fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 960, deviceScaleFactor: 2 });

  console.log("Navigating to http://127.0.0.1:5022...");
  await page.goto('http://127.0.0.1:5022', { waitUntil: 'networkidle0', timeout: 30000 });
  await sleep(2000);

  // 1. Dashboard Overview
  console.log("Capturing 01_dashboard_overview.png...");
  await page.screenshot({
    path: path.join(SCREENSHOTS_DIR, '01_dashboard_overview.png'),
    fullPage: false
  });

  // 2. Input Interface Focused
  console.log("Capturing 02_nlp_input_interface.png...");
  const inputEl = await page.$('.panel');
  if (inputEl) {
    await inputEl.screenshot({
      path: path.join(SCREENSHOTS_DIR, '02_nlp_input_interface.png')
    });
  }

  // 3. Trigger Classification (Billing Preset)
  console.log("Triggering billing classification...");
  await page.evaluate(() => {
    setPreset('billing');
  });
  await sleep(2500);

  console.log("Capturing 03_realtime_classification.png...");
  const resultBox = await page.$('#resultBox');
  if (resultBox) {
    await resultBox.screenshot({
      path: path.join(SCREENSHOTS_DIR, '03_realtime_classification.png')
    });
  }

  // 4. Probability Distribution Chart
  console.log("Capturing 04_probability_distribution.png...");
  const probPanel = await page.$('#probChart');
  if (probPanel) {
    const parentProb = await page.evaluateHandle(el => el.closest('.panel') || el, probPanel);
    await parentProb.asElement().screenshot({
      path: path.join(SCREENSHOTS_DIR, '04_probability_distribution.png')
    });
  }

  // 5. Category & Priority Charts
  console.log("Capturing 05_category_breakdown_chart.png...");
  const catChart = await page.$('#categoryChart');
  if (catChart) {
    const parentGrid = await page.evaluateHandle(el => el.closest('.analytics-row') || el.closest('.panel') || el, catChart);
    await parentGrid.asElement().screenshot({
      path: path.join(SCREENSHOTS_DIR, '05_category_breakdown_chart.png')
    });
  }

  // 6. Ticket Management Table
  console.log("Capturing 06_ticket_management_table.png...");
  await page.evaluate(() => {
    window.scrollTo(0, document.body.scrollHeight / 2);
  });
  await sleep(1000);
  const tablePanel = await page.$('#ticketTbody');
  if (tablePanel) {
    const parentTable = await page.evaluateHandle(el => el.closest('.panel') || el, tablePanel);
    await parentTable.asElement().screenshot({
      path: path.join(SCREENSHOTS_DIR, '06_ticket_management_table.png')
    });
  }

  // 7. RMA / Defect Classification
  console.log("Triggering RMA classification...");
  await page.evaluate(() => {
    window.scrollTo(0, 0);
    setPreset('rma');
  });
  await sleep(2500);
  console.log("Capturing 07_department_routing_matrix.png...");
  await page.screenshot({
    path: path.join(SCREENSHOTS_DIR, '07_department_routing_matrix.png'),
    fullPage: false
  });

  // 8. Filtered tickets & Export section
  console.log("Filtering critical tickets and capturing 08_audit_trail_and_export.png...");
  await page.evaluate(() => {
    document.getElementById('filterPriority').value = 'critical';
    renderTable();
    window.scrollTo(0, 500);
  });
  await sleep(1000);
  await page.screenshot({
    path: path.join(SCREENSHOTS_DIR, '08_audit_trail_and_export.png'),
    clip: { x: 0, y: 300, width: 1440, height: 660 }
  });

  await browser.close();
  console.log("All 8 screenshots successfully captured into " + SCREENSHOTS_DIR);
})();
