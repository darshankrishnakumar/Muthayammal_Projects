import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_33_aircraft_rul/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-033 Video Recording Pipeline ===');
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

    // Spawn backend server if not running
    const serverPath = '/Users/eash/Documents/antigravity/excited-borg/project_33_aircraft_rul/source_code/backend/app.py';
    const serverProc = spawn('python3', [serverPath], { stdio: 'ignore' });
    console.log('Spawned backend server process on Port 5033...');
    await new Promise(r => setTimeout(r, 2000));

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
    // Phase 1: [00:00 - 00:30] Fleet Overview & Telemetry Metrics Strip (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Fleet Overview & Telemetry Metrics Strip');
    await page.goto('http://127.0.0.1:5033/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Subtle scroll to emphasize fleet health metrics
    await page.evaluate(() => window.scrollTo({ top: 60, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Subsystem Selection & C-MAPSS Sensor Array (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Subsystem Selection & C-MAPSS Sensor Array');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectComponent === 'function') {
            window.selectComponent('High-Pressure Compressor (HPC) Rotor');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Scroll to C-MAPSS sensor array
    await page.evaluate(() => {
        const el = document.querySelector('.cmapss-grid');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Weibull Degradation Spline & Sensor Deviations (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Weibull Degradation Spline & Sensor Deviations');
    await page.evaluate(() => {
        const el = document.getElementById('decayChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Pan to sensor deviation chart
    await page.evaluate(() => {
        const el = document.getElementById('sensorBarChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Critical Wear Simulation & AOG Grounding (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Critical Wear Simulation & AOG Grounding');
    await page.evaluate(() => {
        window.scrollTo({ top: 120, behavior: 'smooth' });
        if (typeof window.selectComponent === 'function') {
            window.selectComponent('Mainshaft Roller Bearings (#4 Bearing)');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(30);

    // Trigger high stress worn scenario
    await page.evaluate(async () => {
        if (typeof window.runPrediction === 'function') {
            await window.runPrediction('worn');
        }
    });
    await new Promise(r => setTimeout(r, 1200));

    // Focus on critical emergency directive box
    await page.evaluate(() => {
        const el = document.getElementById('dirBox');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(90);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Maintenance Shop Orders (MSO) Dispatch (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Maintenance Shop Orders (MSO) Dispatch');
    await page.evaluate(() => {
        const el = document.getElementById('shopOrdersList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Create programmatic shop order to showcase live dispatch
    await page.evaluate(async () => {
        if (typeof window.createShopOrder === 'function') {
            await window.createShopOrder({
                component_id: 'COMP-BRG-03',
                priority: 'CRITICAL',
                defect_summary: 'Severe 3.42g vibration anomaly during climb. Immediate shop visit mandated.',
                assigned_technician: 'Senior Powerplant Lead',
                estimated_downtime_hrs: 48.0
            });
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] FAA Regulatory Audit Trail & SQLite WAL Ledger (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: FAA Regulatory Audit Trail & SQLite WAL Ledger');
    await page.evaluate(() => {
        const el = document.getElementById('auditLogList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Scroll to historical ledger
    await page.evaluate(() => {
        const el = document.getElementById('historyList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    console.log(`\nRecording complete! Total frames streamed: ${frameCount} (Target: 720 frames = 180.000s)`);
    await browser.close();

    ffmpeg.stdin.end();

    await new Promise((resolve, reject) => {
        ffmpeg.on('close', (code) => {
            try { serverProc.kill(); } catch (e) {}
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
