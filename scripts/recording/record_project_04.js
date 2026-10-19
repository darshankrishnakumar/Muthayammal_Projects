import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_04_car_price_prediction/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-004 Video Recording Pipeline ===');
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
    await page.goto('http://127.0.0.1:5004', { waitUntil: 'networkidle0' });

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

    console.log('\n[00:00 - 00:25] Step 1: AutoValuate AI Portal Overview & Initial Swift Valuation');
    await streamFrames(25);

    console.log('\n[00:25 - 00:55] Step 2: Honda City ZX (2020) Executive Sedan Valuation');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('.preset-btn'));
        const cityBtn = btns.find(b => b.textContent.includes('City'));
        if (cityBtn) cityBtn.click();
    });
    await streamFrames(30);

    console.log('\n[00:55 - 01:25] Step 3: Toyota Fortuner 4x4 (2021) Premium SUV Valuation');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('.preset-btn'));
        const fortunerBtn = btns.find(b => b.textContent.includes('Fortuner'));
        if (fortunerBtn) fortunerBtn.click();
    });
    await streamFrames(30);

    console.log('\n[01:25 - 01:50] Step 4: BMW 3 Series 330i (2021) Luxury Sports Sedan Valuation');
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('.preset-btn'));
        const bmwBtn = btns.find(b => b.textContent.includes('BMW'));
        if (bmwBtn) bmwBtn.click();
    });
    await streamFrames(25);

    console.log('\n[01:50 - 02:15] Step 5: Model Benchmarks Comparison (Random Forest vs Decision Tree vs Linear)');
    await page.evaluate(() => {
        window.switchTab('benchmarks');
    });
    await streamFrames(25);

    console.log('\n[02:15 - 02:35] Step 6: Feature Importance Hierarchy Visualizer');
    await page.evaluate(() => {
        window.switchTab('importance');
    });
    await streamFrames(20);

    console.log('\n[02:35 - 02:50] Step 7: SQLite Transactional Prediction History Log');
    await page.evaluate(() => {
        window.switchTab('history');
    });
    await streamFrames(15);

    console.log('\n[02:50 - 03:00] Step 8: Historical Sales Dataset Explorer & REST API Docs');
    await page.evaluate(() => {
        window.switchTab('dataset');
    });
    await streamFrames(5);
    await page.evaluate(() => {
        window.switchTab('api');
    });
    await streamFrames(5);

    console.log(`\nClosing browser... Total recorded frames: ${frameCount}`);
    await browser.close();

    console.log('Finalizing FFmpeg encoding...');
    ffmpeg.stdin.end();

    await new Promise((resolve, reject) => {
        ffmpeg.on('close', (code) => {
            if (code === 0) {
                console.log(`\n[SUCCESS] Video encoded successfully to: ${outputVideo}`);
                resolve(null);
            } else {
                reject(new Error(`FFmpeg exited with error code ${code}`));
            }
        });
    });
}

record().catch((err) => {
    console.error('Recording failed:', err);
    process.exit(1);
});
