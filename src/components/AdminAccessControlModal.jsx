import { useCallback, useEffect, useMemo, useState } from 'react';
import { Check, FolderKanban, IndianRupee, Search, Shield, UserCheck, Users } from 'lucide-react';
import api from '../utils/api';
import { Modal, Tabs, Badge, EmptyState, LoadingBlock, Alert, useToast } from './ui';

const PERMISSION_GROUPS = [
  {
    category: 'User management',
    icon: Users,
    permissions: [
      { key: 'USER_VIEW', label: 'View users directory' },
      { key: 'USER_VIEW_PERSONAL_DATA', label: 'View personal details' },
      { key: 'USER_VIEW_REQUIREMENTS', label: 'View user requirements' },
      { key: 'USER_VIEW_PROJECTS', label: 'View user projects' },
      { key: 'USER_VIEW_ORDERS', label: 'View user orders' },
      { key: 'USER_ONBOARD', label: 'Onboard and bulk create users' },
      { key: 'USER_EDIT', label: 'Edit user information' },
    ],
  },
  {
    category: 'Projects and workspace',
    icon: FolderKanban,
    permissions: [
      { key: 'PROJECT_VIEW', label: 'View projects directory' },
      { key: 'PROJECT_VIEW_DETAILS', label: 'View project specifications' },
      { key: 'PROJECT_VIEW_FILES', label: 'View and download project files' },
      { key: 'PROJECT_REVIEW', label: 'Review deliverables' },
      { key: 'PROJECT_APPROVE', label: 'Approve deliverables for the customer' },
    ],
  },
  {
    category: 'Payments and orders',
    icon: IndianRupee,
    permissions: [
      { key: 'PAYMENT_VIEW', label: 'View payments and invoices' },
      { key: 'PAYMENT_VERIFY', label: 'Verify payment invoices' },
      { key: 'ORDER_VIEW', label: 'View customer orders' },
    ],
  },
];

const DATA_SCOPES = [
  { value: 'GLOBAL', label: 'All records' },
  { value: 'USER_ASSIGNED', label: 'Assigned users only' },
  { value: 'PROJECT_ASSIGNED', label: 'Assigned projects only' },
  { value: 'ASSIGNED_ONLY', label: 'Assigned scope only' },
];

const PRESETS = [
  { value: 'COMPANY_ADMIN', label: 'Company admin' },
  { value: 'ONBOARDING_ADMIN', label: 'Onboarding (user scoped)' },
  { value: 'PROJECT_REVIEWER', label: 'Project reviewer (project scoped)' },
  { value: 'FULL_ADMIN', label: 'Full admin (global)' },
];

