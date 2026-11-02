import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  CheckCircle2, Send, Undo2, Wallet, PlayCircle, Lock, UserCog, Eye, AlertTriangle, ArrowRight, Terminal,
} from 'lucide-react';
import { api } from '../utils/api';
import { useAsync } from '../hooks/useAsync';
import { useAuth } from '../context/AuthContext';
import FolderExplorer from '../components/FolderExplorer';
import {
  PageHeader, ErrorState, LoadingBlock, StatusBadge, Card, Timeline, Steps, Field, AsyncButton, useToast, Alert,
  Progress, Badge, Tabs, ConfirmDialog, Avatar,
} from '../components/ui';
import { money, date } from '../utils/format';

const STEPS = [
  { key: 'DEVELOPER_ASSIGNED', label: 'Assigned' },
  { key: 'IN_PROGRESS', label: 'In development' },
  { key: 'READY_FOR_REVIEW', label: 'Review' },
  { key: 'READY_FOR_FINAL_PAYMENT', label: 'Final payment' },
  { key: 'ACCESS_GRANTED', label: 'Delivered' },
];
const STEP_OF = {
  DEVELOPER_ASSIGNED: 'DEVELOPER_ASSIGNED', IN_PROGRESS: 'IN_PROGRESS', TESTING: 'IN_PROGRESS', CHANGES_REQUESTED: 'IN_PROGRESS',
  READY_FOR_REVIEW: 'READY_FOR_REVIEW', REVIEW_APPROVED: 'READY_FOR_FINAL_PAYMENT', READY_FOR_FINAL_PAYMENT: 'READY_FOR_FINAL_PAYMENT',
  ACCESS_GRANTED: 'ACCESS_GRANTED', COMPLETED: 'ACCESS_GRANTED',
};

