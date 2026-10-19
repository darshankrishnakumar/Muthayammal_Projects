import puppeteer from 'puppeteer-core';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_24_financial_fraud_gnn/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-024 Video Recording Pipeline ===');
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
    // Phase 1: [00:00 - 00:30] Dashboard Overview & Global Network Telematics (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:00 - 00:30] Phase 1: Dashboard Overview & Global Network Telematics');
    await page.goto('http://127.0.0.1:5024/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Scroll slightly down to showcase graph canvas physics & telematics banner
    await page.evaluate(() => window.scrollTo({ top: 120, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 2: [00:30 - 01:00] Deep Forensic Node Inspection & Attribution (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[00:30 - 01:00] Phase 2: Deep Forensic Node Inspection & Attribution');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (window.graphData && window.graphData.nodes) {
            const target = window.graphData.nodes.find(n => n.id === 'RING-201' || n.risk > 0.85);
            if (target && typeof window.selectNode === 'function') {
                window.selectNode(target);
            }
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Inspect drawer dossier details and GNN explanation
    await page.evaluate(() => {
        const drawer = document.getElementById('nodeDrawer');
        if (drawer) drawer.scrollTop = 150;
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 3: [01:00 - 01:30] Automated Syndicate Pattern Hunter (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:00 - 01:30] Phase 3: Automated Syndicate Pattern Hunter');
    await page.evaluate(() => {
        const tabs = document.querySelectorAll('.tab-btn');
        if (tabs[1]) tabs[1].click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Click focus on ring button or inspect pattern details
    await page.evaluate(() => {
        const btn = document.querySelector('#patternDetailsBox button');
        if (btn) btn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 4: [01:30 - 02:00] GNN Latent Space Embeddings (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[01:30 - 02:00] Phase 4: GNN Latent Space Embeddings Matrix');
    await page.evaluate(() => {
        const tabs = document.querySelectorAll('.tab-btn');
        if (tabs[2]) tabs[2].click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Scroll embeddings table
    await page.evaluate(() => window.scrollTo({ top: 240, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 5: [02:00 - 02:30] Regulatory FinCEN SAR & Account Freeze (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:00 - 02:30] Phase 5: Regulatory FinCEN SAR & Account Freeze');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        const tabs = document.querySelectorAll('.tab-btn');
        if (tabs[3]) tabs[3].click();
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Trigger an account freeze from SAR table
    await page.evaluate(async () => {
        const freezeBtns = document.querySelectorAll('#sarTableBody button');
        if (freezeBtns.length > 0) freezeBtns[0].click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(60);

    // ─────────────────────────────────────────────────────────────────────────
    // Phase 6: [02:30 - 03:00] Dynamic Laundering Injection & Stress Testing (120 frames)
    // ─────────────────────────────────────────────────────────────────────────
    console.log('\n[02:30 - 03:00] Phase 6: Dynamic Laundering Injection & Stress Testing');
    await page.evaluate(async () => {
        const tabs = document.querySelectorAll('.tab-btn');
        if (tabs[0]) tabs[0].click();
        try {
            await fetch('http://127.0.0.1:5024/api/simulate/ring', { method: 'POST' });
            if (typeof window.loadGraph === 'function') await window.loadGraph();
        } catch(e){}
    });
    await new Promise(r => setTimeout(r, 1200));
    await streamFrames(60);

    // Final pan across updated topology
    await page.evaluate(() => {
        window.scrollTo({ top: 50, behavior: 'smooth' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(60);

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
    console.log('=== PROJECT-024 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
