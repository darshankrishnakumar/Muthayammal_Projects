import puppeteer from 'puppeteer-core';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_06_child_gait_prediction/docs/screenshots';

async function run() {
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('http://127.0.0.1:5006', { waitUntil: 'networkidle0' });

    console.log('Capturing 01_home_dashboard.png...');
    await page.evaluate(() => {
        window.navigate('home');
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '01_home_dashboard.png') });

    console.log('Capturing 02_gait_assessment_input.png...');
    await page.evaluate(() => {
        window.navigate('predict');
        window.loadSamplePreset('diplegic');
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_gait_assessment_input.png') });

    console.log('Capturing 03_diplegic_prediction_result.png...');
    await page.evaluate(() => {
        const form = document.getElementById('gait-form');
        if (form) form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '03_diplegic_prediction_result.png') });

    console.log('Capturing 04_hemiplegic_prediction_result.png...');
    await page.evaluate(() => {
        window.resetForm();
        window.loadSamplePreset('hemiplegic');
        const form = document.getElementById('gait-form');
        if (form) form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '04_hemiplegic_prediction_result.png') });

    console.log('Capturing 05_child_longitudinal_tracking.png...');
    await page.evaluate(() => {
        window.navigate('history');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_child_longitudinal_tracking.png') });

    console.log('Capturing 06_records_audit_history.png...');
    await page.evaluate(() => {
        window.scrollBy({ top: 450, behavior: 'smooth' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '06_records_audit_history.png') });

    console.log('Capturing 07_clinical_recommendations_guide.png...');
    await page.evaluate(() => {
        window.navigate('recommendations');
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_clinical_recommendations_guide.png') });

    await browser.close();
    console.log('All Project 06 screenshots captured successfully.');
}

run().catch(console.error);
