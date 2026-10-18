// Telecom Intelligence - Client-Side Interactivity with Navy Blue & Black Theme
document.addEventListener('DOMContentLoaded', function () {
  // 1. Churn Prediction Form Submission
  const predictionForm = document.getElementById('churnPredictionForm');
  const predictBtn = document.getElementById('predictBtn');
  const btnSpinner = document.getElementById('btnSpinner');
  const btnText = document.getElementById('btnText');
  const errorBanner = document.getElementById('formErrorBanner');

  if (predictionForm) {
    predictionForm.addEventListener('submit', function (e) {
      const monthly = parseFloat(document.getElementById('MonthlyCharges').value);
      const tenure = parseInt(document.getElementById('Tenure').value);

      if (isNaN(monthly) || monthly < 0) {
        e.preventDefault();
        showError('Please enter a valid monthly charge greater than or equal to $0.');
        return;
      }

      if (isNaN(tenure) || tenure < 0) {
        e.preventDefault();
        showError('Please enter a valid tenure in months (0 or more).');
        return;
      }

      // Show spinner while calculating
      if (btnSpinner && btnText && predictBtn) {
        btnSpinner.style.display = 'inline-block';
        btnText.textContent = 'CALCULATING RISK...';
        predictBtn.disabled = true;
      }
    });
  }

  function showError(msg) {
    if (errorBanner) {
      errorBanner.textContent = msg;
      errorBanner.style.display = 'block';
      errorBanner.scrollIntoView({ behavior: 'smooth' });
    } else {
      alert(msg);
    }
  }

  // 2. Churn Distribution Doughnut Chart (Styled for Navy & Black Theme)
  const churnChartCanvas = document.getElementById('churnDistributionChart');
  if (churnChartCanvas && typeof Chart !== 'undefined') {
    const churnCount = parseInt(churnChartCanvas.getAttribute('data-churn') || 1869);
    const stayCount = parseInt(churnChartCanvas.getAttribute('data-stay') || 5174);

    new Chart(churnChartCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Retained Base', 'At-Risk Churn'],
        datasets: [{
          data: [stayCount, churnCount],
          backgroundColor: ['#34D399', '#F87171'],
          borderWidth: 2,
          borderColor: '#101E33'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#94A3B8',
              font: {
                family: 'Inter',
                size: 12,
                weight: '500'
              },
              padding: 16
            }
          },
          tooltip: {
            backgroundColor: '#090D14',
            titleColor: '#F1F5F9',
            bodyColor: '#94A3B8',
            borderColor: '#203047',
            borderWidth: 1,
            callbacks: {
              label: function (context) {
                const total = churnCount + stayCount;
                const val = context.raw;
                const pct = ((val / total) * 100).toFixed(1);
                return ` ${context.label}: ${val.toLocaleString()} (${pct}%)`;
              }
            }
          }
        },
        cutout: '70%'
      }
    });
  }

  // 3. History Search & Filter
  const historySearchInput = document.getElementById('historySearchInput');
  const historyFilterStatus = document.getElementById('historyFilterStatus');
  const historyTable = document.getElementById('historyTable');

  if (historySearchInput && historyTable) {
    function filterTable() {
      const query = historySearchInput.value.toLowerCase().trim();
      const statusFilter = historyFilterStatus ? historyFilterStatus.value : 'ALL';
      const rows = historyTable.querySelectorAll('tbody tr');

      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const rowStatus = row.getAttribute('data-status') || '';
        const matchesQuery = query === '' || text.includes(query);
        const matchesStatus = statusFilter === 'ALL' || rowStatus === statusFilter;

        if (matchesQuery && matchesStatus) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    }

    historySearchInput.addEventListener('input', filterTable);
    if (historyFilterStatus) {
      historyFilterStatus.addEventListener('change', filterTable);
    }
  }

  // 4. Feature Importance Horizontal Bar Chart (Navy Blue Palette)
  const fiCanvas = document.getElementById('featureImportanceChart');
  if (fiCanvas && typeof Chart !== 'undefined') {
    const rawLabels = fiCanvas.getAttribute('data-features');
    const rawScores = fiCanvas.getAttribute('data-scores');

    if (rawLabels && rawScores) {
      try {
        const labels = JSON.parse(rawLabels);
        const scores = JSON.parse(rawScores);

        // Top 10 features
        const combined = labels.map((name, i) => ({ name, score: scores[i] }));
        combined.sort((a, b) => b.score - a.score);
        const top10 = combined.slice(0, 10);

        new Chart(fiCanvas, {
          type: 'bar',
          data: {
            labels: top10.map(d => d.name),
            datasets: [{
              label: 'Importance Score',
              data: top10.map(d => d.score),
              backgroundColor: '#3B82F6',
              borderRadius: 4
            }]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                backgroundColor: '#090D14',
                titleColor: '#F1F5F9',
                bodyColor: '#94A3B8',
                borderColor: '#203047',
                borderWidth: 1
              }
            },
            scales: {
              x: {
                beginAtZero: true,
                grid: { color: '#203047' },
                ticks: {
                  color: '#94A3B8',
                  font: { family: 'Inter', size: 11 }
                }
              },
              y: {
                grid: { display: false },
                ticks: {
                  color: '#F1F5F9',
                  font: { family: 'Inter', size: 12, weight: '500' }
                }
              }
            }
          }
        });
      } catch (e) {
        console.error('Failed to parse feature importances:', e);
      }
    }
  }
});

