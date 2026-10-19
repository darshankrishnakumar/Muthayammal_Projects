import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_22_customer_complaint_classification/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-022 Video Recording Pipeline ===');
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

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 1: [00:00 - 00:30] Overview & Telematics KPI Cockpit (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Overview & Telematics KPI Cockpit');
    await page.goto('http://127.0.0.1:5022/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Scroll to charts
    await page.evaluate(() => window.scrollTo({ top: 350, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Critical Billing Dispute Classification (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Critical Billing Dispute Classification');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof setPreset === 'function') setPreset('billing');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Focus on result card & probability distribution
    await page.evaluate(() => window.scrollTo({ top: 220, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Hardware Defect & Warranty RMA Routing (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Hardware Defect & Warranty RMA Routing');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof setPreset === 'function') setPreset('rma');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Observe updated department routing & SLA deadline
    await page.evaluate(() => window.scrollTo({ top: 240, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Software Bug & Platform DevOps Outage (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Software Bug & Platform DevOps Outage');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof setPreset === 'function') setPreset('api');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Observe probability spike on tech issue & high urgency
    await page.evaluate(() => window.scrollTo({ top: 260, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] IAM Security Lockout & Custom Logistics Input (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: IAM Security Lockout & Custom Logistics Input');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof setPreset === 'function') setPreset('auth');
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(50);

    // Clear and enter custom logistics complaint
    await page.evaluate(() => {
        const input = document.getElementById('complaintInput');
        if (input) {
            input.value = "Air shipment container #ORB-99120 has been delayed in customs for 11 days. Assembly line blocked.";
        }
        if (typeof submitComplaint === 'function') submitComplaint();
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(70);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Ticket Management Table, Filters & CSV Export (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Ticket Management Table, Filters & CSV Export');
    await page.evaluate(() => {
        const el = document.getElementById('ticketTbody');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(30);

    // Filter by priority: critical
    await page.evaluate(() => {
        const filterPri = document.getElementById('filterPriority');
        if (filterPri) {
            filterPri.value = 'critical';
            renderTable();
        }
    });
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(30);

    // Filter by category: payment_issue
    await page.evaluate(() => {
        const filterCat = document.getElementById('filterCategory');
        if (filterCat) {
            filterCat.value = 'payment_issue';
            renderTable();
        }
    });
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(30);

    // Reset filters
    await page.evaluate(() => {
        document.getElementById('filterPriority').value = 'ALL';
        document.getElementById('filterCategory').value = 'ALL';
        renderTable();
    });
    await new Promise(r => setTimeout(r, 600));
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
    console.log('=== PROJECT-022 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
