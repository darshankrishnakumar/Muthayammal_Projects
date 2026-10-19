import puppeteer from 'puppeteer-core';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_07_crop_yield_prediction/docs/screenshots';

async function run() {
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('http://127.0.0.1:5007/#dashboard', { waitUntil: 'networkidle0' });

    console.log('Capturing 01_dashboard_kpis.png...');
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_dashboard_kpis.png') });

    console.log('Capturing 02_predictions_portal.png...');
    await page.evaluate(() => {
        location.hash = 'predictions';
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '02_predictions_portal.png') });

    console.log('Capturing 03_yield_prediction_result.png...');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const predBtn = btns.find(b => b.textContent.includes('Predict Yield'));
        if (predBtn) predBtn.click();
    });
    await new Promise(r => setTimeout(r, 2000));
    await page.screenshot({ path: path.join(outDir, '03_yield_prediction_result.png') });

    console.log('Capturing 04_crop_recommendations.png...');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const recTab = btns.find(b => b.textContent.includes('Crop Recommendation') || b.textContent.includes('Recommendation'));
        if (recTab) recTab.click();
    });
    await new Promise(r => setTimeout(r, 800));
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const recBtn = btns.find(b => b.textContent.includes('Recommend Best Crops'));
        if (recBtn) recBtn.click();
    });
    await new Promise(r => setTimeout(r, 2000));
    await page.screenshot({ path: path.join(outDir, '04_crop_recommendations.png') });

    console.log('Capturing 05_model_benchmarks_regression.png...');
    await page.evaluate(() => {
        window.scrollBy({ top: 400, behavior: 'smooth' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '05_model_benchmarks_regression.png') });

    console.log('Capturing 06_data_exploration_analytics.png...');
    await page.evaluate(() => {
        location.hash = 'exploration';
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '06_data_exploration_analytics.png') });

    console.log('Capturing 07_feature_importance_visuals.png...');
    await page.evaluate(() => {
        location.hash = 'visualizations';
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '07_feature_importance_visuals.png') });

    await browser.close();
    console.log('All Project 07 screenshots captured successfully.');
}

run().catch(console.error);