// View Customer Details in Modal (Dark Navy Design)
function viewCustomerDetails(btn) {
  const dataStr = btn.getAttribute('data-customer');
  if (!dataStr) return;
  try {
    const c = JSON.parse(dataStr);
    const modal = document.getElementById('customerDetailModal');
    const content = document.getElementById('customerModalContent');
    if (!modal || !content) return;

    content.innerHTML = `
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; margin-bottom: 1.25rem; font-size: 0.875rem;">
        <div><span style="color:#94A3B8;">Customer ID:</span> <strong style="color:#F1F5F9;">${c.customer_id}</strong></div>
        <div><span style="color:#94A3B8;">Date:</span> <span style="color:#F1F5F9;">${c.prediction_date}</span></div>
        <div><span style="color:#94A3B8;">Gender / Senior:</span> <span style="color:#F1F5F9;">${c.gender} / ${c.senior_citizen ? 'Yes' : 'No'}</span></div>
        <div><span style="color:#94A3B8;">Partner / Dependents:</span> <span style="color:#F1F5F9;">${c.partner ? 'Yes' : 'No'} / ${c.dependents ? 'Yes' : 'No'}</span></div>
        <div><span style="color:#94A3B8;">Tenure:</span> <span style="color:#F1F5F9;">${c.tenure} months</span></div>
        <div><span style="color:#94A3B8;">Contract:</span> <span style="color:#F1F5F9;">${c.contract}</span></div>
        <div><span style="color:#94A3B8;">Internet Service:</span> <span style="color:#F1F5F9;">${c.internet_service}</span></div>
        <div><span style="color:#94A3B8;">Payment Method:</span> <span style="color:#F1F5F9;">${c.payment_method}</span></div>
        <div><span style="color:#94A3B8;">Monthly Charges:</span> <span style="color:#F1F5F9;">$${c.monthly_charges}</span></div>
        <div><span style="color:#94A3B8;">Total Charges:</span> <span style="color:#F1F5F9;">$${c.total_charges}</span></div>
        <div><span style="color:#94A3B8;">Estimated CLTV:</span> <strong style="color:#3B82F6;">$${c.cltv}</strong></div>
        <div><span style="color:#94A3B8;">Churn Risk:</span> <strong style="color:${c.churn_probability >= 0.5 ? '#F87171' : '#34D399'};">${(c.churn_probability * 100).toFixed(1)}% (${c.risk_level})</strong></div>
      </div>
      <div style="background:#080F1B; border:1px solid #203047; padding:1rem; border-radius:6px;">
        <div style="font-size:0.8rem; font-weight:700; color:#60A5FA; text-transform:uppercase; margin-bottom:0.35rem;">Recommended Retention Strategy:</div>
        <p style="color:#F1F5F9; font-size:0.85rem; line-height:1.5;">${c.action_suggested}</p>
      </div>
    `;
    modal.style.display = 'flex';
  } catch (err) {
    console.error(err);
  }
}

function closeCustomerModal() {
  const modal = document.getElementById('customerDetailModal');
  if (modal) modal.style.display = 'none';
}
