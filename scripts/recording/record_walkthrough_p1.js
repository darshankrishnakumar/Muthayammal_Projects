const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

async function recordWalkthrough() {
  console.log('--- STARTING PROJECT-001 WALKTHROUGH RECORDING ---');
  
  const pdir = path.resolve(__dirname, 'project_01_airfare_price_prediction');
  const screenshotsDir = path.join(pdir, 'docs', 'screenshots');
  const walkthroughDir = path.join(pdir, 'walkthrough');
  const framesDir = path.join(walkthroughDir, 'frames');
  const videoPath = path.join(walkthroughDir, 'walkthrough_video.mp4');

  fs.mkdirSync(screenshotsDir, { recursive: true });
  fs.mkdirSync(framesDir, { recursive: true });

  // Clean old frames
  fs.readdirSync(framesDir).forEach(f => fs.unlinkSync(path.join(framesDir, f)));

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  let frameCount = 0;
  let capturing = true;

  // Frame capture loop at ~10 fps
  async function captureFrame() {
    if (!capturing) return;
    try {
      const buffer = await page.screenshot({ type: 'jpeg', quality: 85 });
      const frameName = path.join(framesDir, `frame_${String(frameCount).padStart(5, '0')}.jpg`);
      fs.writeFileSync(frameName, buffer);
      frameCount++;
    } catch (e) {
      // ignore transient capture errors
    }
    if (capturing) {
      setTimeout(captureFrame, 100);
    }
  }

  // Start frame loop
  captureFrame();

  // Helper wait
  const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  console.log('[1/8] Navigating to http://127.0.0.1:5001/...');
  await page.goto('http://127.0.0.1:5001/', { waitUntil: 'networkidle0' });
  await wait(2000);
  await page.screenshot({ path: path.join(screenshotsDir, '01_dashboard_empty.png') });

  console.log('[2/8] Configuring first flight: IndiGo Banglore -> Delhi (Non-Stop)...');
  await page.select('#airlineSelect', 'IndiGo');
  await page.select('#sourceSelect', 'Banglore');
  await page.select('#destSelect', 'Delhi');
  await page.select('#totalStops', '0');
  await wait(1500);

  console.log('[3/8] Triggering LSTM & RF Prediction...');
  await page.click('#predictBtn');
  await wait(3000); // Wait for inference and banner render
  await page.screenshot({ path: path.join(screenshotsDir, '02_prediction_results_indigo.png') });

  console.log('[4/8] Configuring second flight: Air India Delhi -> Cochin (2 Stops)...');
  await page.select('#airlineSelect', 'Air India');
  await page.select('#sourceSelect', 'Delhi');
  await page.select('#destSelect', 'Cochin');
  await page.select('#totalStops', '2');
  await page.type('#depTime', '06:30');
  await page.type('#arrivalTime', '14:45');
  await wait(1500);

  console.log('[5/8] Predicting multi-stop Air India flight...');
  await page.click('#predictBtn');
  await wait(3000);
  await page.screenshot({ path: path.join(screenshotsDir, '03_prediction_results_airindia.png') });

  console.log('[6/8] Navigating to Model Performance Tab...');
  await page.evaluate(() => switchTab('performance'));
  await wait(3000);
  await page.screenshot({ path: path.join(screenshotsDir, '04_model_performance.png') });

  console.log('[7/8] Navigating to Prediction History Tab (SQLite Persistence)...');
  await page.evaluate(() => switchTab('history'));
  await wait(3000);
  await page.screenshot({ path: path.join(screenshotsDir, '05_prediction_history.png') });

  console.log('[8/8] Navigating to Pricing Analytics Tab...');
  await page.evaluate(() => switchTab('analytics'));
  await wait(3000);
  await page.screenshot({ path: path.join(screenshotsDir, '06_pricing_analytics.png') });

  // Switch back to valuation engine
  await page.evaluate(() => switchTab('predictor'));
  await wait(2000);

  capturing = false;
  await wait(500);
  await browser.close();

  console.log(`Total frames captured: ${frameCount}`);
  console.log('Encoding frames to MP4 with ffmpeg...');

  // Use ffmpeg to encode frames into standard H.264 MP4
  const ffmpegCmd = [
    '-y',
    '-framerate', '10',
    '-i', path.join(framesDir, 'frame_%05d.jpg'),
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-r', '24',
    videoPath
  ];

  const ffmpeg = spawn('/opt/homebrew/bin/ffmpeg', ffmpegCmd);
  
  ffmpeg.stderr.on('data', (d) => {
    // console.log(d.toString());
  });

  ffmpeg.on('close', (code) => {
    if (code === 0) {
      const stats = fs.statSync(videoPath);
      console.log(`SUCCESS: Video encoded at ${videoPath} (${stats.size} bytes)`);
      // Clean up frames to save disk space
      fs.readdirSync(framesDir).forEach(f => fs.unlinkSync(path.join(framesDir, f)));
      fs.rmdirSync(framesDir);
    } else {
      console.error(`ffmpeg failed with code ${code}`);
    }
  });
}

recordWalkthrough().catch(console.error);
