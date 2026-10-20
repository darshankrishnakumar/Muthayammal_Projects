import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_13_crime_prediction_forecasting/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-013 Video Recording Pipeline ===');
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
    await page.goto('http://127.0.0.1:5013/', { waitUntil: 'networkidle0' });

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

    console.log('\n[00:00 - 00:20] Step 1: Executive Dashboard & System Overview (Port 5013)');
    await page.goto('http://127.0.0.1:5013/', { waitUntil: 'networkidle0' });
    await streamFrames(20);

    console.log('\n[00:20 - 00:45] Step 2: Spatio-Temporal Simulation Parameters & Presets');
    await page.evaluate(() => {
        const el = document.getElementById('selDistrict');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await streamFrames(25);

    console.log('\n[00:45 - 01:15] Step 3: Critical Threat Prediction & Automated Code 3 Dispatch');
    await page.evaluate(() => {
        loadPreset('late_night_downtown');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => {
        const el = document.getElementById('resultCard');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    await streamFrames(30);

    console.log('\n[01:15 - 01:45] Step 4: Low-Threat Suburban Baseline Clearance & Patrol Standby');
    await page.evaluate(() => {
        loadPreset('suburban_quiet');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => {
        const el = document.getElementById('resultCard');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    await streamFrames(30);

    console.log('\n[01:45 - 02:10] Step 5: 24-Hour Temporal Threat Risk Curve & Nocturnal Spike');
    await page.evaluate(() => {
        loadPreset('late_night_downtown');
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.evaluate(() => {
        const el = document.getElementById('hourlyBarsContainer');
        if (el) el.parentElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await streamFrames(25);

    console.log('\n[02:10 - 02:35] Step 6: Tactical Patrol Fleet Management & Unit Routing');
    await page.evaluate(() => {
        switchTab('dispatches');
        const el = document.getElementById('dispatchesTableContainer');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await streamFrames(25);

    console.log('\n[02:35 - 02:50] Step 7: Relational Command & Incident Audit Ledger (SQLite)');
    await page.evaluate(() => {
        switchTab('incidents');
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    });
    await streamFrames(15);

    console.log('\n[02:50 - 03:00] Step 8: Return to Executive Portal & Capstone Sign-Off');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    await streamFrames(10);

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
    console.log('=== PROJECT-013 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
