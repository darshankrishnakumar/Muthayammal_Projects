import { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { 
  ShieldCheck, 
  User, 
  Users, 
  Lock, 
  Unlock, 
  Trash2, 
  AlertCircle, 
  CheckCircle2, 
  Plus, 
  Sparkles,
  Info 
} from 'lucide-react';

const AdminPermissionManagerModal = ({ folder, asset, usersList, onClose, onPermissionUpdated }) => {
  const [folderPermissions, setFolderPermissions] = useState([]);
  const [filePermissions, setFilePermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState(folder ? 'folder' : 'file');

  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [targetStatus, setTargetStatus] = useState('ALLOWED');
  const [activeUsersList, setActiveUsersList] = useState(usersList || []);

  useEffect(() => {
    if (!usersList || usersList.length === 0) {
      api.getUsers().then(data => setActiveUsersList(data || [])).catch(console.warn);
    } else {
      setActiveUsersList(usersList);
    }
  }, [usersList]);

  useEffect(() => {
    fetchPermissions();
  }, [folder?.id, asset?.id]);

  const fetchPermissions = async () => {
    try {
      setLoading(true);
      setError('');
      if (folder?.id) {
        const fPerms = await api.getFolderPermissions(folder.id);
        setFolderPermissions(fPerms);
      }

      if (asset?.id) {
        const aPerms = await api.getFilePermissions(asset.id);
        setFilePermissions(aPerms);
      }
    } catch (err) {
      setError(err.message || 'Failed to load access control entries.');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePermission = async (e) => {
    if (e) e.preventDefault();
    if (!selectedUserId && !selectedRole) {
      setError('Please select either a specific User or a Role.');
      return;
    }

    try {
      setError('');
      setSuccess('');

      if (activeTab === 'folder') {
        await api.setFolderPermission(folder.id, selectedUserId ? Number(selectedUserId) : null, selectedRole || null, targetStatus);
        setSuccess(`Folder permission successfully saved as ${targetStatus}!`);
      } else {
        await api.setFilePermission(asset.id, selectedUserId ? Number(selectedUserId) : null, selectedRole || null, targetStatus);
        setSuccess(`File permission successfully saved as ${targetStatus}!`);
      }

      setSelectedUserId('');
      setSelectedRole('');
      fetchPermissions();
      if (onPermissionUpdated) onPermissionUpdated();
    } catch (err) {
      setError(err.message || 'Failed to update access control rule.');
    }
  };

  const handleGrantExclusiveAccess = async () => {
    if (!selectedUserId) {
      setError('Please select a specific User from the dropdown to grant exclusive access.');
      return;
    }

    try {
      setError('');
      setSuccess('');
      setLoading(true);

      if (activeTab === 'folder') {
        // 1. Restrict general USER role
        await api.setFolderPermission(folder.id, null, 'USER', 'RESTRICTED');
        // 2. Grant specific user ALLOWED
        await api.setFolderPermission(folder.id, Number(selectedUserId), null, 'ALLOWED');
        setSuccess(`Exclusive access granted: Locked folder for other users and permitted selected user!`);
      } else {
        // 1. Restrict general USER role
        await api.setFilePermission(asset.id, null, 'USER', 'RESTRICTED');
        // 2. Grant specific user ALLOWED
        await api.setFilePermission(asset.id, Number(selectedUserId), null, 'ALLOWED');
        setSuccess(`Exclusive access granted: Locked file for other users and permitted selected user!`);
      }

      setSelectedUserId('');
      setSelectedRole('');
      fetchPermissions();
      if (onPermissionUpdated) onPermissionUpdated();
    } catch (err) {
      setError(err.message || 'Failed to apply exclusive permission rule.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickRoleRule = async (role, status) => {
    try {
      setError('');
      setSuccess('');
      setLoading(true);

      if (activeTab === 'folder') {
        await api.setFolderPermission(folder.id, null, role, status);
        setSuccess(`Folder rule set: Role ${role} is now ${status}.`);
      } else {
        await api.setFilePermission(asset.id, null, role, status);
        setSuccess(`File rule set: Role ${role} is now ${status}.`);
      }

      fetchPermissions();
      if (onPermissionUpdated) onPermissionUpdated();
    } catch (err) {
      setError(err.message || 'Failed to update role rule.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePermission = async (permId) => {
    try {
      setError('');
      setSuccess('');

      if (activeTab === 'folder') {
        await api.deleteFolderPermission(permId, folder.id);
        setSuccess('Folder permission rule removed.');
      } else {
        await api.deleteFilePermission(permId, asset.id);
        setSuccess('File permission rule removed.');
      }

      fetchPermissions();
      if (onPermissionUpdated) onPermissionUpdated();
    } catch (err) {
      setError(err.message || 'Failed to delete permission rule.');
    }
  };

  const isUserRoleRestricted = (activeTab === 'folder' ? folderPermissions : filePermissions)
    .some(p => p.role === 'USER' && p.permissionStatus === 'RESTRICTED');

  return (
    <div className="modal-backdrop">
      <div className="modal-card card" style={{ maxWidth: '680px', width: '100%', margin: '40px auto', padding: '24px' }}>
        <div className="flex justify-between items-center" style={{ marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
          <div className="flex items-center gap-2">
            <ShieldCheck size={22} style={{ color: 'var(--primary)' }} />
            <div>
              <h3 className="font-display" style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                Access Management & Permission Control
              </h3>
              <p className="text-muted" style={{ fontSize: '0.8rem' }}>
                {folder ? `Folder: ${folder.name}` : ''} {asset ? `| File: ${asset.originalFileName}` : ''}
              </p>
            </div>
          </div>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>

        {/* Tab Switcher if both folder and file are provided */}
        {folder && asset && (
          <div className="flex gap-2 mb-4" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
            <button
              className={`btn btn-sm ${activeTab === 'folder' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('folder')}
            >
              Folder Access Control ({folder.name})
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'file' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('file')}
            >
              File Access Control ({asset.originalFileName})
            </button>
          </div>
        )}

        {/* Banners */}
        {error && (
          <div className="alert alert-danger flex items-center gap-2" style={{ marginBottom: '16px' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}
        {success && (
          <div className="alert alert-success flex items-center gap-2" style={{ marginBottom: '16px' }}>
            <CheckCircle2 size={16} />
            <span>{success}</span>
          </div>
        )}

        {/* Guidance Tip */}
        <div className="flex items-start gap-2 text-muted" style={{ fontSize: '0.78rem', background: 'rgba(59, 130, 246, 0.08)', padding: '10px 14px', borderRadius: '6px', marginBottom: '16px', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
          <Info size={16} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>How Permission Overrides Work:</strong>
            <br />
            To make a folder accessible <em>only</em> to selected users, set <strong>Role: USER → RESTRICTED</strong> (to lock out general users), then add specific individual users as <strong>ALLOWED</strong>. Or use the 1-click preset below.
          </div>
        </div>

        {/* Form: Add / Grant / Restrict Access */}
        <form onSubmit={handleSavePermission} className="card" style={{ padding: '16px', backgroundColor: 'var(--bg-main)', marginBottom: '20px' }}>
          <h4 className="font-display" style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '12px' }}>
            Configure Access Rule
          </h4>
          
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                Specific User (User-Level Override)
              </label>
              <select
                className="form-control"
                value={selectedUserId}
                onChange={(e) => {
                  setSelectedUserId(e.target.value);
                  if (e.target.value) setSelectedRole('');
                }}
              >
                <option value="">-- All Users / Select User --</option>
                {activeUsersList.map(u => (
                  <option key={u.id} value={u.id}>{u.fullName} ({u.email}) - {u.role}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-muted" style={{ fontSize: '0.75rem', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                System Role (Role-Level Rule)
              </label>
              <select
                className="form-control"
                value={selectedRole}
                onChange={(e) => {
                  setSelectedRole(e.target.value);
                  if (e.target.value) setSelectedUserId('');
                }}
              >
                <option value="">-- Select System Role --</option>
                <option value="USER">USER (Student / Researcher)</option>
                <option value="ADMIN">ADMIN (Coordinator)</option>
                <option value="SUPER_ADMIN">SUPER_ADMIN</option>
              </select>
            </div>
          </div>

          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2" style={{ fontSize: '0.85rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="permStatus"
                  value="ALLOWED"
                  checked={targetStatus === 'ALLOWED'}
                  onChange={() => setTargetStatus('ALLOWED')}
                />
                <span className="badge badge-success">🔓 ALLOWED (Grant Access)</span>
              </label>

              <label className="flex items-center gap-2" style={{ fontSize: '0.85rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="permStatus"
                  value="RESTRICTED"
                  checked={targetStatus === 'RESTRICTED'}
                  onChange={() => setTargetStatus('RESTRICTED')}
                />
                <span className="badge badge-danger">🔒 RESTRICTED (Deny Access)</span>
              </label>
            </div>

            <button type="submit" className="btn btn-primary btn-sm flex items-center gap-1" disabled={!selectedUserId && !selectedRole}>
              <Plus size={14} />
              <span>Save Rule</span>
            </button>
          </div>

          {/* Quick 1-Click Exclusive Access Preset */}
          {selectedUserId && (
            <div className="flex justify-between items-center pt-3" style={{ borderTop: '1px solid var(--border-color)' }}>
              <div className="text-muted" style={{ fontSize: '0.75rem' }}>
                Lock out other regular users and permit only this user:
              </div>
              <button 
                type="button" 
                className="btn btn-secondary btn-sm flex items-center gap-1"
                onClick={handleGrantExclusiveAccess}
                style={{ color: 'var(--primary)', borderColor: 'var(--primary)' }}
              >
                <Sparkles size={14} />
                <span>Grant Exclusive Access to User</span>
              </button>
            </div>
          )}
        </form>

        {/* Quick Role Controls */}
        <div className="flex justify-between items-center mb-3">
          <span style={{ fontSize: '0.8rem', fontWeight: 600 }} className="text-muted">
            General USER Role Status: {isUserRoleRestricted ? <span className="badge badge-danger">🔒 Locked for USERs</span> : <span className="badge badge-success">🔓 Open for USERs</span>}
          </span>
          <div className="flex gap-2">
            {!isUserRoleRestricted ? (
              <button 
                type="button" 
                className="btn btn-secondary btn-sm flex items-center gap-1 text-error"
                onClick={() => handleQuickRoleRule('USER', 'RESTRICTED')}
              >
                <Lock size={13} />
                <span>Lock for all USERs</span>
              </button>
            ) : (
              <button 
                type="button" 
                className="btn btn-secondary btn-sm flex items-center gap-1"
                onClick={() => handleQuickRoleRule('USER', 'ALLOWED')}
              >
                <Unlock size={13} />
                <span>Unlock for all USERs</span>
              </button>
            )}
          </div>
        </div>

        {/* Existing Permission Entries Table */}
        <div>
          <h4 className="font-display" style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '12px' }}>
            Current Active Access Control Entries
          </h4>

          {loading ? (
            <p className="text-muted text-center" style={{ padding: '20px' }}>Loading permissions...</p>
          ) : (activeTab === 'folder' ? folderPermissions : filePermissions).length === 0 ? (
            <div className="text-center text-muted" style={{ padding: '24px', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-md)' }}>
              <ShieldCheck size={28} style={{ margin: '0 auto 8px', opacity: 0.5 }} />
              <p style={{ fontSize: '0.85rem' }}>No custom access overrides configured. Default permission is <strong>ALLOWED</strong> for all assigned members.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="table" style={{ width: '100%', fontSize: '0.85rem', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border-color)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '8px 12px' }}>Target Scope</th>
                    <th style={{ padding: '8px 12px' }}>Permission Status</th>
                    <th style={{ padding: '8px 12px', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {(activeTab === 'folder' ? folderPermissions : filePermissions).map(perm => (
                    <tr key={perm.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ padding: '10px 12px' }}>
                        {perm.user ? (
                          <div>
                            <span style={{ fontWeight: 600 }}>User: {perm.user.fullName}</span>
                            <div className="text-muted" style={{ fontSize: '0.75rem' }}>{perm.user.email}</div>
                          </div>
                        ) : (
                          <div>
                            <span style={{ fontWeight: 600 }}>System Role: {perm.role}</span>
                          </div>
                        )}
                      </td>
                      <td style={{ padding: '10px 12px' }}>
                        {perm.permissionStatus === 'ALLOWED' ? (
                          <span className="badge badge-success">🔓 ALLOWED</span>
                        ) : (
                          <span className="badge badge-danger">🔒 RESTRICTED</span>
                        )}
                      </td>
                      <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                        <button
                          onClick={() => handleDeletePermission(perm.id)}
                          className="btn btn-secondary btn-sm"
                          style={{ padding: '4px 8px', color: 'var(--error)' }}
                          title="Remove permission override"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPermissionManagerModal;
