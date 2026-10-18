import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_02_network_intrusion_anomaly/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-002 Video Recording Pipeline ===');
    console.log(`Output: ${outputVideo}`);

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
    await page.goto('http://127.0.0.1:5002', { waitUntil: 'networkidle0' });

    let frameCount = 0;

    async function streamFrames(durationSeconds) {
        const totalFrames = Math.round(durationSeconds * 4);
        for (let i = 0; i < totalFrames; i++) {
            const buf = await page.screenshot({ type: 'png', omitBackground: false });
            if (ffmpeg.stdin.writable) {
                ffmpeg.stdin.write(buf);
            }
            frameCount++;
            await new Promise(r => setTimeout(r, 180));
        }
    }

    console.log('\n[00:00 - 00:20] Step 1: SOC Dashboard & Architecture Overview');
    await streamFrames(20);

    console.log('\n[00:20 - 00:45] Step 2: Neptune SYN Flood DoS Attack Simulation');
    await page.evaluate(() => {
        loadPreset('syn_flood_dos', document.querySelector('.chip:nth-child(1)'));
        executeInspection();
    });
    await streamFrames(25);

    console.log('\n[00:45 - 01:10] Step 3: Port Sweep Reconnaissance Probe Interception');
    await page.evaluate(() => {
        loadPreset('port_scan_probe', document.querySelector('.chip:nth-child(2)'));
        executeInspection();
    });
    await streamFrames(25);

    console.log('\n[01:10 - 01:30] Step 4: Benign Web Browsing (HTTP Session) Verification');
    await page.evaluate(() => {
        loadPreset('normal_http_session', document.querySelector('.chip:nth-child(3)'));
        executeInspection();
    });
    await streamFrames(20);

    console.log('\n[01:30 - 01:50] Step 5: Password Brute-Force (R2L Unauthorized Access)');
    await page.evaluate(() => {
        loadPreset('ssh_brute_force_r2l', document.querySelector('.chip:nth-child(4)'));
        executeInspection();
    });
    await streamFrames(20);

    console.log('\n[01:50 - 02:15] Step 6: Zero-Day Out-of-Distribution Anomaly Detection');
    await page.evaluate(() => {
        loadPreset('zero_day_anomaly', document.querySelector('.chip:nth-child(6)'));
        executeInspection();
    });
    await streamFrames(25);

    console.log('\n[02:15 - 02:30] Step 7: Model Benchmarks & Defense Taxonomy');
    await page.evaluate(() => {
        switchTab('tab-benchmarks', document.querySelectorAll('.tab-btn')[1]);
    });
    await streamFrames(15);

    console.log('\n[02:30 - 02:45] Step 8: Security Event Incident Audit Log (SQLite Store)');
    await page.evaluate(() => {
        switchTab('tab-history', document.querySelectorAll('.tab-btn')[2]);
    });
    await streamFrames(15);

    console.log('\n[02:45 - 03:00] Step 9: Threat Intelligence Analytics & Operational Metrics');
    await page.evaluate(() => {
        switchTab('tab-analytics', document.querySelectorAll('.tab-btn')[3]);
    });
    await streamFrames(15);

    console.log(`\nDemonstration complete. Total frames piped: ${frameCount}`);
    await browser.close();

    ffmpeg.stdin.end();
    await new Promise((resolve) => {
        ffmpeg.on('close', (code) => {
            console.log(`\nFFmpeg encoding completed with exit code ${code}`);
            resolve();
        });
    });
}

record().catch(console.error);
