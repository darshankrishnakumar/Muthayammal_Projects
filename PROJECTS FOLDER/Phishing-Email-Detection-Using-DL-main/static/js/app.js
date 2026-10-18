document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    // Header & Body Inputs
    const hdrFrom = document.getElementById('hdrFrom');
    const hdrReplyTo = document.getElementById('hdrReplyTo');
    const hdrSpfDkim = document.getElementById('hdrSpfDkim');
    const hdrSubject = document.getElementById('hdrSubject');
    const emailInput = document.getElementById('emailInput');
    const charCounter = document.getElementById('charCounter');
    
    const modelSelect = document.getElementById('modelSelect');
    const scanBtn = document.getElementById('scanBtn');
    const clearBtn = document.getElementById('clearBtn');
    const presetChips = document.querySelectorAll('.preset-chip');
    
    const emptyState = document.getElementById('emptyState');
    const resultsState = document.getElementById('resultsState');
    const verdictStatusBadge = document.getElementById('verdictStatusBadge');
    
    const verdictBanner = document.getElementById('verdictBanner');
    const gaugeProgress = document.getElementById('gaugeProgress');
    const threatScoreValue = document.getElementById('threatScoreValue');
    const predictionTag = document.getElementById('predictionTag');
    const verdictHeadline = document.getElementById('verdictHeadline');
    const verdictSummary = document.getElementById('verdictSummary');
    const consensusText = document.getElementById('consensusText');
    
    const headerRiskBar = document.getElementById('headerRiskBar');
    const headerRiskVal = document.getElementById('headerRiskVal');
    const bodyRiskBar = document.getElementById('bodyRiskBar');
    const bodyRiskVal = document.getElementById('bodyRiskVal');
    
    const headerAlertsBox = document.getElementById('headerAlertsBox');
    const headerAlertsList = document.getElementById('headerAlertsList');
    const attentionHeatmap = document.getElementById('attentionHeatmap');
    const modelBarsContainer = document.getElementById('modelBarsContainer');
    const benchmarkTableBody = document.getElementById('benchmarkTableBody');

    let samplesCache = [];

    // --- Tab Navigation ---
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');
            navTabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            tab.classList.add('active');
            const targetPane = document.getElementById(`tab-${targetTab}`);
            if (targetPane) targetPane.classList.add('active');
        });
    });

    // --- Character Counter ---
    emailInput.addEventListener('input', () => {
        const len = emailInput.value.length;
        charCounter.textContent = `${len.toLocaleString()} characters`;
    });

    // --- Load Preset Samples ---
    async function loadSamples() {
        try {
            const res = await fetch('/api/samples');
            const data = await res.json();
            if (data.status === 'success') {
                samplesCache = data.samples;
            }
        } catch (err) {
            console.error('Failed to load samples:', err);
        }
    }
    loadSamples();

    // Preset button handlers
    presetChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const sampleId = chip.getAttribute('data-sample');
            const found = samplesCache.find(s => s.id === sampleId);
            if (found) {
                hdrFrom.value = found.from || '';
                hdrReplyTo.value = found.reply_to || '';
                hdrSubject.value = found.subject || '';
                
                // Set SPF dropdown
                if (found.spf_dkim.includes('pass')) hdrSpfDkim.value = 'pass';
                else if (found.spf_dkim.includes('softfail')) hdrSpfDkim.value = 'softfail';
                else if (found.spf_dkim.includes('none')) hdrSpfDkim.value = 'none';
                else hdrSpfDkim.value = 'fail';

                emailInput.value = found.body || '';
                charCounter.textContent = `${emailInput.value.length.toLocaleString()} characters`;
                
                // Automatically run RCNN analysis
                analyzeEmail();
            }
        });
    });

    // --- Clear Input Handler ---
    clearBtn.addEventListener('click', () => {
        hdrFrom.value = '';
        hdrReplyTo.value = '';
        hdrSubject.value = '';
        hdrSpfDkim.value = 'fail';
        emailInput.value = '';
        charCounter.textContent = '0 characters';
        
        emptyState.classList.remove('hidden');
        resultsState.classList.add('hidden');
        verdictStatusBadge.className = 'badge badge-idle';
        verdictStatusBadge.textContent = 'Awaiting Input';
    });

    // --- Scan Button Handler ---
    scanBtn.addEventListener('click', () => {
        analyzeEmail();
    });

    // Ctrl+Enter trigger
    emailInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            analyzeEmail();
        }
    });

    // --- Analyze Email API Request ---
    async function analyzeEmail() {
        const bodyText = emailInput.value.trim();
        const subjectText = hdrSubject.value.trim();

        if (!bodyText && !subjectText) {
            alert('Please provide at least a subject or body content to analyze.');
            emailInput.focus();
            return;
        }

        // Show loading state
        scanBtn.disabled = true;
        scanBtn.innerHTML = `
            <svg class="spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                <path d="M12 2a10 10 0 0 1 10 10"></path>
            </svg>
            <span>RCNN Modeling...</span>
        `;
        verdictStatusBadge.className = 'badge badge-accent';
        verdictStatusBadge.textContent = 'RCNN Inference Active';

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    from: hdrFrom.value.trim(),
                    subject: subjectText,
                    reply_to: hdrReplyTo.value.trim(),
                    spf_dkim: hdrSpfDkim.value,
                    email_text: bodyText,
                    model: modelSelect.value
                })
            });

            const json = await res.json();
            if (json.status === 'success') {
                renderResults(json.data);
            } else {
                alert('Analysis error: ' + (json.error || 'Unknown error'));
            }
        } catch (err) {
            console.error('Inference error:', err);
            alert('Network error communicating with the RCNN inference engine.');
        } finally {
            scanBtn.disabled = false;
            scanBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="M21 21l-4.35-4.35"/>
                </svg>
                <span>Analyze with RCNN</span>
            `;
        }
    }

    // --- Render Results UI ---
    function renderResults(data) {
        emptyState.classList.add('hidden');
        resultsState.classList.remove('hidden');

        const prob = data.phishing_probability;
        const isPhish = data.is_phishing;
        const riskClass = data.risk_class;

        // Status Badge
        verdictStatusBadge.className = `badge ${isPhish ? 'badge-accent' : 'badge-idle'}`;
        verdictStatusBadge.textContent = data.threat_level;

        // Circular Gauge Animation
        const circumference = 339.292;
        const offset = circumference - (prob / 100) * circumference;
        gaugeProgress.style.strokeDashoffset = offset;
        
        let gaugeColor = '#10b981';
        if (prob >= 75) gaugeColor = '#f43f5e';
        else if (prob >= 45) gaugeColor = '#f59e0b';
        gaugeProgress.setAttribute('stroke', gaugeColor);

        threatScoreValue.textContent = `${prob.toFixed(1)}%`;
        threatScoreValue.style.color = gaugeColor;

        // Verdict Banner
        verdictBanner.className = `threat-score-banner banner-${riskClass}`;
        predictionTag.className = `prediction-tag tag-${riskClass}`;
        predictionTag.textContent = data.prediction.toUpperCase();

        if (isPhish) {
            verdictHeadline.textContent = prob >= 80 ? 'Critical Threat: Phishing Confirmed' : 'Suspicious Email Detected';
        } else {
            verdictHeadline.textContent = 'Legitimate Communication Verified';
        }
        verdictSummary.textContent = data.summary;
        consensusText.textContent = data.consensus;

        // Multilevel Breakdown
        const mlData = data.multilevel_breakdown || {};
        const hRisk = mlData.header_risk || 0;
        const bRisk = mlData.body_risk || 0;

        headerRiskBar.style.width = `${hRisk}%`;
        headerRiskVal.textContent = `${hRisk}%`;
        bodyRiskBar.style.width = `${bRisk}%`;
        bodyRiskVal.textContent = `${bRisk}%`;

        // Header Structural Anomalies
        const anomalies = data.security_intelligence?.header_anomalies || [];
        if (anomalies.length > 0) {
            headerAlertsBox.classList.remove('hidden');
            headerAlertsList.innerHTML = anomalies.map(a => `<li>${a}</li>`).join('');
        } else {
            headerAlertsBox.classList.add('hidden');
            headerAlertsList.innerHTML = '';
        }

        // ATTENTION MECHANISM HEATMAP (Word & Character Sequence Focus)
        const heatmapTokens = data.token_attention_heatmap || [];
        attentionHeatmap.innerHTML = '';
        if (heatmapTokens.length > 0) {
            heatmapTokens.forEach(t => {
                const span = document.createElement('span');
                const score = t.attention_score;
                let heatClass = 'token-low';
                if (score >= 65 || t.is_threat_token) heatClass = 'token-high';
                else if (score >= 35) heatClass = 'token-mid';

                span.className = `heatmap-token ${heatClass}`;
                span.textContent = t.word;
                span.title = `Token: "${t.word}" | Attention Weight: ${score}%`;
                attentionHeatmap.appendChild(span);
            });
        } else {
            attentionHeatmap.innerHTML = '<span class="no-tokens">No sequence tokens processed</span>';
        }

        // Multi-Model Probability Distribution Bars
        const modelProbs = data.all_model_probabilities || {};
        const modelLabels = {
            'rcnn_attn': 'Proposed RCNN + Attention Model',
            'bilstm': 'Bidirectional LSTM (BiRNN)',
            'lstm': 'LSTM Sequence Model',
            'gru': 'Gated Recurrent Unit (GRU)',
            'sgd': 'SGD Classifier (Optimal Loss)',
            'mlp': 'MLP Neural Classifier',
            'logistic_regression': 'Logistic Regression',
            'random_forest': 'Random Forest',
            'naive_bayes': 'Multinomial Naive Bayes'
        };

        modelBarsContainer.innerHTML = '';
        Object.entries(modelProbs).forEach(([key, val]) => {
            const barItem = document.createElement('div');
            barItem.className = 'model-bar-item';

            const barColor = val >= 70 ? '#dc2626' :
                             val >= 40 ? '#d97706' :
                                         '#16a34a';

            barItem.innerHTML = `
                <div class="model-bar-header">
                    <span class="model-bar-name">${modelLabels[key] || key}</span>
                    <span class="model-bar-val" style="color: ${val >= 50 ? '#dc2626' : '#16a34a'}">${val.toFixed(1)}%</span>
                </div>
                <div class="model-bar-track">
                    <div class="model-bar-fill" style="width: ${val}%; background: ${barColor}"></div>
                </div>
            `;
            modelBarsContainer.appendChild(barItem);
        });
    }

    // --- Load Benchmarks Table ---
    async function loadBenchmarks() {
        try {
            const res = await fetch('/api/benchmark');
            const data = await res.json();
            if (data.status === 'success') {
                renderBenchmarks(data.benchmarks);
            }
        } catch (err) {
            console.error('Failed to load benchmarks:', err);
        }
    }
    loadBenchmarks();

    function renderBenchmarks(benchmarks) {
        if (!benchmarkTableBody) return;
        benchmarkTableBody.innerHTML = '';
        Object.entries(benchmarks).forEach(([name, metrics]) => {
            const tr = document.createElement('tr');
            const unb = metrics.unbalanced_eval || {};
            const isProposed = name.includes('Proposed');
            
            tr.innerHTML = `
                <td><strong>${isProposed ? '⭐ ' : ''}${name}</strong></td>
                <td><span class="badge ${metrics.type.includes('RCNN') || metrics.type.includes('Deep') ? 'badge-accent' : 'badge-idle'}">${metrics.type}</span></td>
                <td class="metric-val">${metrics.accuracy.toFixed(2)}%</td>
                <td class="metric-val">${metrics.precision.toFixed(1)}%</td>
                <td class="metric-val" style="color: #15803d; font-weight: 600;">${metrics.recall.toFixed(1)}%</td>
                <td class="metric-val" style="color: #1d4ed8; font-weight: 600;">${(metrics.specificity || 98.0).toFixed(2)}%</td>
                <td class="metric-val">${metrics.f1.toFixed(2)}%</td>
                <td class="${parseFloat(unb.false_positives) < 1.0 ? 'fpr-good' : 'fpr-bad'}">${unb.false_positives || '1.5%'}</td>
            `;
            benchmarkTableBody.appendChild(tr);
        });
    }
});
