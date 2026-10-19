import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_29_sign_language/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-029 Video Recording Pipeline ===');
    console.log(`Target Output: ${outputVideo}`);

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

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 1: [00:00 - 00:30] System Overview & 21-Joint Mesh (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: System Overview, Health Telemetry & 21-Joint Mesh');
    await page.goto('http://127.0.0.1:5029/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Scroll slightly to focus on 3D skeletal canvas and metrics
    await page.evaluate(() => window.scrollTo({ top: 40, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Conversational Sign Translation (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Conversational Sign Translation (HELLO, I LOVE YOU, WATER)');
    // Part A: HELLO
    await page.evaluate(() => {
        if (typeof window.triggerSign === 'function') window.triggerSign('HELLO');
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(40);

    // Part B: I LOVE YOU
    await page.evaluate(() => {
        if (typeof window.triggerSign === 'function') window.triggerSign('I LOVE YOU');
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(40);

    // Part C: WATER
    await page.evaluate(() => {
        if (typeof window.triggerSign === 'function') window.triggerSign('WATER');
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(40);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Critical Emergency & Medical Mode (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Critical Emergency & Medical Mode (HELP, EMERGENCY, DOCTOR)');
    // Part A: HELP
    await page.evaluate(() => {
        if (typeof window.triggerSign === 'function') window.triggerSign('HELP');
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(40);

    // Part B: EMERGENCY
    await page.evaluate(() => {
        if (typeof window.triggerSign === 'function') window.triggerSign('EMERGENCY');
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(40);

    // Part C: DOCTOR
    await page.evaluate(() => {
        if (typeof window.triggerSign === 'function') window.triggerSign('DOCTOR');
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(40);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] A-Z Manual Alphabet Fingerspelling (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: A-Z Manual Alphabet Fingerspelling');
    // Part A: A
    await page.evaluate(() => {
        if (typeof window.triggerSign === 'function') window.triggerSign('A');
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(30);

    // Part B: L
    await page.evaluate(() => {
        if (typeof window.triggerSign === 'function') window.triggerSign('L');
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(30);

    // Part C: Y
    await page.evaluate(() => {
        if (typeof window.triggerSign === 'function') window.triggerSign('Y');
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(30);

    // Part D: Z
    await page.evaluate(() => {
        if (typeof window.triggerSign === 'function') window.triggerSign('Z');
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(30);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Live Sentence Stream & Speech Output (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Live Sentence Stream & Speech Output');
    await page.evaluate(async () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.triggerSign === 'function') {
            await window.triggerSign('PLEASE');
            await window.triggerSign('THANK YOU');
        }
        if (typeof window.speakCurrentSentence === 'function') {
            window.speakCurrentSentence();
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Focus on sentence bar and copy action
    await page.evaluate(() => {
        const el = document.querySelector('.sentence-bar');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Historical Translation Ledger & Conformance (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Historical Translation Ledger & Conformance');
    await page.evaluate(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Scroll smoothly to top for closing view
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    console.log(`\nCompleted streaming ${frameCount} frames.`);
    await browser.close();

    ffmpeg.stdin.end();

    await new Promise((resolve, reject) => {
        ffmpeg.on('close', (code) => {
            if (code === 0) {
                console.log(`FFmpeg encoding completed successfully: ${outputVideo}`);
                resolve();
            } else {
                reject(new Error(`FFmpeg exited with code ${code}`));
            }
        });
    });
}

record().catch((err) => {
    console.error('Recording error:', err);
    process.exit(1);
});
