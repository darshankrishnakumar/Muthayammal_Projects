import { useMemo, useState } from 'react';
import { Code2, FolderKanban, FolderPlus, Layers, Pencil, Power, Search, Trash2, UserPlus } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { useAsync, useDebounced } from '../hooks/useAsync';
import {
  PageHeader, Card, StatCard, Avatar, Badge, StatusBadge, EmptyState, ErrorState, SkeletonRows,
  Modal, Drawer, ConfirmDialog, Field, LoadingBlock, Alert, useToast,
} from '../components/ui';
import { date } from '../utils/format';

const MIN_PASSWORD = 8;
const EMPTY_FORM = { fullName: '', email: '', password: '', phone: '', organization: '', status: 'ACTIVE' };
const isDelivered = (p) => ['ACCESS_GRANTED', 'COMPLETED'].includes(p.lifecycleStatus || p.status);

const projectLabel = (p) => [p.projectCode, p.projectName || p.title || p.name].filter(Boolean).join(' · ') || `Project #${p.id}`;

const DeveloperManagement = () => {
  const { user: currentUser } = useAuth();
  const { notify } = useToast();
  const isSuperAdmin = currentUser?.role === 'SUPER_ADMIN';

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const debouncedSearch = useDebounced(search);

  const devs = useAsync(() => api.getDevelopers(debouncedSearch, statusFilter), [debouncedSearch, statusFilter]);
  const projectsReq = useAsync(() => api.getProjects('', '', 'CUSTOM'), []);
  const developers = useMemo(() => devs.data || [], [devs.data]);
  const customProjects = useMemo(() => projectsReq.data || [], [projectsReq.data]);

  /** Custom projects each developer currently owns, keyed by developer id. */
  const projectsByDev = useMemo(() => {
    const map = {};
    customProjects.forEach((p) => {
      const id = p.developer?.id;
      if (id) (map[id] ||= []).push(p);
    });
    return map;
  }, [customProjects]);

  const activeCount = developers.filter((d) => d.status === 'ACTIVE').length;
  const assignedCount = developers.reduce((n, d) => n + (projectsByDev[d.id]?.length || 0), 0);
  const unassignedProjects = customProjects.filter((p) => !p.developer && !isDelivered(p)).length;

  // Create / edit
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState('');
  const [saving, setSaving] = useState(false);

  // Assign
  const [assignDev, setAssignDev] = useState(null);
  const [assignProjectId, setAssignProjectId] = useState('');
  const [assignError, setAssignError] = useState('');
  const [assigning, setAssigning] = useState(false);

  // Delete / details
  const [deleting, setDeleting] = useState(null);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [detailDev, setDetailDev] = useState(null);
  const detailAssignments = useAsync(
    () => (detailDev ? api.getDeveloperAssignments(detailDev.id) : Promise.resolve([])),
    [detailDev?.id],
  );

  const reloadAll = () => {
    devs.reload();
    projectsReq.reload();
  };

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError('');
    setFormOpen(true);
  };

  const openEdit = (dev) => {
    setEditing(dev);
    setForm({
      fullName: dev.fullName || '',
      email: dev.email || '',
      password: '',
      phone: dev.mobileNumber || dev.phone || '',
      organization: dev.organization || '',
      status: dev.status || 'ACTIVE',
    });
    setFormError('');
    setFormOpen(true);
  };

  const setField = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    if ((!editing || form.password) && form.password.length < MIN_PASSWORD) {
      setFormError(`Password must be at least ${MIN_PASSWORD} characters.`);
      return;
    }
    setSaving(true);
    try {
      const payload = {
        fullName: form.fullName.trim(),
        email: form.email.trim().toLowerCase(),
        phone: form.phone.trim(),
        organization: form.organization.trim(),
        status: form.status,
      };
      if (form.password) payload.password = form.password;
      if (editing) {
        await api.updateDeveloper(editing.id, payload);
        notify(`${payload.fullName} updated`);
      } else {
        await api.createDeveloper(payload);
        notify(`${payload.fullName} added`);
      }
      setFormOpen(false);
      devs.reload();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const toggleStatus = async (dev) => {
    const next = dev.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await api.updateDeveloper(dev.id, { status: next });
      notify(`${dev.fullName} is now ${next === 'ACTIVE' ? 'active' : 'inactive'}`);
      devs.reload();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    }
  };

  const confirmDelete = async () => {
    if (!deleting) return;
    setDeleteBusy(true);
    try {
      await api.deleteDeveloper(deleting.id);
      notify(`${deleting.fullName} deleted`);
      setDeleting(null);
      reloadAll();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setDeleteBusy(false);
    }
  };

  const openAssign = (dev) => {
    setAssignDev(dev);
    setAssignProjectId('');
    setAssignError('');
  };

  const assignableProjects = customProjects.filter((p) => !isDelivered(p));

  const handleAssign = async (e) => {
    e.preventDefault();
    if (!assignProjectId) {
      setAssignError('Select a project.');
      return;
    }
    setAssigning(true);
    setAssignError('');
    try {
      await api.assignDeveloperToProject(assignProjectId, assignDev.id);
      notify(`Assigned to ${assignDev.fullName}`);
      setAssignDev(null);
      reloadAll();
    } catch (err) {
      setAssignError(err.message);
    } finally {
      setAssigning(false);
    }
  };

  /** Owned custom projects plus any manual assignment records, de-duplicated by project id. */
  const detailProjects = useMemo(() => {
    if (!detailDev) return [];
    const byId = new Map();
    (projectsByDev[detailDev.id] || []).forEach((p) => byId.set(p.id, { project: p, source: 'Developer' }));
    (detailAssignments.data || []).forEach((a) => {
      const p = a.project;
      if (p && !byId.has(p.id)) byId.set(p.id, { project: p, source: a.active === false ? 'Inactive grant' : 'Access grant', assignedAt: a.assignedAt });
    });
    return [...byId.values()];
  }, [detailDev, projectsByDev, detailAssignments.data]);

  if (!isSuperAdmin) {
    return <ErrorState error={{ status: 403, message: 'Only the Super Admin can manage developers.' }} />;
  }

  const filtersActive = Boolean(search || statusFilter);

  return (
    <>
      <PageHeader
        title="Developers"
        description="Developer accounts and the custom projects they are building."
        actions={
          <button type="button" className="btn btn-primary" onClick={openCreate}>
            <UserPlus aria-hidden="true" /> Add developer
          </button>
        }
      />

      <div className="stat-grid mb-6">
        <StatCard label="Developers" value={developers.length} icon={Code2} hint={`${activeCount} active`} loading={devs.loading && !devs.data} />
        <StatCard label="Assigned projects" value={assignedCount} icon={FolderKanban} tone="accent" index={1} loading={projectsReq.loading && !projectsReq.data} />
        <StatCard label="Awaiting a developer" value={unassignedProjects} icon={Layers} tone={unassignedProjects ? 'warning' : undefined} index={2} hint="Custom projects without a developer" loading={projectsReq.loading && !projectsReq.data} />
      </div>

      {projectsReq.error && (
        <Alert tone="warning" title="Custom projects could not be loaded">{projectsReq.error.message}</Alert>
      )}

      <div className="toolbar">
        <div className="input-with-icon grow">
          <Search aria-hidden="true" />
          <input className="input" placeholder="Search by name or email" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <select className="select" style={{ width: 160 }} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} aria-label="Status">
          <option value="">All statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
        </select>
      </div>

      {devs.error ? (
        <ErrorState error={devs.error} onRetry={devs.reload} />
      ) : (
        <Card flush>
          {devs.loading && !devs.data ? (
            <div className="p-4"><SkeletonRows rows={5} /></div>
          ) : developers.length === 0 ? (
            <EmptyState
              icon={Code2}
              title={filtersActive ? 'No developers match these filters' : 'No developers yet'}
              text={filtersActive ? 'Try a different search or status.' : 'Add a developer to start assigning custom projects.'}
              action={!filtersActive && (
                <button type="button" className="btn btn-primary" onClick={openCreate}><UserPlus aria-hidden="true" /> Add developer</button>
              )}
            />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Developer</th>
                    <th>Organization</th>
                    <th>Projects</th>
                    <th>Status</th>
                    <th>Joined</th>
                    <th className="text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {developers.map((dev) => {
                    const owned = projectsByDev[dev.id] || [];
                    return (
                      <tr key={dev.id}>
                        <td>
                          <div className="flex items-center gap-3">
                            <Avatar name={dev.fullName} />
                            <div className="min-w-0">
                              <div className="font-medium">{dev.fullName}</div>
                              <div className="text-sm text-muted">{dev.email}</div>
                            </div>
                          </div>
                        </td>
                        <td className="cell-muted">{dev.organization || '—'}</td>
                        <td>
                          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setDetailDev(dev)}>
                            {owned.length ? <Badge tone="accent">{owned.length}</Badge> : <Badge>0</Badge>}
                            View
                          </button>
                        </td>
                        <td><StatusBadge status={dev.status} /></td>
                        <td className="cell-muted nowrap">{date(dev.createdAt)}</td>
                        <td>
                          <div className="flex items-center justify-end gap-1">
                            <button type="button" className="btn btn-secondary btn-sm" onClick={() => openAssign(dev)} disabled={dev.status !== 'ACTIVE'}>
                              <FolderPlus aria-hidden="true" /> Assign
                            </button>
                            <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => openEdit(dev)} title="Edit" aria-label="Edit">
                              <Pencil aria-hidden="true" />
                            </button>
                            <button
                              type="button"
                              className="btn btn-ghost btn-icon btn-sm"
                              onClick={() => toggleStatus(dev)}
                              title={dev.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                              aria-label={dev.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                            >
                              <Power aria-hidden="true" />
                            </button>
                            <button type="button" className="btn btn-danger-ghost btn-icon btn-sm" onClick={() => setDeleting(dev)} title="Delete" aria-label="Delete">
                              <Trash2 aria-hidden="true" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      <Modal
        open={formOpen}
        onClose={() => !saving && setFormOpen(false)}
        title={editing ? 'Edit developer' : 'Add developer'}
        description={editing ? editing.email : 'The developer can sign in immediately with this password.'}
        footer={
          <>
            <button type="button" className="btn btn-secondary" onClick={() => setFormOpen(false)} disabled={saving}>Cancel</button>
            <button type="submit" form="developer-form" className="btn btn-primary" disabled={saving}>
              {saving && <span className="spinner" />} {editing ? 'Save changes' : 'Add developer'}
            </button>
          </>
        }
      >
        <form id="developer-form" onSubmit={handleSubmit}>
          {formError && <div className="alert alert-danger">{formError}</div>}
          <div className="form-grid">
            <Field label="Full name" htmlFor="dev-name" className="span-2">
              <input id="dev-name" name="fullName" className="input" value={form.fullName} onChange={setField} required autoComplete="off" />
            </Field>
            <Field label="Email" htmlFor="dev-email">
              <input id="dev-email" name="email" type="email" className="input" value={form.email} onChange={setField} required autoComplete="off" />
            </Field>
            <Field label="Phone" htmlFor="dev-phone">
              <input id="dev-phone" name="phone" type="tel" className="input" value={form.phone} onChange={setField} placeholder="Optional" />
            </Field>
            <Field label="Organization or team" htmlFor="dev-org" className="span-2">
              <input id="dev-org" name="organization" className="input" value={form.organization} onChange={setField} placeholder="Optional" />
            </Field>
            <Field
              label="Password"
              htmlFor="dev-password"
              hint={editing ? 'Leave blank to keep the current password.' : `At least ${MIN_PASSWORD} characters.`}
            >
              <input
                id="dev-password"
                name="password"
                type="password"
                className="input"
                value={form.password}
                onChange={setField}
                required={!editing}
                minLength={MIN_PASSWORD}
                autoComplete="new-password"
              />
            </Field>
            <Field label="Status" htmlFor="dev-status">
              <select id="dev-status" name="status" className="select" value={form.status} onChange={setField}>
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
              </select>
            </Field>
          </div>
        </form>
      </Modal>

      <Modal
        open={Boolean(assignDev)}
        onClose={() => !assigning && setAssignDev(null)}
        title="Assign a custom project"
        description={assignDev ? `${assignDev.fullName} · ${assignDev.email}` : ''}
        footer={
          <>
            <button type="button" className="btn btn-secondary" onClick={() => setAssignDev(null)} disabled={assigning}>Cancel</button>
            <button type="submit" form="assign-form" className="btn btn-primary" disabled={assigning || !assignProjectId}>
              {assigning && <span className="spinner" />} Assign
            </button>
          </>
        }
      >
        <form id="assign-form" onSubmit={handleAssign}>
          {assignError && <div className="alert alert-danger">{assignError}</div>}
          <Field
            label="Project"
            htmlFor="assign-project"
            hint="Assigning replaces the project's current developer and resets it to awaiting acceptance."
          >
            <select
              id="assign-project"
              className="select"
              value={assignProjectId}
              onChange={(e) => setAssignProjectId(e.target.value)}
              disabled={projectsReq.loading}
              required
            >
              <option value="">{projectsReq.loading ? 'Loading projects…' : 'Select a project'}</option>
              {assignableProjects.map((p) => (
                <option key={p.id} value={p.id} disabled={p.developer?.id === assignDev?.id}>
                  {projectLabel(p)}
                  {p.developer ? ` — ${p.developer.id === assignDev?.id ? 'already assigned' : `currently ${p.developer.fullName}`}` : ' — unassigned'}
                </option>
              ))}
            </select>
          </Field>
          {!projectsReq.loading && assignableProjects.length === 0 && (
            <p className="text-sm text-muted">There are no open custom projects. Projects are created when a requirement is approved and paid.</p>
          )}
        </form>
      </Modal>

      <Drawer
        open={Boolean(detailDev)}
        onClose={() => setDetailDev(null)}
        title={detailDev?.fullName || ''}
        description={detailDev?.email}
        footer={detailDev && (
          <button type="button" className="btn btn-primary" onClick={() => { const d = detailDev; setDetailDev(null); openAssign(d); }} disabled={detailDev.status !== 'ACTIVE'}>
            <FolderPlus aria-hidden="true" /> Assign project
          </button>
        )}
      >
        {detailAssignments.loading ? (
          <LoadingBlock label="Loading projects…" />
        ) : detailAssignments.error ? (
          <Alert tone="danger" title="Could not load assignments">{detailAssignments.error.message}</Alert>
        ) : detailProjects.length === 0 ? (
          <EmptyState icon={FolderKanban} title="No projects yet" text="Assign a custom project to get this developer started." />
        ) : (
          <div className="list border rounded">
            {detailProjects.map(({ project: p, source }) => (
              <Link key={p.id} to={`/projects/${p.id}`} className="list-item" style={{ color: 'inherit', textDecoration: 'none' }}>
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{p.projectName || p.title || `Project #${p.id}`}</div>
                  <div className="text-xs text-subtle">{[p.projectCode, source].filter(Boolean).join(' · ')}</div>
                </div>
                <StatusBadge status={p.status} />
              </Link>
            ))}
          </div>
        )}
      </Drawer>

      <ConfirmDialog
        open={Boolean(deleting)}
        title="Delete developer"
        text={deleting ? `${deleting.fullName} will lose access to every project. Reassign their open projects first.` : ''}
        confirmLabel="Delete"
        tone="danger"
        busy={deleteBusy}
        onConfirm={confirmDelete}
        onClose={() => !deleteBusy && setDeleting(null)}
      />
    </>
  );
};

export default DeveloperManagement;
