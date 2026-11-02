import { Link, useNavigate } from 'react-router-dom';
import {
  Building2, Users, Library, Share2, ClipboardCheck, UserCog, Eye, IndianRupee, FolderKanban, CheckCircle2,
  FileText, Clock, AlertTriangle, Store, BookMarked, Wallet, ArrowRight, Code2, Receipt,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useAsync } from '../hooks/useAsync';
import { api } from '../utils/api';
import {
  PageHeader, StatCard, Card, EmptyState, ErrorState, StatusBadge, Progress, Badge,
} from '../components/ui';
import { money, relativeTime, statusLabel, ROLE_LABELS, titleCase } from '../utils/format';

export default function Dashboard() {
  const { user } = useAuth();
  const { data, loading, error, reload } = useAsync(() => api.getDashboard(), []);
  const greeting = (() => {
    const h = new Date().getHours();
    return h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening';
  })();
  const first = user?.fullName?.split(' ')[0] || '';

  if (error) return <><PageHeader title={`${greeting}, ${first}`} /><ErrorState error={error} onRetry={reload} /></>;

  const d = data || {};
  const props = { d, loading };
  return (
    <>
      <PageHeader
        title={`${greeting}, ${first}`}
        description={
          user?.role === 'ADMIN' && d.college ? `${d.college.name} · College administration`
            : user?.role === 'USER' && d.college ? `${d.college.name} · ${ROLE_LABELS.USER}`
              : ROLE_LABELS[user?.role]
        }
        actions={<DashboardActions role={user?.role} />}
      />
      {user?.role === 'SUPER_ADMIN' && <SuperAdminDashboard {...props} />}
      {user?.role === 'ADMIN' && <CollegeAdminDashboard {...props} />}
      {user?.role === 'PROJECT_DEVELOPER' && <DeveloperDashboard {...props} />}
      {user?.role === 'USER' && <StudentDashboard {...props} />}
    </>
  );
}

function DashboardActions({ role }) {
  if (role === 'SUPER_ADMIN') return (
    <>
      <Link to="/allocations" className="btn btn-secondary"><Share2 /> Allocate projects</Link>
      <Link to="/library" className="btn btn-primary"><Library /> Open library</Link>
    </>
  );
  if (role === 'ADMIN') return <Link to="/requirements?status=SUBMITTED" className="btn btn-primary"><ClipboardCheck /> Review requirements</Link>;
  if (role === 'USER') return (
    <>
      <Link to="/requirements/new" className="btn btn-secondary"><FileText /> Request a project</Link>
      <Link to="/marketplace" className="btn btn-primary"><Store /> Browse projects</Link>
    </>
  );
  return null;
}

/* ------------------------------------------------------------------ */

