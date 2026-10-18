import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_03_apple_disease_detection/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-003 Video Recording Pipeline ===');
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
    await page.goto('http://127.0.0.1:5003', { waitUntil: 'networkidle0' });

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

    console.log('\n[00:00 - 00:20] Step 1: Diagnostic Portal Overview & Status Banner');
    await streamFrames(20);

    console.log('\n[00:20 - 00:45] Step 2: Cedar Apple Rust Leaf Diagnosis & Decision Support');
    await page.evaluate(() => {
        const btn = document.querySelector('.preset-btn[data-sample="cedar_rust"]');
        if (btn) btn.click();
    });
    await streamFrames(25);

    console.log('\n[00:45 - 01:10] Step 3: Apple Scab Foliar Lesion Diagnosis & Fungicide Protocol');
    await page.evaluate(() => {
        const btn = document.querySelector('.preset-btn[data-sample="scab_leaf"]');
        if (btn) btn.click();
    });
    await streamFrames(25);

    console.log('\n[01:10 - 01:30] Step 4: Black Rot / Frog-Eye Leaf Diagnosis');
    await page.evaluate(() => {
        const btn = document.querySelector('.preset-btn[data-sample="black_rot_leaf"]');
        if (btn) btn.click();
    });
    await streamFrames(20);

    console.log('\n[01:30 - 01:50] Step 5: Healthy Pathogen-Free Foliage Verification');
    await page.evaluate(() => {
        const btn = document.querySelector('.preset-btn[data-sample="healthy_leaf"]');
        if (btn) btn.click();
    });
    await streamFrames(20);

    console.log('\n[01:50 - 02:15] Step 6: Apple Fruit Condition Diagnosis (Fresh vs Rotten)');
    await page.evaluate(() => {
        const btn = document.querySelector('.preset-btn[data-sample="rot_fruit"]');
        if (btn) btn.click();
    });
    await streamFrames(25);

    console.log('\n[02:15 - 02:30] Step 7: CNN Feature Maps & Grad-CAM Visual Heatmaps');
    await page.evaluate(() => {
        const tabBtn = document.querySelector('.tab-btn[data-tab="tab-layers"]');
        if (tabBtn) tabBtn.click();
    });
    await streamFrames(15);

    console.log('\n[02:30 - 02:45] Step 8: Agronomic Pathology & Treatment Guide');
    await page.evaluate(() => {
        const tabBtn = document.querySelector('.tab-btn[data-tab="tab-encyclopedia"]');
        if (tabBtn) tabBtn.click();
    });
    await streamFrames(15);

    console.log('\n[02:45 - 03:00] Step 9: Diagnostic Summary & Mobile-Edge Deployment');
    await page.evaluate(() => {
        const tabBtn = document.querySelector('.tab-btn[data-tab="tab-diagnosis"]');
        if (tabBtn) tabBtn.click();
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
