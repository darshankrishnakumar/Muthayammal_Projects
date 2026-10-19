const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function captureScreenshots() {
  const screenshotDir = path.resolve(__dirname, '../../project_30_iot_anomaly/docs/screenshots');
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

  console.log('Navigating to http://127.0.0.1:5030/...');
  await page.goto('http://127.0.0.1:5030/', { waitUntil: 'networkidle0' });
  await sleep(1200);

  // 1. Dashboard Overview
  console.log('Capturing 01_iot_security_dashboard_overview.png...');
  await page.screenshot({ path: path.join(screenshotDir, '01_iot_security_dashboard_overview.png') });

  // 2. Autoencoder Reconstruction Loss Curve
  console.log('Capturing 02_autoencoder_loss_reconstruction_curve.png...');
  await page.screenshot({ path: path.join(screenshotDir, '02_autoencoder_loss_reconstruction_curve.png') });

  // 3. Threat Signature Donut
  console.log('Capturing 03_threat_signature_donut_distribution.png...');
  await page.screenshot({ path: path.join(screenshotDir, '03_threat_signature_donut_distribution.png') });

  // 4. Device Fleet Telemetry Cards
  console.log('Selecting Smart Thermostat and capturing fleet...');
  await page.evaluate(() => window.selectDev('Smart Thermostat'));
  await sleep(1000);
  console.log('Capturing 04_iot_device_fleet_telemetry_cards.png...');
  await page.screenshot({ path: path.join(screenshotDir, '04_iot_device_fleet_telemetry_cards.png') });

  // 5. Mirai Botnet Attack & Quarantine Isolation
  console.log('Triggering attack scenario on Smart IP Camera...');
  await page.evaluate(async () => {
    window.selectDev('Smart IP Camera');
    await window.runInspection('attack');
  });
  await sleep(1200);
  console.log('Capturing 05_mirai_botnet_quarantine_isolation.png...');
  await page.screenshot({ path: path.join(screenshotDir, '05_mirai_botnet_quarantine_isolation.png') });

  // 6. SYN Flood DDoS Mitigation
  console.log('Triggering attack scenario on Edge Wi-Fi Router...');
  await page.evaluate(async () => {
    window.selectDev('Edge Wi-Fi Router');
    await window.runInspection('attack');
  });
  await sleep(1200);
  console.log('Capturing 06_syn_flood_ddos_mitigation.png...');
  await page.screenshot({ path: path.join(screenshotDir, '06_syn_flood_ddos_mitigation.png') });

  // 7. Normal Baseline Traffic Inspection
  console.log('Triggering normal baseline traffic inspection...');
  await page.evaluate(async () => {
    window.selectDev('Smart Lock');
    await window.runInspection('normal');
  });
  await sleep(1200);
  console.log('Capturing 07_normal_baseline_traffic_inspection.png...');
  await page.screenshot({ path: path.join(screenshotDir, '07_normal_baseline_traffic_inspection.png') });

  // 8. Live Firewall Intrusion Feed & History
  console.log('Scrolling down to historical intrusion ledger...');
  await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }));
  await sleep(1000);
  console.log('Capturing 08_firewall_intrusion_ledger_audit.png...');
  await page.screenshot({ path: path.join(screenshotDir, '08_firewall_intrusion_ledger_audit.png') });

  await browser.close();
  console.log('All 8 Project 30 screenshots captured successfully!');
}

captureScreenshots().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
