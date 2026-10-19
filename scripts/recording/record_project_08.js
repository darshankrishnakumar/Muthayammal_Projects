import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_08_customer_churn_prediction/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-008 Video Recording Pipeline ===');
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
    await page.goto('http://127.0.0.1:5008/', { waitUntil: 'networkidle0' });

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

    console.log('\n[00:00 - 00:25] Step 1: Executive Dashboard & KPI Overview');
    await page.goto('http://127.0.0.1:5008/', { waitUntil: 'networkidle0' });
    await streamFrames(25);

    console.log('\n[00:25 - 00:55] Step 2: Subscriber Risk Assessment Workspace & Form Inputs');
    await page.goto('http://127.0.0.1:5008/predict', { waitUntil: 'networkidle0' });
    await streamFrames(30);

    console.log('\n[00:55 - 01:25] Step 3: Random Forest Inference & Real-Time Churn Evaluation');
    await page.click('#predictBtn');
    await page.waitForNavigation({ waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 800));
    await page.evaluate(() => {
        const el = document.getElementById('predictionResultSection');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
    });
    await streamFrames(30);

    console.log('\n[01:25 - 01:50] Step 4: Time-to-Event Survival Curve & Cumulative Hazard');
    await page.evaluate(() => {
        window.scrollBy({ top: 400, behavior: 'smooth' });
    });
    await streamFrames(25);

    console.log('\n[01:50 - 02:15] Step 5: SHAP Feature Attribution Waterfall');
    await page.evaluate(() => {
        window.scrollBy({ top: 450, behavior: 'smooth' });
    });
    await streamFrames(25);

    console.log('\n[02:15 - 02:35] Step 6: Model Performance Benchmarks & Validation Leaderboard');
    await page.goto('http://127.0.0.1:5008/model-performance', { waitUntil: 'networkidle0' });
    await streamFrames(20);

    console.log('\n[02:35 - 02:50] Step 7: Relational Transaction History & SQLite Audit Trail');
    await page.goto('http://127.0.0.1:5008/history', { waitUntil: 'networkidle0' });
    await streamFrames(15);

    console.log('\n[02:50 - 03:00] Step 8: Return to Executive Dashboard & Capstone QA Sign-Off');
    await page.goto('http://127.0.0.1:5008/', { waitUntil: 'networkidle0' });
    await streamFrames(10);

    console.log(`\nFlushing FFmpeg stream... (total frames captured: ${frameCount})`);
    ffmpeg.stdin.end();

    await new Promise((resolve, reject) => {
        ffmpeg.on('close', (code) => {
            if (code === 0) {
                console.log(`Video recording completed successfully: ${outputVideo}`);
                resolve();
            } else {
                reject(new Error(`FFmpeg exited with code ${code}`));
            }
        });
    });

    await browser.close();
    console.log('=== PROJECT-008 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
