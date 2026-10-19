import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_24_financial_fraud_gnn/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function run() {
    console.log('=== Starting Screenshot Capture for PROJECT-024 ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('http://127.0.0.1:5024', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));

    // 1. Dashboard Overview & Metric Strip
    console.log('Capturing 01_dashboard_topology_overview.png...');
    await page.screenshot({ path: path.join(outDir, '01_dashboard_topology_overview.png') });

    // 2. Zoomed Graph Canvas Topology
    console.log('Capturing 02_force_directed_graph_canvas.png...');
    await page.evaluate(() => {
        const canvas = document.getElementById('graphCanvas');
        if (canvas) {
            window.scrollTo({ top: 100, behavior: 'smooth' });
        }
    });
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(outDir, '02_force_directed_graph_canvas.png') });

    // 3. Node Forensic Drawer Inspector
    console.log('Capturing 03_node_forensic_drawer_inspector.png...');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        // Select a critical node
        if (typeof window.selectNode === 'function' && window.graphData && window.graphData.nodes) {
            const critNode = window.graphData.nodes.find(n => n.id === 'RING-201' || n.risk > 0.85);
            if (critNode) {
                window.selectNode(critNode);
            }
        }
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '03_node_forensic_drawer_inspector.png') });

    // 4. Syndicate Pattern Hunter Tab
    console.log('Capturing 04_syndicate_pattern_hunter.png...');
    await page.evaluate(() => {
        const tabs = document.querySelectorAll('.tab-btn');
        if (tabs[1]) tabs[1].click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '04_syndicate_pattern_hunter.png') });

    // 5. GNN Node Embeddings Matrix Tab
    console.log('Capturing 05_gnn_node_embeddings_matrix.png...');
    await page.evaluate(() => {
        const tabs = document.querySelectorAll('.tab-btn');
        if (tabs[2]) tabs[2].click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '05_gnn_node_embeddings_matrix.png') });

    // 6. FinCEN SAR Regulatory Compliance Tab
    console.log('Capturing 06_fincen_sar_regulatory_table.png...');
    await page.evaluate(() => {
        const tabs = document.querySelectorAll('.tab-btn');
        if (tabs[3]) tabs[3].click();
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '06_fincen_sar_regulatory_table.png') });

    // 7. Account Freeze Sanctions Action
    console.log('Capturing 07_account_freeze_sanction_modal.png...');
    await page.evaluate(async () => {
        const tabs = document.querySelectorAll('.tab-btn');
        if (tabs[0]) tabs[0].click();
        if (window.graphData && window.graphData.nodes && window.graphData.nodes.length > 0) {
            const critNode = window.graphData.nodes.find(n => n.id === 'RING-201' || n.risk > 0.85) || window.graphData.nodes[0];
            if (critNode) {
                if (typeof window.selectNode === 'function') await window.selectNode(critNode);
                if (typeof window.toggleFreezeCurrentNode === 'function') await window.toggleFreezeCurrentNode();
            }
        }
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '07_account_freeze_sanction_modal.png') });

    // 8. Dynamic Laundering Injection
    console.log('Capturing 08_dynamic_laundering_injection.png...');
    await page.evaluate(async () => {
        const tabs = document.querySelectorAll('.tab-btn');
        if (tabs[0]) tabs[0].click();
        // Trigger injection
        try {
            await fetch('http://127.0.0.1:5024/api/simulate/ring', { method: 'POST' });
            await window.loadGraph();
        } catch(e){}
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(outDir, '08_dynamic_laundering_injection.png') });

    await browser.close();
    console.log('=== All 8 Screenshots Successfully Captured ===');
}

run().catch(err => {
    console.error('Error capturing screenshots:', err);
    process.exit(1);
});
