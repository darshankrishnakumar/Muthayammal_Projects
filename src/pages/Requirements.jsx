import { useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { FileText, Plus, Search } from 'lucide-react';
import { api } from '../utils/api';
import { useAsync } from '../hooks/useAsync';
import { useAuth } from '../context/AuthContext';
import { PageHeader, EmptyState, ErrorState, SkeletonRows, StatusBadge, Tabs } from '../components/ui';
import { money, relativeTime } from '../utils/format';

/** Work queues per role: each tab is a set of statuses. */
const QUEUES = {
  USER: [
    { value: 'all', label: 'All' },
    { value: 'action', label: 'Needs your action', statuses: ['DRAFT', 'CHANGES_REQUESTED', 'ADVANCE_PAYMENT_PENDING'] },
    { value: 'review', label: 'In review', statuses: ['SUBMITTED', 'SUPER_ADMIN_REVIEW'] },
    { value: 'dev', label: 'In development', statuses: ['ADVANCE_PAYMENT_COMPLETED', 'IN_PROGRESS'] },
    { value: 'closed', label: 'Closed', statuses: ['COMPLETED', 'REJECTED', 'INACTIVE'] },
  ],
  ADMIN: [
    { value: 'review', label: 'To review', statuses: ['SUBMITTED'] },
    { value: 'forwarded', label: 'Forwarded', statuses: ['SUPER_ADMIN_REVIEW', 'ADVANCE_PAYMENT_PENDING', 'ADVANCE_PAYMENT_COMPLETED'] },
    { value: 'dev', label: 'In development', statuses: ['IN_PROGRESS'] },
    { value: 'all', label: 'All' },
  ],
  SUPER_ADMIN: [
    { value: 'approve', label: 'Awaiting approval', statuses: ['SUPER_ADMIN_REVIEW'] },
    { value: 'assign', label: 'Ready to assign', statuses: ['ADVANCE_PAYMENT_COMPLETED'] },
    { value: 'payment', label: 'Awaiting advance', statuses: ['ADVANCE_PAYMENT_PENDING'] },
    { value: 'dev', label: 'In development', statuses: ['IN_PROGRESS'] },
    { value: 'all', label: 'All' },
  ],
  PROJECT_DEVELOPER: [{ value: 'all', label: 'Assigned to me' }],
};

export default function Requirements() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const queues = QUEUES[user?.role] || QUEUES.USER;
  const initial = (() => {
    const s = params.get('status');
    if (!s) return queues[0].value;
    return queues.find((q) => q.statuses?.includes(s))?.value || 'all';
  })();
  const [tab, setTab] = useState(initial);
  const [search, setSearch] = useState('');
  const { data, loading, error, reload } = useAsync(() => api.getRequirements(), []);

  const all = useMemo(() => data || [], [data]);
  const counts = useMemo(() => Object.fromEntries(queues.map((q) => [q.value, q.statuses ? all.filter((r) => q.statuses.includes(r.status)).length : all.length])), [all, queues]);
  const current = queues.find((q) => q.value === tab) || queues[0];
  const rows = all
    .filter((r) => !current.statuses || current.statuses.includes(r.status))
    .filter((r) => !search.trim() || r.title.toLowerCase().includes(search.trim().toLowerCase()) || (r.user?.fullName || '').toLowerCase().includes(search.trim().toLowerCase()));

  const isStudent = user?.role === 'USER';

  return (
    <>
      <PageHeader
        title={isStudent ? 'My requirements' : 'Requirements'}
        description={
          isStudent ? "Request a custom project when the library doesn't have what you need. Your college reviews it first."
            : user?.role === 'ADMIN' ? 'Custom project requests from your students. Forward feasible ones for development approval.'
              : user?.role === 'SUPER_ADMIN' ? 'Custom development requests from every college: quote, collect the advance and assign developers.'
                : 'Requirements behind the projects assigned to you.'
        }
        actions={isStudent && <Link to="/requirements/new" className="btn btn-primary"><Plus /> New requirement</Link>}
      />

      <Tabs value={tab} onChange={setTab} tabs={queues.map((q) => ({ value: q.value, label: q.label, count: loading ? undefined : counts[q.value] }))} />

      <div className="toolbar">
        <div className="input-with-icon grow" style={{ maxWidth: 420 }}>
          <Search aria-hidden="true" />
          <input className="input" placeholder={isStudent ? 'Search requirements' : 'Search by title or student'} value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {error ? <ErrorState error={error} onRetry={reload} /> : (
        <div className="card card-flush">
          {loading && !data ? <div className="p-4"><SkeletonRows rows={6} /></div> : rows.length === 0 ? (
            <EmptyState
              icon={FileText}
              title={all.length === 0 ? (isStudent ? 'No requirements yet' : 'Nothing here yet') : 'Nothing in this queue'}
              text={all.length === 0 && isStudent ? 'Describe the project you need. Your college reviews it, then the platform quotes and assigns a developer.' : 'Requests appear here as they move through review.'}
              action={all.length === 0 && isStudent && <Link to="/requirements/new" className="btn btn-primary"><Plus /> New requirement</Link>}
            />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Requirement</th>
                    {!isStudent && <th>Student</th>}
                    {user?.role === 'SUPER_ADMIN' && <th>College</th>}
                    <th className="cell-num">{isStudent ? 'Budget / quote' : 'Budget'}</th>
                    <th>Status</th>
                    <th>Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r) => (
                    <tr key={r.id} className="is-clickable" onClick={() => navigate(`/requirements/${r.id}`)}>
                      <td style={{ maxWidth: 380 }}>
                        <div className="font-medium truncate">{r.title}</div>
                        <div className="text-xs text-subtle truncate">{r.technologyStack || r.problemStatement}</div>
                      </td>
                      {!isStudent && <td className="cell-muted">{r.user?.fullName}</td>}
                      {user?.role === 'SUPER_ADMIN' && <td className="cell-muted">{r.collegeName || '—'}</td>}
                      <td className="cell-num">{r.budget != null ? money(r.budget) : '—'}</td>
                      <td><StatusBadge status={r.status} /></td>
                      <td className="cell-muted text-sm">{relativeTime(r.updatedAt || r.createdAt)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </>
  );
}
