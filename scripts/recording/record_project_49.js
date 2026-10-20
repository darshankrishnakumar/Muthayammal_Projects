import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_49_healthcare_risk_assessment/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-049 Video Recording Pipeline (Port 5049) ===');
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
    // Phase 1: [00:00 - 00:30] Full Healthcare Risk Dashboard & Port 5049 Gateway (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Healthcare Risk Dashboard & Port 5049 Gateway');
    await page.goto('http://127.0.0.1:5049/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => window.scrollTo({ top: 40, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] SHAP Feature Contribution HUD & Dual PyTorch Engines (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: SHAP Feature Contribution HUD & Dual PyTorch Engines');
    await page.evaluate(() => {
        const el = document.getElementById('shapChart');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('sel-preset');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Robert Vance (Hypertensive CVD High Risk) & Linda Sterling Control (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Robert Vance (Hypertensive CVD High Risk) & Linda Sterling');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-preset').value = 'vance_htn';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-assess').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => {
        document.getElementById('sel-preset').value = 'sterling_norm';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-assess').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Arthur Pendelton (Renal CKD Critical) & Jennifer Montgomery (Diabetic) (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Arthur Pendelton (Renal CKD Critical) & Jennifer Montgomery');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.getElementById('sel-preset').value = 'pendelton_ckd';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-assess').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(() => {
        document.getElementById('sel-preset').value = 'montgomery_t2d';
        document.getElementById('sel-preset').dispatchEvent(new Event('change'));
        document.getElementById('btn-assess').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Patient Clinical Risk Ledger & SQLite WAL Mode (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Patient Clinical Risk Ledger & SQLite WAL Mode');
    await page.evaluate(() => {
        const el = document.getElementById('records-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    await page.evaluate(() => window.scrollBy({ top: 120, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Cryptographic Audit Ledger & SHA-256 Hash Chaining (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Cryptographic Audit Ledger & SHA-256 Hash Chaining');
    await page.evaluate(() => {
        const el = document.getElementById('audit-body');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    await page.evaluate(() => {
        const badge = document.getElementById('ledger-verified-badge');
        if (badge) badge.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    console.log(`\nAll 720 frames captured successfully (${frameCount} frames total). Closing browser.`);
    await browser.close();

    console.log('Finalizing FFmpeg encoding...');
    ffmpeg.stdin.end();

    await new Promise((resolve, reject) => {
        ffmpeg.on('close', code => {
            if (code === 0) resolve();
            else reject(new Error(`FFmpeg exited with code ${code}`));
        });
    });

    console.log(`=== Video Recording Complete: ${outputVideo} ===`);
}

record().catch(err => {
    console.error('Fatal recording error:', err);
    process.exit(1);
});
