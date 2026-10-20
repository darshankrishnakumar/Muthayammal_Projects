import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_47_classroom_engagement_analysis/docs/screenshots';

async function captureScreenshots() {
    console.log('=== Starting Screenshot Capture for PROJECT-047 ===');
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1280,800'
        ]
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    page.on('dialog', async d => { await d.dismiss(); });

    // 1. Full Dashboard Overview
    console.log('Capturing 01_classroom_dashboard.png...');
    await page.goto('http://127.0.0.1:5047/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_classroom_dashboard.png') });

    // 2. 3D Gaze & Pose HUD
    console.log('Capturing 02_3d_gaze_pose_hud.png...');
    await page.evaluate(() => {
        const el = document.getElementById('hud-action-pill');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_3d_gaze_pose_hud.png') });

    // 3. High Focus Lecture (CS-301)
    console.log('Capturing 03_high_focus_consensus_lecture.png...');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-preset').value = 'cs301_high';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-eval').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '03_high_focus_consensus_lecture.png') });

    // 4. MATH-210 Attention Slump (Interactive Poll)
    console.log('Capturing 04_math210_complex_attention_slump.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'math210_slump';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-eval').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_math210_complex_attention_slump.png') });

    // 5. AI-405 Cognitive Fatigue Alert (Refresher Break)
    console.log('Capturing 05_ai405_deep_learning_fatigue.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'ai405_fatigue';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-eval').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_ai405_deep_learning_fatigue.png') });

    // 6. BIO-108 Active Interactive Q&A
    console.log('Capturing 06_bio108_active_interactive_qa.png...');
    await page.evaluate(async () => {
        document.getElementById('sel-preset').value = 'bio108_active';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-eval').click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_bio108_active_interactive_qa.png') });

    // 7. Active Monitored Lecture Sessions Registry
    console.log('Capturing 07_active_lecture_sessions_registry.png...');
    await page.evaluate(() => {
        const el = document.getElementById('sessions-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '07_active_lecture_sessions_registry.png') });

    // 8. Cryptographic Audit Ledger
    console.log('Capturing 08_cryptographic_audit_ledger.png...');
    await page.evaluate(() => {
        const el = document.getElementById('audit-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '08_cryptographic_audit_ledger.png') });

    await browser.close();
    console.log('=== All 8 screenshots captured successfully for PROJECT-047 ===');
}

captureScreenshots().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
