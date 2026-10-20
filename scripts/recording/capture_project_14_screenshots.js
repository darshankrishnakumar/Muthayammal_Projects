import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_14_fake_news_detection/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-014 ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Landing Hero
    console.log('Capturing 01_landing_hero.png...');
    await page.goto('http://127.0.0.1:5014/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_landing_hero.png') });

    // 2. Prediction Console (Clean)
    console.log('Capturing 02_prediction_console.png...');
    await page.goto('http://127.0.0.1:5014/predict', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '02_prediction_console.png') });

    // 3. Sensational Fake Detection
    console.log('Capturing 03_sensational_fake_detection.png...');
    await page.goto('http://127.0.0.1:5014/predict?news=Secret+government+plan+revealed+to+control+weather+with+cell+towers', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1500));
    await page.evaluate(() => {
        const el = document.getElementById('resultsDashboard');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '03_sensational_fake_detection.png') });

    // 4. Feature Attribution & XAI
    console.log('Capturing 04_feature_attribution_xai.png...');
    await page.evaluate(() => {
        const headings = Array.from(document.querySelectorAll('h3'));
        const attrHeading = headings.find(h => h.textContent.includes('Explainable Feature Attribution'));
        if (attrHeading) {
            attrHeading.scrollIntoView({ behavior: 'instant', block: 'start' });
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '04_feature_attribution_xai.png') });

    // 5. Intuitive Indications Radar
    console.log('Capturing 05_intuitive_indications_radar.png...');
    await page.evaluate(() => {
        const headings = Array.from(document.querySelectorAll('h3'));
        const radarHeading = headings.find(h => h.textContent.includes('Intuitive Indications'));
        if (radarHeading) {
            radarHeading.scrollIntoView({ behavior: 'instant', block: 'start' });
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '05_intuitive_indications_radar.png') });

    // 6. Pure Language Stylometry
    console.log('Capturing 06_pure_language_stylometry.png...');
    await page.goto('http://127.0.0.1:5014/predict?news=Wells+Fargo+Chief+Abruptly+Steps+Down+-+The+New+York+Times&pure_language_mode=on', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1500));
    await page.evaluate(() => {
        const el = document.getElementById('resultsDashboard');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '06_pure_language_stylometry.png') });

    // 7. Benchmarks and Verification History
    console.log('Capturing 07_benchmarks_and_history.png...');
    await page.evaluate(() => {
        const table = document.querySelector('table');
        if (table) {
            table.scrollIntoView({ behavior: 'instant', block: 'center' });
        } else {
            window.scrollTo(0, document.body.scrollHeight * 0.85);
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_benchmarks_and_history.png') });

    await browser.close();
    console.log('=== All 7 Screenshots Captured Successfully for PROJECT-014! ===');
}

run().catch(err => {
    console.error('Error during capture:', err);
    process.exit(1);
});
