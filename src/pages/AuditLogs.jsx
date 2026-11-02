import { useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, Download, FileText, RefreshCw, Search, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { useAsync, useDebounced } from '../hooks/useAsync';
import { PageHeader, Card, Badge, EmptyState, ErrorState, SkeletonRows, Drawer, Segmented } from '../components/ui';
import { dateTime, relativeTime, titleCase } from '../utils/format';

const CATEGORY_FILTERS = [
  { id: 'ALL', label: 'All operations' },
  { id: 'AUTH', label: 'Auth and security', actions: ['LOGIN', 'LOGOUT', 'SYSTEM_INIT', 'UPDATE_PASSWORD', 'PASSWORD_RESET', 'ROLE_UPDATE', 'USER_ROLE_CHANGED', 'PRESET_APPLIED'] },
  { id: 'PROJECTS', label: 'Projects and files', actions: ['PROJECT_CREATE', 'UPDATE_PROJECT', 'FOLDER_CREATE', 'UPDATE_FOLDER', 'FOLDER_DELETE', 'FILE_UPLOAD', 'FILE_VERSION_ROLLBACK', 'FILE_DELETE', 'FILE_DOWNLOADED'] },
  { id: 'REQUIREMENTS', label: 'Requirements', actions: ['CREATE_REQUIREMENT', 'SUBMIT_REQUIREMENT', 'APPROVE_REQUIREMENT', 'REJECT_REQUIREMENT', 'UPDATE_REQUIREMENT'] },
  { id: 'USERS', label: 'User management', actions: ['CREATE_USER', 'UPDATE_USER', 'DELETE_USER', 'CREATE_ADMIN', 'UPDATE_ADMIN', 'BULK_USER_CREATE', 'USER_ROLE_CHANGED'] },
  { id: 'COMMERCE', label: 'Marketplace and orders', actions: ['PURCHASE_CHECKOUT', 'INVOICE_GENERATED', 'PAYMENT_VERIFIED', 'ORDER_COMPLETED'] },
];

const DATE_RANGES = [
  { value: 'ALL', label: 'All time' },
  { value: 'TODAY', label: 'Today' },
  { value: '7D', label: '7 days' },
  { value: '30D', label: '30 days' },
];

const ITEMS_PER_PAGE = 15;

/** Local calendar date as YYYY-MM-DD (toISOString would shift to UTC). */
const localDateString = (d = new Date()) => {
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
};

const actionTone = (action = '') => {
  if (/DELETE|REJECT|FAILED|REVOKE/.test(action)) return 'danger';
  if (/UPDATE|ROLLBACK|ROLE|RESET|CHANGED/.test(action)) return 'warning';
  if (/LOGIN|APPROVE|VERIFIED|COMPLETED|SUCCEEDED/.test(action)) return 'success';
  if (/SYSTEM|PRESET|LOGOUT/.test(action)) return 'neutral';
  return 'accent';
};

const csvCell = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;

const AuditLogs = () => {
  const { user } = useAuth();
  const todayStr = localDateString();

  const [range, setRange] = useState('ALL');
  const [selectedDate, setSelectedDate] = useState('');
  const [category, setCategory] = useState('ALL');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [selectedLog, setSelectedLog] = useState(null);

  const debouncedSearch = useDebounced(search, 200);

  // The server filters by a single calendar day; multi-day ranges are filtered client-side.
  const serverDate = selectedDate || (range === 'TODAY' ? todayStr : '');
  const { data, loading, error, reload } = useAsync(() => api.getAuditLogs(serverDate), [serverDate]);
  const logs = useMemo(() => data || [], [data]);

  const filteredLogs = useMemo(() => {
    let result = logs;
    if (!selectedDate && (range === '7D' || range === '30D')) {
      const cutoff = Date.now() - (range === '7D' ? 7 : 30) * 86400000;
      result = result.filter((l) => new Date(l.timestamp).getTime() >= cutoff);
    }
    if (category !== 'ALL') {
      const actions = CATEGORY_FILTERS.find((c) => c.id === category)?.actions || [];
      result = result.filter((l) => actions.includes(l.action));
    }
    const q = debouncedSearch.trim().toLowerCase();
    if (q) {
      result = result.filter((l) =>
        [l.actorEmail, l.action, l.details].some((v) => v && String(v).toLowerCase().includes(q)),
      );
    }
    return result;
  }, [logs, range, selectedDate, category, debouncedSearch]);

  const totalPages = Math.max(1, Math.ceil(filteredLogs.length / ITEMS_PER_PAGE));
  const currentPage = Math.min(page, totalPages);
  const pageLogs = filteredLogs.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE);

  const filtersActive = Boolean(search || category !== 'ALL' || selectedDate || range !== 'ALL');

  const resetFilters = () => {
    setSearch('');
    setCategory('ALL');
    setSelectedDate('');
    setRange('ALL');
    setPage(1);
  };

  const handleExportCSV = () => {
    if (!filteredLogs.length) return;
    const header = ['ID', 'Timestamp', 'Actor email', 'Operation', 'Details'].join(',');
    const rows = filteredLogs.map((l) => [l.id, csvCell(l.timestamp), csvCell(l.actorEmail), csvCell(l.action), csvCell(l.details)].join(','));
    const blob = new Blob([[header, ...rows].join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `audit_logs_${todayStr}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  };

  const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1)
    .filter((p) => p === 1 || p === totalPages || Math.abs(p - currentPage) <= 1);

  return (
    <>
      <PageHeader
        title="Audit log"
        description={user?.role === 'SUPER_ADMIN' ? 'Every recorded action across the platform.' : 'Recorded activity you are permitted to review.'}
        actions={
          <>
            <button type="button" className="btn btn-secondary" onClick={handleExportCSV} disabled={!filteredLogs.length}>
              <Download aria-hidden="true" /> Export CSV
            </button>
            <button type="button" className="btn btn-secondary" onClick={reload} disabled={loading}>
              <RefreshCw aria-hidden="true" /> Refresh
            </button>
          </>
        }
      />

      <div className="toolbar">
        <Segmented
          options={DATE_RANGES}
          value={selectedDate ? '' : range}
          onChange={(v) => { setRange(v); setSelectedDate(''); setPage(1); }}
        />
        <div className="flex items-center gap-1">
          <input
            type="date"
            className="input"
            style={{ width: 160 }}
            max={todayStr}
            value={selectedDate}
            onChange={(e) => { setSelectedDate(e.target.value); setPage(1); }}
            aria-label="Filter by a specific date"
          />
          {selectedDate && (
            <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setSelectedDate('')} aria-label="Clear date">
              <X aria-hidden="true" />
            </button>
          )}
        </div>
        <select
          className="select"
          style={{ width: 200 }}
          value={category}
          onChange={(e) => { setCategory(e.target.value); setPage(1); }}
          aria-label="Category"
        >
          {CATEGORY_FILTERS.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
        </select>
        <div className="input-with-icon grow">
          <Search aria-hidden="true" />
          <input
            className="input"
            placeholder="Search actor, operation or details"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
      </div>

      {error ? (
        <ErrorState error={error} onRetry={reload} />
      ) : (
        <Card flush>
          {loading && !data ? (
            <div className="p-4"><SkeletonRows rows={8} /></div>
          ) : filteredLogs.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No matching events"
              text={filtersActive ? 'No audit entries match the current filters.' : 'Actions will be recorded here as they happen.'}
              action={filtersActive && <button type="button" className="btn btn-secondary" onClick={resetFilters}>Reset filters</button>}
            />
          ) : (
            <>
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Actor</th>
                      <th>Operation</th>
                      <th>Details</th>
                      <th aria-label="Actions" />
                    </tr>
                  </thead>
                  <tbody>
                    {pageLogs.map((log) => (
                      <tr key={log.id} className="is-clickable" onClick={() => setSelectedLog(log)}>
                        <td className="nowrap">
                          <div>{dateTime(log.timestamp)}</div>
                          <div className="text-xs text-subtle">{relativeTime(log.timestamp)}</div>
                        </td>
                        <td className="cell-muted">{log.actorEmail}</td>
                        <td><Badge tone={actionTone(log.action)}>{titleCase(log.action)}</Badge></td>
                        <td style={{ maxWidth: 440 }}>
                          <span className="text-sm" style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                            {log.details}
                          </span>
                        </td>
                        <td className="text-right">
                          <button
                            type="button"
                            className="btn btn-ghost btn-sm"
                            onClick={(e) => { e.stopPropagation(); setSelectedLog(log); }}
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="card-footer" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="text-sm text-muted">
                  {(currentPage - 1) * ITEMS_PER_PAGE + 1}–{Math.min(currentPage * ITEMS_PER_PAGE, filteredLogs.length)} of {filteredLogs.length}
                </span>
                <div className="flex items-center gap-1">
                  <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setPage(currentPage - 1)} disabled={currentPage === 1} aria-label="Previous page">
                    <ChevronLeft aria-hidden="true" />
                  </button>
                  {pageNumbers.map((p, idx) => (
                    <span key={p} className="flex items-center">
                      {idx > 0 && p - pageNumbers[idx - 1] > 1 && <span className="text-subtle text-sm" style={{ padding: '0 4px' }}>…</span>}
                      <button
                        type="button"
                        className={`btn btn-sm ${p === currentPage ? 'btn-secondary' : 'btn-ghost'}`}
                        style={{ minWidth: 28, padding: '0 6px' }}
                        onClick={() => setPage(p)}
                        aria-current={p === currentPage ? 'page' : undefined}
                      >
                        {p}
                      </button>
                    </span>
                  ))}
                  <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setPage(currentPage + 1)} disabled={currentPage === totalPages} aria-label="Next page">
                    <ChevronRight aria-hidden="true" />
                  </button>
                </div>
              </div>
            </>
          )}
        </Card>
      )}

      <Drawer
        open={Boolean(selectedLog)}
        onClose={() => setSelectedLog(null)}
        title={selectedLog ? `Event #${selectedLog.id}` : ''}
        description={selectedLog ? dateTime(selectedLog.timestamp) : ''}
      >
        {selectedLog && (
          <dl className="kv">
            <dt>Time</dt>
            <dd>{selectedLog.timestamp ? new Date(selectedLog.timestamp).toLocaleString('en-IN') : '—'}</dd>
            <dt>Actor</dt>
            <dd>{selectedLog.actorEmail}</dd>
            <dt>Operation</dt>
            <dd><Badge tone={actionTone(selectedLog.action)}>{selectedLog.action}</Badge></dd>
            <dt>Details</dt>
            <dd>
              <div className="surface-muted font-mono text-sm" style={{ padding: 12, whiteSpace: 'pre-wrap' }}>
                {selectedLog.details || '—'}
              </div>
            </dd>
          </dl>
        )}
      </Drawer>
    </>
  );
};

export default AuditLogs;
