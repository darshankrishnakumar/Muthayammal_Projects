import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_36_waste_classification/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-036 Video Recording Pipeline ===');
    console.log(`Target Output: ${outputVideo}`);

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
    page.on('dialog', async d => { await d.dismiss(); });

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

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 1: [00:00 - 00:30] MRF Sorting Command Dashboard & Health (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: MRF Sorting Command Dashboard & Health');
    await page.goto('http://127.0.0.1:5036/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Subtle scroll to inspect KPIs & recovery metrics
    await page.evaluate(() => window.scrollTo({ top: 50, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Optical Conveyor Simulation Canvas & Lines (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Optical Conveyor Simulation Canvas & Lines');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectConveyor === 'function') {
            await window.selectConveyor('CONV-B2');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Pan to conveyor canvas
    await page.evaluate(() => {
        const el = document.querySelector('.conveyor-viewport');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Polymer Classification & Pneumatic Air Jet (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Polymer Classification & Pneumatic Air Jet');
    await page.evaluate(async () => {
        if (typeof window.classifyItem === 'function') {
            await window.classifyItem('plastic_bottle');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Pan to result inspection card & spectroscopic readouts
    await page.evaluate(() => {
        const el = document.getElementById('classificationCard');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Metallic Separation & Eddy Current Diverter (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Metallic Separation & Eddy Current Diverter');
    await page.evaluate(async () => {
        if (typeof window.classifyItem === 'function') {
            await window.classifyItem('aluminum_can');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Focus on actuator bin routing
    await page.evaluate(() => {
        const el = document.querySelector('.bin-grid');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Corrugated Cardboard Recovery & Star Screen (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Corrugated Cardboard Recovery & Star Screen');
    await page.evaluate(async () => {
        if (typeof window.classifyItem === 'function') {
            await window.classifyItem('corrugated_box');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Trigger batch continuous simulation
    await page.evaluate(async () => {
        if (typeof window.simulateConveyorRun === 'function') {
            await window.simulateConveyorRun();
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Commercial Dispatched Batches & Audit Ledger (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Commercial Dispatched Batches & Audit Ledger');
    await page.evaluate(() => {
        const el = document.getElementById('batchesTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Scroll to cryptographic audit ledger
    await page.evaluate(() => {
        const el = document.getElementById('auditTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    console.log(`\nRecording complete! Total frames streamed: ${frameCount} (Target: 720 frames = 180.000s)`);
    await browser.close();

    ffmpeg.stdin.end();

    await new Promise((resolve, reject) => {
        ffmpeg.on('close', (code) => {
            if (code === 0) {
                console.log(`FFmpeg encoding complete! Output saved to: ${outputVideo}`);
                resolve();
            } else {
                reject(new Error(`FFmpeg exited with code ${code}`));
            }
        });
    });
}

record().catch((err) => {
    console.error('Fatal error during recording:', err);
    process.exit(1);
});
