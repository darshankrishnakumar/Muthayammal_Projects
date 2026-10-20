import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_55_accident_emergency_alert/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-055 Video Recording Pipeline (Port 5055) ===');
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
    // Phase 1: [00:00 - 00:15] Command Center & Enterprise Badges (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:15] Phase 1: Command Center & Enterprise Badges (Port 5055, WAL)');
    await page.goto('http://127.0.0.1:5055/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:15 - 00:30] KPI Summary Metrics & Monitored Corridors (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:15 - 00:30] Phase 2: KPI Summary Metrics & Monitored Corridors');
    await page.evaluate(() => window.scrollTo({ top: 30, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [00:30 - 00:45] Multi-Cue Incident Simulator & Telemetry Setup (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 00:45] Phase 3: Multi-Cue Incident Simulator & Telemetry Setup');
    await page.evaluate(() => {
        const el = document.getElementById('preset-select');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [00:45 - 01:00] Scenario A: Interstate 101 Rollover Crash Trigger (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:45 - 01:00] Phase 4: Scenario A: Interstate 101 Rollover Crash Trigger');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        const sel = document.getElementById('preset-select');
        sel.value = 'PRESET-HWY101-ROLLOVER';
        sel.dispatchEvent(new Event('change'));
        document.getElementById('btn-trigger').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [01:00 - 01:15] Level-1 Trauma CAD Alert Banner & ETA Diagnostics (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:15] Phase 5: Level-1 Trauma CAD Alert Banner & ETA Diagnostics');
    await page.evaluate(() => {
        const banner = document.getElementById('cad-banner');
        if (banner) banner.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [01:15 - 01:30] Scenario B: Downtown 5th Ave Multi-Vehicle T-Bone (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:15 - 01:30] Phase 6: Scenario B: Downtown 5th Ave Multi-Vehicle T-Bone');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        const sel = document.getElementById('preset-select');
        sel.value = 'PRESET-URBAN-TBONE';
        sel.dispatchEvent(new Event('change'));
        document.getElementById('btn-trigger').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 7: [01:30 - 01:45] Scenario C: Mountain Route 9 Guardrail Strike (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 01:45] Phase 7: Scenario C: Mountain Route 9 Guardrail Strike');
    await page.evaluate(() => {
        const sel = document.getElementById('preset-select');
        sel.value = 'PRESET-RURAL-GUARDRAIL';
        sel.dispatchEvent(new Event('change'));
        document.getElementById('btn-trigger').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 8: [01:45 - 02:00] Scenario D: False Alarm Suppression on Legal Hard Braking (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:45 - 02:00] Phase 8: Scenario D: False Alarm Suppression on Legal Hard Braking');
    await page.evaluate(() => {
        const sel = document.getElementById('preset-select');
        sel.value = 'PRESET-SAFE-BRAKING';
        sel.dispatchEvent(new Event('change'));
        document.getElementById('btn-trigger').click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 9: [02:00 - 02:15] Dynamic Cue Attribution & 0.0% False Alarm Rate (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:15] Phase 9: Dynamic Cue Attribution & 0.0% False Alarm Rate');
    await page.evaluate(() => {
        const chart = document.getElementById('cueChart');
        if (chart) chart.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 10: [02:15 - 02:30] Cryptographic Audit Ledger & SHA-256 Hash Chaining (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:15 - 02:30] Phase 10: Cryptographic Audit Ledger & SHA-256 Hash Chaining');
    await page.evaluate(() => {
        const ledger = document.getElementById('ledger-body');
        if (ledger) ledger.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 11: [02:30 - 02:45] Active CAD Incident Logs & Telemetry Registry (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 02:45] Phase 11: Active CAD Incident Logs & Telemetry Registry');
    await page.evaluate(() => {
        const registry = document.getElementById('incidents-body');
        if (registry) registry.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 12: [02:45 - 03:00] Grand Capstone Milestone: 55/55 Projects Complete! (60 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:45 - 03:00] Phase 12: Grand Capstone Milestone: 55/55 Projects Complete!');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
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
