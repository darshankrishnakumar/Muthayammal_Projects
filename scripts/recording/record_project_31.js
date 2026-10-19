import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_31_flood_risk/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-031 Video Recording Pipeline ===');
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
    // Phase 1: [00:00 - 00:30] System Overview & Hydrological Metric Strip (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: System Overview & Hydrological Metric Strip');
    await page.goto('http://127.0.0.1:5031/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Subtle scroll to emphasize situation awareness metrics
    await page.evaluate(() => window.scrollTo({ top: 60, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Catchment Topography & River Stage Gauges (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Catchment Topography & River Stage Gauges');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectZone === 'function') window.selectZone('Bay Coastal Lowlands');
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Scroll to river stage gauge chart
    await page.evaluate(() => {
        const el = document.getElementById('gaugeChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Severe Cloudburst Deluge & Critical Red Alert (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Severe Cloudburst Deluge & Critical Red Alert');
    await page.evaluate(async () => {
        window.scrollTo({ top: 100, behavior: 'smooth' });
        if (typeof window.simulateEvent === 'function') {
            await window.simulateEvent('deluge');
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Focus on the alert card and protocol
    await page.evaluate(() => {
        const el = document.getElementById('alertCard');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Inundation Depth Simulation & Contour Mapping (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Inundation Depth Simulation & Physical Contour Mapping');
    await page.evaluate(() => {
        const el = document.getElementById('inundationCanvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Allow wave dynamics to animate on canvas
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Evacuation Lead-Time Forecasting & Emergency Dispatch (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Evacuation Lead-Time Forecasting & Emergency Dispatch');
    await page.evaluate(() => {
        const el = document.getElementById('leadTimeChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Also trigger coastal surge test to show comparative lead times
    await page.evaluate(async () => {
        if (typeof window.simulateEvent === 'function') {
            await window.simulateEvent('surge');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Broadcast History Ledger & SQLite WAL Persistence (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Broadcast History Ledger & SQLite WAL Persistence');
    await page.evaluate(() => {
        const el = document.getElementById('historyList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Final smooth scroll to complete view of the audit ledger
    await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    console.log(`\nTotal Frames Streamed: ${frameCount} (Target: 720 frames for 180.00s)`);

    await browser.close();
    ffmpeg.stdin.end();

    await new Promise((resolve, reject) => {
        ffmpeg.on('close', (code) => {
            if (code === 0) {
                console.log(`Video encoding completed successfully: ${outputVideo}`);
                resolve();
            } else {
                reject(new Error(`FFmpeg exited with code ${code}`));
            }
        });
    });
}

record().catch((err) => {
    console.error('Fatal recording error:', err);
    process.exit(1);
});
