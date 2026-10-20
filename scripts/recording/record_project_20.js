import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_20_weapon_detection/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-020 Video Recording Pipeline ===');
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

    // Phase 1: [00:00 - 00:30] System Overview & Live Detection Console HUD (120 frames)
    console.log('\n[00:00 - 00:30] Phase 1: System Overview & Live Detection Console HUD');
    await page.goto('http://127.0.0.1:5020/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Test civilian clearance preset
    await page.evaluate(() => {
        if (typeof loadPreset === 'function') loadPreset('safe');
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Phase 2: [00:30 - 01:05] Weapon Detection: Handgun & Tactical Knife Interdiction (140 frames)
    console.log('\n[00:30 - 01:05] Phase 2: Weapon Detection: Handgun & Tactical Knife Interdiction');
    await page.evaluate(() => {
        if (typeof loadPreset === 'function') loadPreset('handgun');
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(70);

    // Switch to knife preset
    await page.evaluate(() => {
        if (typeof loadPreset === 'function') loadPreset('knife');
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(70);

    // Phase 3: [01:05 - 01:35] Dual Compare Surveillance Viewport (120 frames)
    console.log('\n[01:05 - 01:35] Phase 3: Dual Compare Surveillance Viewport (Raw vs Neural)');
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab('dual'); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(120);

    // Phase 4: [01:35 - 02:05] Threat Heatmap & Security Radio Dispatch (120 frames)
    console.log('\n[01:35 - 02:05] Phase 4: Threat Heatmap & Security Radio Dispatch');
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab('heatmap'); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Switch to radio tab
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab('radio'); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Phase 5: [02:05 - 02:35] CCTV 4-Camera Wall & Emergency Lockdown Drill (120 frames)
    console.log('\n[02:05 - 02:35] Phase 5: CCTV 4-Camera Wall & Emergency Lockdown Drill');
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab('cctv'); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // Engage lockdown drill
    await page.evaluate(() => {
        if (typeof triggerLockdown === 'function') triggerLockdown();
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(40);

    // Disengage lockdown
    await page.evaluate(() => {
        if (typeof triggerLockdown === 'function') triggerLockdown();
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(20);

    // Phase 6: [02:35 - 03:00] YOLOv8 Model Architecture, SQLite Audit & Analytics (100 frames)
    console.log('\n[02:35 - 03:00] Phase 6: YOLOv8 Model Architecture, SQLite Audit & Analytics');
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab('model'); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(35);

    // Switch to logs tab
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab('logs'); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(35);

    // Switch to analytics tab
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab('analytics'); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(30);

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
    console.log('=== PROJECT-020 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
