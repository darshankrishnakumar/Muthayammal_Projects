import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_26_network_intrusion/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function capture() {
    console.log('=== Capturing PROJECT-026 High-Resolution Screenshots ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,900']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });

    // 1. Dashboard Overview
    console.log('Capturing 01_nids_telematics_dashboard.png...');
    await page.goto('http://127.0.0.1:5026/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_nids_telematics_dashboard.png') });

    // 2. Live Packet Flows & Radar
    console.log('Capturing 02_live_packet_flows_radar.png...');
    await page.evaluate(() => window.scrollTo({ top: 120, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '02_live_packet_flows_radar.png') });

    // 3. Attack Injection Studio
    console.log('Capturing 03_attack_injection_testbench.png...');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.switchTab === 'function') window.switchTab(1);
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '03_attack_injection_testbench.png') });

    // 4. SYN Flood Attack Triggered
    console.log('Capturing 04_syn_flood_interdiction.png...');
    await page.evaluate(async () => {
        if (typeof window.triggerAttack === 'function') await window.triggerAttack('SYN_Flood');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_syn_flood_interdiction.png') });

    // 5. Zero-Day Anomaly Triggered
    console.log('Capturing 05_zero_day_shellcode_anomaly.png...');
    await page.evaluate(async () => {
        if (typeof window.triggerAttack === 'function') await window.triggerAttack('Zero_Day');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_zero_day_shellcode_anomaly.png') });

    // 6. Autoencoder Reconstruction Loss Tab
    console.log('Capturing 06_autoencoder_reconstruction_gauge.png...');
    await page.evaluate(() => {
        if (typeof window.switchTab === 'function') window.switchTab(2);
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '06_autoencoder_reconstruction_gauge.png') });

    // 7. Firewall Quarantine Blacklist Tab
    console.log('Capturing 07_firewall_quarantine_blacklist.png...');
    await page.evaluate(() => {
        if (typeof window.switchTab === 'function') window.switchTab(3);
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '07_firewall_quarantine_blacklist.png') });

    // 8. Automated Firewall Rules Scripts
    console.log('Capturing 08_automated_iptables_ufw_rules.png...');
    await page.evaluate(() => {
        const box = document.getElementById('iptablesRulesBox');
        if (box) box.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '08_automated_iptables_ufw_rules.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Captured Successfully ===');
}

capture().catch(err => {
    console.error('Screenshot capture failed:', err);
    process.exit(1);
});
