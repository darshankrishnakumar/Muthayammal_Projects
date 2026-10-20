import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_15_heart_disease_prediction/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-015 Video Recording Pipeline ===');
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

    console.log('\n[00:00 - 00:20] Step 1: Clinical Portal Landing & Medical Disclaimer (Port 5015)');
    await page.goto('http://127.0.0.1:5015/', { waitUntil: 'networkidle0' });
    await streamFrames(20);

    console.log('\n[00:20 - 00:45] Step 2: Clinical Feature Form & Integrated BMI Calculator');
    await page.evaluate(() => {
        const form = document.getElementById('predictionForm');
        if (form) form.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await streamFrames(25);

    console.log('\n[00:45 - 01:15] Step 3: High-Risk Patient Evaluation & Critical Alert Banner');
    await page.evaluate(() => {
        const setVal = (name, val) => {
            const el = document.querySelector(`[name="${name}"]`);
            if (el) {
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        };
        setVal('Age', 64);
        setVal('Sex', 1);
        setVal('ChestPainType', 3);
        setVal('RestingBP', 160);
        setVal('Cholesterol', 290);
        setVal('FastingBS', 1);
        setVal('RestingECG', 2);
        setVal('MaxHR', 105);
        setVal('ExerciseAngina', 1);
        setVal('Oldpeak', 3.2);
        setVal('ST_Slope', 2);
    });
    await new Promise(r => setTimeout(r, 600));
    await page.evaluate(() => {
        const submitBtn = document.querySelector('button.submit-btn');
        if (submitBtn) submitBtn.click();
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.evaluate(() => {
        const resCard = document.querySelector('.result-card');
        if (resCard) resCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await streamFrames(30);

    console.log('\n[01:15 - 01:45] Step 4: Vital Signs Comparison Chart vs Normal Population');
    await page.evaluate(() => {
        const dash = document.getElementById('dashboard');
        if (dash) dash.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    await streamFrames(30);

    console.log('\n[01:45 - 02:10] Step 5: Cardiovascular Radar Profile & Multi-Factor Polygon');
    await page.evaluate(() => {
        const radarCard = document.querySelector('.secondary-card');
        if (radarCard) radarCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await streamFrames(25);

    console.log('\n[02:10 - 02:35] Step 6: Risk Breakdown & Trend Analytics');
    await page.evaluate(() => {
        const cards = document.querySelectorAll('.dashboard-card');
        if (cards.length > 2) {
            cards[2].scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            window.scrollTo({ top: document.body.scrollHeight * 0.7, behavior: 'smooth' });
        }
    });
    await streamFrames(25);

    console.log('\n[02:35 - 02:50] Step 7: Low-Risk Patient Baseline Clearance & Clean Vitals');
    await page.evaluate(() => {
        const setVal = (name, val) => {
            const el = document.querySelector(`[name="${name}"]`);
            if (el) {
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        };
        setVal('Age', 32);
        setVal('Sex', 0);
        setVal('ChestPainType', 1);
        setVal('RestingBP', 115);
        setVal('Cholesterol', 175);
        setVal('FastingBS', 0);
        setVal('RestingECG', 0);
        setVal('MaxHR', 178);
        setVal('ExerciseAngina', 0);
        setVal('Oldpeak', 0.0);
        setVal('ST_Slope', 0);
    });
    await new Promise(r => setTimeout(r, 600));
    await page.evaluate(() => {
        const submitBtn = document.querySelector('button.submit-btn');
        if (submitBtn) submitBtn.click();
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.evaluate(() => {
        const resCard = document.querySelector('.result-card');
        if (resCard) resCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
    console.log('=== PROJECT-015 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
