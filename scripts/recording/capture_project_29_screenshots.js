const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function captureScreenshots() {
  const screenshotDir = path.resolve(__dirname, '../../project_29_sign_language/docs/screenshots');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  const sleep = ms => new Promise(r => setTimeout(r, ms));
  console.log('Navigating to http://127.0.0.1:5029/...');
  await page.goto('http://127.0.0.1:5029/', { waitUntil: 'networkidle0' });
  await sleep(1000);

  // 1. Overview Dashboard
  console.log('Capturing 01_sign_language_translator_dashboard.png...');
  await page.screenshot({ path: path.join(screenshotDir, '01_sign_language_translator_dashboard.png') });

  // 2. 3D Skeletal Hand Canvas
  console.log('Triggering I LOVE YOU gesture and capturing canvas...');
  await page.evaluate(() => window.triggerSign('I LOVE YOU'));
  await sleep(1000);
  console.log('Capturing 02_3d_skeletal_hand_canvas.png...');
  await page.screenshot({ path: path.join(screenshotDir, '02_3d_skeletal_hand_canvas.png') });

  // 3. Top-5 Candidate Probabilities Chart
  console.log('Triggering WATER gesture...');
  await page.evaluate(() => window.triggerSign('WATER'));
  await sleep(1000);
  console.log('Capturing 03_top5_candidate_probabilities_chart.png...');
  await page.screenshot({ path: path.join(screenshotDir, '03_top5_candidate_probabilities_chart.png') });

  // 4. Alphabet Fingerspelling Palette
  console.log('Triggering alphabet letter Y...');
  await page.evaluate(() => window.triggerSign('Y'));
  await sleep(800);
  console.log('Capturing 04_alphabet_fingerspelling_palette.png...');
  await page.screenshot({ path: path.join(screenshotDir, '04_alphabet_fingerspelling_palette.png') });

  // 5. Live Sentence Assembly Stream
  console.log('Triggering sequence of signs for sentence bar...');
  await page.evaluate(async () => {
    await window.triggerSign('HELLO');
    await window.triggerSign('PLEASE');
    await window.triggerSign('HELP');
  });
  await sleep(1000);
  console.log('Capturing 05_live_sentence_assembly_stream.png...');
  await page.screenshot({ path: path.join(screenshotDir, '05_live_sentence_assembly_stream.png') });

  // 6. Emergency & Medical Signs Mode
  console.log('Triggering EMERGENCY gesture...');
  await page.evaluate(() => window.triggerSign('EMERGENCY'));
  await sleep(1000);
  console.log('Capturing 06_emergency_medical_signs_mode.png...');
  await page.screenshot({ path: path.join(screenshotDir, '06_emergency_medical_signs_mode.png') });

  // 7. Speech Synthesis Audio Output
  console.log('Triggering DOCTOR sign with speech invocation...');
  await page.evaluate(() => {
    window.triggerSign('DOCTOR');
    window.speakCurrentSentence();
  });
  await sleep(1000);
  console.log('Capturing 07_speech_synthesis_audio_output.png...');
  await page.screenshot({ path: path.join(screenshotDir, '07_speech_synthesis_audio_output.png') });

  // 8. Translation History Audit Ledger
  console.log('Scrolling down to historical ledger...');
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await sleep(1000);
  console.log('Capturing 08_translation_history_audit_ledger.png...');
  await page.screenshot({ path: path.join(screenshotDir, '08_translation_history_audit_ledger.png') });

  await browser.close();
  console.log('All 8 screenshots captured successfully!');
}

captureScreenshots().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
