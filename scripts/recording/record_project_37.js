import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_37_traffic_violation/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-037 Video Recording Pipeline ===');
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
    // Phase 1: [00:00 - 00:30] Central Traffic Command Dashboard (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Central Traffic Command Dashboard & Port 5037 Status');
    await page.goto('http://127.0.0.1:5037/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Subtle scroll to inspect KPI cards
    await page.evaluate(() => window.scrollTo({ top: 40, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] 4K CCTV Intersection Canvas & Corridor Switching (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: 4K CCTV Intersection Canvas & Multi-Corridor Switching');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectIntersection === 'function') {
            await window.selectIntersection('INT-02');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Focus on CCTV canvas
    await page.evaluate(() => {
        const el = document.querySelector('.cctv-viewport');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Real-Time Speeding Radar Inference (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Real-Time Speeding Radar Inference & Bounding Boxes');
    await page.evaluate(async () => {
        if (typeof window.runViolationAnalysis === 'function') {
            await window.runViolationAnalysis('speeding');
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Pan to detected vehicle cards
    await page.evaluate(() => {
        const el = document.getElementById('detectedGrid');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Red Light Signal Jump & Stop Line Intrusion (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Red Light Signal Jump & Stop Line Intrusion');
    await page.evaluate(async () => {
        if (typeof window.runViolationAnalysis === 'function') {
            await window.runViolationAnalysis('red_light');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Focus on CCTV view with red light bounding box
    await page.evaluate(() => {
        const el = document.querySelector('.cctv-viewport');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Two-Wheeler Safety & Helmet Violation (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Two-Wheeler Safety & Helmet Violation Enforcement');
    await page.evaluate(async () => {
        if (typeof window.runViolationAnalysis === 'function') {
            await window.runViolationAnalysis('no_helmet');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Continuous CCTV stream simulation
    await page.evaluate(async () => {
        if (typeof window.toggleCctvStream === 'function') {
            window.toggleCctvStream();
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Stop stream
    await page.evaluate(() => {
        if (typeof window.toggleCctvStream === 'function' && window.isStreaming) {
            window.toggleCctvStream();
        }
    });

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Automated MVA E-Challan Feed & Cryptographic Ledger (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Automated MVA E-Challan Feed & Cryptographic Audit Ledger');
    await page.evaluate(() => {
        const el = document.getElementById('challanList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Scroll down to cryptographic audit ledger table
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
