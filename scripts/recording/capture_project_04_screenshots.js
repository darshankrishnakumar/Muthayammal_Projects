import puppeteer from 'puppeteer-core';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_04_car_price_prediction/docs/screenshots';

async function run() {
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('http://127.0.0.1:5004', { waitUntil: 'networkidle0' });

    console.log('Capturing 01_landing_valuation_engine.png...');
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '01_landing_valuation_engine.png') });

    console.log('Capturing 02_toyota_fortuner_valuation.png...');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('.preset-btn'));
        const fortunerBtn = btns.find(b => b.textContent.includes('Fortuner'));
        if (fortunerBtn) fortunerBtn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '02_toyota_fortuner_valuation.png') });

    console.log('Capturing 03_bmw_luxury_sedan_valuation.png...');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('.preset-btn'));
        const bmwBtn = btns.find(b => b.textContent.includes('BMW'));
        if (bmwBtn) bmwBtn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '03_bmw_luxury_sedan_valuation.png') });

    console.log('Capturing 04_model_benchmarks_comparison.png...');
    await page.evaluate(() => {
        window.switchTab('benchmarks');
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '04_model_benchmarks_comparison.png') });

    console.log('Capturing 05_feature_importance_hierarchy.png...');
    await page.evaluate(() => {
        window.switchTab('importance');
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '05_feature_importance_hierarchy.png') });

    console.log('Capturing 06_sqlite_prediction_history.png...');
    await page.evaluate(() => {
        window.switchTab('history');
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '06_sqlite_prediction_history.png') });

    console.log('Capturing 07_dataset_explorer_records.png...');
    await page.evaluate(() => {
        window.switchTab('dataset');
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '07_dataset_explorer_records.png') });

    await browser.close();
    console.log('All Project 04 screenshots captured successfully.');
}

run().catch(console.error);
