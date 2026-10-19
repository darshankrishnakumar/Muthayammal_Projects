import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_10_deepfake_detector/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-010 Video Recording Pipeline ===');
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
    await page.goto('http://127.0.0.1:5010/', { waitUntil: 'networkidle0' });

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

    console.log('\n[00:00 - 00:25] Step 1: Executive Forensics Dashboard & Laboratory Overview');
    await page.goto('http://127.0.0.1:5010/', { waitUntil: 'networkidle0' });
    await streamFrames(25);

    console.log('\n[00:25 - 00:50] Step 2: Facial Image Inspection Workspace & Test Presets');
    await page.evaluate(() => {
        const el = document.getElementById('facePreview');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
    });
    await streamFrames(25);

    console.log('\n[00:50 - 01:20] Step 3: Authentic Face Verification & Biometric Clearance');
    await page.click('#analyzeBtn');
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => {
        const el = document.getElementById('resultBox');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
    });
    await streamFrames(30);

    console.log('\n[01:20 - 01:45] Step 4: Multi-Modal Forensics Breakdown & Signal Metrics');
    await page.evaluate(() => {
        const el = document.getElementById('indFft');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await streamFrames(25);

    console.log('\n[01:45 - 02:10] Step 5: FaceSwap Manipulation Interception');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('.btn-preset'));
        const swapBtn = btns.find(b => b.textContent.includes('FaceSwap'));
        if (swapBtn) swapBtn.click();
    });
    await new Promise(r => setTimeout(r, 500));
    await page.click('#analyzeBtn');
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(25);

    console.log('\n[02:10 - 02:35] Step 6: StyleGAN Synthesis & 2D FFT Frequency Forensics');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('.btn-preset'));
        const ganBtn = btns.find(b => b.textContent.includes('StyleGAN'));
        if (ganBtn) ganBtn.click();
    });
    await new Promise(r => setTimeout(r, 500));
    await page.click('#analyzeBtn');
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(25);

    console.log('\n[02:35 - 02:50] Step 7: Relational Transaction History & SQLite Audit Trail');
    await page.evaluate(() => {
        const el = document.getElementById('historyTableBody');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'end' });
    });
    await streamFrames(15);

    console.log('\n[02:50 - 03:00] Step 8: Return to Executive Dashboard & Capstone QA Sign-Off');
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
    console.log('=== PROJECT-010 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
