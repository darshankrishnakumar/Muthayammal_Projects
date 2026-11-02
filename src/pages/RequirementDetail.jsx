import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Pencil, Send, CheckCircle2, Undo2, XCircle, Wallet, UserCog, ArrowRight, AlertTriangle, Trash2 } from 'lucide-react';
import { api } from '../utils/api';
import { useAsync } from '../hooks/useAsync';
import { useAuth } from '../context/AuthContext';
import {
  PageHeader, ErrorState, LoadingBlock, StatusBadge, Card, Timeline, Steps, Field, AsyncButton, useToast, Alert,
  ConfirmDialog, Progress,
} from '../components/ui';
import { money, date } from '../utils/format';

const STEPS = [
  { key: 'DRAFT', label: 'Draft' },
  { key: 'SUBMITTED', label: 'College review' },
  { key: 'SUPER_ADMIN_REVIEW', label: 'Approval' },
  { key: 'ADVANCE_PAYMENT_PENDING', label: 'Advance' },
  { key: 'IN_PROGRESS', label: 'Development' },
  { key: 'COMPLETED', label: 'Delivered' },
];
const STEP_OF = {
  DRAFT: 'DRAFT', CHANGES_REQUESTED: 'DRAFT', SUBMITTED: 'SUBMITTED', SUPER_ADMIN_REVIEW: 'SUPER_ADMIN_REVIEW',
  ADVANCE_PAYMENT_PENDING: 'ADVANCE_PAYMENT_PENDING', ADVANCE_PAYMENT_COMPLETED: 'IN_PROGRESS', IN_PROGRESS: 'IN_PROGRESS', COMPLETED: 'COMPLETED',
};

export default function RequirementDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const req = useAsync(() => api.getRequirementById(id), [id]);
  const timeline = useAsync(() => api.getRequirementTimeline(id), [id]);
  const project = useAsync(() => api.getProjectByRequirementId(id).catch((e) => (e.status === 404 ? null : Promise.reject(e))), [id]);

  const refresh = () => { req.reload(); timeline.reload(); project.reload(); };

  if (req.error) return <><PageHeader title="Requirement" breadcrumbs={[{ label: 'Requirements', to: '/requirements' }]} /><ErrorState error={req.error} onRetry={req.reload} /></>;
  if (req.loading && !req.data) return <LoadingBlock />;
  const r = req.data;
  const closed = r.status === 'REJECTED' || r.status === 'INACTIVE';

  return (
    <>
      <PageHeader
        breadcrumbs={[{ label: 'Requirements', to: '/requirements' }, { label: `#${r.id}` }]}
        title={r.title}
        description={[r.user?.fullName, r.college?.name, `Created ${date(r.createdAt)}`].filter(Boolean).join(' · ')}
        actions={<StatusBadge status={r.status} />}
      />

      {!closed && <div className="card mb-6" style={{ padding: '14px 18px' }}><Steps steps={STEPS} current={STEP_OF[r.status] || 'DRAFT'} /></div>}

      <div className="layout-split">
        <div className="space-y-6">
          {(r.collegeAdminNotes || r.superAdminNotes) && (
            <Alert tone={r.status === 'CHANGES_REQUESTED' ? 'warning' : r.status === 'REJECTED' ? 'danger' : 'info'} title="Reviewer notes">
              {r.superAdminNotes && <div><span className="font-medium">Platform:</span> {r.superAdminNotes}</div>}
              {r.collegeAdminNotes && <div><span className="font-medium">College:</span> {r.collegeAdminNotes}</div>}
            </Alert>
          )}

          <Card title="Requirement">
            <div className="space-y-4">
              <div>
                <div className="text-xs font-medium text-subtle uppercase mb-1">Problem statement</div>
                <p style={{ color: 'var(--text)', whiteSpace: 'pre-wrap' }}>{r.problemStatement}</p>
              </div>
              {r.description && (
                <div>
                  <div className="text-xs font-medium text-subtle uppercase mb-1">Features and details</div>
                  <p style={{ whiteSpace: 'pre-wrap' }}>{r.description}</p>
                </div>
              )}
              <dl className="kv">
                <dt>Technologies</dt><dd>{r.technologyStack || '—'}</dd>
                <dt>Student budget</dt><dd>{r.budget != null && !r.advanceAmount ? money(r.budget) : r.budget != null ? `${money(r.budget)} (quoted)` : '—'}</dd>
              </dl>
              {(r.imageUrl || r.audioUrl) && (
                <div className="grid grid-cols-2 gap-3">
                  {r.imageUrl && <img src={r.imageUrl} alt="Reference attachment" className="border rounded" style={{ maxHeight: 220, objectFit: 'contain' }} />}
                  {r.audioUrl && <audio controls src={r.audioUrl} style={{ width: '100%' }} />}
                </div>
              )}
            </div>
          </Card>

          {project.data && <LinkedProject project={project.data} />}

          <Card title="Timeline">
            <Timeline items={timeline.data || []} />
          </Card>
        </div>

        <div className="space-y-4 aside-priority">
          <ActionPanel r={r} user={user} onDone={refresh} hasProject={!!project.data} />
          {r.advanceAmount != null && <QuoteCard r={r} />}
        </div>
      </div>
    </>
  );
}

