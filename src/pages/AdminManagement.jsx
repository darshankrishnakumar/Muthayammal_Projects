import { useMemo, useState } from 'react';
import { Pencil, Power, Search, Shield, ShieldCheck, Trash2, UserPlus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { useAsync, useDebounced } from '../hooks/useAsync';
import AdminAccessControlModal from '../components/AdminAccessControlModal';
import {
  PageHeader, Card, Avatar, Badge, StatusBadge, EmptyState, ErrorState, SkeletonRows,
  Modal, ConfirmDialog, Field, useToast,
} from '../components/ui';
import { date } from '../utils/format';

const MIN_PASSWORD = 8;
const EMPTY_FORM = { fullName: '', email: '', password: '', collegeId: '', status: 'ACTIVE' };

const AdminManagement = () => {
  const { user: currentUser } = useAuth();
  const { notify } = useToast();

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const debouncedSearch = useDebounced(search);

  const { data, loading, error, reload } = useAsync(
    () => api.getAdmins(debouncedSearch, statusFilter),
    [debouncedSearch, statusFilter],
  );
  const admins = data || [];

  const colleges = useAsync(() => api.getColleges(), []);
  const collegeOptions = useMemo(
    () => (colleges.data || []).slice().sort((a, b) => (a.name || '').localeCompare(b.name || '')),
    [colleges.data],
  );

  // Create / edit
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState('');
  const [saving, setSaving] = useState(false);

  // Delete / access control
  const [deleting, setDeleting] = useState(null);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [accessAdmin, setAccessAdmin] = useState(null);

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError('');
    setFormOpen(true);
  };

  const openEdit = (admin) => {
    setEditing(admin);
    setForm({
      fullName: admin.fullName || '',
      email: admin.email || '',
      password: '',
      collegeId: admin.college?.id ? String(admin.college.id) : '',
      status: admin.status || 'ACTIVE',
    });
    setFormError('');
    setFormOpen(true);
  };

  const setField = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    if (!form.collegeId) {
      setFormError('Select the college this administrator manages.');
      return;
    }
    if ((!editing || form.password) && form.password.length < MIN_PASSWORD) {
      setFormError(`Password must be at least ${MIN_PASSWORD} characters.`);
      return;
    }
    setSaving(true);
    try {
      const payload = {
        fullName: form.fullName.trim(),
        email: form.email.trim().toLowerCase(),
        status: form.status,
        collegeId: String(form.collegeId),
      };
      if (form.password) payload.password = form.password;
      if (editing) {
        await api.updateAdmin(editing.id, payload);
        notify(`${payload.fullName} updated`);
      } else {
        await api.createAdmin(payload);
        notify(`${payload.fullName} added as a college admin`);
      }
      setFormOpen(false);
      reload();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const toggleStatus = async (admin) => {
    const next = admin.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await api.updateAdmin(admin.id, { status: next });
      notify(`${admin.fullName} is now ${next === 'ACTIVE' ? 'active' : 'inactive'}`);
      reload();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    }
  };

  const confirmDelete = async () => {
    if (!deleting) return;
    setDeleteBusy(true);
    try {
      await api.deleteAdmin(deleting.id);
      notify(`${deleting.fullName} deleted`);
      setDeleting(null);
      reload();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setDeleteBusy(false);
    }
  };

  if (currentUser?.role !== 'SUPER_ADMIN') {
    return <ErrorState error={{ status: 403, message: 'Only the Super Admin can manage college administrators.' }} />;
  }

  return (
    <>
      <PageHeader
        title="College admins"
        description="Administrators manage students and review requirements for their own college."
        actions={
          <button type="button" className="btn btn-primary" onClick={openCreate}>
            <UserPlus aria-hidden="true" /> Add admin
          </button>
        }
      />

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

      {error ? (
        <ErrorState error={error} onRetry={reload} />
      ) : (
        <Card flush>
          {loading && !data ? (
            <div className="p-4"><SkeletonRows rows={5} /></div>
          ) : admins.length === 0 ? (
            <EmptyState
              icon={ShieldCheck}
              title={search || statusFilter ? 'No admins match these filters' : 'No college admins yet'}
              text={search || statusFilter ? 'Try a different search or status.' : 'Add an administrator for each college you onboard.'}
              action={!search && !statusFilter && (
                <button type="button" className="btn btn-primary" onClick={openCreate}><UserPlus aria-hidden="true" /> Add admin</button>
              )}
            />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Administrator</th>
                    <th>College</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th className="text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {admins.map((a) => {
                    const isSelf = currentUser?.id === a.id;
                    return (
                      <tr key={a.id}>
                        <td>
                          <div className="flex items-center gap-3">
                            <Avatar name={a.fullName} />
                            <div className="min-w-0">
                              <div className="font-medium flex items-center gap-2">
                                {a.fullName}
                                {isSelf && <Badge tone="accent">You</Badge>}
                              </div>
                              <div className="text-sm text-muted">{a.email}</div>
                            </div>
                          </div>
                        </td>
                        <td>
                          {a.college ? (
                            <>
                              <div>{a.college.name}</div>
                              {a.college.code && <div className="text-xs text-subtle font-mono">{a.college.code}</div>}
                            </>
                          ) : (
                            <Badge tone="warning">No college</Badge>
                          )}
                        </td>
                        <td><StatusBadge status={a.status} /></td>
                        <td className="cell-muted nowrap">{date(a.createdAt)}</td>
                        <td>
                          <div className="flex items-center justify-end gap-1">
                            <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setAccessAdmin(a)} title="Permissions and scopes" aria-label="Permissions and scopes">
                              <Shield aria-hidden="true" />
                            </button>
                            <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => openEdit(a)} title="Edit" aria-label="Edit">
                              <Pencil aria-hidden="true" />
                            </button>
                            <button
                              type="button"
                              className="btn btn-ghost btn-icon btn-sm"
                              onClick={() => toggleStatus(a)}
                              disabled={isSelf}
                              title={a.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                              aria-label={a.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                            >
                              <Power aria-hidden="true" />
                            </button>
                            <button
                              type="button"
                              className="btn btn-danger-ghost btn-icon btn-sm"
                              onClick={() => setDeleting(a)}
                              disabled={isSelf || a.role === 'SUPER_ADMIN'}
                              title="Delete"
                              aria-label="Delete"
                            >
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
        title={editing ? 'Edit college admin' : 'Add college admin'}
        description={editing ? editing.email : 'The administrator can sign in immediately with this password.'}
        footer={
          <>
            <button type="button" className="btn btn-secondary" onClick={() => setFormOpen(false)} disabled={saving}>Cancel</button>
            <button type="submit" form="admin-form" className="btn btn-primary" disabled={saving}>
              {saving && <span className="spinner" />} {editing ? 'Save changes' : 'Add admin'}
            </button>
          </>
        }
      >
        <form id="admin-form" onSubmit={handleSubmit}>
          {formError && <div className="alert alert-danger">{formError}</div>}
          <Field label="Full name" htmlFor="admin-name">
            <input id="admin-name" name="fullName" className="input" value={form.fullName} onChange={setField} required autoComplete="off" />
          </Field>
          <Field label="Email" htmlFor="admin-email">
            <input id="admin-email" name="email" type="email" className="input" value={form.email} onChange={setField} required autoComplete="off" />
          </Field>
          <Field
            label="College"
            htmlFor="admin-college"
            error={colleges.error ? `Could not load colleges: ${colleges.error.message}` : undefined}
            hint={!colleges.loading && collegeOptions.length === 0 ? 'Create a college first.' : undefined}
          >
            <select id="admin-college" name="collegeId" className="select" value={form.collegeId} onChange={setField} required disabled={colleges.loading}>
              <option value="">{colleges.loading ? 'Loading colleges…' : 'Select a college'}</option>
              {collegeOptions.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}{c.code ? ` (${c.code})` : ''}{c.active === false ? ' — inactive' : ''}
                </option>
              ))}
            </select>
          </Field>
          <div className="form-grid">
            <Field
              label="Password"
              htmlFor="admin-password"
              hint={editing ? 'Leave blank to keep the current password.' : `At least ${MIN_PASSWORD} characters.`}
            >
              <input
                id="admin-password"
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
            <Field label="Status" htmlFor="admin-status">
              <select id="admin-status" name="status" className="select" value={form.status} onChange={setField}>
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
              </select>
            </Field>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={Boolean(deleting)}
        title="Delete college admin"
        text={deleting ? `${deleting.fullName} will lose administrative access immediately.` : ''}
        confirmLabel="Delete"
        tone="danger"
        busy={deleteBusy}
        onConfirm={confirmDelete}
        onClose={() => !deleteBusy && setDeleting(null)}
      />

      <AdminAccessControlModal
        admin={accessAdmin}
        isOpen={Boolean(accessAdmin)}
        onClose={() => setAccessAdmin(null)}
        onUpdated={reload}
      />
    </>
  );
};

export default AdminManagement;
