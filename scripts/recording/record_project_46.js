import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_46_manufacturing_defect_detection/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-046 Video Recording Pipeline ===');
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
    // Phase 1: [00:00 - 00:30] Full Industrial Dashboard & Port 5046 Gateway (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Industrial Dashboard & Port 5046 Gateway');
    await page.goto('http://127.0.0.1:5046/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => window.scrollTo({ top: 40, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] FPN Multi-Scale Defect HUD & Conveyor Belt (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: FPN Multi-Scale Defect HUD & Conveyor Belt');
    await page.evaluate(() => {
        const el = document.getElementById('component-graphic');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('actuator-status-pill');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] SMT PCB Board Nominal Inspection (PASS) (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: SMT PCB Board Nominal Inspection (PASS)');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('part-type').value = 'PCB_BOARD';
        document.getElementById('part-type').dispatchEvent(new Event('change'));
        document.getElementById('assembly-line').value = 'Line-1 SMT PCB Assembly';
        document.getElementById('defect-sim').value = 'NONE';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('scan-result');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] CNC Machined Gear Crack Anomaly (REJECT) (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: CNC Machined Gear Crack Anomaly (REJECT)');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('part-type').value = 'MACHINED_GEAR';
        document.getElementById('part-type').dispatchEvent(new Event('change'));
        document.getElementById('assembly-line').value = 'Line-2 CNC Gear Milling';
        document.getElementById('defect-sim').value = 'CRACK';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('component-graphic');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Metallic Casing & Aerospace Blade Inspections (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Metallic Casing & Aerospace Blade Inspections');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('part-type').value = 'METALLIC_CASING';
        document.getElementById('part-type').dispatchEvent(new Event('change'));
        document.getElementById('assembly-line').value = 'Line-3 Casing Foundry';
        document.getElementById('defect-sim').value = 'DENT';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => {
        document.getElementById('part-type').value = 'TURBINE_BLADE';
        document.getElementById('part-type').dispatchEvent(new Event('change'));
        document.getElementById('assembly-line').value = 'Line-4 Precision Aerospace';
        document.getElementById('defect-sim').value = 'MISSING_COMPONENT';
        document.getElementById('btn-scan').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Inspection Templates & Cryptographic Audit Ledger (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Inspection Templates & Cryptographic Audit Ledger');
    await page.evaluate(() => {
        const el = document.getElementById('templates-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('audit-body');
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
