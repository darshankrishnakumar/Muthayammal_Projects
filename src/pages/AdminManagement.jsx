import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import AdminAccessControlModal from '../components/AdminAccessControlModal';
import { 
  ShieldCheck, 
  UserPlus, 
  Edit3, 
  Trash2,
  X, 
  Check, 
  AlertTriangle,
  Lock,
  Shield
} from 'lucide-react';

const AdminManagement = () => {
  const { user: currentUser } = useAuth();
  const [admins, setAdmins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Access Control Modal State
  const [accessModalOpen, setAccessModalOpen] = useState(false);
  const [selectedAdminForAccess, setSelectedAdminForAccess] = useState(null);

  // Edit/Create Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [editingAdmin, setEditingAdmin] = useState(null); // null means "Create Mode"
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    status: 'ACTIVE'
  });

  const isSuperAdmin = currentUser?.role === 'SUPER_ADMIN';

  const loadAdmins = useCallback(async () => {
    if (!isSuperAdmin) return;
    setLoading(true);
    setError('');
    try {
      const data = await api.getAdmins();
      setAdmins(data);
    } catch (err) {
      setError(err.message || 'Failed to retrieve administrator directories.');
    } finally {
      setLoading(false);
    }
  }, [isSuperAdmin]);

  useEffect(() => {
    loadAdmins();
  }, [loadAdmins]);

  // Access Denied Fallback
  if (!isSuperAdmin) {
    return (
      <div className="card text-center" style={{ padding: '60px 20px', maxWidth: '500px', margin: '40px auto' }}>
        <div className="error-icon-wrapper" style={{ margin: '0 auto 20px', width: '56px', height: '56px', borderRadius: '50%', backgroundColor: 'var(--error-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--error)' }}>
          <Lock size={24} />
        </div>
        <h2 className="font-display" style={{ fontSize: '1.4rem', fontWeight: 600, marginBottom: '8px' }}>Security Access Denied</h2>
        <p className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '24px' }}>
          This administrative management interface is restricted exclusively to <strong>Super Administrators</strong>.
        </p>
        <button className="btn btn-primary" onClick={() => window.history.back()}>
          Return to Dashboard
        </button>
      </div>
    );
  }

  const handleOpenCreateModal = () => {
    setEditingAdmin(null);
    setFormData({
      fullName: '',
      email: '',
      password: '',
      status: 'ACTIVE'
    });
    setModalOpen(true);
  };

  const handleOpenEditModal = (admin) => {
    setEditingAdmin(admin);
    setFormData({
      fullName: admin.fullName,
      email: admin.email,
      password: '', // Keep blank unless resetting
      status: admin.status
    });
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setEditingAdmin(null);
  };

  const handleFormChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (editingAdmin) {
        // Update Admin
        const updatePayload = {
          fullName: formData.fullName,
          email: formData.email,
          status: formData.status
        };
        if (formData.password) {
          updatePayload.password = formData.password;
        }

        await api.updateAdmin(editingAdmin.id, updatePayload);
        setSuccess(`Administrator account "${formData.fullName}" updated successfully.`);
      } else {
        // Create Admin
        if (!formData.password) {
          setError('A password is required to create new administrator credentials.');
          return;
        }
        await api.createAdmin(formData);
        setSuccess(`Administrator account "${formData.fullName}" registered successfully.`);
      }

      handleCloseModal();
      loadAdmins();
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      setError(err.message || 'An error occurred while saving the administrator profile.');
    }
  };

  const handleToggleStatus = async (admin) => {
    setError('');
    const newStatus = admin.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await api.updateAdmin(admin.id, { status: newStatus });
      loadAdmins();
      setSuccess(`Status of Administrator ${admin.fullName} changed to ${newStatus}.`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to update administrator status.');
    }
  };

  const handleDeleteAdmin = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete administrator account "${name}"? This action will revoke their administrative access.`)) {
      return;
    }

    setError('');
    try {
      await api.deleteAdmin(id);
      loadAdmins();
      setSuccess(`Administrator account "${name}" successfully deleted.`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to delete administrator.');
    }
  };

  return (
    <div className="admin-manager-wrapper">
      {success && (
        <div className="alert alert-success">
          <Check size={16} />
          <span>{success}</span>
        </div>
      )}
      {error && (
        <div className="alert alert-danger">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Control Panel */}
      <div className="control-bar card">
        <div className="flex items-center gap-2">
          <ShieldCheck size={20} className="text-primary" />
          <h4 style={{ fontWeight: 600, fontSize: '1rem' }}>Administrator Directory</h4>
        </div>

        <button onClick={handleOpenCreateModal} className="btn btn-primary">
          <UserPlus size={16} />
          <span>Register Admin</span>
        </button>
      </div>

      {/* Admins Table */}
      <div className="table-container card">
        {loading ? (
          <div className="table-loading">
            <p>Loading secure administrator records...</p>
          </div>
        ) : admins.length === 0 ? (
          <div className="table-empty">
            <ShieldCheck size={48} className="text-muted" />
            <h3>No administrators found</h3>
            <p className="text-muted">Register a new administrator to assign project management tasks.</p>
          </div>
        ) : (
          <table className="custom-table">
            <thead>
              <tr>
                <th>Administrator Name</th>
                <th>Email Address</th>
                <th>Access Level</th>
                <th>Status</th>
                <th>Created</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {admins.map((a) => (
                <tr key={a.id}>
                  <td>
                    <div className="table-user-name">
                      <span className="avatar-sm" style={{ backgroundColor: 'var(--error-light)', color: 'var(--error)' }}>
                        {a.fullName.charAt(0)}
                      </span>
                      <span style={{ fontWeight: 600 }}>{a.fullName}</span>
                      {currentUser?.id === a.id && <span className="badge badge-primary ms-1" style={{ fontSize: '0.6rem' }}>You</span>}
                    </div>
                  </td>
                  <td>{a.email}</td>
                  <td>
                    <span className="badge badge-danger">ADMIN</span>
                  </td>
                  <td>
                    <button 
                      onClick={() => handleToggleStatus(a)}
                      className={`status-toggle ${a.status === 'ACTIVE' ? 'status-active' : 'status-inactive'}`}
                      title="Click to toggle administrator status"
                    >
                      <span className="indicator-dot"></span>
                      <span>{a.status}</span>
                    </button>
                  </td>
                  <td>
                    <span className="text-muted" style={{ fontSize: '0.85rem' }}>
                      {new Date(a.createdAt).toLocaleDateString()}
                    </span>
                  </td>
                  <td>
                    <div className="table-actions-cell">
                      <button
                        onClick={() => {
                          setSelectedAdminForAccess(a);
                          setAccessModalOpen(true);
                        }}
                        className="btn-action"
                        style={{ color: 'var(--primary)', borderColor: 'rgba(99, 102, 241, 0.3)' }}
                        title="Manage Permissions, Presets & User Scopes"
                      >
                        <Shield size={16} />
                      </button>
                      <button
                        onClick={() => handleOpenEditModal(a)}
                        className="btn-action edit-action"
                        title="Edit administrator credentials"
                      >
                        <Edit3 size={16} />
                      </button>
                      <button
                        onClick={() => handleDeleteAdmin(a.id, a.fullName)}
                        className="btn-action delete-action"
                        disabled={currentUser?.id === a.id || a.role === 'SUPER_ADMIN'}
                        title={currentUser?.id === a.id ? 'Cannot delete your own account' : 'Delete administrator account'}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Create / Edit Admin Modal */}
      {modalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3 className="modal-title">
                {editingAdmin ? 'Modify Administrator Profile' : 'Register New Administrator'}
              </h3>
              <button onClick={handleCloseModal} className="modal-close">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  name="fullName"
                  className="form-control"
                  placeholder="e.g. Sarah Jenkins"
                  value={formData.fullName}
                  onChange={handleFormChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input
                  type="email"
                  name="email"
                  className="form-control"
                  placeholder="e.g. sjenkins@academic.com"
                  value={formData.email}
                  onChange={handleFormChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  <span>Secret Password</span>
                  {editingAdmin && <span className="text-muted" style={{ fontWeight: 400, fontSize: '0.75rem' }}>(leave blank to keep current)</span>}
                </label>
                <input
                  type="password"
                  name="password"
                  className="form-control"
                  placeholder={editingAdmin ? "••••••••" : "Choose a secure password"}
                  value={formData.password}
                  onChange={handleFormChange}
                  required={!editingAdmin}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Account Status</label>
                <select
                  name="status"
                  className="form-control form-select"
                  value={formData.status}
                  onChange={handleFormChange}
                >
                  <option value="ACTIVE">Active</option>
                  <option value="INACTIVE">Inactive</option>
                </select>
              </div>

              <div className="modal-footer">
                <button type="button" onClick={handleCloseModal} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingAdmin ? 'Save Changes' : 'Register Administrator'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Admin Access Control & Permission Scoping Modal */}
      <AdminAccessControlModal
        admin={selectedAdminForAccess}
        isOpen={accessModalOpen}
        onClose={() => {
          setAccessModalOpen(false);
          setSelectedAdminForAccess(null);
        }}
        onUpdated={loadAdmins}
      />

      <style>{`
        .admin-manager-wrapper {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .alert {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 14px 20px;
          border-radius: var(--radius-md);
          font-size: 0.9rem;
          text-align: left;
        }

        .alert-success {
          background-color: var(--success-light);
          color: var(--success);
          border: 1px solid hsla(142, 70%, 45%, 0.15);
        }

        .alert-danger {
          background-color: var(--error-light);
          color: var(--error);
          border: 1px solid hsla(350, 80%, 55%, 0.15);
        }

        .control-bar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 24px;
        }

        .table-loading, .table-empty {
          padding: 60px 20px;
          text-align: center;
        }

        .table-empty h3 {
          font-family: var(--font-display);
          font-size: 1.2rem;
          font-weight: 600;
          margin: 16px 0 4px;
        }

        .table-user-name {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .avatar-sm {
          width: 32px;
          height: 32px;
          border-radius: var(--radius-full);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 0.85rem;
        }

        .status-toggle {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 4px 10px;
          border-radius: var(--radius-full);
          border: none;
          font-size: 0.75rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .indicator-dot {
          width: 6px;
          height: 6px;
          border-radius: var(--radius-full);
        }

        .status-active {
          background-color: var(--success-light);
          color: var(--success);
        }

        .status-active .indicator-dot {
          background-color: var(--success);
        }

        .status-inactive {
          background-color: var(--error-light);
          color: var(--error);
        }

        .status-inactive .indicator-dot {
          background-color: var(--error);
        }

        .table-actions-cell {
          display: flex;
          justify-content: flex-end;
          gap: 8px;
        }

        .btn-action {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 8px;
          border-radius: var(--radius-sm);
          border: 1px solid var(--border-color);
          background-color: var(--bg-card);
          color: var(--text-muted);
          cursor: pointer;
          transition: all 0.15s ease;
        }

        .btn-action:hover:not(:disabled) {
          border-color: transparent;
        }

        .edit-action:hover:not(:disabled) {
          background-color: var(--primary-light);
          color: var(--primary);
        }

        .delete-action:hover:not(:disabled) {
          background-color: var(--error-light);
          color: var(--error);
        }

        .btn-action:disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default AdminManagement;