function LinkedProject({ project: p }) {
  return (
    <Card title="Development project" actions={<Link to={`/projects/${p.id}`} className="btn btn-secondary btn-sm">Open project <ArrowRight /></Link>}>
      <div className="flex items-center gap-3 mb-3">
        <span className="project-code">{p.projectCode}</span>
        <StatusBadge status={p.lifecycleStatus || p.status} />
      </div>
      <div className="flex justify-between text-xs text-subtle mb-1"><span>Progress</span><span>{p.progressPercent ?? 0}%</span></div>
      <Progress value={p.progressPercent} />
      <dl className="kv mt-4">
        <dt>Developer</dt><dd>{p.developer?.fullName || '—'}</dd>
        <dt>Reviewer</dt><dd>{p.reviewerAdmin?.fullName || '—'}</dd>
      </dl>
    </Card>
  );
}

function QuoteCard({ r }) {
  return (
    <div className="card">
      <div className="section-title mb-3">Quote</div>
      <dl className="kv" style={{ gridTemplateColumns: '1fr auto' }}>
        <dt>Total price</dt><dd className="font-medium tabular text-right">{money(r.budget)}</dd>
        <dt>Advance</dt><dd className="tabular text-right">{money(r.advanceAmount)}</dd>
        <dt>Balance on delivery</dt><dd className="tabular text-right">{money(r.remainingAmount ?? (Number(r.budget || 0) - Number(r.advanceAmount || 0)))}</dd>
        <dt>Advance status</dt><dd className="text-right">{r.advancePaymentStatus === 'COMPLETED' ? <span className="text-success font-medium">Paid</span> : r.advancePaymentStatus === 'NOT_REQUIRED' ? 'Not required' : 'Due'}</dd>
      </dl>
    </div>
  );
}

function ActionPanel({ r, user, onDone, hasProject }) {
  const role = user?.role;
  const isOwner = r.user?.id === user?.id;

  if (role === 'USER' && isOwner) return <StudentActions r={r} onDone={onDone} />;
  if (role === 'ADMIN' && r.status === 'SUBMITTED') return <CollegeReview r={r} onDone={onDone} />;
  if (role === 'SUPER_ADMIN') {
    if (r.status === 'SUPER_ADMIN_REVIEW' || r.status === 'SUBMITTED') return <SuperAdminReview r={r} onDone={onDone} />;
    if (r.status === 'ADVANCE_PAYMENT_COMPLETED') return <StartDevelopment r={r} onDone={onDone} />;
    return <SuperAdminIdle r={r} hasProject={hasProject} />;
  }
  return (
    <div className="card">
      <div className="section-title mb-1">Status</div>
      <p className="text-sm">{statusHelp(r.status, role)}</p>
    </div>
  );
}

const statusHelp = (status, role) => ({
  SUBMITTED: role === 'ADMIN' ? '' : 'Waiting for the college administrator to review.',
  SUPER_ADMIN_REVIEW: 'Forwarded to the platform for approval and a quote.',
  ADVANCE_PAYMENT_PENDING: 'Approved. Waiting for the student to pay the advance.',
  ADVANCE_PAYMENT_COMPLETED: 'Advance received. A developer will be assigned next.',
  IN_PROGRESS: 'A developer is working on this project.',
  COMPLETED: 'Delivered to the student.',
  CHANGES_REQUESTED: 'Returned to the student for changes.',
  REJECTED: 'This request was closed.',
  DRAFT: 'The student is still drafting this request.',
}[status] || '');

