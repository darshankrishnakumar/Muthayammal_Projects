const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const path = require('path');

const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_16_medical_sensor_disease_prediction/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-016 Video Recording Pipeline ===');
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

    console.log('\n[00:00 - 00:25] Phase 1: Clinical Command Center & Telemetry Overview');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(25);

    console.log('\n[00:25 - 00:55] Phase 2: ECG Signal Ingestion & Lead II Canvas');
    await page.goto('http://localhost:5173/ecg', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(30);

    console.log('\n[00:55 - 01:25] Phase 3: 1D CNN Inference & Arrhythmia Classification');
    await page.goto('http://localhost:5173/predictions', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(30);

    console.log('\n[01:25 - 01:50] Phase 4: Multi-Parameter Vitals Monitoring');
    await page.goto('http://localhost:5173/monitoring', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(25);

    console.log('\n[01:50 - 02:15] Phase 5: Evidence-Based Clinical Recommendations');
    await page.goto('http://localhost:5173/recommendations', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(25);

    console.log('\n[02:15 - 02:40] Phase 6: Diagnostic Reports & Critical Alert Center');
    await page.goto('http://localhost:5173/reports', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(25);

    console.log('\n[02:40 - 03:00] Phase 7: Historical Archive & System Sign-Off');
    await page.goto('http://localhost:5173/history', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(20);

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
    console.log('=== PROJECT-016 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
