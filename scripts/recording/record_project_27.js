import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_27_academic_qa_rag/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-027 Video Recording Pipeline ===');
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
    // Phase 1: [00:00 - 00:30] Cockpit Overview & Telemetry Ribbon (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Academic QA Cockpit Overview & Telemetry Ribbon');
    await page.goto('http://127.0.0.1:5027/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Scroll slightly to focus on KPI telemetry strip and question prompt
    await page.evaluate(() => window.scrollTo({ top: 100, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Transformer Attention Query (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Attention Is All You Need Retrieval');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.setQuery === 'function') window.setQuery('transformer');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Focus on the synthesized answer
    await page.evaluate(() => {
        const el = document.getElementById('answerBox');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Provenance Citations & Cosine Chart (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Provenance Citations & Cosine Distribution Chart');
    await page.evaluate(() => {
        const el = document.getElementById('sourcesGrid');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Scroll slightly to feature the Chart.js cosine similarity bar chart
    await page.evaluate(() => {
        const chartEl = document.getElementById('simChart');
        if (chartEl) chartEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] Systems: Virtual Memory & TLB (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: Systems: Virtual Memory Paging & TLB');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.setQuery === 'function') window.setQuery('paging');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    await page.evaluate(() => {
        const el = document.getElementById('answerBox');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Algorithms & Distributed Consensus (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Algorithms (Dijkstra) & Raft Consensus');
    // Part A: Dijkstra Query
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.setQuery === 'function') window.setQuery('dijkstra');
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Part B: Raft Consensus Query
    await page.evaluate(async () => {
        document.getElementById('questionInput').value = "How does Raft consensus elect leaders and maintain replicated logs?";
        await window.askQuestion();
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Indexed Corpora Catalog & Verification (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Indexed Corpora Catalog & Verification');
    await page.evaluate(() => {
        const el = document.getElementById('corporaList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // Scroll back to top for closing view
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
