import puppeteer from 'puppeteer-core';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_05_career_guidance/docs/screenshots';

async function run() {
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('http://127.0.0.1:5005', { waitUntil: 'networkidle0' });

    console.log('Capturing 01_landing_student_assessment.png...');
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '01_landing_student_assessment.png') });

    console.log('Capturing 02_fullstack_developer_recommendation.png...');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const devBtn = btns.find(b => b.textContent.includes('Full-Stack'));
        if (devBtn) devBtn.click();
    });
    await new Promise(r => setTimeout(r, 1200));
    // Click submit evaluation
    await page.evaluate(() => {
        const submitBtn = document.querySelector('button[type="submit"]') || Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Compute') || b.textContent.includes('Predict') || b.textContent.includes('Evaluate'));
        if (submitBtn) submitBtn.click();
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '02_fullstack_developer_recommendation.png') });

    console.log('Capturing 03_cybersecurity_network_recommendation.png...');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const secBtn = btns.find(b => b.textContent.includes('Cybersecurity'));
        if (secBtn) secBtn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.evaluate(() => {
        const submitBtn = document.querySelector('button[type="submit"]') || Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Compute') || b.textContent.includes('Predict') || b.textContent.includes('Evaluate'));
        if (submitBtn) submitBtn.click();
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '03_cybersecurity_network_recommendation.png') });

    console.log('Capturing 04_database_architect_recommendation.png...');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const dbBtn = btns.find(b => b.textContent.includes('Database'));
        if (dbBtn) dbBtn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.evaluate(() => {
        const submitBtn = document.querySelector('button[type="submit"]') || Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Compute') || b.textContent.includes('Predict') || b.textContent.includes('Evaluate'));
        if (submitBtn) submitBtn.click();
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '04_database_architect_recommendation.png') });

    console.log('Capturing 05_alternative_career_pathways.png...');
    await page.evaluate(() => {
        window.scrollBy(0, 550);
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '05_alternative_career_pathways.png') });

    console.log('Capturing 06_sqlite_assessment_history.png...');
    await page.evaluate(() => {
        window.scrollBy(0, 650);
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '06_sqlite_assessment_history.png') });

    await browser.close();
    console.log('All Project 05 screenshots captured successfully.');
}

run().catch(console.error);
