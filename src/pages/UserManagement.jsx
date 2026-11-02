import { useMemo, useState } from 'react';
import { GraduationCap, Pencil, Power, Search, Trash2, UserPlus, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { useAsync, useDebounced } from '../hooks/useAsync';
import BulkUserCreateModal from '../components/BulkUserCreateModal';
import {
  PageHeader, Card, Avatar, Badge, StatusBadge, EmptyState, ErrorState, SkeletonRows,
  Modal, ConfirmDialog, Field, Alert, useToast,
} from '../components/ui';
import { ROLE_LABELS, date } from '../utils/format';

const MIN_PASSWORD = 8;
const ASSIGNABLE_ROLES = ['USER', 'ADMIN', 'PROJECT_DEVELOPER'];
const EMPTY_FORM = { fullName: '', email: '', mobileNumber: '', password: '', status: 'ACTIVE', role: 'USER', collegeId: '' };

const UserManagement = () => {
  const { user: currentUser } = useAuth();
  const { notify } = useToast();
  const isSuperAdmin = currentUser?.role === 'SUPER_ADMIN';
  const isAdmin = currentUser?.role === 'ADMIN';
  const ownCollege = currentUser?.college;

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [collegeFilter, setCollegeFilter] = useState('');
  const debouncedSearch = useDebounced(search);

  // Super Admin: every student platform-wide. College admin: the server scopes to their college.
  const { data, loading, error, reload } = useAsync(
    () => api.getUsers(debouncedSearch, statusFilter, isSuperAdmin ? 'USER' : ''),
    [debouncedSearch, statusFilter, isSuperAdmin],
  );
  const allUsers = useMemo(() => data || [], [data]);
  const users = useMemo(
    () => (collegeFilter ? allUsers.filter((u) => String(u.college?.id) === collegeFilter) : allUsers),
    [allUsers, collegeFilter],
  );

  const colleges = useAsync(() => (isSuperAdmin ? api.getColleges() : Promise.resolve([])), [isSuperAdmin]);
  const collegeOptions = useMemo(
    () => (colleges.data || []).slice().sort((a, b) => (a.name || '').localeCompare(b.name || '')),
    [colleges.data],
  );

  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState('');
  const [saving, setSaving] = useState(false);
  const [bulkOpen, setBulkOpen] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [deleteBusy, setDeleteBusy] = useState(false);

  const canModify = (u) => isSuperAdmin || (isAdmin && u.role === 'USER');

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError('');
    setFormOpen(true);
  };

  const openEdit = (u) => {
    setEditing(u);
    setForm({
      fullName: u.fullName || '',
      email: u.email || '',
      mobileNumber: u.mobileNumber || '',
      password: '',
      status: u.status || 'ACTIVE',
      role: u.role || 'USER',
      collegeId: u.college?.id ? String(u.college.id) : '',
    });
    setFormError('');
    setFormOpen(true);
  };

  const setField = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  const roleNeedsCollege = form.role === 'USER' || form.role === 'ADMIN';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    if ((!editing || form.password) && form.password.length < MIN_PASSWORD) {
      setFormError(`Password must be at least ${MIN_PASSWORD} characters.`);
      return;
    }
    if (isSuperAdmin && roleNeedsCollege && !form.collegeId) {
      setFormError('Select a college.');
      return;
    }
    setSaving(true);
    try {
      const base = {
        fullName: form.fullName.trim(),
        email: form.email.trim().toLowerCase(),
        mobileNumber: form.mobileNumber.trim(),
        status: form.status,
      };
      if (form.password) base.password = form.password;

      if (editing) {
        await api.updateUser(editing.id, base);
        const roleChanged = isSuperAdmin && form.role !== editing.role;
        const collegeChanged = isSuperAdmin && roleNeedsCollege && form.collegeId !== String(editing.college?.id ?? '');
        if (roleChanged || collegeChanged) {
          await api.updateUserRole(editing.id, form.role, roleNeedsCollege ? String(form.collegeId) : null);
        }
        notify(roleChanged ? `${base.fullName} is now ${ROLE_LABELS[form.role] || form.role}` : `${base.fullName} updated`);
      } else {
        const payload = { ...base, role: 'USER' };
        if (isSuperAdmin) payload.collegeId = String(form.collegeId);
        await api.createUser(payload);
        notify(`${base.fullName} added`);
      }
      setFormOpen(false);
      reload();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const toggleStatus = async (u) => {
    const next = u.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await api.updateUser(u.id, { status: next });
      notify(`${u.fullName} is now ${next === 'ACTIVE' ? 'active' : 'inactive'}`);
      reload();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    }
  };

  const confirmDelete = async () => {
    if (!deleting) return;
    setDeleteBusy(true);
    try {
      await api.deleteUser(deleting.id);
      notify(`${deleting.fullName} deleted`);
      setDeleting(null);
      reload();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setDeleteBusy(false);
    }
  };

  const filtersActive = Boolean(search || statusFilter || collegeFilter);

  return (
    <>
      <PageHeader
        title="Students"
        description={
          isSuperAdmin
            ? 'Student accounts across every college.'
            : `Student accounts at ${ownCollege?.name || 'your college'}.`
        }
        actions={
          <>
            <button type="button" className="btn btn-secondary" onClick={() => setBulkOpen(true)}>
              <Users aria-hidden="true" /> Bulk create
            </button>
            <button type="button" className="btn btn-primary" onClick={openCreate}>
              <UserPlus aria-hidden="true" /> Add student
            </button>
          </>
        }
      />

      {isAdmin && !ownCollege && (
        <Alert tone="warning" title="Your account is not linked to a college">
          Ask the Super Admin to assign your college before managing students.
        </Alert>
      )}

      <div className="toolbar">
        <div className="input-with-icon grow">
          <Search aria-hidden="true" />
          <input className="input" placeholder="Search by name or email" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        {isSuperAdmin && (
          <select className="select" style={{ width: 220 }} value={collegeFilter} onChange={(e) => setCollegeFilter(e.target.value)} aria-label="College">
            <option value="">All colleges</option>
            {collegeOptions.map((c) => <option key={c.id} value={String(c.id)}>{c.name}</option>)}
          </select>
        )}
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
            <div className="p-4"><SkeletonRows rows={6} /></div>
          ) : users.length === 0 ? (
            <EmptyState
              icon={GraduationCap}
              title={filtersActive ? 'No students match these filters' : 'No students yet'}
              text={filtersActive ? 'Try a different search, college or status.' : 'Add students one at a time or upload a CSV.'}
              action={!filtersActive && (
                <button type="button" className="btn btn-primary" onClick={openCreate}><UserPlus aria-hidden="true" /> Add student</button>
              )}
            />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>College</th>
                    {isSuperAdmin && <th>Role</th>}
                    <th>Status</th>
                    <th>Created</th>
                    <th className="text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => {
                    const modifiable = canModify(u);
                    const isSelf = currentUser?.id === u.id;
                    return (
                      <tr key={u.id}>
                        <td>
                          <div className="flex items-center gap-3">
                            <Avatar name={u.fullName} />
                            <div className="min-w-0">
                              <div className="font-medium flex items-center gap-2">
                                {u.fullName}
                                {isSelf && <Badge tone="accent">You</Badge>}
                              </div>
                              <div className="text-sm text-muted">{u.email}</div>
                            </div>
                          </div>
                        </td>
                        <td>
                          {u.college ? (
                            <>
                              <div>{u.college.name}</div>
                              {u.college.code && <div className="text-xs text-subtle font-mono">{u.college.code}</div>}
                            </>
                          ) : (
                            <span className="text-subtle">—</span>
                          )}
                        </td>
                        {isSuperAdmin && <td><Badge>{ROLE_LABELS[u.role] || u.role}</Badge></td>}
                        <td><StatusBadge status={u.status} /></td>
                        <td className="cell-muted nowrap">{date(u.createdAt)}</td>
                        <td>
                          <div className="flex items-center justify-end gap-1">
                            <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => openEdit(u)} disabled={!modifiable} title="Edit" aria-label="Edit">
                              <Pencil aria-hidden="true" />
                            </button>
                            <button
                              type="button"
                              className="btn btn-ghost btn-icon btn-sm"
                              onClick={() => toggleStatus(u)}
                              disabled={!modifiable || isSelf}
                              title={u.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                              aria-label={u.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                            >
                              <Power aria-hidden="true" />
                            </button>
                            <button
                              type="button"
                              className="btn btn-danger-ghost btn-icon btn-sm"
                              onClick={() => setDeleting(u)}
                              disabled={!modifiable || isSelf}
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
        title={editing ? 'Edit account' : 'Add student'}
        description={editing ? editing.email : 'The student can sign in immediately with this password.'}
        footer={
          <>
            <button type="button" className="btn btn-secondary" onClick={() => setFormOpen(false)} disabled={saving}>Cancel</button>
            <button type="submit" form="user-form" className="btn btn-primary" disabled={saving}>
              {saving && <span className="spinner" />} {editing ? 'Save changes' : 'Add student'}
            </button>
          </>
        }
      >
        <form id="user-form" onSubmit={handleSubmit}>
          {formError && <div className="alert alert-danger">{formError}</div>}
          <div className="form-grid">
            <Field label="Full name" htmlFor="user-name" className="span-2">
              <input id="user-name" name="fullName" className="input" value={form.fullName} onChange={setField} required autoComplete="off" />
            </Field>
            <Field label="Email" htmlFor="user-email">
              <input id="user-email" name="email" type="email" className="input" value={form.email} onChange={setField} required autoComplete="off" />
            </Field>
            <Field label="Mobile number" htmlFor="user-mobile">
              <input id="user-mobile" name="mobileNumber" type="tel" className="input" value={form.mobileNumber} onChange={setField} placeholder="Optional" />
            </Field>

            {isSuperAdmin && editing && (
              <Field label="Role" htmlFor="user-role" hint={editing.id === currentUser?.id ? 'You cannot change your own role.' : undefined}>
                <select id="user-role" name="role" className="select" value={form.role} onChange={setField} disabled={editing.id === currentUser?.id}>
                  {ASSIGNABLE_ROLES.map((r) => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
                </select>
              </Field>
            )}

            {isSuperAdmin ? (
              roleNeedsCollege && (
                <Field
                  label="College"
                  htmlFor="user-college"
                  className={editing ? '' : 'span-2'}
                  error={colleges.error ? `Could not load colleges: ${colleges.error.message}` : undefined}
                >
                  <select id="user-college" name="collegeId" className="select" value={form.collegeId} onChange={setField} required disabled={colleges.loading}>
                    <option value="">{colleges.loading ? 'Loading colleges…' : 'Select a college'}</option>
                    {collegeOptions.map((c) => (
                      <option key={c.id} value={String(c.id)}>{c.name}{c.code ? ` (${c.code})` : ''}</option>
                    ))}
                  </select>
                </Field>
              )
            ) : (
              <Field label="College" className="span-2">
                <input className="input" value={ownCollege?.name || 'Your college'} disabled readOnly />
              </Field>
            )}

            <Field
              label="Password"
              htmlFor="user-password"
              hint={editing ? 'Leave blank to keep the current password.' : `At least ${MIN_PASSWORD} characters.`}
            >
              <input
                id="user-password"
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
            <Field label="Status" htmlFor="user-status">
              <select id="user-status" name="status" className="select" value={form.status} onChange={setField} disabled={editing?.id === currentUser?.id}>
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
              </select>
            </Field>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={Boolean(deleting)}
        title="Delete account"
        text={deleting ? `${deleting.fullName} will no longer be able to sign in.` : ''}
        confirmLabel="Delete"
        tone="danger"
        busy={deleteBusy}
        onConfirm={confirmDelete}
        onClose={() => !deleteBusy && setDeleting(null)}
      />

      <BulkUserCreateModal
        isOpen={bulkOpen}
        onClose={() => setBulkOpen(false)}
        onSuccess={reload}
        existingUsers={allUsers}
        colleges={collegeOptions}
      />
    </>
  );
};

export default UserManagement;
