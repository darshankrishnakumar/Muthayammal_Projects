import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Building2, Search, Pencil, Share2, UserPlus, MapPin, Mail, Phone } from 'lucide-react';
import { api } from '../utils/api';
import { useAsync } from '../hooks/useAsync';
import {
  PageHeader, EmptyState, ErrorState, SkeletonRows, Badge, Drawer, Field, Spinner, useToast, Avatar, ConfirmDialog,
} from '../components/ui';
import { date } from '../utils/format';

const EMPTY = { name: '', code: '', city: '', state: '', contactEmail: '', contactPhone: '', address: '', active: true };

export default function Colleges() {
  const { notify } = useToast();
  const { data, loading, error, reload } = useAsync(() => api.getColleges(), []);
  const [search, setSearch] = useState('');
  const [editing, setEditing] = useState(null);
  const [viewing, setViewing] = useState(null);
  const [toggling, setToggling] = useState(null);

  const rows = (data || []).filter((c) => {
    const q = search.trim().toLowerCase();
    return !q || c.name.toLowerCase().includes(q) || c.code.toLowerCase().includes(q) || (c.city || '').toLowerCase().includes(q);
  });

  const toggleActive = async () => {
    try {
      await api.setCollegeActive(toggling.id, !toggling.active);
      notify(`${toggling.name} ${toggling.active ? 'deactivated' : 'activated'}.`);
      setToggling(null);
      reload();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };

  return (
    <>
      <PageHeader
        title="Colleges"
        description="Partner colleges, their administrators and the projects allocated to them."
        actions={<button className="btn btn-primary" onClick={() => setEditing('new')}><Plus /> Register college</button>}
      />

      <div className="toolbar">
        <div className="input-with-icon grow" style={{ maxWidth: 420 }}>
          <Search aria-hidden="true" />
          <input className="input" placeholder="Search colleges" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {error ? <ErrorState error={error} onRetry={reload} /> : (
        <div className="card card-flush">
          {loading && !data ? <div className="p-4"><SkeletonRows rows={5} /></div> : rows.length === 0 ? (
            <EmptyState
              icon={Building2}
              title={search ? 'No colleges match' : 'No colleges yet'}
              text={search ? 'Try a different search.' : 'Register a college, create its administrator, then allocate projects to it.'}
              action={!search && <button className="btn btn-primary" onClick={() => setEditing('new')}><Plus /> Register college</button>}
            />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>College</th><th className="hide-lg">Location</th><th className="cell-num hide-md">Admins</th><th className="cell-num">Students</th>
                    <th className="cell-num">Projects</th><th className="cell-num hide-lg">Orders</th><th>Status</th><th />
                  </tr>
                </thead>
                <tbody>
                  {rows.map((c) => (
                    <tr key={c.id} className="is-clickable" onClick={() => setViewing(c)}>
                      <td style={{ minWidth: 240 }}>
                        <div className="font-medium">{c.name}</div>
                        <div className="project-code">{c.code}</div>
                      </td>
                      <td className="cell-muted hide-lg">{[c.city, c.state].filter(Boolean).join(', ') || '—'}</td>
                      <td className="cell-num hide-md">{c.adminCount}</td>
                      <td className="cell-num">{c.studentCount}</td>
                      <td className="cell-num">{c.allocatedProjects}</td>
                      <td className="cell-num hide-lg">{c.orderCount}</td>
                      <td>{c.active ? <Badge tone="success" dot>Active</Badge> : <Badge dot>Inactive</Badge>}</td>
                      <td onClick={(e) => e.stopPropagation()}>
                        <div className="flex gap-1 justify-end">
                          <Link to={`/allocations?college=${c.id}`} className="btn btn-ghost btn-icon btn-sm" title="Allocate projects" aria-label="Allocate projects"><Share2 /></Link>
                          <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setEditing(c)} title="Edit" aria-label={`Edit ${c.name}`}><Pencil /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <CollegeEditor open={editing !== null} college={editing === 'new' ? null : editing} onClose={() => setEditing(null)} onSaved={() => { setEditing(null); reload(); }} />
      <CollegeDetail college={viewing} onClose={() => setViewing(null)} onToggle={(c) => setToggling(c)} onEdit={(c) => { setViewing(null); setEditing(c); }} onChanged={reload} />
      <ConfirmDialog
        open={!!toggling}
        title={toggling?.active ? `Deactivate ${toggling?.name}?` : `Activate ${toggling?.name}?`}
        text={toggling?.active
          ? 'Students and administrators of this college will lose access to the marketplace and purchases until it is reactivated. Existing data is kept.'
          : 'Students and administrators will regain access.'}
        confirmLabel={toggling?.active ? 'Deactivate' : 'Activate'}
        tone={toggling?.active ? 'danger' : 'primary'}
        onConfirm={toggleActive}
        onClose={() => setToggling(null)}
      />
    </>
  );
}

function CollegeEditor({ open, college, onClose, onSaved }) {
  const { notify } = useToast();
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (open) {
      setErrors({});
      setForm(college ? { ...EMPTY, ...Object.fromEntries(Object.keys(EMPTY).map((k) => [k, college[k] ?? EMPTY[k]])) } : EMPTY);
    }
  }, [open, college]);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const save = async () => {
    const e = {};
    if (!form.name.trim()) e.name = 'Name is required.';
    if (!/^[A-Za-z0-9_-]{2,30}$/.test(form.code.trim())) e.code = 'Use 2–30 letters, digits, - or _.';
    if (form.contactEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.contactEmail)) e.contactEmail = 'Enter a valid email.';
    setErrors(e);
    if (Object.keys(e).length) return;
    setSaving(true);
    try {
      if (college) await api.updateCollege(college.id, form);
      else await api.createCollege(form);
      notify(college ? 'College updated.' : 'College registered.');
      onSaved();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title={college ? 'Edit college' : 'Register college'}
      footer={<><button className="btn btn-secondary" onClick={onClose}>Cancel</button><button className="btn btn-primary" onClick={save} disabled={saving}>{saving && <Spinner />} Save</button></>}
    >
      <Field label="College name" error={errors.name}><input className="input" value={form.name} onChange={set('name')} /></Field>
      <div className="form-grid">
        <Field label="Code" error={errors.code} hint="Short unique identifier, e.g. MEC"><input className="input font-mono" value={form.code} onChange={set('code')} style={{ textTransform: 'uppercase' }} /></Field>
        <Field label="City"><input className="input" value={form.city} onChange={set('city')} /></Field>
        <Field label="State"><input className="input" value={form.state} onChange={set('state')} /></Field>
        <Field label="Contact phone"><input className="input" value={form.contactPhone} onChange={set('contactPhone')} /></Field>
        <Field label="Contact email" error={errors.contactEmail} className="span-2"><input className="input" type="email" value={form.contactEmail} onChange={set('contactEmail')} /></Field>
      </div>
      <Field label="Address"><textarea className="textarea" rows={3} value={form.address} onChange={set('address')} /></Field>
    </Drawer>
  );
}

function CollegeDetail({ college, onClose, onToggle, onEdit, onChanged }) {
  const { notify } = useToast();
  const detail = useAsync(() => (college ? api.getCollege(college.id) : Promise.resolve(null)), [college?.id]);
  const [admin, setAdmin] = useState({ fullName: '', email: '', password: '', mobileNumber: '' });
  const [adding, setAdding] = useState(false);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    setShowForm(false);
    setAdmin({ fullName: '', email: '', password: '', mobileNumber: '' });
  }, [college?.id]);

  const createAdmin = async () => {
    if (!admin.fullName.trim() || !admin.email.trim() || admin.password.length < 8) {
      notify('Enter a name, email and a password of at least 8 characters.', { tone: 'error' });
      return;
    }
    setAdding(true);
    try {
      await api.createCollegeAdmin(college.id, admin);
      notify(`Administrator ${admin.email} created.`);
      setShowForm(false);
      setAdmin({ fullName: '', email: '', password: '', mobileNumber: '' });
      detail.reload();
      onChanged();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    } finally {
      setAdding(false);
    }
  };

  const d = detail.data || college || {};
  return (
    <Drawer
      open={!!college}
      onClose={onClose}
      title={d.name}
      description={`${d.code || ''}${d.createdAt ? ` · Registered ${date(d.createdAt)}` : ''}`}
      footer={
        <>
          <button className={`btn ${d.active ? 'btn-danger-ghost' : 'btn-secondary'}`} onClick={() => onToggle(d)}>{d.active ? 'Deactivate' : 'Activate'}</button>
          <span className="ml-auto" />
          <button className="btn btn-secondary" onClick={() => onEdit(d)}><Pencil /> Edit</button>
          <Link to={`/allocations?college=${d.id}`} className="btn btn-primary"><Share2 /> Manage allocations</Link>
        </>
      }
    >
      <div className="grid grid-cols-2 gap-3 mb-6">
        {[['Students', d.studentCount], ['Allocated projects', d.allocatedProjects], ['Requirements', d.requirementCount], ['Orders', d.orderCount]].map(([l, v]) => (
          <div key={l} className="surface-muted p-3">
            <div className="text-xs text-muted">{l}</div>
            <div className="text-xl font-semibold tabular">{v ?? '—'}</div>
          </div>
        ))}
      </div>

      <dl className="kv mb-6">
        <dt>Location</dt><dd className="flex items-center gap-2"><MapPin size={14} className="text-subtle" />{[d.city, d.state].filter(Boolean).join(', ') || '—'}</dd>
        <dt>Contact</dt><dd className="flex items-center gap-2"><Mail size={14} className="text-subtle" />{d.contactEmail || '—'}</dd>
        <dt>Phone</dt><dd className="flex items-center gap-2"><Phone size={14} className="text-subtle" />{d.contactPhone || '—'}</dd>
        {d.address && <><dt>Address</dt><dd>{d.address}</dd></>}
      </dl>

      <div className="section-header">
        <div className="section-title">College administrators</div>
        {!showForm && <button className="btn btn-secondary btn-sm" onClick={() => setShowForm(true)}><UserPlus /> Add administrator</button>}
      </div>

      {showForm && (
        <div className="surface-muted p-4 mb-4">
          <div className="form-grid">
            <Field label="Full name"><input className="input" value={admin.fullName} onChange={(e) => setAdmin({ ...admin, fullName: e.target.value })} /></Field>
            <Field label="Email"><input className="input" type="email" value={admin.email} onChange={(e) => setAdmin({ ...admin, email: e.target.value })} /></Field>
            <Field label="Temporary password" hint="At least 8 characters; ask them to change it"><input className="input" type="password" value={admin.password} onChange={(e) => setAdmin({ ...admin, password: e.target.value })} autoComplete="new-password" /></Field>
            <Field label="Mobile"><input className="input" value={admin.mobileNumber} onChange={(e) => setAdmin({ ...admin, mobileNumber: e.target.value })} /></Field>
          </div>
          <div className="flex justify-end gap-2">
            <button className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}>Cancel</button>
            <button className="btn btn-primary btn-sm" onClick={createAdmin} disabled={adding}>{adding && <Spinner />} Create administrator</button>
          </div>
        </div>
      )}

      {detail.loading ? <SkeletonRows rows={2} /> : (d.admins || []).length === 0 ? (
        <p className="text-sm text-subtle">No administrators yet. Add one so the college can manage its students and requirements.</p>
      ) : (
        <div className="border rounded overflow-hidden">
          {d.admins.map((a) => (
            <div key={a.id} className="list-item">
              <Avatar name={a.fullName} />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm">{a.fullName}</div>
                <div className="text-xs text-subtle truncate">{a.email}</div>
              </div>
              <Badge tone={a.status === 'ACTIVE' ? 'success' : 'neutral'} dot>{a.status === 'ACTIVE' ? 'Active' : 'Inactive'}</Badge>
            </div>
          ))}
        </div>
      )}
    </Drawer>
  );
}
