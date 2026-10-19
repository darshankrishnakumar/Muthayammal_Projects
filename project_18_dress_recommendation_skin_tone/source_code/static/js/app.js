document.addEventListener('DOMContentLoaded', () => {
    // Tab Switching
    const tabs = document.querySelectorAll('.nav-tab');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = `tab-${tab.dataset.tab}`;
            tabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const targetPane = document.getElementById(targetId);
            if (targetPane) {
                targetPane.classList.add('active');
                if (tab.dataset.tab === 'catalogue') loadCatalogue();
                if (tab.dataset.tab === 'history') loadHistory();
            }
        });
    });

    // Budget Slider
    const budgetSlider = document.getElementById('budgetMax');
    const budgetValue = document.getElementById('budgetValue');
    if (budgetSlider && budgetValue) {
        budgetSlider.addEventListener('input', (e) => {
            budgetValue.textContent = `₹${parseInt(e.target.value).toLocaleString()}`;
        });
    }

    // Presets Configuration
    const presets = {
        p1: {
            skin_tone: 'Fair',
            undertone: 'Cool',
            body_shape: 'Hourglass',
            preferred_occasions: 'Party',
            preferred_styles: 'Classic',
            preferred_colours: 'Emerald',
            query_text: 'emerald wrap maxi dress',
            budget_max: 8000
        },
        p2: {
            skin_tone: 'Medium',
            undertone: 'Warm',
            body_shape: 'Pear',
            preferred_occasions: 'Formal',
            preferred_styles: 'Classic',
            preferred_colours: 'Navy Blue',
            query_text: 'crisp white oxford shirt',
            budget_max: 6000
        },
        p3: {
            skin_tone: 'Olive',
            undertone: 'Warm',
            body_shape: 'Rectangle',
            preferred_occasions: 'Ethnic',
            preferred_styles: 'Classic',
            preferred_colours: 'Crimson',
            query_text: 'kanjeevaram silk saree',
            budget_max: 12000
        },
        p4: {
            skin_tone: 'Deep',
            undertone: 'Neutral',
            body_shape: 'Inverted Triangle',
            preferred_occasions: 'Casual',
            preferred_styles: 'Modern',
            preferred_colours: 'Charcoal',
            query_text: 'dark indigo straight jeans',
            budget_max: 5000
        }
    };

    const presetChips = document.querySelectorAll('.preset-chip');
    presetChips.forEach(chip => {
        chip.addEventListener('click', () => {
            presetChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            const pKey = chip.dataset.preset;
            const p = presets[pKey];
            if (p) {
                document.getElementById('skinTone').value = p.skin_tone;
                document.getElementById('undertone').value = p.undertone;
                document.getElementById('bodyShape').value = p.body_shape;
                document.getElementById('preferredOccasion').value = p.preferred_occasions;
                document.getElementById('preferredStyle').value = p.preferred_styles;
                document.getElementById('preferredColour').value = p.preferred_colours;
                document.getElementById('queryText').value = p.query_text;
                document.getElementById('budgetMax').value = p.budget_max;
                budgetValue.textContent = `₹${p.budget_max.toLocaleString()}`;
                submitRecommendationForm();
            }
        });
    });

    // Form Submit
    const form = document.getElementById('recommendForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            submitRecommendationForm();
        });
    }

    async function submitRecommendationForm() {
        const outfitGrid = document.getElementById('outfitGrid');
        if (!outfitGrid) return;
        outfitGrid.innerHTML = '<div class="loading-state">Synthesizing multi-modal compatibility scores...</div>';

        const formData = new FormData(form);
        try {
            const resp = await fetch('/api/recommend', {
                method: 'POST',
                body: formData
            });
            const res = await resp.json();

            if (res.status === 'success') {
                // Update Telemetry Banner
                document.getElementById('telCategory').textContent = res.gbm_predicted_category || 'N/A';
                document.getElementById('telConfidence').textContent = `${res.gbm_confidence || 80.0}%`;
                document.getElementById('telCandidates').textContent = `${res.total_candidates_analyzed || 20} Outfits`;
                document.getElementById('telLatency').textContent = `${res.latency_ms || 12.0} ms`;

                renderOutfits(res.recommendations || []);
            } else {
                outfitGrid.innerHTML = `<div class="error-state">Error generating recommendations: ${res.detail || 'Unknown error'}</div>`;
            }
        } catch (err) {
            outfitGrid.innerHTML = `<div class="error-state">Failed to connect to recommendation service: ${err.message}</div>`;
        }
    }

    function renderOutfits(outfits) {
        const outfitGrid = document.getElementById('outfitGrid');
        document.getElementById('outfitCountBadge').textContent = `Top ${outfits.length} Matches`;

        if (!outfits.length) {
            outfitGrid.innerHTML = '<div class="empty-state">No matching outfits found for criteria.</div>';
            return;
        }

        outfitGrid.innerHTML = outfits.map(o => {
            const matchPct = Math.round((o.final_score || 0.5) * 100);
            const tfidfPct = Math.round(((o.component_scores && o.component_scores.tfidf_score) || 0.3) * 100);
            const gbmPct = Math.round(((o.component_scores && o.component_scores.gbm_score) || 0.4) * 100);
            const attrPct = Math.round(((o.component_scores && o.component_scores.attribute_score) || 0.8) * 100);
            const imgPath = o.image_path ? `/${o.image_path}` : '/outfits/formal_navy_wool_suit.jpg';

            const reasonsHtml = (o.recommendation_reasons || [])
                .map(r => `<li>${r}</li>`)
                .join('');

            return `
                <div class="outfit-card">
                    <div class="outfit-image-wrapper">
                        <img src="${imgPath}" alt="${o.outfit_name}" class="outfit-img" onerror="this.src='/outfits/formal_navy_wool_suit.jpg'">
                        <span class="outfit-match-badge">${matchPct}% Match</span>
                        <span class="outfit-cat-badge">${o.category}</span>
                    </div>
                    <div class="outfit-info">
                        <div class="outfit-price-row">
                            <span class="outfit-price">₹${(o.price || 0).toLocaleString()}</span>
                            <div class="outfit-tags">
                                <span class="mini-tag">${o.occasion || 'Versatile'}</span>
                                <span class="mini-tag">${o.style || 'Classic'}</span>
                            </div>
                        </div>
                        <h4 class="outfit-name">${o.outfit_name}</h4>
                        
                        <div class="score-breakdown">
                            <div class="breakdown-row"><span>TF-IDF Text Relevance</span><span>${tfidfPct}%</span></div>
                            <div class="breakdown-bar"><div class="bar-fill fill-blue" style="width: ${tfidfPct}%;"></div></div>
                            <div class="breakdown-row"><span>GBM Category Affinity</span><span>${gbmPct}%</span></div>
                            <div class="breakdown-bar"><div class="bar-fill fill-accent" style="width: ${gbmPct}%;"></div></div>
                            <div class="breakdown-row"><span>Skin Tone & Silhouette Harmony</span><span>${attrPct}%</span></div>
                            <div class="breakdown-bar"><div class="bar-fill fill-green" style="width: ${attrPct}%;"></div></div>
                        </div>

                        <ul class="reasons-list">
                            ${reasonsHtml}
                        </ul>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Load Catalogue Table
    async function loadCatalogue() {
        const tbody = document.getElementById('catalogueTableBody');
        try {
            const resp = await fetch('/api/catalogue');
            const data = await resp.json();
            if (data.status === 'success' && data.data) {
                document.getElementById('catalogueTotalBadge').textContent = `${data.count} Items Available`;
                tbody.innerHTML = data.data.map(item => `
                    <tr>
                        <td><img src="/${item.image_path}" class="table-thumbnail" onerror="this.src='/outfits/formal_navy_wool_suit.jpg'"></td>
                        <td><code>${item.outfit_id}</code></td>
                        <td><strong>${item.outfit_name}</strong><br><small style="color:var(--text-muted)">${item.garment_type}</small></td>
                        <td><span class="badge-tag">${item.category}</span></td>
                        <td>${item.occasion}</td>
                        <td>${item.dominant_colour}</td>
                        <td><small>${item.suitable_skin_tones || 'All'}</small></td>
                        <td><small>${item.compatible_body_shapes || 'All'}</small></td>
                        <td><strong>₹${(item.price || 0).toLocaleString()}</strong></td>
                    </tr>
                `).join('');
            }
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="9">Failed to load catalogue: ${err.message}</td></tr>`;
        }
    }

    // Load History Table
    async function loadHistory() {
        const tbody = document.getElementById('historyTableBody');
        try {
            const resp = await fetch('/api/history');
            const data = await resp.json();
            if (data.status === 'success' && data.data) {
                tbody.innerHTML = data.data.map(h => `
                    <tr>
                        <td><code>#${h.recommendation_id}</code></td>
                        <td><small>${h.created_at || 'Just now'}</small></td>
                        <td>${h.user_id}</td>
                        <td><code>${h.outfit_id}</code></td>
                        <td><strong>${h.outfit_name}</strong></td>
                        <td><span class="badge-tag">${h.category || 'N/A'}</span></td>
                        <td><strong style="color:var(--accent-emerald)">${Math.round((h.match_score || 0.8) * 100)}%</strong></td>
                        <td><small>${h.recommendation_reason || 'Matched'}</small></td>
                    </tr>
                `).join('');
            }
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="8">Failed to load history: ${err.message}</td></tr>`;
        }
    }

    // Initial load
    submitRecommendationForm();
});
