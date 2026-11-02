import { useRef, useState } from 'react';
import { CheckCircle2, Download, FileDown, FileSpreadsheet, Plus, Trash2, Upload, XCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { Modal, Segmented, Field, Badge, Alert, StatCard, useToast } from './ui';
import { ROLE_LABELS } from '../utils/format';

const EMAIL_REGEX = /^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$/;
const MIN_PASSWORD = 8;
const COLLEGE_ROLES = ['USER', 'ADMIN'];

const TEMPLATE_HEADER = 'Full Name,Email,Password,Phone,Role,Department,Organization';
const TEMPLATE_STUDENTS = [
  'Priya Sharma,priya.sharma@example.edu,Welcome-2026,9876543210,USER,Computer Science,',
  'Anita Desai,anita.desai@example.edu,Campus#Start1,9876543212,USER,Biotechnology,',
];
const TEMPLATE_SUPER_ADMIN_EXTRA = ['Rajesh Verma,rajesh.verma@example.com,Build-Ready-9,9876543211,PROJECT_DEVELOPER,,Development Core'];

let rowSeq = 0;
const blankRow = () => ({ id: `row-${++rowSeq}`, fullName: '', email: '', password: '', phone: '', role: 'USER', department: '', organization: '' });

/** Splits one CSV line, honouring double-quoted fields and escaped quotes. */
const splitCsvLine = (line) => {
  const out = [];
  let cur = '';
  let quoted = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (quoted) {
      if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; }
      else if (ch === '"') quoted = false;
      else cur += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ',') { out.push(cur); cur = ''; }
    else cur += ch;
  }
  out.push(cur);
  return out.map((v) => v.trim());
};

