/**
 * Puppeteer script to capture 8 high-resolution screenshots of PROJECT-023 UI.
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

  console.log("Navigating to http://127.0.0.1:5023...");
  await page.goto('http://127.0.0.1:5023', { waitUntil: 'networkidle0', timeout: 30000 });
  await sleep(2000);

  // 1. Dashboard Overview
  console.log("Capturing 01_dashboard_overview.png...");
  await page.screenshot({
    path: path.join(SCREENSHOTS_DIR, '01_dashboard_overview.png'),
    fullPage: false
  });

  // 2. Transcript Input Interface Focused
  console.log("Capturing 02_transcript_input_interface.png...");
  const inputEl = await page.$('.panel');
  if (inputEl) {
    await inputEl.screenshot({
      path: path.join(SCREENSHOTS_DIR, '02_transcript_input_interface.png')
    });
  }

  // 3. Trigger Summarization (Sprint preset)
  console.log("Triggering Sprint preset summarization...");
  await page.evaluate(() => {
    setPreset('sprint');
  });
  await sleep(2500);

  // 3. Executive Summary Panel
  console.log("Capturing 03_executive_summary_panel.png...");
  const execCard = await page.$('.exec-box');
  if (execCard) {
    await execCard.screenshot({
      path: path.join(SCREENSHOTS_DIR, '03_executive_summary_panel.png')
    });
  }

  // 4. Action Items Extraction
  console.log("Capturing 04_action_items_extraction.png...");
  const taskBox = await page.$('#resActionList');
  if (taskBox) {
    const parentBox = await page.evaluateHandle(el => el.closest('.action-box') || el, taskBox);
    await parentBox.asElement().screenshot({
      path: path.join(SCREENSHOTS_DIR, '04_action_items_extraction.png')
    });
  }

  // 5. Decisions Logged Panel
  console.log("Capturing 05_decisions_logged_panel.png...");
  const decBox = await page.$('#resDecisionList');
  if (decBox) {
    const parentDec = await page.evaluateHandle(el => el.closest('.action-box') || el, decBox);
    await parentDec.asElement().screenshot({
      path: path.join(SCREENSHOTS_DIR, '05_decisions_logged_panel.png')
    });
  }

  // 6. Speaker Analytics Donut Chart
  console.log("Capturing 06_speaker_analytics_donut.png...");
  const spkChart = await page.$('#speakerChart');
  if (spkChart) {
    const parentChart = await page.evaluateHandle(el => el.closest('.chart-box') || el, spkChart);
    await parentChart.asElement().screenshot({
      path: path.join(SCREENSHOTS_DIR, '06_speaker_analytics_donut.png')
    });
  }

  // 7. Meeting Radar Profile
  console.log("Capturing 07_meeting_radar_profile.png...");
  const radarChart = await page.$('#metricsRadar');
  if (radarChart) {
    const parentRadar = await page.evaluateHandle(el => el.closest('.chart-box') || el, radarChart);
    await parentRadar.asElement().screenshot({
      path: path.join(SCREENSHOTS_DIR, '07_meeting_radar_profile.png')
    });
  }

  // 8. Meeting Archive Ledger
  console.log("Capturing 08_meeting_archive_ledger.png...");
  await page.evaluate(() => {
    window.scrollTo(0, document.body.scrollHeight);
  });
  await sleep(1000);
  const ledgerPanel = await page.$('.ledger-panel');
  if (ledgerPanel) {
    await ledgerPanel.screenshot({
      path: path.join(SCREENSHOTS_DIR, '08_meeting_archive_ledger.png')
    });
  } else {
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, '08_meeting_archive_ledger.png'),
      clip: { x: 0, y: 400, width: 1440, height: 560 }
    });
  }

  await browser.close();
  console.log("All 8 screenshots successfully captured into " + SCREENSHOTS_DIR);
})();
