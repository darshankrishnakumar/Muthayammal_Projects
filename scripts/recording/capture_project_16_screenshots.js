const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function capture() {
  const outputDir = path.resolve(__dirname, '../../project_16_medical_sensor_disease_prediction/docs/screenshots');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800, deviceScaleFactor: 2 });

  const routes = [
    { name: '01_dashboard_overview.png', path: '/' },
    { name: '02_ecg_analysis_upload.png', path: '/ecg' },
    { name: '03_cnn_prediction_results.png', path: '/predictions' },
    { name: '04_vitals_monitoring.png', path: '/monitoring' },
    { name: '05_clinical_recommendations.png', path: '/recommendations' },
    { name: '06_diagnostic_reports.png', path: '/reports' },
    { name: '07_model_architecture_forensics.png', path: '/history' }
  ];

  for (const r of routes) {
    const url = `http://localhost:5173${r.path}`;
    console.log(`Navigating to ${url}...`);
    try {
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 15000 });
      await new Promise(res => setTimeout(res, 1200));
      const targetPath = path.join(outputDir, r.name);
      await page.screenshot({ path: targetPath, fullPage: false });
      console.log(`Captured ${r.name}`);
    } catch (e) {
      console.error(`Error capturing ${r.name}: ${e.message}`);
    }
  }

  await browser.close();
  console.log('All screenshots captured successfully!');
}

capture().catch(err => {
  console.error(err);
  process.exit(1);
});
