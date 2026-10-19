import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_26_network_intrusion/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-026 Video Recording Pipeline ===');
    console.log(`Output: ${outputVideo}`);

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
    // Phase 1: [00:00 - 00:30] Cockpit Overview & 360 Threat Radar (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Cockpit Overview & 360 Threat Radar');
    await page.goto('http://127.0.0.1:5026/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Scroll slightly to focus on live rotating threat radar and packet stream
    await page.evaluate(() => window.scrollTo({ top: 80, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] SYN Flood Interdiction (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: SYN Flood Interdiction');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.switchTab === 'function') window.switchTab(1);
        if (typeof window.triggerAttack === 'function') await window.triggerAttack('SYN_Flood');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Focus on diagnostic inspection result
    await page.evaluate(() => {
        const insp = document.getElementById('inspResultContainer');
        if (insp) insp.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Reconnaissance & SSH Brute Force (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Reconnaissance & SSH Brute Force');
    await page.evaluate(async () => {
        if (typeof window.triggerAttack === 'function') await window.triggerAttack('Port_Scan');
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    await page.evaluate(async () => {
        if (typeof window.triggerAttack === 'function') await window.triggerAttack('SSH_BruteForce');
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Mirai Botnet C2 Beaconing (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Mirai Botnet C2 Beaconing');
    await page.evaluate(async () => {
        if (typeof window.triggerAttack === 'function') await window.triggerAttack('Mirai_Botnet');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Scroll to inspect flow details
    await page.evaluate(() => window.scrollBy({ top: 60, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Autoencoder Zero-Day Anomaly Gauge (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Autoencoder Zero-Day Anomaly Gauge');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.switchTab === 'function') window.switchTab(2);
        if (typeof window.triggerAttack === 'function') await window.triggerAttack('Zero_Day');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Focus on reconstruction loss meter and formula
    await page.evaluate(() => {
        const gauge = document.getElementById('lossFillBar');
        if (gauge) gauge.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Autonomous Firewall Quarantine & Rules (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Autonomous Firewall Quarantine & Rules');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.switchTab === 'function') window.switchTab(3);
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Scroll to inspect generated iptables and ufw rules
    await page.evaluate(() => {
        const box = document.getElementById('iptablesRulesBox');
        if (box) box.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    console.log(`\nFlushing FFmpeg stream... (total frames captured: ${frameCount})`);
    ffmpeg.stdin.end();

    await new Promise((resolve, reject) => {
        ffmpeg.on('close', (code) => {
            if (code === 0) {
                console.log(`\nVideo recording completed successfully: ${outputVideo}`);
                resolve();
            } else {
                reject(new Error(`FFmpeg exited with code ${code}`));
            }
        });
    });

    await browser.close();
    console.log('=== PROJECT-026 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
