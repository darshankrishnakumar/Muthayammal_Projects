import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_34_road_damage/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-034 Video Recording Pipeline ===');
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
    const serverPath = '/Users/eash/Documents/antigravity/excited-borg/project_34_road_damage/source_code/backend/app.py';
    const serverProc = spawn('python3', [serverPath], { stdio: 'ignore' });
    console.log('Spawned backend server process on Port 5034...');
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
    // Phase 1: [00:00 - 00:30] Municipal Highway Survey Overview (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Municipal Highway Survey Overview');
    await page.goto('http://127.0.0.1:5034/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Subtle scroll to emphasize fleet health metrics
    await page.evaluate(() => window.scrollTo({ top: 60, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Corridor Selection & YOLO Bounding Box Canvas (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Corridor Selection & YOLO Bounding Box Canvas');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.selectSector === 'function') {
            window.selectSector('SEC-URBAN-02');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Focus on road canvas
    await page.evaluate(() => {
        const el = document.getElementById('roadCanvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Pavement Condition Index (PCI) & Roughness (IRI) (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Pavement Condition Index (PCI) & Roughness (IRI)');
    await page.evaluate(() => {
        const el = document.querySelector('.hero-pci');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Pan to charts
    await page.evaluate(() => {
        const el = document.getElementById('defectChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Critical Wear Simulation & Emergency Resurfacing (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Critical Wear Simulation & Emergency Resurfacing');
    await page.evaluate(() => {
        window.scrollTo({ top: 120, behavior: 'smooth' });
        if (typeof window.selectSector === 'function') {
            window.selectSector('SEC-IND-03');
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(30);

    // Trigger severe scenario
    await page.evaluate(async () => {
        if (typeof window.runInspection === 'function') {
            await window.runInspection('severe');
        }
    });
    await new Promise(r => setTimeout(r, 1200));

    // Focus on critical PCI rating & cost alert
    await page.evaluate(() => {
        const el = document.querySelector('.hero-pci');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(90);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Municipal Work Orders (MWO) Dispatch (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Municipal Work Orders (MWO) Dispatch');
    await page.evaluate(() => {
        const el = document.getElementById('workOrdersList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Create programmatic municipal work order
    await page.evaluate(async () => {
        if (typeof window.createWorkOrder === 'function') {
            await window.createWorkOrder({
                sector_id: 'SEC-IND-03',
                priority: 'CRITICAL',
                remediation_scope: 'Emergency asphalt cold patch & compactor roll on severe pothole clusters',
                assigned_contractor: 'Apex Municipal Pavement Corp',
                budget_allocated_usd: 9500
            });
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] DOT Regulatory Compliance & Relational SQLite WAL Ledger (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: DOT Regulatory Compliance & Relational SQLite WAL Ledger');
    await page.evaluate(() => {
        const el = document.getElementById('auditLogList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Scroll to historical survey ledger
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