function StudentActions({ r, onDone }) {
  const navigate = useNavigate();
  const { notify } = useToast();
  const payment = useAsync(() => api.getPaymentConfig(), []);
  const [confirmPay, setConfirmPay] = useState(false);
  const [paying, setPaying] = useState(false);

  const submit = async () => {
    try {
      await api.submitRequirement(r.id);
      notify('Submitted to your college for review.');
      onDone();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };

  const pay = async () => {
    setPaying(true);
    try {
      const res = await api.payRequirementAdvance(r.id);
      notify(res.message, { title: 'Advance paid' });
      setConfirmPay(false);
      onDone();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    } finally {
      setPaying(false);
    }
  };

  if (r.status === 'DRAFT' || r.status === 'CHANGES_REQUESTED') {
    return (
      <div className="card">
        <div className="section-title mb-1">{r.status === 'DRAFT' ? 'Ready to submit?' : 'Update and resubmit'}</div>
        <p className="text-sm mb-4">Your college administrator reviews the request before it goes to the platform.</p>
        <div className="flex flex-col gap-2">
          <AsyncButton className="btn btn-primary btn-block" onClick={submit}><Send /> Submit to college</AsyncButton>
          <button className="btn btn-secondary btn-block" onClick={() => navigate(`/requirements/${r.id}/edit`)}><Pencil /> Edit</button>
        </div>
      </div>
    );
  }
  if (r.status === 'ADVANCE_PAYMENT_PENDING') {
    const pay_ = payment.data || {};
    return (
      <div className="card">
        <div className="section-title mb-1">Approved — pay the advance</div>
        <p className="text-sm">Development starts once the advance is verified.</p>
        <div className="price price-lg mt-3">{money(r.advanceAmount)}</div>
        {pay_.simulation && <div className="mt-2"><span className="notice-simulated"><AlertTriangle size={12} /> Development payment mode</span></div>}
        <button className="btn btn-primary btn-block btn-lg mt-4" onClick={() => setConfirmPay(true)} disabled={pay_.available === false}><Wallet /> Pay advance</button>
        {pay_.available === false && <p className="text-xs text-warning mt-2">Online payments are not configured on this server yet.</p>}
        <ConfirmDialog
          open={confirmPay}
          title="Confirm advance payment"
          confirmLabel={`Pay ${money(r.advanceAmount)}`}
          busy={paying}
          onConfirm={pay}
          onClose={() => setConfirmPay(false)}
          text={`You are paying the advance for "${r.title}". The balance of ${money(r.remainingAmount)} is due after the project passes review.`}
        >
          {pay_.simulation && <Alert tone="warning" title="Simulated payment">No money is charged on this development server.</Alert>}
        </ConfirmDialog>
      </div>
    );
  }
  return (
    <div className="card">
      <div className="section-title mb-1">Status</div>
      <p className="text-sm">{statusHelp(r.status, 'USER') || 'Nothing to do right now.'}</p>
    </div>
  );
}

function CollegeReview({ r, onDone }) {
  const { notify } = useToast();
  const [notes, setNotes] = useState('');
  const act = (action, msg) => async () => {
    if ((action === 'RETURN' || action === 'REJECT') && !notes.trim()) {
      notify('Add a note so the student knows why.', { tone: 'error' });
      return;
    }
    try {
      await api.collegeReviewRequirement(r.id, action, notes.trim() || null);
      notify(msg);
      onDone();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };
  return (
    <div className="card">
      <div className="section-title mb-1">College review</div>
      <p className="text-sm mb-4">Forward feasible requests to the platform for a quote, or return them to the student.</p>
      <Field label="Notes" hint="Required when returning or rejecting">
        <textarea className="textarea" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
      </Field>
      <div className="flex flex-col gap-2">
        <AsyncButton className="btn btn-primary btn-block" onClick={act('FORWARD', 'Forwarded for development approval.')}><Send /> Forward for approval</AsyncButton>
        <AsyncButton className="btn btn-secondary btn-block" onClick={act('RETURN', 'Returned to the student.')}><Undo2 /> Return for changes</AsyncButton>
        <AsyncButton className="btn btn-danger-ghost btn-block" onClick={act('REJECT', 'Requirement rejected.')}><XCircle /> Reject</AsyncButton>
      </div>
    </div>
  );
}

function SuperAdminReview({ r, onDone }) {
  const { notify } = useToast();
  const [total, setTotal] = useState(r.budget ?? '');
  const [advance, setAdvance] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (total !== '' && advance === '') setAdvance(String(Math.round(Number(total) * 0.3)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const approve = async () => {
    const t = Number(total);
    const a = advance === '' ? 0 : Number(advance);
    if (!(t > 0)) return notify('Enter a total price greater than 0.', { tone: 'error' });
    if (Number.isNaN(a) || a < 0 || a > t) return notify('The advance must be between 0 and the total.', { tone: 'error' });
    try {
      await api.superAdminReviewRequirement(r.id, 'APPROVE', { notes: notes || null, budget: t, advanceAmount: a });
      notify(a > 0 ? 'Approved. The student has been asked to pay the advance.' : 'Approved. Ready for developer assignment.');
      onDone();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };
  const other = (action, msg) => async () => {
    if (!notes.trim()) return notify('Add a note explaining the decision.', { tone: 'error' });
    try {
      await api.superAdminReviewRequirement(r.id, action, { notes });
      notify(msg);
      onDone();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };

  return (
    <div className="card">
      <div className="section-title mb-1">Approve and quote</div>
      <p className="text-sm mb-4">{r.status === 'SUBMITTED' ? 'Not yet forwarded by the college. You can still decide directly.' : `Forwarded by ${r.forwardedBy || 'the college'}.`}</p>
      <div className="form-grid">
        <Field label="Total price (INR)"><input className="input" inputMode="decimal" value={total} onChange={(e) => setTotal(e.target.value)} /></Field>
        <Field label="Advance (INR)"><input className="input" inputMode="decimal" value={advance} onChange={(e) => setAdvance(e.target.value)} /></Field>
      </div>
      <Field label="Notes to student"><textarea className="textarea" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} /></Field>
      <div className="flex flex-col gap-2">
        <AsyncButton className="btn btn-primary btn-block" onClick={approve}><CheckCircle2 /> Approve with quote</AsyncButton>
        <AsyncButton className="btn btn-secondary btn-block" onClick={other('REQUEST_CHANGES', 'Changes requested from the student.')}><Undo2 /> Request changes</AsyncButton>
        <AsyncButton className="btn btn-danger-ghost btn-block" onClick={other('REJECT', 'Requirement rejected.')}><XCircle /> Reject</AsyncButton>
      </div>
    </div>
  );
}

function StartDevelopment({ r, onDone }) {
  const { notify } = useToast();
  const devs = useAsync(() => api.getWorkflowDevelopers(), []);
  const reviewers = useAsync(() => api.getWorkflowReviewers(), []);
  const [developerId, setDeveloperId] = useState('');
  const [reviewerId, setReviewerId] = useState('');
  const [notes, setNotes] = useState('');
  const navigate = useNavigate();

  const start = async () => {
    if (!developerId) return notify('Select a developer.', { tone: 'error' });
    try {
      const project = await api.startDevelopment(r.id, Number(developerId), reviewerId ? Number(reviewerId) : null, notes || null);
      notify(`Project ${project.projectCode} created and assigned.`);
      onDone();
      navigate(`/projects/${project.id}`);
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };

  return (
    <div className="card">
      <div className="section-title mb-1">Start development</div>
      <p className="text-sm mb-4">Advance received. Create the project and assign a developer.</p>
      <Field label="Developer">
        <select className="select" value={developerId} onChange={(e) => setDeveloperId(e.target.value)}>
          <option value="">Select a developer</option>
          {(devs.data || []).map((d) => <option key={d.id} value={d.id}>{d.fullName} · {d.activeProjects} active</option>)}
        </select>
      </Field>
      <Field label="Reviewer" hint="Optional. Without one, reviews come to you.">
        <select className="select" value={reviewerId} onChange={(e) => setReviewerId(e.target.value)}>
          <option value="">Review it myself</option>
          {(reviewers.data || []).map((u) => <option key={u.id} value={u.id}>{u.fullName}{u.collegeName ? ` · ${u.collegeName}` : ' · Platform'}</option>)}
        </select>
      </Field>
      <Field label="Notes for the developer"><textarea className="textarea" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Deadline, scope clarifications…" /></Field>
      <AsyncButton className="btn btn-primary btn-block" onClick={start}><UserCog /> Create project and assign</AsyncButton>
      {(devs.data || []).length === 0 && !devs.loading && <p className="text-xs text-warning mt-2">No active developers. Add one under People → Developers.</p>}
    </div>
  );
}

function SuperAdminIdle({ r, hasProject }) {
  const navigate = useNavigate();
  const { notify } = useToast();
  const [confirm, setConfirm] = useState(false);
  const remove = async () => {
    try {
      await api.deleteRequirement(r.id);
      notify('Requirement deleted.');
      navigate('/requirements');
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };
  return (
    <div className="card">
      <div className="section-title mb-1">Status</div>
      <p className="text-sm">{statusHelp(r.status, 'SUPER_ADMIN') || 'No action needed.'}</p>
      {!hasProject && (
        <>
          <button className="btn btn-danger-ghost btn-sm mt-4" onClick={() => setConfirm(true)}><Trash2 /> Delete requirement</button>
          <ConfirmDialog open={confirm} title="Delete this requirement?" text="This cannot be undone." tone="danger" confirmLabel="Delete" onConfirm={remove} onClose={() => setConfirm(false)} />
        </>
      )}
    </div>
  );
}