const downloadCsv = (filename, text) => {
  const blob = new Blob([text], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
};

const csvCell = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;

/**
 * Bulk account creation from a CSV file or an editable grid.
 * Super Admin picks the college for student/admin rows; a college admin always creates students of their own college.
 * Every row needs its own password (at least 8 characters); there is no default password.
 */
const BulkUserCreateModal = ({ isOpen, onClose, onSuccess, existingUsers = [], colleges = [] }) => {
  const { user: currentUser } = useAuth();
  const { notify } = useToast();
  const fileInputRef = useRef(null);
  const isSuperAdmin = currentUser?.role === 'SUPER_ADMIN';
  const allowedRoles = isSuperAdmin ? ['USER', 'PROJECT_DEVELOPER', 'ADMIN'] : ['USER'];

  const [mode, setMode] = useState('upload');
  const [parsedRows, setParsedRows] = useState([]);
  const [manualRows, setManualRows] = useState(() => [blankRow(), blankRow(), blankRow()]);
  const [fileName, setFileName] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [collegeId, setCollegeId] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [result, setResult] = useState(null);

  if (!isOpen) return null;

  const handleDownloadTemplate = () => {
    const lines = [TEMPLATE_HEADER, ...TEMPLATE_STUDENTS, ...(isSuperAdmin ? TEMPLATE_SUPER_ADMIN_EXTRA : [])];
    downloadCsv('bulk_users_template.csv', lines.join('\n'));
  };

  const parseCSVText = (text) => {
    const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);
    if (lines.length <= 1) throw new Error('The file has no rows below the header.');
    const headers = splitCsvLine(lines[0]).map((h) => h.toLowerCase().replace(/['"]/g, ''));
    const indexOf = (keys) => headers.findIndex((h) => keys.some((k) => h.includes(k)));
    const idx = {
      fullName: indexOf(['full name', 'fullname', 'name']),
      email: indexOf(['email', 'mail']),
      password: indexOf(['password', 'pass', 'pwd']),
      phone: indexOf(['phone', 'mobile', 'contact']),
      role: indexOf(['role', 'type', 'designation']),
      department: indexOf(['dept', 'department', 'branch']),
      organization: indexOf(['org', 'organization', 'institution', 'university']),
    };
    if (idx.fullName === -1 || idx.email === -1) throw new Error('The header must include "Full Name" and "Email" columns.');

    const rows = [];
    for (let i = 1; i < lines.length; i++) {
      const values = splitCsvLine(lines[i]);
      const get = (k) => (idx[k] === -1 ? '' : values[idx[k]] || '');
      const row = {
        id: `csv-${i}`,
        fullName: get('fullName'),
        email: get('email').toLowerCase(),
        password: get('password'),
        phone: get('phone'),
        role: (get('role') || 'USER').toUpperCase(),
        department: get('department'),
        organization: get('organization'),
      };
      if (row.fullName || row.email) rows.push(row);
    }
    return rows;
  };

  const readFile = (file) => {
    if (!file) return;
    setFileName(file.name);
    setErrorMsg('');
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        setParsedRows(parseCSVText(String(event.target?.result || '')));
      } catch (err) {
        setErrorMsg(err.message);
        setParsedRows([]);
      }
    };
    reader.onerror = () => setErrorMsg('The file could not be read.');
    reader.readAsText(file);
  };

  const updateManualRow = (id, field, value) => setManualRows((prev) => prev.map((r) => (r.id === id ? { ...r, [field]: value } : r)));

  const activeRows = mode === 'upload' ? parsedRows : manualRows.filter((r) => r.fullName.trim() || r.email.trim());

  const seen = new Set();
  const validated = activeRows.map((row, i) => {
    const issues = [];
    const fullName = (row.fullName || '').trim();
    const email = (row.email || '').trim().toLowerCase();
    const role = (row.role || 'USER').toUpperCase();
    if (!fullName) issues.push('Full name required');
    if (!email) issues.push('Email required');
    else if (!EMAIL_REGEX.test(email)) issues.push('Invalid email');
    if (email && seen.has(email)) issues.push('Duplicate in this batch');
    else if (email) seen.add(email);
    if (email && existingUsers.some((u) => !u.deleted && u.email?.toLowerCase() === email)) issues.push('Email already registered');
    if (!allowedRoles.includes(role)) issues.push(role === 'SUPER_ADMIN' ? 'Super Admin cannot be created here' : `Role ${role} not allowed`);
    if ((row.password || '').length < MIN_PASSWORD) issues.push(`Password needs ${MIN_PASSWORD}+ characters`);
    return { ...row, role, rowNum: i + 1, isValid: issues.length === 0, issueText: issues.join(', ') };
  });
  const validRows = validated.filter((r) => r.isValid);
  const invalidRows = validated.filter((r) => !r.isValid);
  const needsCollege = isSuperAdmin && validRows.some((r) => COLLEGE_ROLES.includes(r.role));
  const collegeMissing = needsCollege && !collegeId;

  const downloadClientErrors = () => {
    const lines = ['Row,Full name,Email,Role,Error', ...invalidRows.map((r) => [r.rowNum, csvCell(r.fullName), csvCell(r.email), csvCell(r.role), csvCell(r.issueText)].join(','))];
    downloadCsv('bulk_users_validation_errors.csv', lines.join('\n'));
  };

  const downloadServerErrors = () => {
    const lines = ['Row,Email,Reason', ...(result?.errors || []).map((e) => [e.rowIndex, csvCell(e.email), csvCell(e.reason)].join(','))];
    downloadCsv('bulk_users_failed_records.csv', lines.join('\n'));
  };

  const handleCreate = async () => {
    if (!validRows.length || collegeMissing) return;
    setLoading(true);
    setErrorMsg('');
    try {
      const payload = validRows.map((r) => ({
        fullName: r.fullName.trim(),
        email: r.email.trim().toLowerCase(),
        password: r.password,
        phone: r.phone || '',
        role: r.role,
        department: r.department || '',
        organization: r.organization || r.department || '',
      }));
      const res = await api.bulkCreateUsers(payload, isSuperAdmin && collegeId ? Number(collegeId) : null);
      setResult(res || { totalRecords: payload.length, successCount: payload.length, failedCount: 0, duplicateCount: 0, errors: [] });
      if (res?.successCount) notify(`${res.successCount} account${res.successCount === 1 ? '' : 's'} created`);
      onSuccess?.();
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (loading) return;
    setParsedRows([]);
    setManualRows([blankRow(), blankRow(), blankRow()]);
    setFileName('');
    setResult(null);
    setErrorMsg('');
    setCollegeId('');
    onClose();
  };

  const collegeSelector = isSuperAdmin ? (
    <Field
      label="College"
      htmlFor="bulk-college"
      hint="Required for student and college admin rows. Developer rows ignore it."
      className="mb-4"
    >
      <select id="bulk-college" className="select" value={collegeId} onChange={(e) => setCollegeId(e.target.value)}>
        <option value="">Select a college</option>
        {colleges.map((c) => <option key={c.id} value={String(c.id)}>{c.name}{c.code ? ` (${c.code})` : ''}</option>)}
      </select>
    </Field>
  ) : (
    <Alert tone="info">
      Accounts are created as students of {currentUser?.college?.name || 'your college'}.
    </Alert>
  );

  return (
    <Modal
      open
      size="xl"
      onClose={handleClose}
      title="Bulk create accounts"
      description={isSuperAdmin ? 'Create students, college admins and developers from a CSV file or the table below.' : 'Create student accounts from a CSV file or the table below.'}
      footer={
        result ? (
          <button type="button" className="btn btn-primary" onClick={handleClose}>Done</button>
        ) : (
          <>
            <span className="text-sm text-muted" style={{ marginRight: 'auto', alignSelf: 'center' }}>
              {collegeMissing
                ? 'Select a college to continue.'
                : validRows.length
                  ? `${validRows.length} account${validRows.length === 1 ? '' : 's'} ready to create.`
                  : 'Add rows to validate them.'}
            </span>
            <button type="button" className="btn btn-secondary" onClick={handleClose} disabled={loading}>Cancel</button>
            <button type="button" className="btn btn-primary" onClick={handleCreate} disabled={!validRows.length || collegeMissing || loading}>
              {loading && <span className="spinner" />} Create {validRows.length || ''} account{validRows.length === 1 ? '' : 's'}
            </button>
          </>
        )
      }
    >
      {result ? (
        <div>
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle2 size={20} className="text-success" aria-hidden="true" />
            <div>
              <div className="font-semibold">Bulk creation finished</div>
              <div className="text-sm text-muted">New accounts are active and can sign in with the passwords you provided.</div>
            </div>
          </div>
          <div className="stat-grid mb-4">
            <StatCard label="Submitted" value={result.totalRecords ?? validRows.length} />
            <StatCard label="Created" value={result.successCount ?? 0} tone="success" index={1} />
            <StatCard label="Duplicates" value={result.duplicateCount ?? 0} tone="warning" index={2} />
            <StatCard label="Failed" value={result.failedCount ?? 0} tone="danger" index={3} />
          </div>
          {result.errors?.length > 0 && (
            <div className="card card-flush">
              <div className="card-header">
                <h3 className="card-title">Rows the server rejected</h3>
                <button type="button" className="btn btn-secondary btn-sm" onClick={downloadServerErrors}>
                  <Download aria-hidden="true" /> Download report
                </button>
              </div>
              <div className="table-wrap" style={{ maxHeight: 240 }}>
                <table className="table">
                  <thead><tr><th>Row</th><th>Email</th><th>Reason</th></tr></thead>
                  <tbody>
                    {result.errors.map((e, i) => (
                      <tr key={`${e.rowIndex}-${i}`}>
                        <td className="cell-muted">{e.rowIndex}</td>
                        <td>{e.email || '—'}</td>
                        <td className="text-danger">{e.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between gap-3 flex-wrap mb-4">
            <Segmented
              value={mode}
              onChange={setMode}
              options={[
                { value: 'upload', label: 'Upload CSV' },
                { value: 'manual', label: 'Enter in table' },
              ]}
            />
            <button type="button" className="btn btn-secondary btn-sm" onClick={handleDownloadTemplate}>
              <Download aria-hidden="true" /> Download template
            </button>
          </div>

          {collegeSelector}

          {errorMsg && <Alert tone="danger">{errorMsg}</Alert>}

          {mode === 'upload' ? (
            <div
              className={`dropzone mb-4 ${dragActive ? 'is-active' : ''}`}
              role="button"
              tabIndex={0}
              onClick={() => fileInputRef.current?.click()}
              onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && fileInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragActive(false);
                readFile(e.dataTransfer.files?.[0]);
              }}
            >
              <input type="file" ref={fileInputRef} accept=".csv,.txt" className="hidden" onChange={(e) => { readFile(e.target.files?.[0]); e.target.value = ''; }} />
              <Upload size={20} aria-hidden="true" className="mx-auto mb-2" />
              <div className="font-medium text-base" style={{ color: 'var(--text)' }}>
                {fileName ? fileName : 'Drop a CSV file here, or click to browse'}
              </div>
              <p className="text-sm mt-1">
                Columns: Full Name, Email, Password, Phone, Role, Department, Organization.
                Every row needs a password of at least {MIN_PASSWORD} characters — there is no default password.
                {isSuperAdmin ? ' Role can be USER, ADMIN or PROJECT_DEVELOPER.' : ' Role must be USER.'}
              </p>
            </div>
          ) : (
            <div className="mb-4">
              <p className="text-sm text-muted mb-2">
                Each account needs a password of at least {MIN_PASSWORD} characters. Share it with the person securely; they can change it from their profile.
              </p>
              <div className="table-wrap border rounded">
                <table className="table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Full name</th>
                      <th>Email</th>
                      {isSuperAdmin && <th>Role</th>}
                      <th>Password</th>
                      <th>Department</th>
                      <th>Phone</th>
                      <th aria-label="Remove" />
                    </tr>
                  </thead>
                  <tbody>
                    {manualRows.map((row, i) => (
                      <tr key={row.id}>
                        <td className="cell-muted">{i + 1}</td>
                        <td><input className="input input-sm" style={{ minWidth: 140 }} value={row.fullName} onChange={(e) => updateManualRow(row.id, 'fullName', e.target.value)} aria-label="Full name" /></td>
                        <td><input className="input input-sm" type="email" style={{ minWidth: 180 }} value={row.email} onChange={(e) => updateManualRow(row.id, 'email', e.target.value)} aria-label="Email" /></td>
                        {isSuperAdmin && (
                          <td>
                            <select className="select input-sm" style={{ minWidth: 130 }} value={row.role} onChange={(e) => updateManualRow(row.id, 'role', e.target.value)} aria-label="Role">
                              {allowedRoles.map((r) => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
                            </select>
                          </td>
                        )}
                        <td><input className="input input-sm" style={{ minWidth: 120 }} value={row.password} placeholder={`${MIN_PASSWORD}+ characters`} onChange={(e) => updateManualRow(row.id, 'password', e.target.value)} aria-label="Password" autoComplete="off" /></td>
                        <td><input className="input input-sm" style={{ minWidth: 120 }} value={row.department} onChange={(e) => updateManualRow(row.id, 'department', e.target.value)} aria-label="Department" /></td>
                        <td><input className="input input-sm" style={{ minWidth: 110 }} value={row.phone} onChange={(e) => updateManualRow(row.id, 'phone', e.target.value)} aria-label="Phone" /></td>
                        <td>
                          <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setManualRows((prev) => prev.filter((r) => r.id !== row.id))} aria-label="Remove row">
                            <Trash2 aria-hidden="true" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <button type="button" className="btn btn-secondary btn-sm mt-3" onClick={() => setManualRows((prev) => [...prev, blankRow()])}>
                <Plus aria-hidden="true" /> Add row
              </button>
            </div>
          )}

          {validated.length > 0 && (
            <div className="card card-flush">
              <div className="card-header">
                <div className="flex items-center gap-2">
                  <FileSpreadsheet size={16} aria-hidden="true" className="text-muted" />
                  <h3 className="card-title">Preview</h3>
                  <Badge tone="success">{validRows.length} valid</Badge>
                  {invalidRows.length > 0 && <Badge tone="danger">{invalidRows.length} with issues</Badge>}
                </div>
                {invalidRows.length > 0 && (
                  <button type="button" className="btn btn-ghost btn-sm" onClick={downloadClientErrors}>
                    <FileDown aria-hidden="true" /> Error report
                  </button>
                )}
              </div>
              <div className="table-wrap" style={{ maxHeight: 260 }}>
                <table className="table">
                  <thead>
                    <tr><th>#</th><th>Full name</th><th>Email</th><th>Role</th><th>Status</th></tr>
                  </thead>
                  <tbody>
                    {validated.map((row) => (
                      <tr key={row.id}>
                        <td className="cell-muted">{row.rowNum}</td>
                        <td className="font-medium">{row.fullName || '—'}</td>
                        <td className="cell-muted">{row.email || '—'}</td>
                        <td><Badge>{ROLE_LABELS[row.role] || row.role}</Badge></td>
                        <td>
                          {row.isValid ? (
                            <span className="flex items-center gap-1 text-success text-sm"><CheckCircle2 size={14} aria-hidden="true" /> Ready</span>
                          ) : (
                            <span className="flex items-center gap-1 text-danger text-sm"><XCircle size={14} aria-hidden="true" /> {row.issueText}</span>
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
    </Modal>
  );
};

export default BulkUserCreateModal;
