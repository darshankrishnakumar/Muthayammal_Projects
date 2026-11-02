import { useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { FolderKanban, Search, BookMarked, Store } from 'lucide-react';
import { api } from '../utils/api';
import { useAsync } from '../hooks/useAsync';
import { useAuth } from '../context/AuthContext';
import { PageHeader, EmptyState, ErrorState, SkeletonRows, StatusBadge, Tabs, Progress, Badge, SpotlightCard } from '../components/ui';
import { relativeTime } from '../utils/format';

const DELIVERED = ['ACCESS_GRANTED', 'COMPLETED'];

export default function Projects() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const statusParam = params.get('status') || '';
  const [search, setSearch] = useState(params.get('search') || '');
  const role = user?.role;
  const [tab, setTab] = useState(statusParam ? 'filtered' : role === 'SUPER_ADMIN' ? 'CUSTOM' : 'all');
  const { data, loading, error, reload } = useAsync(() => api.getProjects(), []);

  const all = useMemo(() => data || [], [data]);
  const lifecycle = (p) => p.lifecycleStatus || p.status;

  const tabs = useMemo(() => {
    const base = [];
    if (statusParam) base.push({ value: 'filtered', label: 'Filtered', count: all.filter((p) => lifecycle(p) === statusParam).length });
    if (role === 'SUPER_ADMIN') {
      base.push({ value: 'CUSTOM', label: 'Development', count: all.filter((p) => p.projectType === 'CUSTOM').length });
      base.push({ value: 'active', label: 'Active', count: all.filter((p) => p.projectType === 'CUSTOM' && !DELIVERED.includes(lifecycle(p))).length });
      base.push({ value: 'LIBRARY', label: 'Library', count: all.filter((p) => p.projectType === 'LIBRARY').length });
    } else if (role === 'USER') {
      base.push({ value: 'all', label: 'All', count: all.length });
      base.push({ value: 'LIBRARY', label: 'Purchased', count: all.filter((p) => p.projectType === 'LIBRARY').length });
      base.push({ value: 'CUSTOM', label: 'Custom development', count: all.filter((p) => p.projectType === 'CUSTOM').length });
    } else {
      base.push({ value: 'all', label: 'All', count: all.length });
      base.push({ value: 'active', label: 'Active', count: all.filter((p) => !DELIVERED.includes(lifecycle(p))).length });
      base.push({ value: 'done', label: 'Delivered', count: all.filter((p) => DELIVERED.includes(lifecycle(p))).length });
    }
    return base;
  }, [all, role, statusParam]);

  const rows = all.filter((p) => {
    if (tab === 'filtered') return lifecycle(p) === statusParam;
    if (tab === 'CUSTOM' || tab === 'LIBRARY') return p.projectType === tab;
    if (tab === 'active') return (role !== 'SUPER_ADMIN' || p.projectType === 'CUSTOM') && !DELIVERED.includes(lifecycle(p));
    if (tab === 'done') return DELIVERED.includes(lifecycle(p));
    return true;
  }).filter((p) => {
    const q = search.trim().toLowerCase();
    return !q || p.projectName.toLowerCase().includes(q) || p.projectCode.toLowerCase().includes(q);
  });

  const title = role === 'USER' ? 'My projects' : role === 'PROJECT_DEVELOPER' ? 'My assignments' : role === 'ADMIN' ? 'Projects' : 'Development projects';
  const description = {
    USER: 'Projects you purchased and projects being built for you.',
    PROJECT_DEVELOPER: 'Custom projects assigned to you. Only you and the reviewer can see their deliverables.',
    ADMIN: "Custom projects for your college's students, plus submissions you review.",
    SUPER_ADMIN: 'Every custom development project across colleges. Library projects are managed in the Project library.',
  }[role];

  return (
    <>
      <PageHeader
        title={title}
        description={description}
        actions={role === 'USER' && <Link to="/marketplace" className="btn btn-primary"><Store /> Browse projects</Link>}
      />
      <Tabs value={tab} onChange={setTab} tabs={tabs.map((t) => ({ ...t, count: loading ? undefined : t.count }))} />
      <div className="toolbar">
        <div className="input-with-icon grow" style={{ maxWidth: 420 }}>
          <Search aria-hidden="true" />
          <input className="input" placeholder="Search by name or code" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {error ? <ErrorState error={error} onRetry={reload} /> : loading && !data ? <div className="card"><SkeletonRows rows={6} /></div> : rows.length === 0 ? (
        <div className="card">
          <EmptyState
            icon={role === 'USER' ? BookMarked : FolderKanban}
            title={all.length ? 'Nothing here' : role === 'USER' ? 'No projects yet' : 'No projects yet'}
            text={all.length ? 'Try another tab or search.' : role === 'USER' ? 'Buy a project from your college catalogue or request a custom one.' : role === 'PROJECT_DEVELOPER' ? 'You will see projects here once the platform assigns them to you.' : 'Projects appear once custom requirements are approved and assigned.'}
            action={!all.length && role === 'USER' && <Link to="/marketplace" className="btn btn-primary">Browse projects</Link>}
          />
        </div>
      ) : role === 'USER' ? (
        <div className="card-grid">
          {rows.map((p, i) => (
            <SpotlightCard key={p.id} className="card-interactive project-card reveal" style={{ '--i': Math.min(i, 12) }} role="link" tabIndex={0}
              onClick={() => navigate(`/projects/${p.id}`)} onKeyDown={(e) => e.key === 'Enter' && navigate(`/projects/${p.id}`)}>
              <div className="project-card-head">
                <span className="project-code">{p.projectCode}</span>
                <Badge tone={p.projectType === 'LIBRARY' ? 'neutral' : 'accent'}>{p.projectType === 'LIBRARY' ? 'Library' : 'Custom'}</Badge>
              </div>
              <div className="project-title">{p.projectName}</div>
              {p.projectType === 'CUSTOM' ? (
                <div>
                  <div className="flex justify-between text-xs text-subtle mb-1"><span>{p.developer ? `Developer: ${p.developer.fullName}` : 'Awaiting developer'}</span><span>{p.progressPercent}%</span></div>
                  <Progress value={p.progressPercent} tone={DELIVERED.includes(lifecycle(p)) ? 'success' : undefined} />
                </div>
              ) : <p className="project-abstract">{p.abstractText}</p>}
              <div className="project-card-foot">
                <StatusBadge status={p.projectType === 'LIBRARY' ? 'ACCESS_GRANTED' : lifecycle(p)} label={p.projectType === 'LIBRARY' ? 'Owned' : undefined} />
                <span className="text-xs text-subtle">{relativeTime(p.updatedAt || p.createdAt)}</span>
              </div>
            </SpotlightCard>
          ))}
        </div>
      ) : (
        <div className="card card-flush">
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr><th>Project</th><th>Status</th>{role !== 'PROJECT_DEVELOPER' && <th>Developer</th>}<th>Reviewer</th><th style={{ width: 160 }}>Progress</th><th>Updated</th></tr>
              </thead>
              <tbody>
                {rows.map((p) => (
                  <tr key={p.id} className="is-clickable" onClick={() => navigate(`/projects/${p.id}`)}>
                    <td style={{ maxWidth: 360 }}>
                      <div className="project-code">{p.projectCode}</div>
                      <div className="font-medium truncate">{p.projectName}</div>
                    </td>
                    <td>{p.projectType === 'LIBRARY' ? <StatusBadge status={p.catalogStatus} /> : <StatusBadge status={lifecycle(p)} />}</td>
                    {role !== 'PROJECT_DEVELOPER' && <td className="cell-muted">{p.developer?.fullName || '—'}</td>}
                    <td className="cell-muted">{p.reviewerAdmin?.fullName || (p.projectType === 'CUSTOM' ? 'Platform' : '—')}</td>
                    <td>{p.projectType === 'CUSTOM' ? <div className="flex items-center gap-2"><Progress value={p.progressPercent} /><span className="text-xs tabular text-subtle">{p.progressPercent}%</span></div> : '—'}</td>
                    <td className="cell-muted text-sm">{relativeTime(p.updatedAt || p.createdAt)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}
