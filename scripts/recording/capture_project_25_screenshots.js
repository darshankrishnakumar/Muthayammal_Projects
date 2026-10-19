import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_25_speech_emotion/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-025 ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('http://127.0.0.1:5025', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));

    // 1. Full Cockpit Overview & Metric Strip
    console.log('Capturing 01_ser_cockpit_overview.png...');
    await page.screenshot({ path: path.join(outDir, '01_ser_cockpit_overview.png') });

    // 2. Spectrogram Wave Visualizer Zoom
    console.log('Capturing 02_spectrogram_wave_visualizer.png...');
    await page.evaluate(() => {
        window.scrollTo({ top: 100, behavior: 'smooth' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_spectrogram_wave_visualizer.png') });

    // 3. Happy / Joy Classification Scenario
    console.log('Capturing 03_joy_happy_classification.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.setScenario === 'function') {
            await window.setScenario('happy', 'English');
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_joy_happy_classification.png') });

    // 4. Angry Escalation Scenario
    console.log('Capturing 04_angry_escalation_detection.png...');
    await page.evaluate(async () => {
        if (typeof window.setScenario === 'function') {
            await window.setScenario('angry', 'German');
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_angry_escalation_detection.png') });

    // 5. Fear / Anxiety Scenario
    console.log('Capturing 05_fear_anxiety_telemedicine.png...');
    await page.evaluate(async () => {
        if (typeof window.setScenario === 'function') {
            await window.setScenario('fear', 'Hindi');
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_fear_anxiety_telemedicine.png') });

    // 6. Emotion Probability Radar Chart Zoom
    console.log('Capturing 06_emotion_probability_radar.png...');
    await page.evaluate(() => {
        const radar = document.getElementById('emotionRadar');
        if (radar) radar.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '06_emotion_probability_radar.png') });

    // 7. 13 MFCC Coefficients Spectral Bar Chart
    console.log('Capturing 07_13_mfcc_coefficients_spectral.png...');
    await page.evaluate(() => {
        const mfcc = document.getElementById('mfccChart');
        if (mfcc) mfcc.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_13_mfcc_coefficients_spectral.png') });

    // 8. Acoustic Classification History Log
    console.log('Capturing 08_sqlite_acoustic_history_ledger.png...');
    await page.evaluate(() => {
        const history = document.getElementById('historyList');
        if (history) history.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '08_sqlite_acoustic_history_ledger.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Successfully Captured for PROJECT-025 ===');
}

run().catch(err => {
    console.error('Error capturing screenshots:', err);
    process.exit(1);
});
