import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  UserCheck, 
  Clock, 
  Activity, 
  Layers, 
  RefreshCw, 
  ShieldAlert, 
  CheckCircle2, 
  HelpCircle, 
  Server, 
  ArrowRight, 
  TrendingUp,
  FileText,
  AlertTriangle,
  Info
} from 'lucide-react';
import { predictCustomer, fetchDashboard, fetchModelMetrics, fetchHistory, fetchHealth } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemHealth, setSystemHealth] = useState(null);
  
  // Dashboard state
  const [dashboardData, setDashboardData] = useState(null);
  const [loadingDashboard, setLoadingDashboard] = useState(false);

  // Model performance state
  const [modelMetrics, setModelMetrics] = useState(null);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  // History state
  const [historyRecords, setHistoryRecords] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [historySearch, setHistorySearch] = useState('');
  const [selectedRecord, setSelectedRecord] = useState(null);

  // Prediction Form State
  const initialForm = {
    gender: 'Female',
    seniorCitizen: 0,
    partner: 'No',
    dependents: 'No',
    tenure: 1,
    phoneService: 'Yes',
    multipleLines: 'No',
    internetService: 'Fiber optic',
    onlineSecurity: 'No',
    onlineBackup: 'No',
    deviceProtection: 'No',
    techSupport: 'No',
    streamingTV: 'No',
    streamingMovies: 'No',
    contract: 'Month-to-month',
    paperlessBilling: 'Yes',
    paymentMethod: 'Electronic check',
    monthlyCharges: 70.0,
    totalCharges: 70.0
  };

  const [formData, setFormData] = useState(initialForm);
  const [predicting, setPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [formError, setFormError] = useState(null);

  // Check health and load initial data
  useEffect(() => {
    checkHealth();
    loadDashboard();
  }, []);

  const checkHealth = async () => {
    try {
      const data = await fetchHealth();
      setSystemHealth(data);
    } catch {
      setSystemHealth({ overallStatus: 'DEGRADED', backendStatus: 'UNKNOWN', mlServiceStatus: 'UNKNOWN' });
    }
  };

  const loadDashboard = async () => {
    setLoadingDashboard(true);
    try {
      const data = await fetchDashboard();
      setDashboardData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDashboard(false);
    }
  };

  const loadHistory = async () => {
    setLoadingHistory(true);
    try {
      const data = await fetchHistory();
      setHistoryRecords(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const loadMetrics = async () => {
    setLoadingMetrics(true);
    try {
      const data = await fetchModelMetrics();
      setModelMetrics(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingMetrics(false);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'dashboard') loadDashboard();
    if (tab === 'history') loadHistory();
    if (tab === 'performance') loadMetrics();
  };

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    let parsedVal = value;
    if (type === 'number') {
      parsedVal = value === '' ? '' : parseFloat(value);
    }
    setFormData(prev => {
      const updated = { ...prev, [name]: parsedVal };
      if (name === 'monthlyCharges' || name === 'tenure') {
        const mc = name === 'monthlyCharges' ? (parsedVal || 0) : prev.monthlyCharges;
        const ten = name === 'tenure' ? (parsedVal || 0) : prev.tenure;
        updated.totalCharges = Math.round(mc * Math.max(1, ten) * 100) / 100;
      }
      return updated;
    });
  };

  const handlePreset = (type) => {
    if (type === 'high_risk') {
      setFormData({
        gender: 'Female',
        seniorCitizen: 1,
        partner: 'No',
        dependents: 'No',
        tenure: 2,
        phoneService: 'Yes',
        multipleLines: 'No',
        internetService: 'Fiber optic',
        onlineSecurity: 'No',
        onlineBackup: 'No',
        deviceProtection: 'No',
        techSupport: 'No',
        streamingTV: 'Yes',
        streamingMovies: 'Yes',
        contract: 'Month-to-month',
        paperlessBilling: 'Yes',
        paymentMethod: 'Electronic check',
        monthlyCharges: 95.50,
        totalCharges: 191.00
      });
    } else if (type === 'low_risk') {
      setFormData({
        gender: 'Male',
        seniorCitizen: 0,
        partner: 'Yes',
        dependents: 'Yes',
        tenure: 48,
        phoneService: 'Yes',
        multipleLines: 'Yes',
        internetService: 'DSL',
        onlineSecurity: 'Yes',
        onlineBackup: 'Yes',
        deviceProtection: 'Yes',
        techSupport: 'Yes',
        streamingTV: 'Yes',
        streamingMovies: 'Yes',
        contract: 'Two year',
        paperlessBilling: 'No',
        paymentMethod: 'Credit card (automatic)',
        monthlyCharges: 62.00,
        totalCharges: 2976.00
      });
    } else {
      setFormData(initialForm);
    }
  };

  const handlePredictSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);
    setPredicting(true);

    try {
      const result = await predictCustomer(formData);
      setPredictionResult(result);
      // Refresh dashboard background
      fetchDashboard().then(setDashboardData).catch(() => {});
    } catch (err) {
      setFormError(err.message || 'Error occurred while contacting backend service.');
    } finally {
      setPredicting(false);
    }
  };

  const filteredHistory = historyRecords.filter(rec => {
    if (!historySearch) return true;
    const term = historySearch.toLowerCase();
    return (
      rec.id?.toString().includes(term) ||
      rec.predictedClass?.toLowerCase().includes(term) ||
      rec.riskLevel?.toLowerCase().includes(term) ||
      rec.contract?.toLowerCase().includes(term) ||
      rec.internetService?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand-section">
          <div className="brand-title">
            <Layers className="text-blue-500" size={24} color="#3B82F6" />
            <span>TELCO CHURN IQ</span>
          </div>
          <span className="brand-badge">ML Core v1.0.0</span>
        </div>

        <nav className="nav-links">
          <button 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => handleTabChange('dashboard')}
          >
            <BarChart3 size={18} />
            <span>Executive Dashboard</span>
          </button>
          
          <button 
            className={`nav-item ${activeTab === 'predict' ? 'active' : ''}`}
            onClick={() => handleTabChange('predict')}
          >
            <UserCheck size={18} />
            <span>Predict Customer</span>
          </button>

          <button 
            className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => handleTabChange('history')}
          >
            <Clock size={18} />
            <span>Prediction History</span>
          </button>

          <button 
            className={`nav-item ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => handleTabChange('performance')}
          >
            <Activity size={18} />
            <span>Model Performance</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="health-status-badge">
            <span className={`status-dot ${systemHealth?.overallStatus === 'HEALTHY' ? '' : (systemHealth?.overallStatus === 'DEGRADED' ? 'down' : '')}`} />
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.78rem' }}>
                {systemHealth?.overallStatus === 'HEALTHY' ? 'SYSTEM OPERATIONAL' : 'SYSTEM STATUS'}
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                Spring Boot + FastAPI ML
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-wrapper">
        <header className="top-bar">
          <div className="top-bar-title">
            {activeTab === 'dashboard' && 'Enterprise Churn Intelligence & Telemetry'}
            {activeTab === 'predict' && 'Customer Churn Risk Inference Engine'}
            {activeTab === 'history' && 'Audited Historical Prediction Logs'}
            {activeTab === 'performance' && 'Random Forest Classifier Evaluation & Metrics'}
          </div>

          <div className="top-bar-meta">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Server size={14} color="#60A5FA" />
              <span>Spring Boot: <strong>8080</strong></span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={14} color="#34D399" />
              <span>Python ML: <strong>8000</strong></span>
            </div>
          </div>
        </header>

        <main className="content-body">
          {/* TAB 1: EXECUTIVE DASHBOARD */}
          {activeTab === 'dashboard' && (
            <div>
              {/* KPI Cards */}
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-label">Total Customers Analyzed</div>
                  <div className="kpi-value">{dashboardData?.totalCustomers ?? '--'}</div>
                  <div className="kpi-sub">Persistent database records</div>
                </div>

                <div className="kpi-card churn">
                  <div className="kpi-label">Predicted to Churn</div>
                  <div className="kpi-value" style={{ color: '#EF4444' }}>
                    {dashboardData?.churnCount ?? '--'}
                  </div>
                  <div className="kpi-sub">Customers at high retention risk</div>
                </div>

                <div className="kpi-card retention">
                  <div className="kpi-label">Predicted to Retain</div>
                  <div className="kpi-value" style={{ color: '#10B981' }}>
                    {dashboardData?.noChurnCount ?? '--'}
                  </div>
                  <div className="kpi-sub">Stable active subscribers</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-label">Predicted Churn Rate</div>
                  <div className="kpi-value">
                    {dashboardData?.churnRate != null ? `${dashboardData.churnRate}%` : '--'}
                  </div>
                  <div className="kpi-sub">Aggregate telemetry ratio</div>
                </div>
              </div>

              {/* Charts & Highlights Row */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', marginBottom: '28px' }}>
                <div className="card">
                  <div className="card-title">
                    <TrendingUp size={18} color="#3B82F6" />
                    <span>Portfolio Churn Ratio</span>
                  </div>
                  
                  {dashboardData && (
                    <div style={{ textAlign: 'center', padding: '16px 0' }}>
                      <div style={{ 
                        fontSize: '2.5rem', 
                        fontWeight: 800, 
                        color: dashboardData.churnRate > 40 ? '#EF4444' : '#3B82F6',
                        marginBottom: '8px'
                      }}>
                        {dashboardData.churnRate}%
                      </div>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '20px' }}>
                        Estimated Portfolio Risk Level
                      </div>

                      <div style={{ display: 'flex', height: '14px', borderRadius: '7px', overflow: 'hidden', background: '#0A1020' }}>
                        <div style={{ 
                          width: `${dashboardData.churnRate}%`, 
                          background: 'linear-gradient(90deg, #EF4444, #F87171)' 
                        }} />
                        <div style={{ 
                          width: `${100 - dashboardData.churnRate}%`, 
                          background: 'linear-gradient(90deg, #10B981, #34D399)' 
                        }} />
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '12px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        <span style={{ color: '#EF4444' }}>● Churn: {dashboardData.churnCount}</span>
                        <span style={{ color: '#10B981' }}>● Retained: {dashboardData.noChurnCount}</span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="card">
                  <div className="card-title">
                    <Clock size={18} color="#60A5FA" />
                    <span>Recent Customer Evaluations</span>
                  </div>

                  <div className="table-container">
                    <table className="custom-table">
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Tenure</th>
                          <th>Contract</th>
                          <th>Monthly</th>
                          <th>Prediction</th>
                          <th>Probability</th>
                          <th>Risk Level</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dashboardData?.recentPredictions?.length ? (
                          dashboardData.recentPredictions.map((row) => (
                            <tr key={row.id}>
                              <td style={{ fontFamily: 'JetBrains Mono', color: '#94A3B8' }}>#{row.id}</td>
                              <td>{row.tenure} mo</td>
                              <td>{row.contract}</td>
                              <td>${row.monthlyCharges?.toFixed(2)}</td>
                              <td>
                                <span className={`badge ${row.predictedClass === 'Churn' ? 'badge-high' : 'badge-low'}`}>
                                  {row.predictedClass}
                                </span>
                              </td>
                              <td style={{ fontFamily: 'JetBrains Mono' }}>
                                {(row.churnProbability * 100).toFixed(1)}%
                              </td>
                              <td>
                                <span className={`badge ${
                                  row.riskLevel === 'High' ? 'badge-high' : 
                                  row.riskLevel === 'Medium' ? 'badge-medium' : 'badge-low'
                                }`}>
                                  {row.riskLevel}
                                </span>
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={7} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                              No evaluations recorded yet. Run a prediction on the "Predict Customer" tab.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: PREDICT CUSTOMER */}
          {activeTab === 'predict' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '28px' }}>
              <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <div className="card-title" style={{ margin: 0 }}>
                    <UserCheck size={20} color="#3B82F6" />
                    <span>Customer Profile Input Form</span>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button 
                      type="button" 
                      className="btn btn-secondary" 
                      style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                      onClick={() => handlePreset('high_risk')}
                    >
                      Sample: High Risk
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-secondary" 
                      style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                      onClick={() => handlePreset('low_risk')}
                    >
                      Sample: Low Risk
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-secondary" 
                      style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                      onClick={() => handlePreset('reset')}
                    >
                      Reset
                    </button>
                  </div>
                </div>

                {formError && (
                  <div className="alert alert-error">
                    <AlertTriangle size={18} />
                    <span>{formError}</span>
                  </div>
                )}

                <form onSubmit={handlePredictSubmit}>
                  <div className="form-grid">
                    {/* Demographics */}
                    <div className="form-section-title">1. Demographics & Household</div>
                    
                    <div className="form-group">
                      <label className="form-label">Gender</label>
                      <select name="gender" className="form-select" value={formData.gender} onChange={handleInputChange}>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Senior Citizen</label>
                      <select name="seniorCitizen" className="form-select" value={formData.seniorCitizen} onChange={handleInputChange}>
                        <option value={0}>No (0)</option>
                        <option value={1}>Yes (1)</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Partner</label>
                      <select name="partner" className="form-select" value={formData.partner} onChange={handleInputChange}>
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Dependents</label>
                      <select name="dependents" className="form-select" value={formData.dependents} onChange={handleInputChange}>
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                      </select>
                    </div>

                    {/* Services */}
                    <div className="form-section-title">2. Telecom & Internet Services</div>

                    <div className="form-group">
                      <label className="form-label">Phone Service</label>
                      <select name="phoneService" className="form-select" value={formData.phoneService} onChange={handleInputChange}>
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Multiple Lines</label>
                      <select name="multipleLines" className="form-select" value={formData.multipleLines} onChange={handleInputChange}>
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No phone service">No phone service</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Internet Service</label>
                      <select name="internetService" className="form-select" value={formData.internetService} onChange={handleInputChange}>
                        <option value="Fiber optic">Fiber optic</option>
                        <option value="DSL">DSL</option>
                        <option value="No">No (No Internet)</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Online Security</label>
                      <select name="onlineSecurity" className="form-select" value={formData.onlineSecurity} onChange={handleInputChange}>
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Online Backup</label>
                      <select name="onlineBackup" className="form-select" value={formData.onlineBackup} onChange={handleInputChange}>
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Device Protection</label>
                      <select name="deviceProtection" className="form-select" value={formData.deviceProtection} onChange={handleInputChange}>
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Tech Support</label>
                      <select name="techSupport" className="form-select" value={formData.techSupport} onChange={handleInputChange}>
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Streaming TV</label>
                      <select name="streamingTV" className="form-select" value={formData.streamingTV} onChange={handleInputChange}>
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Streaming Movies</label>
                      <select name="streamingMovies" className="form-select" value={formData.streamingMovies} onChange={handleInputChange}>
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    {/* Contract & Billing */}
                    <div className="form-section-title">3. Contract & Account Billing</div>

                    <div className="form-group">
                      <label className="form-label">Contract Plan</label>
                      <select name="contract" className="form-select" value={formData.contract} onChange={handleInputChange}>
                        <option value="Month-to-month">Month-to-month</option>
                        <option value="One year">One year</option>
                        <option value="Two year">Two year</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Paperless Billing</label>
                      <select name="paperlessBilling" className="form-select" value={formData.paperlessBilling} onChange={handleInputChange}>
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Payment Method</label>
                      <select name="paymentMethod" className="form-select" value={formData.paymentMethod} onChange={handleInputChange}>
                        <option value="Electronic check">Electronic check</option>
                        <option value="Mailed check">Mailed check</option>
                        <option value="Bank transfer (automatic)">Bank transfer (automatic)</option>
                        <option value="Credit card (automatic)">Credit card (automatic)</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Tenure (Months: 0-72)</label>
                      <input 
                        type="number" 
                        name="tenure" 
                        className="form-input" 
                        min="0" 
                        max="72"
                        value={formData.tenure} 
                        onChange={handleInputChange} 
                        required 
                      />
                    </div>

                    <div className="form-group">
                      <label className="form-label">Monthly Charges ($)</label>
                      <input 
                        type="number" 
                        name="monthlyCharges" 
                        className="form-input" 
                        step="0.05"
                        min="1" 
                        max="200"
                        value={formData.monthlyCharges} 
                        onChange={handleInputChange} 
                        required 
                      />
                    </div>

                    <div className="form-group">
                      <label className="form-label">Calculated Total Charges ($)</label>
                      <input 
                        type="number" 
                        name="totalCharges" 
                        className="form-input" 
                        value={formData.totalCharges} 
                        readOnly 
                        style={{ background: '#050914', color: '#94A3B8' }}
                      />
                    </div>
                  </div>

                  <div style={{ marginTop: '24px', display: 'flex', gap: '16px' }}>
                    <button 
                      type="submit" 
                      className="btn btn-primary" 
                      style={{ flex: 1 }}
                      disabled={predicting}
                    >
                      {predicting ? (
                        <>
                          <RefreshCw size={18} className="animate-spin" />
                          <span>Forwarding to ML Pipeline...</span>
                        </>
                      ) : (
                        <>
                          <span>EXECUTE CHURN PREDICTION</span>
                          <ArrowRight size={18} />
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>

              {/* Prediction Result Display */}
              <div>
                <div className="card" style={{ position: 'sticky', top: '100px' }}>
                  <div className="card-title">
                    <Activity size={20} color="#3B82F6" />
                    <span>Real-Time Inference Output</span>
                  </div>

                  {predictionResult ? (
                    <div>
                      <div style={{
                        padding: '24px',
                        borderRadius: 'var(--radius-md)',
                        background: predictionResult.prediction === 'Churn' ? 'rgba(239, 68, 68, 0.08)' : 'rgba(16, 185, 129, 0.08)',
                        border: `1px solid ${predictionResult.prediction === 'Churn' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
                        textAlign: 'center',
                        marginBottom: '20px'
                      }}>
                        <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                          Target Prediction Result
                        </div>

                        <div style={{
                          fontSize: '2.4rem',
                          fontWeight: 900,
                          margin: '8px 0',
                          color: predictionResult.prediction === 'Churn' ? '#EF4444' : '#10B981'
                        }}>
                          {predictionResult.prediction.toUpperCase()}
                        </div>

                        <span className={`badge ${
                          predictionResult.riskLevel === 'High' ? 'badge-high' : 
                          predictionResult.riskLevel === 'Medium' ? 'badge-medium' : 'badge-low'
                        }`}>
                          {predictionResult.riskLevel} RISK LEVEL
                        </span>
                      </div>

                      {/* Probability Gauge */}
                      <div style={{ marginBottom: '22px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                          <span style={{ color: 'var(--text-secondary)' }}>Calculated Churn Probability:</span>
                          <span style={{ fontWeight: 800, fontFamily: 'JetBrains Mono', color: '#FFFFFF' }}>
                            {(predictionResult.churnProbability * 100).toFixed(1)}%
                          </span>
                        </div>

                        <div style={{ height: '10px', background: '#0A1020', borderRadius: '5px', overflow: 'hidden' }}>
                          <div style={{
                            width: `${predictionResult.churnProbability * 100}%`,
                            height: '100%',
                            background: predictionResult.churnProbability > 0.65 ? '#EF4444' : (predictionResult.churnProbability > 0.35 ? '#F59E0B' : '#10B981'),
                            transition: 'width 0.6s ease'
                          }} />
                        </div>
                      </div>

                      {/* Tailored Recommendation */}
                      <div style={{
                        background: '#080E1C',
                        border: '1px solid var(--border-color)',
                        borderRadius: 'var(--radius-md)',
                        padding: '16px',
                        marginBottom: '20px'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#60A5FA', fontSize: '0.85rem', fontWeight: 700, marginBottom: '6px' }}>
                          <Info size={16} />
                          <span>Actionable Business Recommendation</span>
                        </div>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                          {predictionResult.recommendation}
                        </p>
                      </div>

                      {/* Technical Audit Meta */}
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-color)', paddingTop: '14px' }}>
                        <div>Persisted ID: <span style={{ color: '#FFFFFF', fontFamily: 'JetBrains Mono' }}>#{predictionResult.id}</span></div>
                        <div>Model Artifact: <span style={{ color: '#FFFFFF' }}>{predictionResult.model}</span></div>
                        <div>Timestamp: <span style={{ color: '#FFFFFF' }}>{new Date(predictionResult.timestamp).toLocaleString()}</span></div>
                      </div>
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
                      <HelpCircle size={40} style={{ margin: '0 auto 16px', opacity: 0.4 }} />
                      <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                        Inference Pipeline Idle
                      </div>
                      <p style={{ fontSize: '0.82rem', marginTop: '6px' }}>
                        Fill out customer features on the left and click "Execute Churn Prediction" to evaluate the Random Forest model.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: PREDICTION HISTORY */}
          {activeTab === 'history' && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div className="card-title" style={{ margin: 0 }}>
                  <Clock size={20} color="#3B82F6" />
                  <span>Audit Trail of Historical Evaluations</span>
                </div>

                <div style={{ display: 'flex', gap: '12px' }}>
                  <input 
                    type="text" 
                    placeholder="Search by ID, class, risk, plan..." 
                    className="form-input"
                    style={{ width: '280px', padding: '8px 12px' }}
                    value={historySearch}
                    onChange={(e) => setHistorySearch(e.target.value)}
                  />
                  <button className="btn btn-secondary" onClick={loadHistory}>
                    <RefreshCw size={16} className={loadingHistory ? 'animate-spin' : ''} />
                    <span>Refresh</span>
                  </button>
                </div>
              </div>

              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Date / Time</th>
                      <th>Contract</th>
                      <th>Tenure</th>
                      <th>Internet</th>
                      <th>Monthly</th>
                      <th>Prediction</th>
                      <th>Probability</th>
                      <th>Risk</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredHistory.length ? (
                      filteredHistory.map((row) => (
                        <tr key={row.id}>
                          <td style={{ fontFamily: 'JetBrains Mono', color: '#94A3B8' }}>#{row.id}</td>
                          <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            {new Date(row.timestamp).toLocaleDateString()} {new Date(row.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </td>
                          <td>{row.contract}</td>
                          <td>{row.tenure} mo</td>
                          <td>{row.internetService}</td>
                          <td>${row.monthlyCharges?.toFixed(2)}</td>
                          <td>
                            <span className={`badge ${row.predictedClass === 'Churn' ? 'badge-high' : 'badge-low'}`}>
                              {row.predictedClass}
                            </span>
                          </td>
                          <td style={{ fontFamily: 'JetBrains Mono' }}>
                            {(row.churnProbability * 100).toFixed(1)}%
                          </td>
                          <td>
                            <span className={`badge ${
                              row.riskLevel === 'High' ? 'badge-high' : 
                              row.riskLevel === 'Medium' ? 'badge-medium' : 'badge-low'
                            }`}>
                              {row.riskLevel}
                            </span>
                          </td>
                          <td>
                            <button 
                              className="btn btn-secondary" 
                              style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                              onClick={() => setSelectedRecord(row)}
                            >
                              Inspect
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={10} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                          {loadingHistory ? 'Loading records from backend...' : 'No historical evaluations match your filter.'}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: MODEL PERFORMANCE */}
          {activeTab === 'performance' && (
            <div>
              <div className="card" style={{ marginBottom: '24px' }}>
                <div className="card-title">
                  <Activity size={20} color="#3B82F6" />
                  <span>Held-Out Test Set Metrics (IBM Telecom Churn Dataset)</span>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '24px' }}>
                  Model trained using Scikit-learn Pipeline with ColumnTransformer (StandardScaler & OneHotEncoder) and RandomForestClassifier.
                  Evaluation performed on 20% holdout test dataset (1,409 unobserved customers) with zero data leakage.
                </p>

                {modelMetrics ? (
                  <>
                    <div className="kpi-grid" style={{ marginBottom: '28px' }}>
                      <div className="kpi-card">
                        <div className="kpi-label">Test Accuracy</div>
                        <div className="kpi-value" style={{ color: '#60A5FA' }}>
                          {(modelMetrics.accuracy * 100).toFixed(2)}%
                        </div>
                        <div className="kpi-sub">Overall correct classifications</div>
                      </div>

                      <div className="kpi-card">
                        <div className="kpi-label">ROC - AUC Score</div>
                        <div className="kpi-value" style={{ color: '#34D399' }}>
                          {(modelMetrics.rocAuc * 100).toFixed(2)}%
                        </div>
                        <div className="kpi-sub">Discriminative ranking power</div>
                      </div>

                      <div className="kpi-card">
                        <div className="kpi-label">Recall (Sensitivity)</div>
                        <div className="kpi-value" style={{ color: '#FBBF24' }}>
                          {(modelMetrics.recall * 100).toFixed(2)}%
                        </div>
                        <div className="kpi-sub">Detected churners ratio</div>
                      </div>

                      <div className="kpi-card">
                        <div className="kpi-label">F1 - Score</div>
                        <div className="kpi-value" style={{ color: '#A78BFA' }}>
                          {(modelMetrics.f1Score * 100).toFixed(2)}%
                        </div>
                        <div className="kpi-sub">Harmonic mean precision/recall</div>
                      </div>
                    </div>

                    {/* Confusion Matrix and Dataset Specifications */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                      <div className="card" style={{ background: '#0A1121' }}>
                        <div className="card-title">
                          <CheckCircle2 size={18} color="#34D399" />
                          <span>Confusion Matrix (Held-out Test: 1,409)</span>
                        </div>

                        <div className="cm-grid">
                          <div className="cm-cell">
                            <div className="cm-cell-label">True Negative (Retained Correctly)</div>
                            <div className="cm-cell-value" style={{ color: '#10B981' }}>
                              {modelMetrics.confusionMatrix?.trueNegative}
                            </div>
                          </div>

                          <div className="cm-cell">
                            <div className="cm-cell-label">False Positive (False Alarm)</div>
                            <div className="cm-cell-value" style={{ color: '#F59E0B' }}>
                              {modelMetrics.confusionMatrix?.falsePositive}
                            </div>
                          </div>

                          <div className="cm-cell">
                            <div className="cm-cell-label">False Negative (Missed Churn)</div>
                            <div className="cm-cell-value" style={{ color: '#EF4444' }}>
                              {modelMetrics.confusionMatrix?.falseNegative}
                            </div>
                          </div>

                          <div className="cm-cell">
                            <div className="cm-cell-label">True Positive (Churn Detected)</div>
                            <div className="cm-cell-value" style={{ color: '#3B82F6' }}>
                              {modelMetrics.confusionMatrix?.truePositive}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="card" style={{ background: '#0A1121' }}>
                        <div className="card-title">
                          <FileText size={18} color="#60A5FA" />
                          <span>Dataset & Pipeline Specifications</span>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.88rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Dataset Source:</span>
                            <span style={{ fontWeight: 600 }}>{modelMetrics.datasetSource}</span>
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Total Records:</span>
                            <span style={{ fontWeight: 600 }}>{modelMetrics.totalRecordCount?.toLocaleString()}</span>
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Training Partition (80%):</span>
                            <span style={{ fontWeight: 600 }}>{modelMetrics.trainRecordCount?.toLocaleString()} rows</span>
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Test Partition (20%):</span>
                            <span style={{ fontWeight: 600 }}>{modelMetrics.testRecordCount?.toLocaleString()} rows</span>
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Estimator:</span>
                            <span style={{ fontWeight: 600, color: '#60A5FA' }}>{modelMetrics.model}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                    <RefreshCw size={24} className="animate-spin" style={{ margin: '0 auto 12px' }} />
                    <div>Loading genuine model metrics from backend...</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Record Inspection Modal */}
      {selectedRecord && (
        <div className="modal-overlay" onClick={() => setSelectedRecord(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#FFFFFF' }}>
                Customer Audit Detail #{selectedRecord.id}
              </h3>
              <button 
                className="btn btn-secondary" 
                style={{ padding: '6px 12px' }} 
                onClick={() => setSelectedRecord(null)}
              >
                ✕ Close
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Prediction Result:</span>
                <div>
                  <span className={`badge ${selectedRecord.predictedClass === 'Churn' ? 'badge-high' : 'badge-low'}`}>
                    {selectedRecord.predictedClass}
                  </span>
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Churn Probability:</span>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, fontFamily: 'JetBrains Mono', color: '#FFFFFF' }}>
                  {(selectedRecord.churnProbability * 100).toFixed(1)}%
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Contract Plan:</span>
                <div style={{ fontWeight: 600 }}>{selectedRecord.contract}</div>
              </div>

              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Customer Tenure:</span>
                <div style={{ fontWeight: 600 }}>{selectedRecord.tenure} months</div>
              </div>

              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Monthly Charges:</span>
                <div style={{ fontWeight: 600 }}>${selectedRecord.monthlyCharges?.toFixed(2)}</div>
              </div>

              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Internet Service:</span>
                <div style={{ fontWeight: 600 }}>{selectedRecord.internetService}</div>
              </div>

              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Payment Method:</span>
                <div style={{ fontWeight: 600 }}>{selectedRecord.paymentMethod}</div>
              </div>

              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Model Artifact:</span>
                <div style={{ fontWeight: 600, color: '#60A5FA' }}>{selectedRecord.modelVersion}</div>
              </div>
            </div>

            <div style={{ background: '#090F1E', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#60A5FA', marginBottom: '6px' }}>
                Retention Recommendation
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                {selectedRecord.recommendation}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
