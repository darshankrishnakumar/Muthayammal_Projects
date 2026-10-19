import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_18_dress_recommendation_skin_tone/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-018 (Port 5018) ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // 1. Landing View
    console.log('Capturing 01_landing_recommender_studio.png...');
    await page.goto('http://127.0.0.1:5018/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_landing_recommender_studio.png') });

    // 2. Click Preset 1 (Fair Cool Gala)
    console.log('Capturing 02_fair_cool_gala_recommendations.png...');
    await page.click('button[data-preset="p1"]');
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '02_fair_cool_gala_recommendations.png') });

    // 3. Click Preset 2 (Medium Warm Formal)
    console.log('Capturing 03_medium_warm_formal_recommendations.png...');
    await page.click('button[data-preset="p2"]');
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_medium_warm_formal_recommendations.png') });

    // 4. Click Preset 3 (Olive Warm Ethnic)
    console.log('Capturing 04_olive_warm_ethnic_recommendations.png...');
    await page.click('button[data-preset="p3"]');
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_olive_warm_ethnic_recommendations.png') });

    // 5. Scroll down to Outfit Card Forensics
    console.log('Capturing 05_outfit_card_forensics.png...');
    await page.evaluate(() => {
        const el = document.querySelector('.outfit-card');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 600));
    await page.screenshot({ path: path.join(outDir, '05_outfit_card_forensics.png') });

    // 6. Switch to Catalogue Explorer Tab
    console.log('Capturing 06_clothing_catalogue_explorer.png...');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.click('.nav-tab[data-tab="catalogue"]');
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '06_clothing_catalogue_explorer.png') });

    // 7. Switch to Model Benchmarks Tab
    console.log('Capturing 07_model_benchmarks_metrics.png...');
    await page.click('.nav-tab[data-tab="models"]');
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '07_model_benchmarks_metrics.png') });

    // 8. Switch to SQLite History Tab
    console.log('Capturing 08_sqlite_history_audit.png...');
    await page.click('.nav-tab[data-tab="history"]');
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '08_sqlite_history_audit.png') });

    // 9. Switch to Architecture Tab
    console.log('Capturing 09_neural_pipeline_architecture.png...');
    await page.click('.nav-tab[data-tab="architecture"]');
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '09_neural_pipeline_architecture.png') });

    await browser.close();
    console.log('All 9 high-res screenshots captured successfully in:', outDir);
}

run().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