export default function ProjectDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const project = useAsync(() => api.getProjectById(id), [id]);
  const isCustom = project.data?.projectType === 'CUSTOM';
  const timeline = useAsync(() => (isCustom ? api.getProjectTimeline(id) : Promise.resolve([])), [id, isCustom]);
  const [tab, setTab] = useState('overview');

  useEffect(() => setTab('overview'), [id]);
  const refresh = () => { project.reload(); timeline.reload(); };

  if (project.error) return <><PageHeader title="Project" breadcrumbs={[{ label: 'Projects', to: '/projects' }]} /><ErrorState error={project.error} onRetry={project.reload} /></>;
  if (project.loading && !project.data) return <LoadingBlock />;

  const p = project.data;
  const lifecycle = p.lifecycleStatus || p.status;
  const full = p.accessLevel === 'FULL';
  const crumbs = user?.role === 'SUPER_ADMIN' && !isCustom
    ? [{ label: 'Project library', to: '/library' }, { label: p.projectCode }]
    : [{ label: user?.role === 'USER' ? 'My projects' : 'Projects', to: '/projects' }, { label: p.projectCode }];

  return (
    <>
      <PageHeader
        breadcrumbs={crumbs}
        title={p.projectName}
        description={[p.projectCode, isCustom ? p.requirement?.collegeName : p.domain].filter(Boolean).join(' · ')}
        actions={
          <div className="flex items-center gap-2">
            <Badge tone={isCustom ? 'accent' : 'neutral'}>{isCustom ? 'Custom project' : 'Library project'}</Badge>
            {isCustom ? <StatusBadge status={lifecycle} /> : <StatusBadge status={full ? 'ACCESS_GRANTED' : 'PREVIEW'} label={full ? 'Full access' : 'Preview'} />}
          </div>
        }
      />

      {isCustom && !['REJECTED', 'INACTIVE'].includes(lifecycle) && (
        <div className="card mb-6" style={{ padding: '14px 18px' }}><Steps steps={STEPS} current={STEP_OF[lifecycle] || 'DEVELOPER_ASSIGNED'} /></div>
      )}

      <Tabs value={tab} onChange={setTab} tabs={[
        { value: 'overview', label: 'Overview' },
        { value: 'files', label: full ? 'Deliverables' : 'Files' },
        ...(isCustom ? [{ value: 'activity', label: 'Activity' }] : []),
      ]} />

      {tab === 'overview' && (
        <div className="layout-split">
          <div className="space-y-6">
            {isCustom ? <CustomOverview p={p} /> : <LibraryOverview p={p} full={full} user={user} />}
          </div>
          <div className="space-y-4 aside-priority">
            {isCustom && <WorkflowPanel p={p} user={user} onDone={refresh} />}
            {isCustom && <PeopleCard p={p} />}
            {isCustom && <AmountsCard p={p} />}
            {!isCustom && user?.role === 'SUPER_ADMIN' && (
              <div className="card">
                <div className="section-title mb-1">Catalogue</div>
                <p className="text-sm mb-3">Manage metadata, pricing and publishing from the library.</p>
                <Link to={`/library?search=${encodeURIComponent(p.projectCode)}`} className="btn btn-secondary btn-block">Open in library</Link>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === 'files' && (
        <>
          {!full && (
            <Alert tone="info" title="Preview access">
              {isCustom ? 'Deliverables unlock for you after the final payment is verified.' : 'Screenshots and demo files are visible now. The rest unlock after purchase.'}
            </Alert>
          )}
          <FolderExplorer project={p} />
        </>
      )}

      {tab === 'activity' && (
        <Card title="Timeline" subtitle="Every status change, review and payment on this project">
          <Timeline items={timeline.data || []} />
        </Card>
      )}
    </>
  );
}

function LibraryOverview({ p, full, user }) {
  const techs = (p.technologyStack || '').split(',').map((t) => t.trim()).filter(Boolean);
  return (
    <>
      {!full && user?.role === 'USER' && (
        <div className="alert alert-info">
          <Lock aria-hidden="true" />
          <div className="flex-1">You are viewing a preview. <Link to={`/marketplace/${p.id}`}>Buy this project</Link> to unlock the code and documentation.</div>
        </div>
      )}
      <Card title="Abstract">
        <p style={{ whiteSpace: 'pre-wrap', color: 'var(--text)', lineHeight: 1.7 }}>{p.abstractText || 'No abstract yet.'}</p>
      </Card>
      {p.description && p.description !== p.abstractText && (
        <Card title="Overview"><p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{p.description}</p></Card>
      )}
      {full && p.installationInstructions && (
        <Card title="Installation and execution" actions={<Terminal size={15} className="text-subtle" />}>
          <pre className="surface-muted p-4 text-sm" style={{ whiteSpace: 'pre-wrap', overflowX: 'auto', fontFamily: 'var(--font-mono)' }}>{p.installationInstructions}</pre>
        </Card>
      )}
      {techs.length > 0 && (
        <Card title="Technologies"><div className="flex flex-wrap gap-2">{techs.map((t) => <span key={t} className="tag">{t}</span>)}</div></Card>
      )}
    </>
  );
}

function CustomOverview({ p }) {
  return (
    <>
      {p.lifecycleStatus === 'CHANGES_REQUESTED' && p.changeRequestNotes && (
        <Alert tone="warning" title="Changes requested by the reviewer">{p.changeRequestNotes}</Alert>
      )}
      <Card title="Progress">
        <div className="flex items-end justify-between mb-2">
          <span className="text-3xl font-semibold tabular" style={{ fontSize: 'var(--text-3xl)', letterSpacing: '-0.03em' }}>{p.progressPercent ?? 0}%</span>
          <span className="text-sm text-muted">{p.developerAcceptedAt ? `Accepted ${date(p.developerAcceptedAt)}` : 'Not accepted yet'}</span>
        </div>
        <Progress value={p.progressPercent} tone={['ACCESS_GRANTED', 'COMPLETED'].includes(p.lifecycleStatus) ? 'success' : undefined} />
        {p.reviewNotes && <p className="text-sm mt-4"><span className="font-medium" style={{ color: 'var(--text)' }}>Latest notes:</span> {p.reviewNotes}</p>}
      </Card>
      <Card title="Brief" actions={p.requirement && <Link to={`/requirements/${p.requirement.id}`} className="btn btn-ghost btn-sm">Requirement <ArrowRight /></Link>}>
        <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{p.description || '—'}</p>
        {p.technologyStack && <div className="flex flex-wrap gap-2 mt-4">{p.technologyStack.split(',').map((t) => t.trim()).filter(Boolean).map((t) => <span key={t} className="tag">{t}</span>)}</div>}
      </Card>
    </>
  );
}

function PeopleCard({ p }) {
  const people = [
    ['Student', p.requirement?.studentName],
    ['Developer', p.developer?.fullName],
    ['Reviewer', p.reviewerAdmin?.fullName || 'Platform owner'],
  ];
  return (
    <div className="card">
      <div className="section-title mb-3">People</div>
      <ul className="space-y-3">
        {people.map(([role, name]) => (
          <li key={role} className="flex items-center gap-3">
            <Avatar name={name || '?'} size="sm" />
            <div className="min-w-0">
              <div className="text-sm font-medium truncate">{name || 'Not assigned'}</div>
              <div className="text-xs text-subtle">{role}</div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function AmountsCard({ p }) {
  if (p.budget == null) return null;
  return (
    <div className="card">
      <div className="section-title mb-3">Payments</div>
      <dl className="kv" style={{ gridTemplateColumns: '1fr auto' }}>
        <dt>Total</dt><dd className="text-right tabular font-medium">{money(p.budget)}</dd>
        <dt>Advance</dt><dd className="text-right tabular">{money(p.advanceAmount)} <span className="text-xs text-success">{p.advancePaymentStatus === 'COMPLETED' ? 'paid' : ''}</span></dd>
        <dt>Balance</dt><dd className="text-right tabular">{money(p.remainingAmount)} <span className="text-xs text-success">{p.remainingPaymentStatus === 'COMPLETED' ? 'paid' : ''}</span></dd>
      </dl>
    </div>
  );
}

/* ------------------------------------------------------------------ */

function WorkflowPanel({ p, user, onDone }) {
  const s = p.lifecycleStatus || p.status;
  if (p.isDeveloper && user.role === 'PROJECT_DEVELOPER') return <DeveloperActions p={p} s={s} onDone={onDone} />;
  if ((p.isReviewer || user.role === 'SUPER_ADMIN') && s === 'READY_FOR_REVIEW') return <ReviewActions p={p} onDone={onDone} />;
  if (p.isRequester && s === 'READY_FOR_FINAL_PAYMENT') return <FinalPayment p={p} onDone={onDone} />;
  if (user.role === 'SUPER_ADMIN') return <AssignmentActions p={p} onDone={onDone} />;
  const help = {
    DEVELOPER_ASSIGNED: 'Waiting for the developer to accept the assignment.',
    IN_PROGRESS: 'The developer is building the project.',
    CHANGES_REQUESTED: 'The developer is addressing review feedback.',
    READY_FOR_REVIEW: 'Submitted and waiting for review.',
    READY_FOR_FINAL_PAYMENT: 'Approved. Waiting for the student to pay the balance.',
    REVIEW_APPROVED: 'Approved.',
    ACCESS_GRANTED: 'Delivered. The student has full access.',
  }[s];
  return <div className="card"><div className="section-title mb-1">Status</div><p className="text-sm">{help || 'No action needed.'}</p></div>;
}

function DeveloperActions({ p, s, onDone }) {
  const { notify } = useToast();
  const [percent, setPercent] = useState(p.progressPercent ?? 0);
  const [note, setNote] = useState('');
  const [submitNotes, setSubmitNotes] = useState('');
  const run = (fn, msg) => async () => {
    try {
      await fn();
      notify(msg);
      onDone();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };

  if (s === 'DEVELOPER_ASSIGNED') {
    return (
      <div className="card">
        <div className="section-title mb-1">New assignment</div>
        <p className="text-sm mb-4">Review the brief and accept to start development. The platform owner is notified.</p>
        <AsyncButton className="btn btn-primary btn-block" onClick={run(() => api.acceptAssignment(p.id), 'Assignment accepted.')}><PlayCircle /> Accept assignment</AsyncButton>
      </div>
    );
  }
  if (['IN_PROGRESS', 'CHANGES_REQUESTED', 'TESTING'].includes(s)) {
    return (
      <div className="card">
        <div className="section-title mb-3">Update progress</div>
        <Field label={`Progress · ${percent}%`}>
          <input type="range" min={0} max={100} step={5} value={percent} onChange={(e) => setPercent(Number(e.target.value))} style={{ accentColor: 'var(--accent)' }} />
        </Field>
        <Field label="What changed?"><textarea className="textarea" rows={2} value={note} onChange={(e) => setNote(e.target.value)} /></Field>
        <AsyncButton className="btn btn-secondary btn-block" onClick={run(() => api.updateProgress(p.id, percent, note), 'Progress updated.')}>Save progress</AsyncButton>
        <hr className="divider" />
        <div className="section-title mb-1">Submit for review</div>
        <p className="text-sm mb-3">Upload source code, documentation and the demo video under Deliverables first.</p>
        <Field label="Notes for the reviewer"><textarea className="textarea" rows={2} value={submitNotes} onChange={(e) => setSubmitNotes(e.target.value)} /></Field>
        <AsyncButton className="btn btn-primary btn-block" onClick={run(() => api.developerSubmitReview(p.id, submitNotes), 'Submitted for review.')}><Send /> Submit for review</AsyncButton>
      </div>
    );
  }
  return <div className="card"><div className="section-title mb-1">Status</div><p className="text-sm">{s === 'READY_FOR_REVIEW' ? 'Waiting for the reviewer.' : 'Nothing to do right now.'}</p></div>;
}

function ReviewActions({ p, onDone }) {
  const { notify } = useToast();
  const [notes, setNotes] = useState('');
  const act = (action, msg) => async () => {
    if (action === 'REQUEST_CHANGES' && !notes.trim()) return notify('Describe the changes you need.', { tone: 'error' });
    try {
      await api.adminReviewProject(p.id, action, notes);
      notify(msg);
      onDone();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };
  return (
    <div className="card">
      <div className="section-title mb-1">Review submission</div>
      <p className="text-sm mb-4">Check the deliverables tab, then approve or request changes.</p>
      <Field label="Review notes" hint="Required when requesting changes"><textarea className="textarea" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} /></Field>
      <div className="flex flex-col gap-2">
        <AsyncButton className="btn btn-primary btn-block" onClick={act('APPROVE', 'Approved. The student has been asked to pay the balance.')}><CheckCircle2 /> Approve</AsyncButton>
        <AsyncButton className="btn btn-secondary btn-block" onClick={act('REQUEST_CHANGES', 'Changes requested.')}><Undo2 /> Request changes</AsyncButton>
      </div>
    </div>
  );
}

function FinalPayment({ p, onDone }) {
  const { notify } = useToast();
  const payment = useAsync(() => api.getPaymentConfig(), []);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const pay = async () => {
    setBusy(true);
    try {
      const res = await api.payProjectRemaining(p.id);
      notify(res.message, { title: 'Payment complete' });
      setOpen(false);
      onDone();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    } finally {
      setBusy(false);
    }
  };
  const cfg = payment.data || {};
  return (
    <div className="card">
      <div className="section-title mb-1">Your project is ready</div>
      <p className="text-sm">It passed review. Pay the balance to unlock every deliverable.</p>
      <div className="price price-lg mt-3">{money(p.remainingAmount)}</div>
      {cfg.simulation && <div className="mt-2"><span className="notice-simulated"><AlertTriangle size={12} /> Development payment mode</span></div>}
      <button className="btn btn-primary btn-block btn-lg mt-4" onClick={() => setOpen(true)} disabled={cfg.available === false}><Wallet /> Pay balance</button>
      <ConfirmDialog open={open} title="Confirm final payment" confirmLabel={`Pay ${money(p.remainingAmount)}`} busy={busy} onConfirm={pay} onClose={() => setOpen(false)}
        text={`Paying the balance for "${p.projectName}" unlocks the source code, documentation and demo.`}>
        {cfg.simulation && <Alert tone="warning" title="Simulated payment">No money is charged on this development server.</Alert>}
      </ConfirmDialog>
    </div>
  );
}

function AssignmentActions({ p, onDone }) {
  const { notify } = useToast();
  const devs = useAsync(() => api.getWorkflowDevelopers(), []);
  const reviewers = useAsync(() => api.getWorkflowReviewers(), []);
  const [developerId, setDeveloperId] = useState('');
  const [reviewerId, setReviewerId] = useState('');
  const delivered = ['ACCESS_GRANTED', 'COMPLETED'].includes(p.lifecycleStatus);
  return (
    <div className="card">
      <div className="section-title mb-3 flex items-center gap-2"><UserCog size={15} /> Assignment</div>
      <Field label="Reassign developer">
        <div className="flex gap-2">
          <select className="select" value={developerId} onChange={(e) => setDeveloperId(e.target.value)} disabled={delivered}>
            <option value="">{p.developer ? `Current: ${p.developer.fullName}` : 'Select developer'}</option>
            {(devs.data || []).filter((d) => d.id !== p.developer?.id).map((d) => <option key={d.id} value={d.id}>{d.fullName} · {d.activeProjects} active</option>)}
          </select>
          <AsyncButton className="btn btn-secondary" disabled={!developerId} onClick={async () => {
            try { await api.assignDeveloperToProject(p.id, Number(developerId)); notify('Developer reassigned.'); setDeveloperId(''); onDone(); } catch (e) { notify(e.message, { tone: 'error' }); }
          }}>Save</AsyncButton>
        </div>
      </Field>
      <Field label="Reviewer">
        <div className="flex gap-2">
          <select className="select" value={reviewerId} onChange={(e) => setReviewerId(e.target.value)}>
            <option value="">{p.reviewerAdmin ? `Current: ${p.reviewerAdmin.fullName}` : 'Platform owner (default)'}</option>
            {(reviewers.data || []).map((u) => <option key={u.id} value={u.id}>{u.fullName}{u.collegeName ? ` · ${u.collegeName}` : ''}</option>)}
          </select>
          <AsyncButton className="btn btn-secondary" disabled={!reviewerId} onClick={async () => {
            try { await api.assignReviewerToProject(p.id, Number(reviewerId)); notify('Reviewer updated.'); setReviewerId(''); onDone(); } catch (e) { notify(e.message, { tone: 'error' }); }
          }}><Eye /> Save</AsyncButton>
        </div>
      </Field>
    </div>
  );
}
