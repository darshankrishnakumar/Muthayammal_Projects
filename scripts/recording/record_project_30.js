import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_30_iot_anomaly/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-030 Video Recording Pipeline ===');
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
    // Phase 1: [00:00 - 00:30] System Overview & IoT Fleet Carousel (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: System Overview, Health Telemetry & IoT Fleet Carousel');
    await page.goto('http://127.0.0.1:5030/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Scroll slightly to focus on device fleet cards and telemetry strip
    await page.evaluate(() => window.scrollTo({ top: 50, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Autoencoder Reconstruction Loss Curve (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Autoencoder Reconstruction Loss Curve & Threat Donut');
    await page.evaluate(() => {
        const el = document.getElementById('lossChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Pan down to threat donut chart
    await page.evaluate(() => {
        const el = document.getElementById('threatDonut');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Mirai Botnet Quarantine Isolation (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Critical Threat Detection & Mirai Botnet Quarantine');
    await page.evaluate(async () => {
        window.scrollTo({ top: 120, behavior: 'smooth' });
        if (typeof window.selectDev === 'function') window.selectDev('Smart IP Camera');
        if (typeof window.runInspection === 'function') await window.runInspection('attack');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Scroll to examine quarantine isolation card
    await page.evaluate(() => {
        const el = document.querySelector('.quarantine-box');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Volumetric SYN Flood DDoS Mitigation (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Volumetric SYN Flood DDoS Mitigation');
    await page.evaluate(async () => {
        window.scrollTo({ top: 120, behavior: 'smooth' });
        if (typeof window.selectDev === 'function') window.selectDev('Edge Wi-Fi Router');
        if (typeof window.runInspection === 'function') await window.runInspection('attack');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Inspect telemetry quadrant
    await page.evaluate(() => {
        const el = document.querySelector('.telemetry-grid');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Normal Baseline Traffic Whitelisting (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Normal Baseline Traffic Whitelisting');
    await page.evaluate(async () => {
        window.scrollTo({ top: 120, behavior: 'smooth' });
        if (typeof window.selectDev === 'function') window.selectDev('Smart Lock');
        if (typeof window.runInspection === 'function') await window.runInspection('normal');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Focus on result card with emerald badge
    await page.evaluate(() => {
        const el = document.getElementById('resStatus');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Historical Intrusion Ledger & Conformance (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Historical Intrusion Ledger & Conformance');
    await page.evaluate(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Scroll smoothly to top for closing view
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    console.log(`\nCompleted streaming ${frameCount} frames.`);
    await browser.close();

    ffmpeg.stdin.end();

    await new Promise((resolve, reject) => {
        ffmpeg.on('close', (code) => {
            if (code === 0) {
                console.log(`FFmpeg encoding completed successfully: ${outputVideo}`);
                resolve();
            } else {
                reject(new Error(`FFmpeg exited with code ${code}`));
            }
        });
    });
}

record().catch((err) => {
    console.error('Recording error:', err);
    process.exit(1);
});
