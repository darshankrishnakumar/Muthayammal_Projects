import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import BulkUserCreateModal from '../components/BulkUserCreateModal';
import { 
  Search, 
  UserPlus, 
  Edit3, 
  Trash2, 
  Check, 
  X, 
  User, 
  Users,
  Filter, 
  AlertTriangle 
} from 'lucide-react';

const UserManagement = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [bulkModalOpen, setBulkModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null); // null means "Create Mode"
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    role: 'USER',
    status: 'ACTIVE'
  });

  const isSuperAdmin = currentUser.role === 'SUPER_ADMIN';
  const isAdmin = currentUser.role === 'ADMIN';

  // Load Users
  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getUsers(searchTerm, statusFilter);
      setUsers(data);
    } catch (err) {
      setError(err.message || 'Failed to load user directories.');
    } finally {
      setLoading(false);
    }
  }, [searchTerm, statusFilter]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleOpenCreateModal = () => {
    setEditingUser(null);
    setFormData({
      fullName: '',
      email: '',
      password: '',
      role: 'USER',
      status: 'ACTIVE'
    });
    setModalOpen(true);
  };

  const handleOpenEditModal = (user) => {
    setEditingUser(user);
    setFormData({
      fullName: user.fullName,
      email: user.email,
      password: '', // Keep blank unless resetting
      role: user.role,
      status: user.status
    });
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setEditingUser(null);
  };

  const handleFormChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    try {
      if (editingUser) {
        // Edit User
        const updatePayload = {
          fullName: formData.fullName,
          email: formData.email,
          role: formData.role,
          status: formData.status
        };
        // Only update password if provided
        if (formData.password) {
          updatePayload.password = formData.password;
        }

        await api.updateUser(editingUser.id, updatePayload);
        setSuccess(`User "${formData.fullName}" updated successfully.`);
      } else {
        // Create User
        if (!formData.password) {
          setError('A password is required for new accounts.');
          return;
        }
        await api.createUser(formData);
        setSuccess(`User "${formData.fullName}" created successfully.`);
      }
      
      handleCloseModal();
      loadUsers();
      
      // Auto clear success alert
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      setError(err.message || 'An error occurred while saving the user profile.');
    }
  };

  const handleToggleStatus = async (user) => {
    setError('');
    const newStatus = user.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await api.updateUser(user.id, { status: newStatus });
      loadUsers();
      setSuccess(`Status of ${user.fullName} changed to ${newStatus}.`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to toggle account state.');
    }
  };

  const handleDeleteUser = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete ${name}? This action can be undone by restoring the profile.`)) {
      return;
    }
    setError('');
    try {
      await api.deleteUser(id);
      loadUsers();
      setSuccess(`User "${name}" successfully deleted.`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to delete user.');
    }
  };

  return (
    <div className="user-manager-wrapper">
      {/* Alert Banners */}
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
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search by full name or email address..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-actions">
          <div className="select-wrapper">
            <Filter size={14} className="select-icon" />
            <select 
              value={statusFilter} 
              onChange={(e) => setStatusFilter(e.target.value)}
              className="form-control form-select select-filter"
            >
              <option value="">All Statuses</option>
              <option value="ACTIVE">Active Users</option>
              <option value="INACTIVE">Inactive Users</option>
            </select>
          </div>

          {(isSuperAdmin || isAdmin) && (
            <button 
              onClick={() => setBulkModalOpen(true)} 
              className="btn btn-secondary flex items-center gap-2"
              title="Bulk upload users via CSV or interactive table"
            >
              <Users size={16} />
              <span>Bulk Create Users</span>
            </button>
          )}

          <button onClick={handleOpenCreateModal} className="btn btn-primary flex items-center gap-2">
            <UserPlus size={16} />
            <span>Add User</span>
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="table-container card">
        {loading ? (
          <div className="table-loading">
            <p>Loading secure user directory...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="table-empty">
            <User size={48} className="text-muted" />
            <h3>No users found</h3>
            <p className="text-muted">Try adjusting your filters or search query.</p>
          </div>
        ) : (
          <table className="custom-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email Address</th>
                <th>Role</th>
                <th>Status</th>
                <th>Created</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => {
                // Rule: Admins cannot edit/delete another Admin
                const canModify = isSuperAdmin || (isAdmin && u.role === 'USER');
                
                return (
                  <tr key={u.id}>
                    <td>
                      <div className="table-user-name">
                        <span className="avatar-sm">
                          {u.fullName.charAt(0)}
                        </span>
                        <div>
                          <span style={{ fontWeight: 600 }}>{u.fullName}</span>
                          {currentUser.id === u.id && <span className="badge badge-primary ms-1" style={{ fontSize: '0.6rem' }}>You</span>}
                        </div>
                      </div>
                    </td>
                    <td>{u.email}</td>
                    <td>
                      <span className={`badge ${
                        u.role === 'ADMIN' ? 'badge-primary' : 'badge-success'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td>
                      <button 
                        onClick={() => canModify && handleToggleStatus(u)}
                        className={`status-toggle ${u.status === 'ACTIVE' ? 'status-active' : 'status-inactive'}`}
                        disabled={!canModify}
                        title={canModify ? 'Click to toggle status' : 'Unauthorized to change status'}
                      >
                        <span className="indicator-dot"></span>
                        <span>{u.status}</span>
                      </button>
                    </td>
                    <td>
                      <span className="text-muted" style={{ fontSize: '0.85rem' }}>
                        {new Date(u.createdAt).toLocaleDateString()}
                      </span>
                    </td>
                    <td>
                      <div className="table-actions-cell">
                        <button
                          onClick={() => handleOpenEditModal(u)}
                          className="btn-action edit-action"
                          disabled={!canModify}
                          title={canModify ? 'Edit user profile' : 'Admins cannot modify Admin accounts'}
                        >
                          <Edit3 size={16} />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(u.id, u.fullName)}
                          className="btn-action delete-action"
                          disabled={!canModify || currentUser.id === u.id}
                          title={canModify ? 'Delete user account' : 'Cannot delete this user'}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Create / Edit User Modal */}
      {modalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3 className="modal-title">
                {editingUser ? 'Modify User Profile' : 'Register New User'}
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
                  placeholder="e.g. John Doe"
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
                  placeholder="e.g. jdoe@academic.com"
                  value={formData.email}
                  onChange={handleFormChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  <span>Password</span>
                  {editingUser && <span className="text-muted" style={{ fontWeight: 400, fontSize: '0.75rem' }}>(leave blank to keep current)</span>}
                </label>
                <input
                  type="password"
                  name="password"
                  className="form-control"
                  placeholder={editingUser ? "••••••••" : "Choose a secure password"}
                  value={formData.password}
                  onChange={handleFormChange}
                  required={!editingUser}
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
                  {editingUser ? 'Save Changes' : 'Register User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bulk User Creation Modal */}
      <BulkUserCreateModal
        isOpen={bulkModalOpen}
        onClose={() => setBulkModalOpen(false)}
        onSuccess={() => {
          loadUsers();
          setSuccess('Bulk user creation completed successfully.');
          setTimeout(() => setSuccess(''), 4000);
        }}
        existingUsers={users}
      />

      <style>{`
        .user-manager-wrapper {
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
          gap: 20px;
        }

        .search-box {
          position: relative;
          flex: 1;
          max-width: 450px;
        }

        .search-icon {
          position: absolute;
          left: 14px;
          top: 50%;
          transform: translateY(-50%);
          color: var(--text-muted);
        }

        .search-box input {
          width: 100%;
          padding: 10px 16px 10px 42px;
          border-radius: var(--radius-md);
          border: 1.5px solid var(--border-color);
          font-family: var(--font-sans);
          font-size: 0.9rem;
          outline: none;
          transition: all 0.2s ease;
        }

        .search-box input:focus {
          border-color: var(--primary);
          box-shadow: 0 0 0 3px var(--primary-glow);
        }

        .filter-actions {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .select-wrapper {
          position: relative;
        }

        .select-icon {
          position: absolute;
          left: 12px;
          top: 50%;
          transform: translateY(-50%);
          color: var(--text-muted);
          pointer-events: none;
        }

        .select-filter {
          padding: 9px 36px 9px 34px !important;
          font-size: 0.88rem;
          border-radius: var(--radius-md);
          border: 1.5px solid var(--border-color);
          cursor: pointer;
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
          background-color: var(--primary-light);
          color: var(--primary);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 0.85rem;
        }

        .ms-1 {
          margin-left: 6px;
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

        .status-toggle:disabled {
          cursor: default;
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

        @media (max-width: 768px) {
          .control-bar {
            flex-direction: column;
            align-items: stretch;
            padding: 16px;
          }
          .filter-actions {
            flex-direction: column;
            align-items: stretch;
          }
          .select-filter {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default UserManagement;
