import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_42_face_attendance_antispoofing/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-042 Video Recording Pipeline ===');
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
    console.log('\n[00:00 - 00:30] Phase 1: Biometric Command Dashboard & Port 5042 Gateway');
    await page.goto('http://127.0.0.1:5042/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => window.scrollTo({ top: 30, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Biometric Gate Controller & Student Select (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Biometric Gate Controller & Student Selection');
    await page.evaluate(() => {
        const el = document.getElementById('sel-student');
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.value = '0';
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('sel-attack');
        if (el) el.value = 'LIVE';
    });
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] 60 FPS Face Mesh & Optical Flow HUD (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: 60 FPS Face Mesh & Micro-Tremor Optical Flow HUD');
    await page.evaluate(() => {
        const el = document.getElementById('hud-canvas');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('telemetryChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Genuine Student Verification & Liveness Audit (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Genuine Student Verification (Alex Chen - STU-101)');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-student').value = '0';
        document.getElementById('sel-attack').value = 'LIVE';
        document.getElementById('btn-verify').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('verif-card');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Adversarial Presentation Attack Interception (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Presentation Attack Interception (2D Print & 4K Replay)');
    await page.evaluate(() => {
        document.getElementById('sel-student').value = '1';
        document.getElementById('sel-attack').value = 'PRINT_ATTACK_2D';
        document.getElementById('btn-verify').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => {
        document.getElementById('sel-student').value = '2';
        document.getElementById('sel-attack').value = 'SCREEN_REPLAY_ATTACK';
        document.getElementById('btn-verify').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Cryptographic SHA-256 Audit Ledger & Records (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Cryptographic SHA-256 Audit Ledger & Verification Records');
    await page.evaluate(() => {
        const el = document.getElementById('tbl-attendance');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('tbl-audit');
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
