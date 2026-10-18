/**
 * Apple Fruit Disease Prediction and Recommendation System - Frontend Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    // State
    let currentImageBase64 = null;
    let currentSampleId = null;
    let selectedFile = null;
    let webcamStream = null;

    // Elements
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    const presetsGrid = document.getElementById('presetsGrid');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const webcamBtn = document.getElementById('webcamBtn');
    const webcamBox = document.getElementById('webcamBox');
    const webcamVideo = document.getElementById('webcamVideo');
    const webcamCanvas = document.getElementById('webcamCanvas');
    const captureWebcamBtn = document.getElementById('captureWebcamBtn');
    const closeWebcamBtn = document.getElementById('closeWebcamBtn');

    const runDiagnosisBtn = document.getElementById('runDiagnosisBtn');

    const emptyStateCard = document.getElementById('emptyStateCard');
    const loadingCard = document.getElementById('loadingCard');
    const resultsView = document.getElementById('resultsView');
    const loadingPreviewImg = document.getElementById('loadingPreviewImg');

    // Result elements
    const resSeverityBadge = document.getElementById('resSeverityBadge');
    const resSpecimenBadge = document.getElementById('resSpecimenBadge');
    const resUncertaintyBanner = document.getElementById('resUncertaintyBanner');
    const resDiseaseTitle = document.getElementById('resDiseaseTitle');
    const resScientificName = document.getElementById('resScientificName');
    const resConfidenceVal = document.getElementById('resConfidenceVal');
    const resDiseaseDesc = document.getElementById('resDiseaseDesc');
    const resOrigImg = document.getElementById('resOrigImg');
    const resCamImg = document.getElementById('resCamImg');
    const resProbBarsList = document.getElementById('resProbBarsList');

    // Decision-support elements
    const resPesticideBody = document.getElementById('resPesticideBody');
    const resPreventiveList = document.getElementById('resPreventiveList');
    const resOrganicList = document.getElementById('resOrganicList');

    const heatmapOpacity = document.getElementById('heatmapOpacity');
    const sliderVal = document.getElementById('sliderVal');

    const layerThumbConv1 = document.getElementById('layerThumbConv1');
    const layerThumbConv2 = document.getElementById('layerThumbConv2');
    const layerThumbConv3 = document.getElementById('layerThumbConv3');
    const layerThumbConv4 = document.getElementById('layerThumbConv4');
    const encyclopediaGrid = document.getElementById('encyclopediaGrid');

    // Tab Switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(targetId)?.classList.add('active');
        });
    });

    // Fetch and populate sample thumbnails
    async function loadSamples() {
        try {
            const res = await fetch('/api/samples');
            const data = await res.json();
            if (data.success && data.samples) {
                data.samples.forEach(s => {
                    const imgEl = document.getElementById(`thumb-${s.id}`);
                    if (imgEl && s.thumbnail) {
                        imgEl.src = s.thumbnail;
                    }
                });
            }
        } catch (e) {
            console.error('Error fetching samples:', e);
        }
    }

    // Fetch encyclopedia data
    async function loadEncyclopedia() {
        try {
            const res = await fetch('/api/encyclopedia');
            const data = await res.json();
            if (data.success && data.diseases) {
                renderEncyclopedia(data.diseases);
            }
        } catch (e) {
            console.error('Error fetching encyclopedia:', e);
        }
    }

    function renderEncyclopedia(diseases) {
        encyclopediaGrid.innerHTML = '';
        Object.entries(diseases).forEach(([key, d]) => {
            const card = document.createElement('div');
            card.className = 'ency-card';
            
            const pesticides = d.decision_support?.pesticide_suggestions || [];
            const organic = d.decision_support?.organic_remedies || [];

            card.innerHTML = `
                <div class="ency-title-row">
                    <div>
                        <div class="ency-title">${d.name}</div>
                        <div class="ency-latin">${d.latin}</div>
                    </div>
                    <span class="severity-badge" style="background:${d.severity_color}22; color:${d.severity_color}; border-color:${d.severity_color}44;">
                        ${d.severity}
                    </span>
                </div>
                <p class="ency-desc">${d.description}</p>
                <div>
                    <strong style="font-size:0.84rem; color:var(--text-main); font-weight:700;">Pathological Symptoms:</strong>
                    <ul class="ency-symptoms-list" style="margin-top:6px;">
                        ${d.symptoms.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
                <div style="font-size:0.84rem; padding-top:10px; border-top:1px solid var(--border-subtle); display:flex; flex-direction:column; gap:6px;">
                    <div><strong style="color:#be123c;">Chemical Fungicides:</strong> ${pesticides.map(p => p.name).join(', ') || 'None needed'}</div>
                    <div><strong style="color:#15803d;">Organic Remedies:</strong> ${organic.map(o => o.name).join(', ') || 'Preventive biological management'}</div>
                </div>
            `;
            encyclopediaGrid.appendChild(card);
        });
    }

    // Preset Clicks
    presetsGrid.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            presetsGrid.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            currentSampleId = btn.getAttribute('data-sample');
            currentImageBase64 = null;
            selectedFile = null;

            const thumbImg = btn.querySelector('.preset-thumb-img');
            if (thumbImg && thumbImg.src) {
                loadingPreviewImg.src = thumbImg.src;
            }

            runDiagnosisBtn.disabled = false;
            triggerDiagnosis();
        });
    });

    // File Upload handling
    browseBtn.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    function handleFileSelect(file) {
        selectedFile = file;
        currentSampleId = null;
        presetsGrid.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('selected'));

        const reader = new FileReader();
        reader.onload = (e) => {
            currentImageBase64 = e.target.result;
            loadingPreviewImg.src = currentImageBase64;
            runDiagnosisBtn.disabled = false;
            triggerDiagnosis();
        };
        reader.readAsDataURL(file);
    }

    // Webcam handling
    webcamBtn.addEventListener('click', async () => {
        try {
            webcamStream = await navigator.mediaDevices.getUserMedia({ video: { width: 480, height: 480 } });
            webcamVideo.srcObject = webcamStream;
            webcamBox.style.display = 'block';
        } catch (err) {
            alert('Unable to access camera: ' + err.message);
        }
    });

    closeWebcamBtn.addEventListener('click', () => {
        if (webcamStream) {
            webcamStream.getTracks().forEach(t => t.stop());
            webcamStream = null;
        }
        webcamBox.style.display = 'none';
    });

    captureWebcamBtn.addEventListener('click', () => {
        if (!webcamVideo.videoWidth) return;
        webcamCanvas.width = webcamVideo.videoWidth;
        webcamCanvas.height = webcamVideo.videoHeight;
        const ctx = webcamCanvas.getContext('2d');
        ctx.drawImage(webcamVideo, 0, 0);
        const dataUrl = webcamCanvas.toDataURL('image/jpeg', 0.9);

        if (webcamStream) {
            webcamStream.getTracks().forEach(t => t.stop());
            webcamStream = null;
        }
        webcamBox.style.display = 'none';

        currentImageBase64 = dataUrl;
        currentSampleId = null;
        selectedFile = null;
        loadingPreviewImg.src = dataUrl;
        runDiagnosisBtn.disabled = false;
        triggerDiagnosis();
    });

    // Run Diagnosis Button
    runDiagnosisBtn.addEventListener('click', triggerDiagnosis);

    async function triggerDiagnosis() {
        const modelType = document.querySelector('input[name="modelType"]:checked')?.value || 'transfer';

        emptyStateCard.style.display = 'none';
        resultsView.style.display = 'none';
        loadingCard.style.display = 'block';

        try {
            let res;
            if (currentSampleId) {
                res = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sample_id: currentSampleId,
                        model_type: modelType
                    })
                });
            } else if (currentImageBase64) {
                res = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: currentImageBase64,
                        model_type: modelType
                    })
                });
            } else if (selectedFile) {
                const formData = new FormData();
                formData.append('image', selectedFile);
                formData.append('model_type', modelType);
                res = await fetch('/api/predict', {
                    method: 'POST',
                    body: formData
                });
            } else {
                throw new Error('No image specified');
            }

            const json = await res.json();
            if (!json.success) {
                throw new Error(json.error || 'Diagnostic inference failed');
            }

            renderResults(json.data);
        } catch (err) {
            alert('Diagnostic Analysis Error: ' + err.message);
            emptyStateCard.style.display = 'block';
        } finally {
            loadingCard.style.display = 'none';
        }
    }

    function renderResults(data) {
        resultsView.style.display = 'block';

        // Specimen type badge
        if (resSpecimenBadge) {
            if (data.specimen_type === 'apple_fruit') {
                resSpecimenBadge.style.display = 'inline-block';
                resSpecimenBadge.textContent = '🍎 Specimen: Apple Fruit';
                resSpecimenBadge.style.color = '#0284c7';
                resSpecimenBadge.style.borderColor = '#bae6fd';
                resSpecimenBadge.style.background = '#e0f2fe';
            } else if (data.specimen_type === 'apple_leaf') {
                resSpecimenBadge.style.display = 'inline-block';
                resSpecimenBadge.textContent = '🍃 Specimen: Apple Foliage';
                resSpecimenBadge.style.color = '#15803d';
                resSpecimenBadge.style.borderColor = '#86efac';
                resSpecimenBadge.style.background = '#dcfce7';
            } else if (data.specimen_type) {
                resSpecimenBadge.style.display = 'inline-block';
                resSpecimenBadge.textContent = `Specimen: ${data.specimen_type}`;
            }
        }

        // Uncertainty safety banner
        if (resUncertaintyBanner) {
            if (data.is_uncertain && data.uncertainty_reason) {
                resUncertaintyBanner.style.display = 'block';
                resUncertaintyBanner.textContent = `⚠️ Safety Advisory: ${data.uncertainty_reason}`;
            } else {
                resUncertaintyBanner.style.display = 'none';
            }
        }

        // Header info
        resSeverityBadge.textContent = data.severity;
        resSeverityBadge.style.color = data.severity_color;
        resSeverityBadge.style.borderColor = data.severity_color;
        resSeverityBadge.style.background = `${data.severity_color}22`;

        resDiseaseTitle.textContent = data.display_name;
        resScientificName.textContent = data.scientific_name;
        resConfidenceVal.textContent = `${data.confidence}%`;
        resDiseaseDesc.textContent = data.description;

        // Images
        resOrigImg.src = data.original_image;
        resCamImg.src = data.gradcam_image;

        // Opacity
        heatmapOpacity.value = 85;
        sliderVal.textContent = '85%';
        resCamImg.style.opacity = 0.85;

        // Probability bars
        resProbBarsList.innerHTML = '';
        const classDisplayNames = {
            'Fresh': 'Fresh Apple (Sound Fruit)',
            'Rotten': 'Rotten / Decayed Fruit',
            'Healthy': 'Healthy Foliage',
            'Apple_Scab': 'Apple Scab',
            'Black_Rot': 'Black Rot / Frog-Eye',
            'Cedar_Apple_Rust': 'Cedar Apple Rust',
            'Healthy_Apple': 'Healthy Specimen',
            'Apple_Blotch': 'Apple Blotch'
        };

        Object.entries(data.all_probabilities).forEach(([cls, prob]) => {
            const isWinner = cls === data.predicted_class;
            const row = document.createElement('div');
            row.className = 'prob-row';
            row.innerHTML = `
                <div class="prob-info">
                    <span class="prob-name" style="${isWinner ? 'color: #15803d; font-weight:700;' : 'color: var(--text-main);'}">${classDisplayNames[cls] || cls}</span>
                    <span class="prob-val" style="${isWinner ? 'color: #15803d; font-weight:700;' : 'color: var(--text-secondary);'}">${prob.toFixed(1)}%</span>
                </div>
                <div class="prob-bar-track">
                    <div class="prob-bar-fill" style="width: 0%; ${isWinner ? 'background: linear-gradient(90deg, #22c55e, #15803d);' : 'background: #cbd5e1;'}"></div>
                </div>
            `;
            resProbBarsList.appendChild(row);

            setTimeout(() => {
                row.querySelector('.prob-bar-fill').style.width = `${Math.max(1, prob)}%`;
            }, 60);
        });

        // Decision-Support Modules
        const ds = data.decision_support || {};

        // 1. Pesticide Suggestions
        resPesticideBody.innerHTML = '';
        if (ds.pesticide_suggestions && ds.pesticide_suggestions.length > 0) {
            ds.pesticide_suggestions.forEach(pest => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${pest.name}</strong></td>
                    <td><span style="font-family:var(--font-mono); font-size:0.76rem; color:#0284c7; font-weight:600;">${pest.type}</span></td>
                    <td><span style="font-family:var(--font-mono); font-size:0.76rem; color:#15803d; font-weight:700;">${pest.rate}</span></td>
                    <td style="color:var(--text-secondary);">${pest.timing}</td>
                `;
                resPesticideBody.appendChild(tr);
            });
        } else {
            resPesticideBody.innerHTML = '<tr><td colspan="4" style="color:var(--text-muted); text-align:center;">No chemical pesticide intervention required.</td></tr>';
        }

        // 2. Preventive Measures
        resPreventiveList.innerHTML = '';
        if (ds.preventive_measures && ds.preventive_measures.length > 0) {
            ds.preventive_measures.forEach(prev => {
                const li = document.createElement('li');
                li.textContent = prev;
                resPreventiveList.appendChild(li);
            });
        }

        // 3. Organic Remedies
        resOrganicList.innerHTML = '';
        if (ds.organic_remedies && ds.organic_remedies.length > 0) {
            ds.organic_remedies.forEach(org => {
                const div = document.createElement('div');
                div.className = 'organic-item';
                div.innerHTML = `
                    <div class="organic-item-name">${org.name}</div>
                    <div class="organic-item-usage">${org.usage}</div>
                `;
                resOrganicList.appendChild(div);
            });
        }

        // Layer Activations
        if (data.activations) {
            renderActivations(data.activations);
        }
    }

    function renderActivations(activations) {
        const layerContainers = {
            'conv1': layerThumbConv1,
            'conv2': layerThumbConv2,
            'conv3': layerThumbConv3,
            'conv4': layerThumbConv4
        };

        Object.entries(activations).forEach(([layer, info]) => {
            const container = layerContainers[layer];
            if (!container) return;
            container.innerHTML = '';
            info.thumbnails.forEach((thumb, idx) => {
                const div = document.createElement('div');
                div.className = 'filter-thumb';
                div.title = `Channel ${idx + 1} (${info.dim})`;
                div.innerHTML = `<img src="${thumb}" alt="Filter ${idx + 1}">`;
                container.appendChild(div);
            });
        });
    }

    // Heatmap opacity slider
    heatmapOpacity.addEventListener('input', (e) => {
        const val = e.target.value;
        sliderVal.textContent = `${val}%`;
        resCamImg.style.opacity = val / 100.0;
    });

    // Initialize
    loadSamples();
    loadEncyclopedia();
});
