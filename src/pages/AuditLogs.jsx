import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { 
  FileText, 
  RefreshCw, 
  Info,
  Calendar as CalendarIcon,
  User,
  Activity,
  X,
  Search,
  Filter,
  Download,
  ChevronLeft,
  ChevronRight,
  Shield,
  Clock,
  ExternalLink,
  Layers,
  Key,
  FolderKanban,
  Users,
  ShoppingCart
} from 'lucide-react';

const CATEGORY_FILTERS = [
  { id: 'ALL', label: 'All Operations', icon: Activity },
  { id: 'AUTH', label: 'Auth & Security', icon: Key, actions: ['LOGIN', 'LOGOUT', 'SYSTEM_INIT', 'UPDATE_PASSWORD', 'PASSWORD_RESET', 'ROLE_UPDATE', 'PRESET_APPLIED'] },
  { id: 'PROJECTS', label: 'Projects & Files', icon: FolderKanban, actions: ['PROJECT_CREATE', 'UPDATE_PROJECT', 'FOLDER_CREATE', 'FOLDER_DELETE', 'FILE_UPLOAD', 'FILE_VERSION_ROLLBACK', 'FILE_DELETE'] },
  { id: 'REQUIREMENTS', label: 'Requirements', icon: FileText, actions: ['CREATE_REQUIREMENT', 'SUBMIT_REQUIREMENT', 'APPROVE_REQUIREMENT', 'REJECT_REQUIREMENT', 'UPDATE_REQUIREMENT'] },
  { id: 'USERS', label: 'User Management', icon: Users, actions: ['CREATE_USER', 'UPDATE_USER', 'DELETE_USER', 'CREATE_ADMIN', 'UPDATE_ADMIN'] },
  { id: 'COMMERCE', label: 'Marketplace & Orders', icon: ShoppingCart, actions: ['PURCHASE_CHECKOUT', 'INVOICE_GENERATED', 'PAYMENT_VERIFIED', 'ORDER_COMPLETED'] }
];

const ITEMS_PER_PAGE = 15;

