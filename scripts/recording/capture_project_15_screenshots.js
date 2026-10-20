import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_15_heart_disease_prediction/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-015 ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Landing Assessment Form
    console.log('Capturing 01_landing_assessment_form.png...');
    await page.goto('http://127.0.0.1:5015/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_landing_assessment_form.png') });

    // 2. Clinical Parameters Input
    console.log('Capturing 02_clinical_parameters_input.png...');
    await page.evaluate(() => {
        const form = document.getElementById('predictionForm');
        if (form) form.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '02_clinical_parameters_input.png') });

    // 3. High-Risk Prediction Alert
    console.log('Simulating High-Risk Patient and capturing 03_high_risk_prediction_alert.png...');
    await page.evaluate(() => {
        const setVal = (name, val) => {
            const el = document.querySelector(`[name="${name}"]`);
            if (el) {
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        };
        setVal('Age', 64);
        setVal('Sex', 1);
        setVal('ChestPainType', 3); // Asymptomatic
        setVal('RestingBP', 160);
        setVal('Cholesterol', 290);
        setVal('FastingBS', 1);
        setVal('RestingECG', 2);
        setVal('MaxHR', 105);
        setVal('ExerciseAngina', 1);
        setVal('Oldpeak', 3.2);
        setVal('ST_Slope', 2);
    });
    await new Promise(r => setTimeout(r, 600));
    await page.evaluate(() => {
        const submitBtn = document.querySelector('button.submit-btn');
        if (submitBtn) submitBtn.click();
    });
    await new Promise(r => setTimeout(r, 2000));
    await page.evaluate(() => {
        const resCard = document.querySelector('.result-card');
        if (resCard) resCard.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '03_high_risk_prediction_alert.png') });

    // 4. Vitals Comparison Chart
    console.log('Capturing 04_vitals_comparison_chart.png...');
    await page.evaluate(() => {
        const dash = document.getElementById('dashboard');
        if (dash) dash.scrollIntoView({ behavior: 'instant', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '04_vitals_comparison_chart.png') });

    // 5. Cardiovascular Radar Profile
    console.log('Capturing 05_cardiovascular_radar_profile.png...');
    await page.evaluate(() => {
        const radarCard = document.querySelector('.secondary-card');
        if (radarCard) radarCard.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '05_cardiovascular_radar_profile.png') });

    // 6. Risk Distribution Pie & Trend
    console.log('Capturing 06_risk_distribution_pie_trend.png...');
    await page.evaluate(() => {
        const pieCard = document.querySelectorAll('.dashboard-card');
        if (pieCard.length > 2) {
            pieCard[2].scrollIntoView({ behavior: 'instant', block: 'center' });
        } else {
            window.scrollTo(0, document.body.scrollHeight * 0.7);
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '06_risk_distribution_pie_trend.png') });

    // 7. Low-Risk Clearance and BMI
    console.log('Simulating Low-Risk Patient & BMI and capturing 07_low_risk_clearance_and_bmi.png...');
    await page.evaluate(() => {
        const setVal = (name, val) => {
            const el = document.querySelector(`[name="${name}"]`);
            if (el) {
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        };
        setVal('Age', 32);
        setVal('Sex', 0);
        setVal('ChestPainType', 1);
        setVal('RestingBP', 115);
        setVal('Cholesterol', 175);
        setVal('FastingBS', 0);
        setVal('RestingECG', 0);
        setVal('MaxHR', 178);
        setVal('ExerciseAngina', 0);
        setVal('Oldpeak', 0.0);
        setVal('ST_Slope', 0);
    });
    await new Promise(r => setTimeout(r, 600));
    await page.evaluate(() => {
        const submitBtn = document.querySelector('button.submit-btn');
        if (submitBtn) submitBtn.click();
    });
    await new Promise(r => setTimeout(r, 2000));
    await page.evaluate(() => {
        const resCard = document.querySelector('.result-card');
        if (resCard) resCard.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '07_low_risk_clearance_and_bmi.png') });

    await browser.close();
    console.log('=== All 7 Screenshots Captured Successfully for PROJECT-015! ===');
}

run().catch(err => {
    console.error('Error during capture:', err);
    process.exit(1);
});
