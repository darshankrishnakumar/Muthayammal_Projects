import puppeteer from 'puppeteer-core';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_03_apple_disease_detection/docs/screenshots';

async function run() {
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('http://127.0.0.1:5003', { waitUntil: 'networkidle0' });

    console.log('Capturing 01_landing_diagnostic_portal.png...');
    await page.screenshot({ path: path.join(outDir, '01_landing_diagnostic_portal.png') });

    console.log('Capturing 02_cedar_apple_rust_diagnosis.png...');
    await page.evaluate(() => {
        const btn = document.querySelector('.preset-btn[data-sample="cedar_rust"]');
        if (btn) btn.click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '02_cedar_apple_rust_diagnosis.png') });

    console.log('Capturing 03_apple_scab_diagnosis.png...');
    await page.evaluate(() => {
        const btn = document.querySelector('.preset-btn[data-sample="scab_leaf"]');
        if (btn) btn.click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_apple_scab_diagnosis.png') });

    console.log('Capturing 04_black_rot_fruit_condition.png...');
    await page.evaluate(() => {
        const btn = document.querySelector('.preset-btn[data-sample="rot_fruit"]');
        if (btn) btn.click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_black_rot_fruit_condition.png') });

    console.log('Capturing 05_cnn_feature_maps_gradcam.png...');
    await page.evaluate(() => {
        const tabBtn = document.querySelector('.tab-btn[data-tab="tab-layers"]');
        if (tabBtn) tabBtn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '05_cnn_feature_maps_gradcam.png') });

    console.log('Capturing 06_treatment_encyclopedia.png...');
    await page.evaluate(() => {
        const tabBtn = document.querySelector('.tab-btn[data-tab="tab-encyclopedia"]');
        if (tabBtn) tabBtn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '06_treatment_encyclopedia.png') });

    await browser.close();
    console.log('All Project 03 screenshots captured successfully.');
}

run().catch(console.error);