const AuditLogs = () => {
  const { user: currentUser } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Date filter state (YYYY-MM-DD)
  const todayDateStr = new Date().toISOString().split('T')[0];
  const [selectedDate, setSelectedDate] = useState('');
  const [activeDateChip, setActiveDateChip] = useState('ALL'); // 'ALL', 'TODAY', '7D', '30D', 'CUSTOM'

  // Additional Filter Controls
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [currentPage, setCurrentPage] = useState(1);

  // Modal inspection state
  const [selectedLog, setSelectedLog] = useState(null);

  const loadLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getAuditLogs(selectedDate);
      setLogs(data || []);
      setCurrentPage(1);
    } catch (err) {
      setError(err.message || 'Failed to retrieve secure audit records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [selectedDate]);

  // Handle Quick Date Chips
  const handleDateChipClick = (chip) => {
    setActiveDateChip(chip);
    if (chip === 'ALL') {
      setSelectedDate('');
    } else if (chip === 'TODAY') {
      setSelectedDate(todayDateStr);
    } else if (chip === '7D') {
      setSelectedDate(''); // Multi-day filtering handled in client memo
    } else if (chip === '30D') {
      setSelectedDate(''); // Multi-day filtering handled in client memo
    } else if (chip === 'CUSTOM') {
      // Focus/open calendar input
    }
  };

  // Format database timestamp without UTC timezone shift
  const formatAuditTimestamp = (ts) => {
    if (!ts) return 'N/A';
    const cleanStr = String(ts).replace('T', ' ').split('.')[0];
    const parts = cleanStr.split(' ');
    if (parts.length < 1) return ts;
    
    const dateParts = parts[0].split('-');
    if (dateParts.length !== 3) return ts;
    
    const year = dateParts[0];
    const month = dateParts[1];
    const day = dateParts[2];
    const time = parts[1] || '';
    
    return `${day}/${month}/${year}${time ? ' ' + time : ''}`;
  };

  // Format YYYY-MM-DD input date to DD/MM/YYYY for UI display
  const formatSelectedDateDisplay = (dateStr) => {
    if (!dateStr) return 'All Historical Dates';
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }
    return dateStr;
  };

  const getActionBadgeClass = (action) => {
    switch (action) {
      case 'LOGIN':
      case 'APPROVE_REQUIREMENT':
      case 'PAYMENT_VERIFIED':
      case 'ORDER_COMPLETED':
        return 'badge-success';
      case 'LOGOUT':
      case 'CREATE_USER':
      case 'CREATE_ADMIN':
      case 'CREATE_REQUIREMENT':
      case 'PROJECT_CREATE':
      case 'FOLDER_CREATE':
      case 'FILE_UPLOAD':
      case 'PURCHASE_CHECKOUT':
        return 'badge-primary';
      case 'UPDATE_USER':
      case 'UPDATE_ADMIN':
      case 'UPDATE_REQUIREMENT':
      case 'UPDATE_PROJECT':
      case 'FILE_VERSION_ROLLBACK':
        return 'badge-warning';
      case 'REJECT_REQUIREMENT':
      case 'DELETE_USER':
      case 'FOLDER_DELETE':
      case 'FILE_DELETE':
        return 'badge-danger';
      case 'SYSTEM_INIT':
      case 'PRESET_APPLIED':
        return 'badge-secondary';
      default:
        return 'badge-primary';
    }
  };

  // Filtered Logs
  const filteredLogs = useMemo(() => {
    let result = [...logs];
    const now = Date.now();

    // 1. Quick Date Chip Range Filter
    if (activeDateChip === '7D') {
      const sevenDaysAgo = now - 7 * 86400000;
      result = result.filter(l => new Date(l.timestamp).getTime() >= sevenDaysAgo);
    } else if (activeDateChip === '30D') {
      const thirtyDaysAgo = now - 30 * 86400000;
      result = result.filter(l => new Date(l.timestamp).getTime() >= thirtyDaysAgo);
    }

    // 2. Category Filter
    if (selectedCategory !== 'ALL') {
      const categoryObj = CATEGORY_FILTERS.find(c => c.id === selectedCategory);
      if (categoryObj && categoryObj.actions) {
        result = result.filter(l => categoryObj.actions.includes(l.action));
      }
    }

    // 3. Search Query Filter (Actor Email, Details, Action)
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter(l => 
        (l.actorEmail && l.actorEmail.toLowerCase().includes(q)) ||
        (l.action && l.action.toLowerCase().includes(q)) ||
        (l.details && l.details.toLowerCase().includes(q))
      );
    }

    return result;
  }, [logs, activeDateChip, selectedCategory, searchQuery]);

  // Pagination Math
  const totalPages = Math.ceil(filteredLogs.length / ITEMS_PER_PAGE) || 1;
  const paginatedLogs = useMemo(() => {
    const startIdx = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredLogs.slice(startIdx, startIdx + ITEMS_PER_PAGE);
  }, [filteredLogs, currentPage]);

  // Export CSV
  const handleExportCSV = () => {
    if (!filteredLogs.length) return;
    const headers = ['ID', 'Timestamp', 'Actor Email', 'Operation', 'Details'];
    const rows = filteredLogs.map(l => [
      l.id,
      `"${formatAuditTimestamp(l.timestamp)}"`,
      `"${l.actorEmail || ''}"`,
      `"${l.action || ''}"`,
      `"${(l.details || '').replace(/"/g, '""')}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `audit_logs_export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="audit-logs-wrapper text-left">
      {error && (
        <div className="alert alert-danger" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Info size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Header & Actions */}
      <div className="card" style={{ padding: '20px 24px' }}>
        <div className="flex justify-between items-center flex-wrap gap-4" style={{ marginBottom: '16px' }}>
          <div className="flex items-center gap-3">
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, var(--primary), #4338ca)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.25)'
            }}>
              <Shield size={22} />
            </div>
            <div>
              <h3 style={{ fontWeight: 700, fontSize: '1.25rem', margin: 0, color: 'var(--text-main)' }}>
                System Security & Audit Trail
              </h3>
              <p className="text-muted" style={{ fontSize: '0.82rem', margin: '2px 0 0 0' }}>
                {currentUser.role === 'SUPER_ADMIN' ? 'Global Immutable System Audit Events' : 'Restricted Project & Team Activity Logs'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button 
              onClick={handleExportCSV} 
              className="btn btn-secondary btn-sm"
              disabled={filteredLogs.length === 0}
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
              title="Download CSV report of currently filtered audit logs"
            >
              <Download size={14} />
              <span>Export CSV</span>
            </button>

            <button 
              onClick={loadLogs} 
              className="btn btn-primary btn-sm" 
              disabled={loading} 
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <RefreshCw size={14} className={loading ? 'spin' : ''} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Quick Date Chips & Search Filter Bar */}
        <div className="flex justify-between items-center flex-wrap gap-3" style={{ paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
          {/* Quick Date Window Chips */}
          <div className="flex items-center gap-2 flex-wrap">
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Date Range:</span>
            {[
              { id: 'ALL', label: 'All Time' },
              { id: 'TODAY', label: 'Today (24h)' },
              { id: '7D', label: 'Last 7 Days' },
              { id: '30D', label: 'Last 30 Days' }
            ].map(chip => (
              <button
                key={chip.id}
                type="button"
                onClick={() => handleDateChipClick(chip.id)}
                className={`btn btn-sm ${activeDateChip === chip.id && !selectedDate ? 'btn-primary' : 'btn-secondary'}`}
                style={{ fontSize: '0.78rem', padding: '4px 10px', borderRadius: 'var(--radius-full)' }}
              >
                {chip.label}
              </button>
            ))}

            {/* Custom Date Input */}
            <div className="flex items-center gap-1" style={{ marginLeft: '4px' }}>
              <input 
                type="date" 
                className="input-field"
                style={{ padding: '3px 8px', fontSize: '0.8rem', cursor: 'pointer', height: '28px' }}
                max={todayDateStr}
                value={selectedDate}
                onChange={(e) => {
                  setSelectedDate(e.target.value);
                  setActiveDateChip('CUSTOM');
                }}
                title="Filter by exact single date"
              />
              {selectedDate && (
                <button 
                  type="button"
                  onClick={() => {
                    setSelectedDate('');
                    setActiveDateChip('ALL');
                  }}
                  className="btn btn-secondary btn-sm"
                  style={{ padding: '2px 6px', height: '28px', fontSize: '0.72rem' }}
                  title="Clear custom date filter"
                >
                  <X size={12} />
                </button>
              )}
            </div>
          </div>

          {/* Search Box & Category Selector */}
          <div className="flex items-center gap-2 flex-wrap">
            {/* Category Dropdown */}
            <div className="flex items-center gap-1">
              <select
                className="input-field"
                style={{ padding: '4px 8px', fontSize: '0.82rem', height: '32px', cursor: 'pointer' }}
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setCurrentPage(1);
                }}
              >
                {CATEGORY_FILTERS.map(c => (
                  <option key={c.id} value={c.id}>{c.label}</option>
                ))}
              </select>
            </div>

            {/* Live Search Input */}
            <div style={{ position: 'relative', width: '220px' }}>
              <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                placeholder="Search actor or details..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
                }}
                className="input-field"
                style={{ paddingLeft: '30px', fontSize: '0.82rem', height: '32px', width: '100%' }}
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
                >
                  <X size={12} />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Selected Filter Status Ribbon */}
      <div className="flex justify-between items-center card" style={{ padding: '10px 18px', backgroundColor: 'var(--bg-main)', fontSize: '0.82rem' }}>
        <div className="text-muted flex items-center gap-2">
          <span>Viewing:</span>
          <strong style={{ color: 'var(--text-main)' }}>
            {selectedDate ? formatSelectedDateDisplay(selectedDate) : activeDateChip === '7D' ? 'Last 7 Days' : activeDateChip === '30D' ? 'Last 30 Days' : 'All Historical Logs'}
          </strong>
          {selectedCategory !== 'ALL' && (
            <span className="badge badge-info" style={{ marginLeft: '4px' }}>
              Category: {CATEGORY_FILTERS.find(c => c.id === selectedCategory)?.label}
            </span>
          )}
          {searchQuery && (
            <span className="badge badge-secondary" style={{ marginLeft: '4px' }}>
              Query: "{searchQuery}"
            </span>
          )}
          <span className="badge badge-primary" style={{ marginLeft: '6px' }}>
            {filteredLogs.length} matching events
          </span>
        </div>

        <div className="text-muted" style={{ fontSize: '0.76rem' }}>
          Page {currentPage} of {totalPages}
        </div>
      </div>

      {/* Logs Table */}
      <div className="table-container card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div className="table-loading" style={{ padding: '60px', textAlign: 'center' }}>
            <div style={{ border: '4px solid var(--border-color)', borderTop: '4px solid var(--primary)', borderRadius: '50%', width: '36px', height: '36px', animation: 'spin 1s linear infinite', margin: '0 auto 12px' }}></div>
            <p className="text-muted" style={{ fontSize: '0.88rem' }}>Fetching secure audit logs from database...</p>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="table-empty" style={{ padding: '60px', textAlign: 'center' }}>
            <FileText size={48} className="text-muted" style={{ margin: '0 auto 12px', opacity: 0.3 }} />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', margin: '12px 0 4px' }}>No Matching Audit Logs Found</h3>
            <p className="text-muted" style={{ fontSize: '0.85rem', maxWidth: '400px', margin: '0 auto' }}>
              {searchQuery || selectedCategory !== 'ALL' || selectedDate 
                ? 'No audit log entries match your active search criteria or date filter. Try clearing filters.'
                : 'Security actions will be logged here automatically in real-time.'}
            </p>
            {(searchQuery || selectedCategory !== 'ALL' || selectedDate || activeDateChip !== 'ALL') && (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('ALL');
                  setSelectedDate('');
                  setActiveDateChip('ALL');
                }}
                className="btn btn-secondary btn-sm"
                style={{ marginTop: '16px' }}
              >
                Reset All Filters
              </button>
            )}
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: 'var(--bg-main)', borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                  <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.5px' }}>TIMESTAMP (UTC)</th>
                  <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.5px' }}>ACTOR</th>
                  <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.5px' }}>OPERATION</th>
                  <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, letterSpacing: '0.5px' }}>TARGET RESOURCE & DETAILS</th>
                  <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, textAlign: 'right' }}>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {paginatedLogs.map((log) => (
                  <tr 
                    key={log.id} 
                    style={{ borderBottom: '1px solid var(--border-color)', transition: 'background-color 0.15s ease' }}
                    className="hover:bg-[var(--bg-main)]"
                  >
                    <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                      <div className="flex items-center gap-2 text-muted" style={{ fontSize: '0.84rem' }}>
                        <Clock size={13} className="text-primary" />
                        <span>{formatAuditTimestamp(log.timestamp)}</span>
                      </div>
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <div className="flex items-center gap-2" style={{ fontWeight: 500, fontSize: '0.84rem' }}>
                        <User size={13} className="text-muted" />
                        <span>{log.actorEmail}</span>
                      </div>
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <span className={`badge ${getActionBadgeClass(log.action)}`}>
                        {log.action.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td style={{ padding: '14px 16px', maxWidth: '420px' }}>
                      <span className="log-details-text" style={{ fontSize: '0.86rem', color: 'var(--text-main)', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {log.details}
                      </span>
                    </td>
                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <button
                        type="button"
                        onClick={() => setSelectedLog(log)}
                        className="btn btn-secondary btn-sm"
                        style={{ padding: '3px 8px', fontSize: '0.74rem' }}
                        title="View complete event payload"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Toolbar */}
        {filteredLogs.length > 0 && (
          <div className="flex justify-between items-center" style={{ padding: '14px 20px', borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)' }}>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Showing <strong>{(currentPage - 1) * ITEMS_PER_PAGE + 1}</strong> to <strong>{Math.min(currentPage * ITEMS_PER_PAGE, filteredLogs.length)}</strong> of <strong>{filteredLogs.length}</strong> logs
            </div>

            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="btn btn-secondary btn-sm"
                style={{ padding: '4px 8px' }}
                title="Previous page"
              >
                <ChevronLeft size={14} />
              </button>

              {/* Page Number Chips */}
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(page => page === 1 || page === totalPages || Math.abs(page - currentPage) <= 1)
                .map((page, idx, arr) => {
                  const showEllipsis = idx > 0 && page - arr[idx - 1] > 1;
                  return (
                    <span key={page} style={{ display: 'inline-flex', alignItems: 'center' }}>
                      {showEllipsis && <span style={{ padding: '0 4px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>...</span>}
                      <button
                        type="button"
                        onClick={() => setCurrentPage(page)}
                        className={`btn btn-sm ${currentPage === page ? 'btn-primary' : 'btn-secondary'}`}
                        style={{ minWidth: '28px', height: '28px', padding: '0 6px', fontSize: '0.78rem' }}
                      >
                        {page}
                      </button>
                    </span>
                  );
                })}

              <button
                type="button"
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="btn btn-secondary btn-sm"
                style={{ padding: '4px 8px' }}
                title="Next page"
              >
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal: Detailed Event Inspector */}
      {selectedLog && (
        <div className="modal-backdrop" style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1100,
          padding: '20px'
        }}>
          <div className="card" style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-lg)',
            width: '100%',
            maxWidth: '540px',
            padding: '24px',
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
              <div className="flex items-center gap-2">
                <Shield size={18} className="text-primary" />
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                  Audit Event #{selectedLog.id}
                </h3>
              </div>
              <button 
                onClick={() => setSelectedLog(null)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="flex flex-col gap-3" style={{ fontSize: '0.88rem' }}>
              <div>
                <span className="text-muted" style={{ fontSize: '0.78rem', display: 'block' }}>Timestamp</span>
                <strong style={{ color: 'var(--text-main)' }}>{formatAuditTimestamp(selectedLog.timestamp)}</strong>
              </div>

              <div>
                <span className="text-muted" style={{ fontSize: '0.78rem', display: 'block' }}>Actor Identity</span>
                <strong style={{ color: 'var(--text-main)' }}>{selectedLog.actorEmail}</strong>
              </div>

              <div>
                <span className="text-muted" style={{ fontSize: '0.78rem', display: 'block' }}>Operation Type</span>
                <span className={`badge ${getActionBadgeClass(selectedLog.action)}`} style={{ marginTop: '4px' }}>
                  {selectedLog.action}
                </span>
              </div>

              <div>
                <span className="text-muted" style={{ fontSize: '0.78rem', display: 'block' }}>Full Event Description & Target</span>
                <div style={{
                  background: 'var(--bg-main)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  padding: '12px',
                  marginTop: '4px',
                  fontFamily: 'var(--font-mono, monospace)',
                  fontSize: '0.82rem',
                  color: 'var(--text-main)',
                  lineHeight: '1.5',
                  wordBreak: 'break-word'
                }}>
                  {selectedLog.details}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px', paddingTop: '12px', borderTop: '1px solid var(--border-color)' }}>
              <button 
                type="button" 
                onClick={() => setSelectedLog(null)} 
                className="btn btn-secondary btn-sm"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .audit-logs-wrapper {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .spin {
          animation: rotate 1s linear infinite;
        }

        @keyframes rotate {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default AuditLogs;
