import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_23_meeting_summarization/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-023 Video Recording Pipeline ===');
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
    // Phase 1: [00:00 - 00:30] Overview & Telematics Metric Strip (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Overview & Telematics Metric Strip');
    await page.goto('http://127.0.0.1:5023/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Scroll to charts (Speaker Donut & Radar Chart)
    await page.evaluate(() => window.scrollTo({ top: 350, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Cloud Architecture Review Summarization (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Cloud Architecture Review Summarization');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof setPreset === 'function') setPreset('cloud');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Scroll down to observe executive summary and action items
    await page.evaluate(() => window.scrollTo({ top: 200, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Sprint Planning & Blocker Triage (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Sprint Planning & Blocker Triage');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof setPreset === 'function') setPreset('sprint');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Observe extracted tasks & decisions
    await page.evaluate(() => window.scrollTo({ top: 220, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Product Launch Retrospective & Diagnostics (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Product Launch Retrospective & Diagnostics');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof setPreset === 'function') setPreset('launch');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Focus on speaker donut and radar quality profile
    await page.evaluate(() => window.scrollTo({ top: 320, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Custom Incident Postmortem Ingestion (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Custom Incident Postmortem Ingestion');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        const titleEl = document.getElementById('meetingTitle');
        const inputEl = document.getElementById('transcriptInput');
        if (titleEl) titleEl.value = "P1 Redis Cluster Failover Postmortem";
        if (inputEl) {
            inputEl.value = `[Sarah (Incident Lead)]: Let's review the Redis session cluster failover event from yesterday.
[Marcus (Chief Architect)]: I will implement circuit breaker thresholds in the gateway by Thursday.
[Elena (DevOps SRE)]: We decided to scale cluster nodes from 3 to 6 replicas before the weekend.
[David (Engineering Mgr)]: I will publish the root-cause summary to enterprise customers by tomorrow.`;
        }
        if (typeof runSummarize === 'function') runSummarize();
    });
    await new Promise(r => setTimeout(r, 1400));
    await streamFrames(60);

    // Observe newly extracted postmortem tasks
    await page.evaluate(() => window.scrollTo({ top: 220, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Processed Archives & Interactive Checkboxes (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Processed Archives & Interactive Checkboxes');
    // Toggle checkboxes on action items
    await page.evaluate(() => {
        const checkboxes = document.querySelectorAll('#resActionList input[type="checkbox"]');
        if (checkboxes.length > 0) checkboxes[0].checked = true;
        if (checkboxes.length > 1) checkboxes[1].checked = true;
    });
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(40);

    // Scroll to historical archive ledger
    await page.evaluate(() => {
        const el = document.getElementById('meetingArchiveList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(80);

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
    console.log('=== PROJECT-023 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
