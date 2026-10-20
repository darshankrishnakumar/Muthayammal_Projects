import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_21_credit_card_fraud/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-021 Video Recording Pipeline ===');
    console.log(`Output: ${outputVideo}`);

    const outDir = path.dirname(outputVideo);
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
    }

    const ffmpeg = spawn(ffmpegPath, [
        '-y',
        '-f', 'image2pipe',
        '-vcodec', 'png',
        '-framerate', '4',
        '-i', '-',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '22',
        '-pix_fmt', 'yuv420p',
        '-r', '24',
        outputVideo
    ]);

    ffmpeg.stderr.on('data', (data) => {
        const msg = data.toString();
        if (msg.includes('frame=') || msg.includes('Error')) {
            process.stdout.write(`FFmpeg: ${msg.trim().split('\n').pop()}\r`);
        }
    });

    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    let frameCount = 0;

    async function streamFrames(count) {
        for (let i = 0; i < count; i++) {
            const buf = await page.screenshot({ type: 'png', omitBackground: false });
            if (ffmpeg.stdin.writable) {
                ffmpeg.stdin.write(buf);
            }
            frameCount++;
            await new Promise(r => setTimeout(r, 60));
        }
    }

    // Phase 1: [00:00 - 00:30] System Overview & Real-Time Telematics Stream (120 frames)
    console.log('\n[00:00 - 00:30] Phase 1: System Overview & Real-Time Telematics Stream');
    await page.goto('http://127.0.0.1:5021/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Fetch stream next items
    await page.evaluate(() => {
        if (typeof fetchStreamNext === 'function') fetchStreamNext();
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Phase 2: [00:30 - 01:05] Critical Fraud Interdiction & Instant Sanction (140 frames)
    console.log('\n[00:30 - 01:05] Phase 2: Critical Fraud Interdiction & Instant Sanction');
    await page.evaluate(() => {
        if (typeof injectInstantFraud === 'function') injectInstantFraud();
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(70);

    // Scroll to see full details of the alert
    await page.evaluate(() => window.scrollTo(0, 150));
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(70);

    // Phase 3: [01:05 - 01:35] Forensic Inspector & SHAP Explainability (120 frames)
    console.log('\n[01:05 - 01:35] Phase 3: Forensic Inspector & SHAP Explainability');
    await page.evaluate(() => {
        window.scrollTo(0, 0);
        const btns = document.querySelectorAll('.tab-btn');
        if (btns[1]) switchTab(1, btns[1]);
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(40);

    // Load preset fraud and evaluate
    await page.evaluate(() => {
        if (typeof loadPreset === 'function') loadPreset('fraud1');
        if (typeof runInspectorEvaluation === 'function') runInspectorEvaluation();
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(80);

    // Phase 4: [01:35 - 02:05] Model Benchmarks & Threshold Studio (120 frames)
    console.log('\n[01:35 - 02:05] Phase 4: Model Benchmarks & Threshold Studio');
    await page.evaluate(() => {
        window.scrollTo(0, 0);
        const btns = document.querySelectorAll('.tab-btn');
        if (btns[2]) switchTab(2, btns[2]);
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Tune threshold slider
    await page.evaluate(() => {
        const slider = document.getElementById('decisionThreshold');
        if (slider) {
            slider.value = '0.65';
            if (typeof onThresholdChange === 'function') onThresholdChange(0.65);
        }
        window.scrollTo(0, 300);
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Phase 5: [02:05 - 02:35] Batch Evaluation & Card Sanctions (120 frames)
    console.log('\n[02:05 - 02:35] Phase 5: Batch Evaluation & Card Sanctions');
    await page.evaluate(() => {
        window.scrollTo(0, 0);
        const btns = document.querySelectorAll('.tab-btn');
        if (btns[3]) switchTab(3, btns[3]);
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(40);

    // Run batch simulation
    await page.evaluate(() => {
        if (typeof runBatchSimulation === 'function') runBatchSimulation();
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(40);

    // Scroll to blocked cards table
    await page.evaluate(() => {
        const el = document.getElementById('blockedCardsTableBody');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(40);

    // Phase 6: [02:35 - 03:00] Relational SQLite Persistence & Forensic Audit Dossier (100 frames)
    console.log('\n[02:35 - 03:00] Phase 6: Relational SQLite Persistence & Forensic Audit Dossier');
    await page.evaluate(() => {
        window.scrollTo(0, 0);
        const btns = document.querySelectorAll('.tab-btn');
        if (btns[0]) switchTab(0, btns[0]);
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(50);

    // Scroll down to transaction ledger
    await page.evaluate(() => window.scrollTo(0, 400));
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(50);

    console.log(`\nFlushing FFmpeg stream... (total frames captured: ${frameCount})`);
    ffmpeg.stdin.end();

    await new Promise((resolve, reject) => {
        ffmpeg.on('close', (code) => {
            if (code === 0) {
                console.log(`\nVideo recording completed successfully: ${outputVideo}`);
                resolve();
            } else {
                reject(new Error(`FFmpeg exited with code ${code}`));
            }
        });
    });

    await browser.close();
    console.log('=== PROJECT-021 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
