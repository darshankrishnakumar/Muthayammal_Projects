import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_41_fruit_quality_grading/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-041 Video Recording Pipeline ===');
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

    let frameCount = 0;
    let lastBuf = null;

    async function streamFrames(count) {
        for (let i = 0; i < count; i++) {
            try {
                lastBuf = await page.screenshot({ type: 'png', omitBackground: false });
            } catch (err) {
                console.warn(`Frame ${frameCount} warning: ${err.message}`);
            }
            if (lastBuf && ffmpeg.stdin.writable) {
                ffmpeg.stdin.write(lastBuf);
            }
            frameCount++;
            await new Promise(r => setTimeout(r, 60));
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 1: [00:00 - 00:30] Command Dashboard & Status (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Central Packhouse Sorter Dashboard & Port 5041 Status');
    await page.goto('http://127.0.0.1:5041/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => window.scrollTo({ top: 30, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Conveyor Belt Canvas & Charts (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: 60 FPS Conveyor Belt Canvas & Optical Scanning Tunnel');
    await page.evaluate(() => {
        const el = document.getElementById('conveyorCanvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('gradeChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Apple Optical Inspection & Grade A Export (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Lane 1 Apple Optical Inspection & Grade A Export Sorting');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectLane === 'function') {
            window.selectLane(1, 'Lane 1: High-Speed Apple Optical Sorter', 'APPLE', 'NONE');
            await new Promise(r => setTimeout(r, 300));
            await window.triggerFruitInspection();
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('sort-result');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Orange Skin Rot Defect & Discard Routing (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Lane 2 Citrus Orange Skin Rot Defect & Discard Routing');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectLane === 'function') {
            window.selectLane(2, 'Lane 2: Citrus / Orange Surface Defect Sorter', 'ORANGE', 'SKIN_ROT');
            await new Promise(r => setTimeout(r, 300));
            await window.triggerFruitInspection();
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('sort-result');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Mango Export Inspection & Freshness Profile (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Lane 4 Tropical Mango Export Inspection & Sugar Brix Rating');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectLane === 'function') {
            window.selectLane(4, 'Lane 4: Premium Mango Export Inspection Line', 'MANGO', 'NONE');
            await new Promise(r => setTimeout(r, 300));
            await window.triggerFruitInspection();
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('freshnessChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Cryptographic Audit Ledger & Telemetry Register (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Cryptographic Audit Ledger & Conveyor Telemetry Register');
    await page.evaluate(() => {
        const el = document.getElementById('itemsTable');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('auditLedgerSection');
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
