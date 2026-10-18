const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export async function predictCustomer(customerData) {
  const response = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(customerData),
  });

  if (!response.ok) {
    const errorJson = await response.json().catch(() => ({}));
    let msg = errorJson.error || 'Prediction request failed';
    if (errorJson.validationErrors) {
      msg = Object.values(errorJson.validationErrors).join(', ');
    }
    throw new Error(msg);
  }

  return response.json();
}

export async function fetchDashboard() {
  const response = await fetch(`${API_BASE}/dashboard`);
  if (!response.ok) {
    throw new Error(`Failed to load dashboard metrics (HTTP ${response.status})`);
  }
  return response.json();
}

export async function fetchModelMetrics() {
  const response = await fetch(`${API_BASE}/model-metrics`);
  if (!response.ok) {
    throw new Error(`Failed to load model evaluation metrics (HTTP ${response.status})`);
  }
  return response.json();
}

export async function fetchHistory() {
  const response = await fetch(`${API_BASE}/history`);
  if (!response.ok) {
    throw new Error(`Failed to load prediction history (HTTP ${response.status})`);
  }
  return response.json();
}

export async function fetchHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    return { overallStatus: 'DEGRADED', backendStatus: 'UP', mlServiceStatus: 'DOWN' };
  }
  return response.json();
}
