import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_28_air_quality_forecast/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function capture() {
    console.log('=== Capturing PROJECT-028 High-Resolution Screenshots ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,900']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });

    // 1. Dashboard Overview (Delhi Default)
    console.log('Capturing 01_aqi_monitoring_dashboard.png...');
    await page.goto('http://127.0.0.1:5028/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_aqi_monitoring_dashboard.png') });

    // 2. Hourly Predicted AQI Line Chart
    console.log('Capturing 02_hourly_forecast_trend_chart.png...');
    await page.evaluate(() => {
        const el = document.getElementById('hourlyChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '02_hourly_forecast_trend_chart.png') });

    // 3. Criteria Air Pollutants Telemetry
    console.log('Capturing 03_criteria_pollutants_telemetry.png...');
    await page.evaluate(() => {
        const el = document.querySelector('.hero-aqi-card');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_criteria_pollutants_telemetry.png') });

    // 4. Mumbai Coastal Forecast
    console.log('Capturing 04_mumbai_coastal_forecast.png...');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.changeCity === 'function') window.changeCity('Mumbai');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_mumbai_coastal_forecast.png') });

    // 5. London Clean Air Baseline
    console.log('Capturing 05_london_clean_air_baseline.png...');
    await page.evaluate(() => {
        if (typeof window.changeCity === 'function') window.changeCity('London');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_london_clean_air_baseline.png') });

    // 6. Tokyo Pristine Air Monitoring
    console.log('Capturing 06_tokyo_pristine_air_monitoring.png...');
    await page.evaluate(() => {
        if (typeof window.changeCity === 'function') window.changeCity('Tokyo');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_tokyo_pristine_air_monitoring.png') });

    // 7. Clinical & Lifestyle Health Advisories
    console.log('Capturing 07_health_advisories_recommendations.png...');
    await page.evaluate(() => {
        if (typeof window.changeCity === 'function') window.changeCity('Delhi');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => {
        const el = document.getElementById('advisoriesList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_health_advisories_recommendations.png') });

    // 8. 7-Day Forecast Trajectory Strip
    console.log('Capturing 08_7day_forecast_trajectory_strip.png...');
    await page.evaluate(() => {
        const el = document.getElementById('forecastStrip');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_7day_forecast_trajectory_strip.png') });

    await browser.close();
    console.log('=== All 8 PROJECT-028 Screenshots captured successfully ===');
}

capture().catch(err => {
    console.error('Capture failed:', err);
    process.exit(1);
});
