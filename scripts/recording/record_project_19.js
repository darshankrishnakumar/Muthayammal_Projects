const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const outputVideo = '/Users/eash/Documents/antigravity/excited-borg/project_19_stock_management/walkthrough/walkthrough_video.mp4';
const ffmpegPath = '/opt/homebrew/bin/ffmpeg';

async function record() {
    console.log('=== Starting PROJECT-019 Video Recording Pipeline ===');
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

    // Phase 1: [00:00 - 00:30] Landing Overview & Stock Ledger (30s = 120 frames)
    console.log('\n[00:00 - 00:30] Phase 1: System Overview & Real-Time Warehouse Stock Ledger');
    await page.goto('http://127.0.0.1:5019/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(18);
    // Demonstrate quick restock action
    await page.evaluate(() => {
        const qtyInput = document.getElementById('restockQty');
        if (qtyInput) qtyInput.value = '25';
        restockItem();
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(12);

    // Phase 2: [00:30 - 01:05] IoT Hardware Terminal: Barcode Laser & UHF RFID Gate (35s = 140 frames)
    console.log('\n[00:30 - 01:05] Phase 2: IoT Hardware Terminal: Barcode Laser & UHF RFID Gate');
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab(1); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(10);
    // Select preset and trigger LOOKUP
    await page.evaluate(() => {
        document.getElementById('hardwareScanAction').value = 'LOOKUP';
        triggerHardwareScan();
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(10);
    // Trigger SALE auto-checkout
    await page.evaluate(() => {
        document.getElementById('hardwareScanAction').value = 'SALE';
        triggerHardwareScan();
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(15);

    // Phase 3: [01:05 - 01:30] Smart Weighing Shelf Telemetry & Shrinkage Detection (25s = 100 frames)
    console.log('\n[01:05 - 01:30] Phase 3: Smart Weighing Shelf Telemetry & Shrinkage Detection');
    // Test match
    await page.evaluate(() => {
        document.getElementById('scaleWeightInput').value = '10.0';
        testSmartScale();
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(12);
    // Test simulated shrinkage discrepancy (deficit)
    await page.evaluate(() => {
        document.getElementById('scaleWeightInput').value = '7.5';
        testSmartScale();
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(13);

    // Phase 4: [01:30 - 02:00] Wholesaler Purchase Orders & Logistics Cargo Tracking (30s = 120 frames)
    console.log('\n[01:30 - 02:00] Phase 4: Wholesaler Purchase Orders & Logistics Cargo Tracking');
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab(2); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(15);
    // Scroll down to shipments
    await page.evaluate(() => {
        const el = document.getElementById('shipmentsContainer');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(15);

    // Phase 5: [02:00 - 02:35] 7-Day AI Demand Forecasting & Dynamic ROP/EOQ (35s = 140 frames)
    console.log('\n[02:00 - 02:35] Phase 5: 7-Day AI Demand Forecasting & Dynamic ROP/EOQ');
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab(3); });
    await new Promise(r => setTimeout(r, 1000));
    await streamFrames(15);
    // Change SKU filter to SKU-001
    await page.evaluate(() => {
        const sel = document.getElementById('forecastSkuSelect');
        if (sel && sel.options.length > 1) {
            sel.selectedIndex = 1;
            changeForecastSku();
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(10);
    // Scroll to ROP table
    await page.evaluate(() => {
        const el = document.getElementById('ropAlertsBody');
        if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(10);

    // Phase 6: [02:35 - 03:00] Management Reports, Neural Architecture & SQLite Schema (25s = 100 frames)
    console.log('\n[02:35 - 03:00] Phase 6: Management Reports, Neural Architecture & SQLite Schema');
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab(4); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(10);
    await page.evaluate(() => { window.scrollTo(0, 0); switchTab(5); });
    await new Promise(r => setTimeout(r, 800));
    await streamFrames(10);
    // Scroll to database schema
    await page.evaluate(() => window.scrollTo(0, 400));
    await new Promise(r => setTimeout(r, 600));
    await streamFrames(5);

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
    console.log('=== PROJECT-019 Walkthrough Video Generation Complete ===');
}

record().catch(err => {
    console.error('Recording error:', err);
    process.exit(1);
});
