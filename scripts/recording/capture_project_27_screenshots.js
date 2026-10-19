import puppeteer from 'puppeteer-core';
import path from 'path';
import fs from 'fs';

const chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const outDir = '/Users/eash/Documents/antigravity/excited-borg/project_27_academic_qa_rag/docs/screenshots';

if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

async function capture() {
    console.log('=== Capturing PROJECT-027 High-Resolution Screenshots ===');
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,900']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });

    // 1. Dashboard Overview
    console.log('Capturing 01_rag_system_dashboard.png...');
    await page.goto('http://127.0.0.1:5027/', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '01_rag_system_dashboard.png') });

    // 2. Transformer Attention Query
    console.log('Capturing 02_transformer_attention_retrieval.png...');
    await page.evaluate(() => {
        if (typeof window.setQuery === 'function') window.setQuery('transformer');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '02_transformer_attention_retrieval.png') });

    // 3. Source Citations & Cosine Chart
    console.log('Capturing 03_source_citations_evidence.png...');
    await page.evaluate(() => window.scrollTo({ top: 380, behavior: 'smooth' }));
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '03_source_citations_evidence.png') });

    // 4. Virtual Memory & TLB Query
    console.log('Capturing 04_virtual_memory_tlb_query.png...');
    await page.evaluate(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (typeof window.setQuery === 'function') window.setQuery('paging');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '04_virtual_memory_tlb_query.png') });

    // 5. Dijkstra Algorithm Query
    console.log('Capturing 05_dijkstra_shortest_path_analysis.png...');
    await page.evaluate(() => {
        if (typeof window.setQuery === 'function') window.setQuery('dijkstra');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '05_dijkstra_shortest_path_analysis.png') });

    // 6. Database ACID & WAL Query
    console.log('Capturing 06_database_acid_wal_recovery.png...');
    await page.evaluate(() => {
        if (typeof window.setQuery === 'function') window.setQuery('wal');
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '06_database_acid_wal_recovery.png') });

    // 7. Raft Consensus Query
    console.log('Capturing 07_raft_consensus_distributed.png...');
    await page.evaluate(async () => {
        document.getElementById('questionInput').value = "How does Raft consensus elect leaders and maintain replicated logs?";
        await window.askQuestion();
    });
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(outDir, '07_raft_consensus_distributed.png') });

    // 8. Indexed Academic Corpora Scrolled
    console.log('Capturing 08_indexed_academic_corpora.png...');
    await page.evaluate(() => {
        const el = document.getElementById('corporaList');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(outDir, '08_indexed_academic_corpora.png') });

    await browser.close();
    console.log('=== All 8 Screenshots captured successfully ===');
}

capture().catch(err => {
    console.error('Capture failed:', err);
    process.exit(1);
});
