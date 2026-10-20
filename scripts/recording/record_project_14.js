import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_14_fake_news_detection/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-014 Video Recording Pipeline ===');
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

    console.log('\n[00:00 - 00:20] Step 1: Executive Landing & System Architecture (Port 5014)');
    await page.goto('http://127.0.0.1:5014/', { waitUntil: 'networkidle0' });
    await streamFrames(20);

    console.log('\n[00:20 - 00:45] Step 2: Prediction Console & Sample Selection');
    await page.goto('http://127.0.0.1:5014/predict', { waitUntil: 'networkidle0' });
    await streamFrames(25);

    console.log('\n[00:45 - 01:15] Step 3: Sensational Fake News Classification & Decision Margin');
    await page.goto('http://127.0.0.1:5014/predict?news=Secret+government+plan+revealed+to+control+weather+with+cell+towers', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => {
        const el = document.getElementById('resultsDashboard');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    await streamFrames(30);

    console.log('\n[01:15 - 01:45] Step 4: Explainable Feature Attribution & Mathematical Token Weights');
    await page.evaluate(() => {
        const headings = Array.from(document.querySelectorAll('h3'));
        const attrHeading = headings.find(h => h.textContent.includes('Explainable Feature Attribution'));
        if (attrHeading) {
            attrHeading.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
    await streamFrames(30);

    console.log('\n[01:45 - 02:10] Step 5: 4-Signal Linguistic Stylometric Radar');
    await page.evaluate(() => {
        const headings = Array.from(document.querySelectorAll('h3'));
        const radarHeading = headings.find(h => h.textContent.includes('Intuitive Indications'));
        if (radarHeading) {
            radarHeading.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
    await streamFrames(25);

    console.log('\n[02:10 - 02:35] Step 6: Beyond Blacklists — Pure Language Stylometry Mode');
    await page.goto('http://127.0.0.1:5014/predict?news=Wells+Fargo+Chief+Abruptly+Steps+Down+-+The+New+York+Times&pure_language_mode=on', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => {
        const el = document.getElementById('resultsDashboard');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    await streamFrames(25);

    console.log('\n[02:35 - 02:50] Step 7: Multi-Model Benchmarks & SQLite Audit Ledger');
    await page.evaluate(() => {
        const table = document.querySelector('table');
        if (table) {
            table.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }
    });
    await streamFrames(15);

    console.log('\n[02:50 - 03:00] Step 8: Return to Portal & Capstone Sign-Off');
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
    console.log('=== PROJECT-014 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
