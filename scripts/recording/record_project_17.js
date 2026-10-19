const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_17_phishing_email_detection/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-017 Video Recording Pipeline ===');
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
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    let frameCount = 0;

    async function streamFrames(durationSeconds) {
        const totalFrames = Math.round(durationSeconds * 4);
        for (let i = 0; i < totalFrames; i++) {
            const buf = await page.screenshot({ type: 'png', omitBackground: false });
            if (ffmpeg.stdin.writable) {
                ffmpeg.stdin.write(buf);
            }
            frameCount++;
            await new Promise(r => setTimeout(r, 120));
        }
    }

    // Phase 1: [00:00 - 00:30] Landing Overview (30s = 120 frames)
    console.log('\n[00:00 - 00:30] Phase 1: System Overview & Problem Formulation');
    await page.goto('http://127.0.0.1:5017/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(30);

    // Phase 2: [00:30 - 01:05] Threat Detection: Bank Header Spoofing (35s = 140 frames)
    console.log('\n[00:30 - 01:05] Phase 2: Threat Detection Demo - Bank Header Spoofing');
    await page.click('button[data-sample="sample-phish-rcnn-1"]');
    await new Promise(r => setTimeout(r, 400));
    await page.click('#scanBtn');
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(35);

    // Phase 3: [01:05 - 01:40] Explainable AI: Token Attention Heatmap (35s = 140 frames)
    console.log('\n[01:05 - 01:40] Phase 3: Explainable AI (XAI) - Token-Level Attention Heatmap');
    await page.evaluate(() => {
        const el = document.getElementById('attentionContainer');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(35);

    // Phase 4: [01:40 - 02:10] Legitimate Verification: Authenticated Corporate Email (30s = 120 frames)
    console.log('\n[01:40 - 02:10] Phase 4: High Specificity Verification - Legitimate Corporate Email');
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 600));
    await page.click('button[data-sample="sample-safe-rcnn-1"]');
    await new Promise(r => setTimeout(r, 400));
    await page.click('#scanBtn');
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(30);

    // Phase 5: [02:10 - 02:35] Academic Benchmarks (25s = 100 frames)
    console.log('\n[02:10 - 02:35] Phase 5: Academic Benchmarks under Realistic Unbalanced Traffic');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.click('.nav-tab[data-tab="benchmarks"]');
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(25);

    // Phase 6: [02:35 - 03:00] SQLite Audit History & Architecture (25s = 100 frames)
    console.log('\n[02:35 - 03:00] Phase 6: SQLite Audit History & Deep Neural Architecture');
    await page.click('.nav-tab[data-tab="history"]');
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(15);
    await page.click('.nav-tab[data-tab="architecture"]');
    await new Promise(r => setTimeout(r, 800));
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
    console.log('=== PROJECT-017 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