function SuperAdminDashboard({ d, loading }) {
  const navigate = useNavigate();
  const stats = [
    { label: 'Colleges', value: d.colleges, hint: `${d.activeColleges ?? 0} active`, icon: Building2, to: '/colleges' },
    { label: 'College admins', value: d.admins, icon: UserCog, to: '/admins' },
    { label: 'Students', value: d.students, icon: Users, to: '/users' },
    { label: 'Library projects', value: d.libraryProjects, hint: `${d.publishedProjects ?? 0} published`, icon: Library, to: '/library' },
    { label: 'Allocated projects', value: d.allocatedProjects, hint: `${d.activeAllocations ?? 0} college allocations`, icon: Share2, to: '/allocations' },
    { label: 'Custom requests', value: d.customRequests, icon: FileText, to: '/requirements' },
    { label: 'Active developers', value: d.developers, icon: Code2, to: '/developers' },
    { label: 'Orders', value: d.orders, icon: Receipt, to: '/orders' },
  ];
  const attention = [
    { label: 'Awaiting your approval', value: d.pendingApprovals, to: '/requirements?status=SUPER_ADMIN_REVIEW', icon: ClipboardCheck },
    { label: 'Ready for developer assignment', value: d.awaitingAssignment, to: '/requirements?status=ADVANCE_PAYMENT_COMPLETED', icon: UserCog },
    { label: 'Submissions awaiting review', value: d.awaitingReview, to: '/projects?status=READY_FOR_REVIEW', icon: Eye },
  ];

  return (
    <div className="space-y-6">
      <div className="stat-grid">
        {stats.map((s, i) => (
          <StatCard key={s.label} {...s} index={i} loading={loading} onClick={() => navigate(s.to)} />
        ))}
      </div>

      <div className="layout-split">
        <div className="space-y-6">
          <Card title="Needs attention" subtitle="Items waiting on the platform owner">
            <div className="list" style={{ margin: '-20px' }}>
              {attention.map((a) => (
                <Link key={a.label} to={a.to} className="list-item" style={{ color: 'var(--text)', textDecoration: 'none' }}>
                  <span className="stat-icon"><a.icon aria-hidden="true" /></span>
                  <span className="flex-1">{a.label}</span>
                  <span className="font-semibold tabular">{loading ? '—' : a.value ?? 0}</span>
                  <ArrowRight size={15} className="text-subtle" aria-hidden="true" />
                </Link>
              ))}
            </div>
          </Card>

          <Card title="Requirement pipeline" subtitle="Custom development requests by stage">
            <PipelineBars data={d.requirementPipeline} loading={loading} />
          </Card>

          <Card title="Colleges" subtitle="Most active by orders" actions={<Link to="/colleges" className="btn btn-ghost btn-sm">View all</Link>} flush>
            {(d.collegeLeaderboard || []).length === 0 ? (
              <EmptyState icon={Building2} title="No colleges yet" text="Register a college to start allocating projects." action={<Link to="/colleges" className="btn btn-primary btn-sm">Add college</Link>} />
            ) : (
              <div className="table-wrap">
                <table className="table">
                  <thead><tr><th>College</th><th className="cell-num">Students</th><th className="cell-num">Projects</th><th className="cell-num">Orders</th></tr></thead>
                  <tbody>
                    {d.collegeLeaderboard.map((c) => (
                      <tr key={c.id}>
                        <td><div className="font-medium">{c.name}</div><div className="text-xs text-subtle font-mono">{c.code}</div></td>
                        <td className="cell-num">{c.students}</td>
                        <td className="cell-num">{c.allocated}</td>
                        <td className="cell-num">{c.orders}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center justify-between">
              <span className="stat-label">Verified revenue</span>
              <span className="stat-icon"><IndianRupee aria-hidden="true" /></span>
            </div>
            <div className="stat-value mt-2">{loading ? '—' : money(d.verifiedRevenue)}</div>
            <p className="text-xs text-subtle mt-1">Completed payments confirmed by a real payment gateway.</p>
            {d.paymentSimulation && (
              <div className="alert alert-warning mt-4" style={{ marginBottom: 0 }}>
                <AlertTriangle aria-hidden="true" />
                <div className="text-sm">
                  Payment simulation is on. {money(d.simulatedRevenue)} in simulated orders is excluded from revenue.
                </div>
              </div>
            )}
          </div>

          <Card title="Recent activity" actions={<Link to="/audit-logs" className="btn btn-ghost btn-sm">Audit log</Link>}>
            <ActivityFeed items={d.recentActivity} loading={loading} />
          </Card>
        </div>
      </div>
    </div>
  );
}

function PipelineBars({ data, loading }) {
  if (loading) return <div className="skeleton" style={{ height: 120 }} />;
  const entries = Object.entries(data || {}).sort((a, b) => b[1] - a[1]);
  if (!entries.length) return <p className="text-sm text-subtle">No requests yet.</p>;
  const max = Math.max(...entries.map(([, v]) => v));
  return (
    <div className="space-y-3" role="table" aria-label="Requirements by stage">
      {entries.map(([status, value]) => (
        <div key={status} role="row" className="flex items-center gap-3" title={`${statusLabel(status)}: ${value}`}>
          <span role="cell" className="text-sm text-muted truncate" style={{ width: 170, flexShrink: 0 }}>{statusLabel(status)}</span>
          <span role="cell" className="flex-1" style={{ height: 10, background: 'var(--surface-2)', borderRadius: 4 }}>
            <span style={{ display: 'block', height: '100%', width: `${Math.max(4, (value / max) * 100)}%`, background: 'var(--accent)', borderRadius: 4, transition: 'width 320ms var(--ease)' }} />
          </span>
          <span role="cell" className="text-sm font-medium tabular" style={{ width: 28, textAlign: 'right' }}>{value}</span>
        </div>
      ))}
    </div>
  );
}

function ActivityFeed({ items, loading }) {
  if (loading) return <div className="skeleton" style={{ height: 160 }} />;
  if (!items?.length) return <p className="text-sm text-subtle">Nothing recorded yet.</p>;
  return (
    <ol className="space-y-3">
      {items.slice(0, 8).map((log) => (
        <li key={log.id} className="flex gap-3">
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--border-strong)', marginTop: 8, flexShrink: 0 }} />
          <div className="min-w-0">
            <div className="text-sm font-medium">{titleCase(log.action)}</div>
            <div className="text-xs text-muted" style={{ overflowWrap: 'anywhere' }}>{log.details}</div>
            <div className="text-xs text-subtle mt-1">{log.actorEmail} · {relativeTime(log.timestamp)}</div>
          </div>
        </li>
      ))}
    </ol>
  );
}

/* ------------------------------------------------------------------ */

function CollegeAdminDashboard({ d, loading }) {
  const navigate = useNavigate();
  if (!loading && !d.college) {
    return <div className="card"><EmptyState icon={Building2} title="No college linked" text={d.message || 'Ask the platform administrator to link your account to a college.'} /></div>;
  }
  const stats = [
    { label: 'Allocated projects', value: d.allocatedProjects, icon: Library, to: '/marketplace' },
    { label: 'Registered students', value: d.students, icon: Users, to: '/users' },
    { label: 'New requirements', value: d.newRequirements, icon: FileText, tone: d.newRequirements ? 'accent' : undefined, to: '/requirements?status=SUBMITTED' },
    { label: 'Pending requests', value: d.pendingRequests, icon: Clock, to: '/requirements' },
    { label: 'Active projects', value: d.activeProjects, icon: FolderKanban, to: '/projects' },
    { label: 'Completed projects', value: d.completedProjects, icon: CheckCircle2, to: '/projects' },
    { label: 'Orders', value: d.orders, icon: Receipt, to: '/orders' },
    { label: 'College revenue', value: d.revenue, icon: IndianRupee, format: money, to: '/orders' },
  ];
  return (
    <div className="space-y-6">
      {d.reviewQueue > 0 && (
        <Link to="/projects?status=READY_FOR_REVIEW" className="alert alert-info" style={{ textDecoration: 'none' }}>
          <Eye aria-hidden="true" /><div>You have {d.reviewQueue} project submission{d.reviewQueue > 1 ? 's' : ''} to review.</div>
        </Link>
      )}
      <div className="stat-grid">
        {stats.map((s, i) => <StatCard key={s.label} {...s} index={i} loading={loading} onClick={() => navigate(s.to)} />)}
      </div>
      <div className="layout-split">
        <Card title="Latest requirements" subtitle="Submitted by your students" actions={<Link to="/requirements" className="btn btn-ghost btn-sm">View all</Link>} flush>
          {(d.recentRequirements || []).length === 0 ? (
            <EmptyState icon={FileText} title="No requirements yet" text="When students request custom projects they appear here for your review." />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead><tr><th>Requirement</th><th>Student</th><th>Status</th><th>Submitted</th></tr></thead>
                <tbody>
                  {d.recentRequirements.map((r) => (
                    <tr key={r.id} className="is-clickable" onClick={() => navigate(`/requirements/${r.id}`)}>
                      <td className="font-medium">{r.title}</td>
                      <td className="cell-muted">{r.student}</td>
                      <td><StatusBadge status={r.status} /></td>
                      <td className="cell-muted">{relativeTime(r.createdAt)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
        <Card title="Requirement pipeline">
          <PipelineBars data={d.requirementPipeline} loading={loading} />
        </Card>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */

function DeveloperDashboard({ d, loading }) {
  const navigate = useNavigate();
  const stats = [
    { label: 'Assigned projects', value: d.assigned, icon: FolderKanban },
    { label: 'Awaiting acceptance', value: d.pendingAcceptance, icon: Clock, tone: d.pendingAcceptance ? 'accent' : undefined },
    { label: 'In progress', value: d.inProgress, icon: Code2 },
    { label: 'In review', value: d.inReview, icon: Eye },
    { label: 'Changes requested', value: d.changesRequested, icon: AlertTriangle, tone: d.changesRequested ? 'warning' : undefined },
    { label: 'Completed', value: d.completed, icon: CheckCircle2 },
  ];
  const next = (p) => ({
    DEVELOPER_ASSIGNED: 'Review and accept',
    IN_PROGRESS: 'Upload deliverables',
    CHANGES_REQUESTED: 'Address feedback',
    READY_FOR_REVIEW: 'Waiting for reviewer',
  }[p.status] || 'Open');
  return (
    <div className="space-y-6">
      <div className="stat-grid">{stats.map((s, i) => <StatCard key={s.label} {...s} index={i} loading={loading} />)}</div>
      <Card title="Your assignments" flush>
        {(d.projects || []).length === 0 ? (
          <EmptyState icon={FolderKanban} title="No assignments yet" text="Projects assigned to you by the platform owner will appear here." />
        ) : (
          <div className="list">
            {d.projects.map((p) => (
              <button key={p.id} className="list-item w-full text-left" onClick={() => navigate(`/projects/${p.id}`)}>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2"><span className="project-code">{p.projectCode}</span><StatusBadge status={p.status} /></div>
                  <div className="font-medium mt-1 truncate">{p.projectName}</div>
                </div>
                <div className="desktop-only" style={{ width: 160 }}>
                  <div className="flex justify-between text-xs text-subtle mb-1"><span>Progress</span><span>{p.progressPercent}%</span></div>
                  <Progress value={p.progressPercent} />
                </div>
                <span className="btn btn-secondary btn-sm">{next(p)}</span>
              </button>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

/* ------------------------------------------------------------------ */

function StudentDashboard({ d, loading }) {
  const navigate = useNavigate();
  const stats = [
    { label: 'Available projects', value: d.availableProjects, icon: Store, to: '/marketplace' },
    { label: 'Purchased projects', value: d.purchased, icon: BookMarked, to: '/projects' },
    { label: 'Requested projects', value: d.requested, icon: FileText, to: '/requirements' },
    { label: 'Active development', value: d.activeDevelopment, icon: Code2, to: '/projects' },
    { label: 'Pending payments', value: d.pendingPayments, icon: Wallet, tone: d.pendingPayments ? 'warning' : undefined, to: '/requirements' },
  ];
  return (
    <div className="space-y-6">
      <div className="stat-grid">{stats.map((s, i) => <StatCard key={s.label} {...s} index={i} loading={loading} onClick={() => navigate(s.to)} />)}</div>

      <div className="layout-split">
        <div className="space-y-6">
          <Card title="Custom development" subtitle="Projects being built for you" actions={<Link to="/requirements/new" className="btn btn-ghost btn-sm">New request</Link>} flush>
            {(d.customProjects || []).length === 0 ? (
              <EmptyState icon={Code2} title="No custom projects yet" text="Can't find what you need in the library? Submit a requirement and your college will forward it for development." action={<Link to="/requirements/new" className="btn btn-primary btn-sm">Submit a requirement</Link>} />
            ) : (
              <div className="list">
                {d.customProjects.map((p) => (
                  <Link key={p.id} to={`/projects/${p.id}`} className="list-item" style={{ color: 'var(--text)', textDecoration: 'none' }}>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{p.projectName}</div>
                      <div className="mt-2" style={{ maxWidth: 280 }}><Progress value={p.progressPercent} /></div>
                    </div>
                    <StatusBadge status={p.status} />
                  </Link>
                ))}
              </div>
            )}
          </Card>

          <Card title="Your library" actions={<Link to="/projects" className="btn btn-ghost btn-sm">View all</Link>} flush>
            {(d.library || []).length === 0 ? (
              <EmptyState icon={BookMarked} title="Nothing purchased yet" text="Projects you buy appear here with full access to code, documentation and demo videos." action={<Link to="/marketplace" className="btn btn-primary btn-sm">Browse projects</Link>} />
            ) : (
              <div className="list">
                {d.library.map((p) => (
                  <Link key={p.id} to={`/projects/${p.id}`} className="list-item" style={{ color: 'var(--text)', textDecoration: 'none' }}>
                    <span className="project-code">{p.projectCode}</span>
                    <span className="flex-1 truncate font-medium">{p.projectName}</span>
                    {p.domain && <Badge>{p.domain}</Badge>}
                    <ArrowRight size={15} className="text-subtle" aria-hidden="true" />
                  </Link>
                ))}
              </div>
            )}
          </Card>
        </div>

        <Card title="Recent orders" actions={<Link to="/orders" className="btn btn-ghost btn-sm">All orders</Link>}>
          {(d.recentOrders || []).length === 0 ? (
            <p className="text-sm text-subtle">No orders yet.</p>
          ) : (
            <ul className="space-y-3">
              {d.recentOrders.map((o) => (
                <li key={o.id} className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-sm font-medium truncate">{o.itemName}</div>
                    <div className="text-xs text-subtle">{o.orderNumber} · {relativeTime(o.createdAt)}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium tabular">{money(o.amount)}</div>
                    {o.simulated ? <span className="notice-simulated">Simulated</span> : <StatusBadge status={o.paymentStatus} />}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