export default function AdminAccessControlModal({ admin, isOpen, onClose, onUpdated }) {
  const { notify } = useToast();
  const [permissions, setPermissions] = useState({});
  const [scopes, setScopes] = useState({});
  const [students, setStudents] = useState([]);
  const [assignedUserIds, setAssignedUserIds] = useState([]);
  const [userSearch, setUserSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState('');
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('permissions');

  const adminId = admin?.id;
  const adminCollegeId = admin?.college?.id;

  const loadAdminData = useCallback(async () => {
    if (!adminId) return;
    setLoading(true);
    setLoadError('');
    try {
      const [perms, users, assigned] = await Promise.all([
        api.getAdminPermissions(adminId),
        api.getUsers('', '', 'USER').catch(() => []),
        api.getAssignedUsers(adminId).catch(() => []),
      ]);
      const permMap = {};
      const scopeMap = {};
      (perms || []).forEach((p) => {
        permMap[p.permissionKey] = true;
        scopeMap[p.permissionKey] = p.dataScope || 'GLOBAL';
      });
      setPermissions(permMap);
      setScopes(scopeMap);
      // A college admin can only ever act on students of their own college.
      setStudents((users || []).filter((u) => !adminCollegeId || u.college?.id === adminCollegeId));
      setAssignedUserIds((assigned || []).map((a) => a.assignedUser?.id || a.assignedUserId || a.id).filter(Boolean));
    } catch (err) {
      setLoadError(err.message);
    } finally {
      setLoading(false);
    }
  }, [adminId, adminCollegeId]);

  useEffect(() => {
    if (isOpen && adminId) {
      setActiveTab('permissions');
      setUserSearch('');
      loadAdminData();
    }
  }, [isOpen, adminId, loadAdminData]);

  const filteredStudents = useMemo(() => {
    const q = userSearch.trim().toLowerCase();
    if (!q) return students;
    return students.filter((u) => (u.fullName || '').toLowerCase().includes(q) || (u.email || '').toLowerCase().includes(q));
  }, [students, userSearch]);

  if (!isOpen || !admin) return null;

  const togglePermission = (key) => {
    setPermissions((prev) => ({ ...prev, [key]: !prev[key] }));
    setScopes((prev) => (prev[key] ? prev : { ...prev, [key]: 'GLOBAL' }));
  };

  const toggleUser = (userId) =>
    setAssignedUserIds((prev) => (prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]));

  const applyPreset = async (preset) => {
    setSaving(true);
    try {
      await api.applyAdminPreset(admin.id, preset.value);
      notify(`Applied the ${preset.label.toLowerCase()} preset`);
      await loadAdminData();
      onUpdated?.();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const save = async () => {
    setSaving(true);
    try {
      const payload = Object.keys(permissions)
        .filter((k) => permissions[k])
        .map((k) => ({ permissionKey: k, dataScope: scopes[k] || 'GLOBAL' }));
      await api.updateAdminPermissions(admin.id, payload);
      await api.assignUsersToAdmin(admin.id, assignedUserIds);
      notify('Permissions saved');
      onUpdated?.();
      onClose();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const activeCount = Object.values(permissions).filter(Boolean).length;

  return (
    <Modal
      open
      size="xl"
      onClose={() => !saving && onClose()}
      title="Permissions and scopes"
      description={`${admin.fullName || 'Administrator'} · ${admin.email}${admin.college ? ` · ${admin.college.name}` : ''}`}
      footer={
        <>
          <span className="text-sm text-muted" style={{ marginRight: 'auto', alignSelf: 'center' }}>
            {activeCount} permission{activeCount === 1 ? '' : 's'} enabled · {assignedUserIds.length} assigned student{assignedUserIds.length === 1 ? '' : 's'}
          </span>
          <button type="button" className="btn btn-secondary" onClick={onClose} disabled={saving}>Cancel</button>
          <button type="button" className="btn btn-primary" onClick={save} disabled={saving || loading || Boolean(loadError)}>
            {saving && <span className="spinner" />} Save
          </button>
        </>
      }
    >
      <div className="flex items-center gap-2 flex-wrap mb-4">
        <span className="text-sm text-muted">Presets</span>
        {PRESETS.map((p) => (
          <button key={p.value} type="button" className="btn btn-secondary btn-sm" onClick={() => applyPreset(p)} disabled={saving || loading}>
            {p.label}
          </button>
        ))}
      </div>

      <Tabs
        value={activeTab}
        onChange={setActiveTab}
        tabs={[
          { value: 'permissions', label: 'Permissions', icon: Shield, count: activeCount },
          { value: 'users', label: 'Assigned students', icon: UserCheck, count: assignedUserIds.length },
        ]}
      />

      {loading ? (
        <LoadingBlock label="Loading permissions…" />
      ) : loadError ? (
        <Alert tone="danger" title="Could not load permissions">{loadError}</Alert>
      ) : activeTab === 'permissions' ? (
        <div className="space-y-4">
          {PERMISSION_GROUPS.map((group) => {
            const Icon = group.icon;
            return (
              <section key={group.category} className="surface-muted" style={{ padding: 16 }}>
                <h3 className="section-title flex items-center gap-2 mb-3">
                  <Icon size={16} aria-hidden="true" className="text-muted" /> {group.category}
                </h3>
                <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))' }}>
                  {group.permissions.map((p) => {
                    const checked = Boolean(permissions[p.key]);
                    return (
                      <div
                        key={p.key}
                        className="flex items-center justify-between gap-3 rounded border"
                        style={{ padding: '8px 12px', background: 'var(--surface)', borderColor: checked ? 'var(--accent)' : 'var(--border)' }}
                      >
                        <label className="checkbox flex-1">
                          <input type="checkbox" checked={checked} onChange={() => togglePermission(p.key)} />
                          <span className="min-w-0">
                            <span className="block text-sm font-medium">{p.label}</span>
                            <span className="block text-xs text-subtle font-mono">{p.key}</span>
                          </span>
                        </label>
                        {checked && (
                          <select
                            className="select input-sm"
                            style={{ width: 'auto' }}
                            value={scopes[p.key] || 'GLOBAL'}
                            onChange={(e) => setScopes((prev) => ({ ...prev, [p.key]: e.target.value }))}
                            aria-label={`Scope for ${p.label}`}
                          >
                            {DATA_SCOPES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                          </select>
                        )}
                      </div>
                    );
                  })}
                </div>
              </section>
            );
          })}
        </div>
      ) : (
        <div>
          <div className="flex items-end justify-between gap-3 flex-wrap mb-4">
            <p className="text-sm text-muted" style={{ maxWidth: 480 }}>
              Students {admin.fullName || 'this admin'} may manage when a permission uses the <span className="font-mono">USER_ASSIGNED</span> scope.
              {admin.college ? ` Only students of ${admin.college.name} are listed.` : ''}
            </p>
            <div className="input-with-icon" style={{ minWidth: 240 }}>
              <Search aria-hidden="true" />
              <input className="input" value={userSearch} onChange={(e) => setUserSearch(e.target.value)} placeholder="Search students" />
            </div>
          </div>

          {filteredStudents.length === 0 ? (
            <EmptyState
              icon={Users}
              title={students.length === 0 ? 'No students found' : 'No students match your search'}
              text={students.length === 0 ? 'Students added to this college will appear here.' : undefined}
            />
          ) : (
            <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))' }}>
              {filteredStudents.map((u) => {
                const assigned = assignedUserIds.includes(u.id);
                return (
                  <button
                    key={u.id}
                    type="button"
                    onClick={() => toggleUser(u.id)}
                    aria-pressed={assigned}
                    className="flex items-center justify-between gap-3 rounded border text-left"
                    style={{
                      padding: '10px 12px',
                      background: assigned ? 'var(--accent-soft)' : 'var(--surface)',
                      borderColor: assigned ? 'var(--accent)' : 'var(--border)',
                    }}
                  >
                    <span className="min-w-0">
                      <span className="block text-sm font-medium truncate">{u.fullName || `User #${u.id}`}</span>
                      <span className="block text-xs text-muted truncate">{u.email}</span>
                    </span>
                    {assigned ? <Badge tone="accent"><Check aria-hidden="true" /> Assigned</Badge> : null}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      )}
    </Modal>
  );
}
