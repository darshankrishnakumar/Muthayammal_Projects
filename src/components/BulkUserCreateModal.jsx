import { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { 
  Upload, 
  FileSpreadsheet, 
  Download, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Users, 
  Plus, 
  Trash2, 
  X, 
  Sparkles,
  ArrowRight,
  RefreshCw,
  FileDown
} from 'lucide-react';

const EMAIL_REGEX = /^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$/;

const SAMPLE_CSV_TEMPLATE = `Full Name,Email,Password,Phone,Role,Department,Organization
Dr. Priya Sharma,priya.sharma@academic.edu,Research123!,9876543210,USER,Computer Science,IIT Madras
Prof. Rajesh Verma,rajesh.verma@academic.edu,Passw0rd123!,9876543211,PROJECT_DEVELOPER,Data Science,IISc Bangalore
Anita Desai,anita.desai@academic.edu,Secure2026!,9876543212,USER,Biotechnology,Delhi University`;

const BulkUserCreateModal = ({ isOpen, onClose, onSuccess, existingUsers = [] }) => {
  const { user: currentUser } = useAuth();
  const fileInputRef = useRef(null);

  const [activeTab, setActiveTab] = useState('upload'); // 'upload' | 'manual'
  const [parsedRows, setParsedRows] = useState([]);
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [resultSummary, setResultSummary] = useState(null); // When complete

  const isSuperAdmin = currentUser?.role === 'SUPER_ADMIN';
  const isAdmin = currentUser?.role === 'ADMIN';

  // Manual grid initial state
  const [manualRows, setManualRows] = useState([
    { id: 1, fullName: '', email: '', password: '', phone: '', role: 'USER', department: '', organization: '' },
    { id: 2, fullName: '', email: '', password: '', phone: '', role: 'USER', department: '', organization: '' },
    { id: 3, fullName: '', email: '', password: '', phone: '', role: 'USER', department: '', organization: '' }
  ]);

  if (!isOpen) return null;

  // 1. Download CSV Template
  const handleDownloadTemplate = () => {
    const blob = new Blob([SAMPLE_CSV_TEMPLATE], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'bulk_users_template.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 2. Parse CSV text
  const parseCSVText = (text) => {
    const lines = text.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0);
    if (lines.length <= 1) {
      throw new Error('CSV file contains no user records or only contains a header.');
    }

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
    
    // Header mappings
    const getIndex = (keys) => headers.findIndex(h => keys.some(k => h.includes(k)));
    const nameIdx = getIndex(['full name', 'name', 'fullname']);
    const emailIdx = getIndex(['email', 'mail']);
    const passIdx = getIndex(['password', 'pass', 'pwd']);
    const phoneIdx = getIndex(['phone', 'mobile', 'contact']);
    const roleIdx = getIndex(['role', 'type', 'designation']);
    const deptIdx = getIndex(['dept', 'department', 'branch']);
    const orgIdx = getIndex(['org', 'organization', 'institution', 'college', 'university']);

    if (nameIdx === -1 || emailIdx === -1) {
      throw new Error('CSV header must contain at least "Full Name" and "Email" columns.');
    }

    const rows = [];
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i];
      // Split by comma ignoring commas inside quotes
      const values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || line.split(',');
      const cleanVal = (idx) => {
        if (idx === -1 || !values[idx]) return '';
        return values[idx].replace(/^["']|["']$/g, '').trim();
      };

      const fullName = cleanVal(nameIdx);
      const email = cleanVal(emailIdx).toLowerCase();
      const password = cleanVal(passIdx) || 'User12345!';
      const phone = cleanVal(phoneIdx);
      let role = cleanVal(roleIdx).toUpperCase() || 'USER';
      const department = cleanVal(deptIdx);
      const organization = cleanVal(orgIdx);

      if (fullName || email) {
        rows.push({
          id: i,
          fullName,
          email,
          password,
          phone,
          role,
          department,
          organization
        });
      }
    }

    return rows;
  };

  // 3. Handle File Upload
  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setErrorMsg('');

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const text = event.target?.result;
        if (typeof text !== 'string') return;
        const parsed = parseCSVText(text);
        setParsedRows(parsed);
      } catch (err) {
        setErrorMsg(err.message || 'Failed to parse CSV file.');
        setParsedRows([]);
      }
    };
    reader.onerror = () => {
      setErrorMsg('Error reading uploaded file.');
    };
    reader.readAsText(file);
  };

  // 4. Manual Row Helpers
  const handleAddManualRow = () => {
    setManualRows(prev => [
      ...prev,
      { id: Date.now(), fullName: '', email: '', password: '', phone: '', role: 'USER', department: '', organization: '' }
    ]);
  };

  const handleUpdateManualRow = (id, field, value) => {
    setManualRows(prev => prev.map(r => r.id === id ? { ...r, [field]: value } : r));
  };

  const handleRemoveManualRow = (id) => {
    setManualRows(prev => prev.filter(r => r.id !== id));
  };

  // 5. Validation Engine
  const getActiveRows = () => {
    if (activeTab === 'upload') {
      return parsedRows;
    } else {
      return manualRows.filter(r => r.fullName.trim() || r.email.trim());
    }
  };

  const validateRows = (rows) => {
    const processedEmailsInBatch = new Set();
    
    return rows.map((row, idx) => {
      const rowNum = idx + 1;
      const issues = [];

      const fullName = (row.fullName || '').trim();
      const email = (row.email || '').trim().toLowerCase();
      let role = (row.role || 'USER').toUpperCase();

      // Required fields
      if (!fullName) issues.push('Full Name required');
      if (!email) issues.push('Email required');
      else if (!EMAIL_REGEX.test(email)) issues.push('Invalid email format');

      // Duplicate check within batch
      if (email && processedEmailsInBatch.has(email)) {
        issues.push('Duplicate email in upload batch');
      } else if (email) {
        processedEmailsInBatch.add(email);
      }

      // Duplicate check against existing users
      if (email && existingUsers.some(u => !u.deleted && u.email?.toLowerCase() === email)) {
        issues.push('Email already registered in system');
      }

      // RBAC check
      if (isAdmin && (role === 'SUPER_ADMIN' || role === 'ADMIN')) {
        issues.push(`Admin cannot assign ${role} role`);
      }

      const isValid = issues.length === 0;
      return {
        ...row,
        rowNum,
        isValid,
        issueText: issues.join(', ')
      };
    });
  };

  const currentValidatedRows = validateRows(getActiveRows());
  const validRows = currentValidatedRows.filter(r => r.isValid);
  const invalidRows = currentValidatedRows.filter(r => !r.isValid);

  // 6. Download Error Report
  const handleDownloadErrorReport = () => {
    if (invalidRows.length === 0) return;

    let csvContent = 'Row,Full Name,Email,Role,Department,Error Reason\n';
    invalidRows.forEach(r => {
      csvContent += `"${r.rowNum}","${r.fullName || ''}","${r.email || ''}","${r.role || ''}","${r.department || ''}","${r.issueText}"\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'bulk_creation_error_report.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 7. Execute Bulk Creation
  const handleCreateValidUsers = async () => {
    if (validRows.length === 0) return;

    setLoading(true);
    setErrorMsg('');

    try {
      const payload = validRows.map(r => ({
        fullName: r.fullName.trim(),
        email: r.email.trim().toLowerCase(),
        password: r.password || 'User12345!',
        phone: r.phone || '',
        role: r.role || 'USER',
        department: r.department || '',
        organization: r.organization || r.department || 'Academic Institution'
      }));

      const res = await api.bulkCreateUsers(payload);
      setResultSummary(res);
      if (onSuccess) onSuccess();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to complete bulk user creation.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setParsedRows([]);
    setFileName('');
    setResultSummary(null);
    setErrorMsg('');
    onClose();
  };

  return (
    <div className="modal-overlay" style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(15, 23, 42, 0.75)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(6px)', padding: '20px' }}>
      <div className="modal-content" style={{ width: '100%', maxWidth: '950px', maxHeight: '90vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: 0, border: '1px solid var(--border-color)', borderRadius: '14px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)', backgroundColor: 'var(--bg-card, #ffffff)' }}>
        
        {/* Modal Header */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'var(--bg-card, #ffffff)' }}>
          <div className="flex items-center gap-3">
            <div style={{ width: '42px', height: '42px', borderRadius: '10px', background: 'linear-gradient(135deg, rgba(79, 70, 229, 0.2), rgba(124, 58, 237, 0.2))', border: '1px solid rgba(99, 102, 241, 0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
              <Users size={22} />
            </div>
            <div>
              <h2 className="font-display" style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                Bulk User Provisioning & Ingestion
              </h2>
              <p className="text-muted" style={{ fontSize: '0.82rem', margin: '2px 0 0 0' }}>
                Batch create academic researchers, project developers, and system users with instant validation.
              </p>
            </div>
          </div>
          <button 
            onClick={handleClose}
            className="btn btn-secondary" 
            style={{ padding: '6px 10px', border: 'none', background: 'transparent', cursor: 'pointer', color: 'var(--text-muted)' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '24px', overflowY: 'auto', flex: 1, backgroundColor: 'var(--bg-card, #ffffff)' }}>
          
          {/* Result Summary Screen */}
          {resultSummary ? (
            <div style={{ textAlign: 'center', padding: '24px 16px' }}>
              <div style={{ width: '64px', height: '64px', borderRadius: '50%', backgroundColor: 'var(--success-light)', color: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                <CheckCircle2 size={36} />
              </div>
              <h3 className="font-display" style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '6px' }}>
                Bulk User Creation Completed
              </h3>
              <p className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '24px' }}>
                Successfully processed user batch and updated system access directories.
              </p>

              {/* Metric Cards */}
              <div className="grid grid-cols-4 gap-4" style={{ marginBottom: '24px' }}>
                <div className="card text-center" style={{ padding: '16px' }}>
                  <span className="text-muted" style={{ fontSize: '0.78rem', display: 'block' }}>Total Records</span>
                  <span style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {resultSummary.totalRecords || validRows.length}
                  </span>
                </div>
                <div className="card text-center" style={{ padding: '16px', borderLeft: '4px solid var(--success)' }}>
                  <span className="text-muted" style={{ fontSize: '0.78rem', display: 'block' }}>Successfully Created</span>
                  <span style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--success)' }}>
                    {resultSummary.successCount || validRows.length}
                  </span>
                </div>
                <div className="card text-center" style={{ padding: '16px', borderLeft: '4px solid var(--warning)' }}>
                  <span className="text-muted" style={{ fontSize: '0.78rem', display: 'block' }}>Duplicates Skipped</span>
                  <span style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--warning)' }}>
                    {resultSummary.duplicateCount || 0}
                  </span>
                </div>
                <div className="card text-center" style={{ padding: '16px', borderLeft: '4px solid var(--error)' }}>
                  <span className="text-muted" style={{ fontSize: '0.78rem', display: 'block' }}>Failed / Invalid</span>
                  <span style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--error)' }}>
                    {resultSummary.failedCount || invalidRows.length}
                  </span>
                </div>
              </div>

              {/* Download Errors Button if any */}
              {resultSummary.errors && resultSummary.errors.length > 0 && (
                <div className="mb-6 flex justify-center">
                  <button 
                    onClick={handleDownloadErrorReport} 
                    className="btn btn-secondary flex items-center gap-2"
                    style={{ borderColor: 'var(--error)', color: 'var(--error)' }}
                  >
                    <Download size={16} />
                    <span>Download Failed Records Report ({resultSummary.errors.length})</span>
                  </button>
                </div>
              )}

              <div className="flex justify-center gap-4">
                <button onClick={handleClose} className="btn btn-primary" style={{ minWidth: '180px' }}>
                  Return to User Management
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Tabs Bar */}
              <div className="flex justify-between items-center mb-5 flex-wrap gap-3">
                <div className="flex gap-2" style={{ backgroundColor: 'var(--bg-main)', padding: '4px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <button
                    onClick={() => setActiveTab('upload')}
                    className={`btn ${activeTab === 'upload' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 14px', fontSize: '0.85rem' }}
                  >
                    <Upload size={15} className="mr-1.5 inline" />
                    Upload CSV / File
                  </button>
                  <button
                    onClick={() => setActiveTab('manual')}
                    className={`btn ${activeTab === 'manual' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 14px', fontSize: '0.85rem' }}
                  >
                    <FileSpreadsheet size={15} className="mr-1.5 inline" />
                    Interactive Table Entry
                  </button>
                </div>

                {/* Template Download Button */}
                <button
                  onClick={handleDownloadTemplate}
                  className="btn btn-secondary flex items-center gap-2"
                  style={{ fontSize: '0.82rem', padding: '6px 14px' }}
                >
                  <Download size={15} />
                  <span>Download Sample CSV Template</span>
                </button>
              </div>

              {errorMsg && (
                <div className="alert alert-error mb-4 flex items-center gap-2" style={{ padding: '10px 14px', borderRadius: '8px' }}>
                  <AlertTriangle size={18} />
                  <span style={{ fontSize: '0.88rem' }}>{errorMsg}</span>
                </div>
              )}

              {/* Tab 1: CSV Upload */}
              {activeTab === 'upload' && (
                <div>
                  <div 
                    onClick={() => fileInputRef.current?.click()}
                    style={{
                      border: '2px dashed var(--border-color)',
                      borderRadius: '12px',
                      padding: '36px 20px',
                      textAlign: 'center',
                      cursor: 'pointer',
                      backgroundColor: 'rgba(255, 255, 255, 0.02)',
                      transition: 'border-color 0.2s',
                      marginBottom: '20px'
                    }}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={(e) => {
                      e.preventDefault();
                      if (e.dataTransfer.files?.[0]) {
                        const file = e.dataTransfer.files[0];
                        const fakeEvent = { target: { files: [file] } };
                        handleFileUpload(fakeEvent);
                      }
                    }}
                  >
                    <input 
                      type="file" 
                      ref={fileInputRef} 
                      onChange={handleFileUpload} 
                      accept=".csv, .txt" 
                      style={{ display: 'none' }} 
                    />
                    <div style={{ width: '50px', height: '50px', borderRadius: '50%', backgroundColor: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px' }}>
                      <Upload size={24} />
                    </div>
                    <h4 style={{ fontSize: '1rem', fontWeight: 600, margin: '0 0 4px 0' }}>
                      {fileName ? `Selected: ${fileName}` : 'Click or Drag & Drop CSV file here'}
                    </h4>
                    <p className="text-muted" style={{ fontSize: '0.82rem', margin: 0 }}>
                      Supports standard CSV files with headers: Full Name, Email, Password, Phone, Role, Department
                    </p>
                  </div>
                </div>
              )}

              {/* Tab 2: Manual Grid Entry */}
              {activeTab === 'manual' && (
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ overflowX: 'auto', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
                    <table style={{ width: '100%', fontSize: '0.84rem', borderCollapse: 'collapse' }}>
                      <thead style={{ backgroundColor: 'var(--bg-main)', borderBottom: '1px solid var(--border-color)' }}>
                        <tr>
                          <th style={{ padding: '10px 12px', textAlign: 'left' }}>#</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left' }}>Full Name *</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left' }}>Email Address *</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left' }}>Role</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left' }}>Password</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left' }}>Department</th>
                          <th style={{ padding: '10px 12px', textAlign: 'left' }}>Phone</th>
                          <th style={{ padding: '10px 12px', textAlign: 'center' }}></th>
                        </tr>
                      </thead>
                      <tbody>
                        {manualRows.map((row, idx) => (
                          <tr key={row.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                            <td style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>{idx + 1}</td>
                            <td style={{ padding: '8px 12px' }}>
                              <input 
                                type="text"
                                className="form-control"
                                placeholder="e.g. John Doe"
                                value={row.fullName}
                                onChange={(e) => handleUpdateManualRow(row.id, 'fullName', e.target.value)}
                                style={{ padding: '6px 10px', fontSize: '0.84rem', width: '140px' }}
                              />
                            </td>
                            <td style={{ padding: '8px 12px' }}>
                              <input 
                                type="email"
                                className="form-control"
                                placeholder="e.g. john@academic.edu"
                                value={row.email}
                                onChange={(e) => handleUpdateManualRow(row.id, 'email', e.target.value)}
                                style={{ padding: '6px 10px', fontSize: '0.84rem', width: '180px' }}
                              />
                            </td>
                            <td style={{ padding: '8px 12px' }}>
                              <select
                                className="form-control"
                                value={row.role}
                                onChange={(e) => handleUpdateManualRow(row.id, 'role', e.target.value)}
                                style={{ padding: '6px 8px', fontSize: '0.84rem', width: '130px' }}
                              >
                                <option value="USER">User (Student)</option>
                                <option value="PROJECT_DEVELOPER">Developer</option>
                                {isSuperAdmin && <option value="ADMIN">Admin</option>}
                              </select>
                            </td>
                            <td style={{ padding: '8px 12px' }}>
                              <input 
                                type="text"
                                className="form-control"
                                placeholder="Auto-generate"
                                value={row.password}
                                onChange={(e) => handleUpdateManualRow(row.id, 'password', e.target.value)}
                                style={{ padding: '6px 10px', fontSize: '0.84rem', width: '110px' }}
                              />
                            </td>
                            <td style={{ padding: '8px 12px' }}>
                              <input 
                                type="text"
                                className="form-control"
                                placeholder="Dept / Org"
                                value={row.department}
                                onChange={(e) => handleUpdateManualRow(row.id, 'department', e.target.value)}
                                style={{ padding: '6px 10px', fontSize: '0.84rem', width: '120px' }}
                              />
                            </td>
                            <td style={{ padding: '8px 12px' }}>
                              <input 
                                type="text"
                                className="form-control"
                                placeholder="9876543210"
                                value={row.phone}
                                onChange={(e) => handleUpdateManualRow(row.id, 'phone', e.target.value)}
                                style={{ padding: '6px 10px', fontSize: '0.84rem', width: '100px' }}
                              />
                            </td>
                            <td style={{ padding: '8px 12px', textAlign: 'center' }}>
                              <button
                                onClick={() => handleRemoveManualRow(row.id)}
                                className="btn btn-secondary"
                                style={{ padding: '4px 8px', color: 'var(--error)', border: 'none', background: 'transparent' }}
                                title="Remove row"
                              >
                                <Trash2 size={15} />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="mt-3 flex justify-start">
                    <button
                      onClick={handleAddManualRow}
                      className="btn btn-secondary flex items-center gap-1.5"
                      style={{ fontSize: '0.82rem', padding: '6px 12px' }}
                    >
                      <Plus size={14} />
                      <span>Add Row</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Preview & Validation Table */}
              {currentValidatedRows.length > 0 && (
                <div style={{ marginTop: '16px' }}>
                  <div className="flex justify-between items-center mb-3">
                    <div className="flex items-center gap-2">
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>
                        Ingestion Preview ({currentValidatedRows.length} Records)
                      </h4>
                      <span className="badge badge-success" style={{ fontSize: '0.74rem' }}>
                        {validRows.length} Valid
                      </span>
                      {invalidRows.length > 0 && (
                        <span className="badge badge-danger" style={{ fontSize: '0.74rem' }}>
                          {invalidRows.length} Issues Found
                        </span>
                      )}
                    </div>

                    {invalidRows.length > 0 && (
                      <button
                        onClick={handleDownloadErrorReport}
                        className="btn btn-secondary flex items-center gap-1.5 text-error"
                        style={{ fontSize: '0.78rem', padding: '4px 10px' }}
                      >
                        <FileDown size={14} />
                        <span>Download Error Report</span>
                      </button>
                    )}
                  </div>

                  <div style={{ maxHeight: '240px', overflowY: 'auto', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
                    <table style={{ width: '100%', fontSize: '0.82rem', borderCollapse: 'collapse' }}>
                      <thead style={{ backgroundColor: 'var(--bg-main)', borderBottom: '1px solid var(--border-color)', position: 'sticky', top: 0, zIndex: 1 }}>
                        <tr>
                          <th style={{ padding: '8px 12px', textAlign: 'left' }}>#</th>
                          <th style={{ padding: '8px 12px', textAlign: 'left' }}>Full Name</th>
                          <th style={{ padding: '8px 12px', textAlign: 'left' }}>Email Address</th>
                          <th style={{ padding: '8px 12px', textAlign: 'left' }}>Role</th>
                          <th style={{ padding: '8px 12px', textAlign: 'left' }}>Department</th>
                          <th style={{ padding: '8px 12px', textAlign: 'left' }}>Validation Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {currentValidatedRows.map((row) => (
                          <tr key={row.rowNum} style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: row.isValid ? 'transparent' : 'rgba(239, 68, 68, 0.05)' }}>
                            <td style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>{row.rowNum}</td>
                            <td style={{ padding: '8px 12px', fontWeight: 500 }}>{row.fullName || '—'}</td>
                            <td style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>{row.email || '—'}</td>
                            <td style={{ padding: '8px 12px' }}>
                              <span className="badge badge-secondary" style={{ fontSize: '0.72rem' }}>
                                {row.role}
                              </span>
                            </td>
                            <td style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>{row.department || '—'}</td>
                            <td style={{ padding: '8px 12px' }}>
                              {row.isValid ? (
                                <span className="flex items-center gap-1 text-success" style={{ fontSize: '0.78rem', fontWeight: 600 }}>
                                  <CheckCircle2 size={14} />
                                  <span>Ready</span>
                                </span>
                              ) : (
                                <span className="flex items-center gap-1 text-error" style={{ fontSize: '0.78rem', fontWeight: 600 }}>
                                  <XCircle size={14} />
                                  <span>{row.issueText}</span>
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}

        </div>

        {/* Modal Footer */}
        {!resultSummary && (
          <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'var(--bg-card, #ffffff)' }}>
            <div className="text-muted" style={{ fontSize: '0.82rem' }}>
              {validRows.length > 0 ? (
                <span><strong>{validRows.length}</strong> valid users will be created and activated.</span>
              ) : (
                <span>Upload a CSV or fill in rows to validate user records.</span>
              )}
            </div>

            <div className="flex gap-3">
              <button 
                onClick={handleClose} 
                className="btn btn-secondary"
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                onClick={handleCreateValidUsers}
                disabled={validRows.length === 0 || loading}
                className="btn btn-primary flex items-center gap-2"
                style={{ minWidth: '180px' }}
              >
                {loading ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    <span>Processing Batch...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={16} />
                    <span>Create {validRows.length} Valid Users</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default BulkUserCreateModal;
