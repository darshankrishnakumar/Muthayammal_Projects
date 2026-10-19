const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_18_dress_recommendation_skin_tone/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-018 Video Recording Pipeline ===');
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
    console.log('\n[00:00 - 00:30] Phase 1: System Overview & Styling Controls');
    await page.goto('http://127.0.0.1:5018/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(30);

    // Phase 2: [00:30 - 01:05] Persona 1: Fair-Cool Evening Gala (35s = 140 frames)
    console.log('\n[00:30 - 01:05] Phase 2: Persona 1 Curation - Fair-Cool Evening Gala');
    await page.click('button[data-preset="p1"]');
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(35);

    // Phase 3: [01:05 - 01:40] Persona 2: Medium-Warm Business Formal (35s = 140 frames)
    console.log('\n[01:05 - 01:40] Phase 3: Persona 2 Curation - Medium-Warm Business Formal');
    await page.click('button[data-preset="p2"]');
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(35);

    // Phase 4: [01:40 - 02:10] Persona 3: Olive-Warm Traditional Ethnic (30s = 120 frames)
    console.log('\n[01:40 - 02:10] Phase 4: Persona 3 Curation - Olive-Warm Traditional Ethnic');
    await page.click('button[data-preset="p3"]');
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(30);

    // Phase 5: [02:10 - 02:35] Catalogue Explorer & Model Benchmarks (25s = 100 frames)
    console.log('\n[02:10 - 02:35] Phase 5: Catalogue Explorer & Model Benchmarks');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.click('.nav-tab[data-tab="catalogue"]');
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(15);
    await page.click('.nav-tab[data-tab="models"]');
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(10);

    // Phase 6: [02:35 - 03:00] SQLite Audit History & Neural Pipeline (25s = 100 frames)
    console.log('\n[02:35 - 03:00] Phase 6: SQLite Audit History & Neural Architecture');
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
    console.log('=== PROJECT-018 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
