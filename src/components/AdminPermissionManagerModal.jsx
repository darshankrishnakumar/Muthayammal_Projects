import { useCallback, useEffect, useState } from 'react';
import { Lock, Plus, ShieldCheck, Trash2, Unlock, UserCheck } from 'lucide-react';
import { api } from '../utils/api';
import { Modal, Tabs, Badge, EmptyState, Alert, Field, SkeletonRows, useToast } from './ui';
import { ROLE_LABELS } from '../utils/format';

const RULE_ROLES = ['USER', 'ADMIN', 'PROJECT_DEVELOPER'];

const StatusPill = ({ status }) =>
  status === 'ALLOWED'
    ? <Badge tone="success"><Unlock aria-hidden="true" /> Allowed</Badge>
    : <Badge tone="danger"><Lock aria-hidden="true" /> Restricted</Badge>;

/**
 * Folder and file access overrides. Super Admin only: the explorer never renders this for anyone else,
 * and the permission endpoints reject other roles.
 */
const AdminPermissionManagerModal = ({ folder, asset, usersList, onClose, onPermissionUpdated }) => {
  const { notify } = useToast();
  const [activeTab, setActiveTab] = useState(asset ? 'file' : 'folder');
  const [folderPermissions, setFolderPermissions] = useState([]);
  const [filePermissions, setFilePermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [busy, setBusy] = useState(false);

  const [users, setUsers] = useState(usersList || []);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [targetStatus, setTargetStatus] = useState('ALLOWED');

  useEffect(() => {
    if (usersList?.length) {
      setUsers(usersList);
      return;
    }
    api.getUsers().then((data) => setUsers(data || [])).catch(() => setUsers([]));
  }, [usersList]);

  const folderId = folder?.id;
  const assetId = asset?.id;

  const fetchPermissions = useCallback(async () => {
    setLoading(true);
    setLoadError('');
    try {
      const [fPerms, aPerms] = await Promise.all([
        folderId ? api.getFolderPermissions(folderId) : Promise.resolve([]),
        assetId ? api.getFilePermissions(assetId) : Promise.resolve([]),
      ]);
      setFolderPermissions(fPerms || []);
      setFilePermissions(aPerms || []);
    } catch (err) {
      setLoadError(err.message);
    } finally {
      setLoading(false);
    }
  }, [folderId, assetId]);

  useEffect(() => {
    fetchPermissions();
  }, [fetchPermissions]);

  const isFolderTab = activeTab === 'folder';
  const currentPermissions = isFolderTab ? folderPermissions : filePermissions;
  const targetName = isFolderTab ? folder?.name : asset?.originalFileName;
  const isUserRoleRestricted = currentPermissions.some((p) => p.role === 'USER' && p.permissionStatus === 'RESTRICTED');

  const setRule = (userId, role, status) =>
    isFolderTab
      ? api.setFolderPermission(folderId, userId, role, status)
      : api.setFilePermission(assetId, userId, role, status);

  const afterChange = async (message) => {
    notify(message);
    await fetchPermissions();
    onPermissionUpdated?.();
  };

  const run = async (fn) => {
    setBusy(true);
    try {
      await fn();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setBusy(false);
    }
  };

  const handleSaveRule = (e) => {
    e.preventDefault();
    if (!selectedUserId && !selectedRole) return;
    run(async () => {
      await setRule(selectedUserId ? Number(selectedUserId) : null, selectedRole || null, targetStatus);
      setSelectedUserId('');
      setSelectedRole('');
      await afterChange(`Rule saved: ${targetStatus === 'ALLOWED' ? 'allowed' : 'restricted'}`);
    });
  };

  const handleExclusiveAccess = () =>
    run(async () => {
      await setRule(null, 'USER', 'RESTRICTED');
      await setRule(Number(selectedUserId), null, 'ALLOWED');
      setSelectedUserId('');
      await afterChange(`Only the selected student can now open this ${isFolderTab ? 'folder' : 'file'}`);
    });

  const handleQuickRoleRule = (status) =>
    run(async () => {
      await setRule(null, 'USER', status);
      await afterChange(status === 'RESTRICTED' ? 'Locked for all students' : 'Unlocked for all students');
    });

  const handleDelete = (permId) =>
    run(async () => {
      if (isFolderTab) await api.deleteFolderPermission(permId);
      else await api.deleteFilePermission(permId);
      await afterChange('Rule removed');
    });

  const tabs = [
    folder && { value: 'folder', label: `Folder: ${folder.name}` },
    asset && { value: 'file', label: `File: ${asset.originalFileName}` },
  ].filter(Boolean);

  return (
    <Modal
      open
      size="lg"
      onClose={() => !busy && onClose()}
      title="Access rules"
      description={targetName}
      footer={<button type="button" className="btn btn-secondary" onClick={onClose} disabled={busy}>Done</button>}
    >
      {tabs.length > 1 && <Tabs tabs={tabs} value={activeTab} onChange={setActiveTab} />}

      <Alert tone="info" title="How overrides work">
        Everyone with project access can open this {isFolderTab ? 'folder' : 'file'} by default. To limit it to specific
        students, restrict the Student role, then allow individual people — or use “Allow only this student” below.
      </Alert>

      <form onSubmit={handleSaveRule} className="surface-muted mb-4" style={{ padding: 16 }}>
        <div className="form-grid">
          <Field label="Person" htmlFor="perm-user">
            <select
              id="perm-user"
              className="select"
              value={selectedUserId}
              onChange={(e) => { setSelectedUserId(e.target.value); if (e.target.value) setSelectedRole(''); }}
            >
              <option value="">Select a person</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.fullName} ({u.email}) · {ROLE_LABELS[u.role] || u.role}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Or a whole role" htmlFor="perm-role">
            <select
              id="perm-role"
              className="select"
              value={selectedRole}
              onChange={(e) => { setSelectedRole(e.target.value); if (e.target.value) setSelectedUserId(''); }}
            >
              <option value="">Select a role</option>
              {RULE_ROLES.map((r) => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
            </select>
          </Field>
        </div>
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-4" role="radiogroup" aria-label="Access">
            <label className="checkbox">
              <input type="radio" name="perm-status" checked={targetStatus === 'ALLOWED'} onChange={() => setTargetStatus('ALLOWED')} />
              Allow
            </label>
            <label className="checkbox">
              <input type="radio" name="perm-status" checked={targetStatus === 'RESTRICTED'} onChange={() => setTargetStatus('RESTRICTED')} />
              Restrict
            </label>
          </div>
          <div className="flex items-center gap-2">
            {selectedUserId && (
              <button type="button" className="btn btn-secondary btn-sm" onClick={handleExclusiveAccess} disabled={busy}>
                <UserCheck aria-hidden="true" /> Allow only this student
              </button>
            )}
            <button type="submit" className="btn btn-primary btn-sm" disabled={busy || (!selectedUserId && !selectedRole)}>
              <Plus aria-hidden="true" /> Save rule
            </button>
          </div>
        </div>
      </form>

      <div className="section-header">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-muted">Students</span>
          {isUserRoleRestricted ? <Badge tone="danger">Locked</Badge> : <Badge tone="success">Open</Badge>}
        </div>
        {isUserRoleRestricted ? (
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => handleQuickRoleRule('ALLOWED')} disabled={busy}>
            <Unlock aria-hidden="true" /> Unlock for all students
          </button>
        ) : (
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => handleQuickRoleRule('RESTRICTED')} disabled={busy}>
            <Lock aria-hidden="true" /> Lock for all students
          </button>
        )}
      </div>

      {loading ? (
        <SkeletonRows rows={3} />
      ) : loadError ? (
        <Alert tone="danger" title="Could not load rules">{loadError}</Alert>
      ) : currentPermissions.length === 0 ? (
        <div className="surface-muted">
          <EmptyState icon={ShieldCheck} title="No overrides" text="Default access applies to everyone on this project." />
        </div>
      ) : (
        <div className="table-wrap border rounded">
          <table className="table">
            <thead>
              <tr><th>Applies to</th><th>Access</th><th aria-label="Remove" /></tr>
            </thead>
            <tbody>
              {currentPermissions.map((perm) => (
                <tr key={perm.id}>
                  <td>
                    {perm.user ? (
                      <>
                        <div className="font-medium">{perm.user.fullName}</div>
                        <div className="text-xs text-muted">{perm.user.email}</div>
                      </>
                    ) : (
                      <div className="font-medium">All {(ROLE_LABELS[perm.role] || perm.role || '').toLowerCase()}s</div>
                    )}
                  </td>
                  <td><StatusPill status={perm.permissionStatus} /></td>
                  <td className="text-right">
                    <button
                      type="button"
                      className="btn btn-danger-ghost btn-icon btn-sm"
                      onClick={() => handleDelete(perm.id)}
                      disabled={busy}
                      aria-label="Remove rule"
                      title="Remove rule"
                    >
                      <Trash2 aria-hidden="true" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Modal>
  );
};

export default AdminPermissionManagerModal;
