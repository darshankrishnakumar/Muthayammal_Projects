import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { 
  Code2, 
  UserPlus, 
  Edit3, 
  Trash2, 
  Check, 
  X, 
  Search, 
  Filter, 
  AlertTriangle, 
  Lock, 
  FolderKanban, 
  Calendar, 
  CheckCircle2, 
  Layers,
  Clock
} from 'lucide-react';

const DeveloperManagement = () => {
  const { user: currentUser } = useAuth();
  const [developers, setDevelopers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [assignmentsMap, setAssignmentsMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Create / Edit Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [editingDev, setEditingDev] = useState(null); // null means "Create Mode"
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    phone: '',
    department: '',
    organization: '',
    status: 'ACTIVE'
  });

  // Assign Project Modal State
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [selectedDevForAssign, setSelectedDevForAssign] = useState(null);
  const [assignFormData, setAssignFormData] = useState({
    projectId: '',
    notes: 'Assigned by Super Admin',
    expiredAt: ''
  });
  const [assignLoading, setAssignLoading] = useState(false);

  const isSuperAdmin = currentUser?.role === 'SUPER_ADMIN';

  // Load Developers & Project Repository Data
  const loadData = useCallback(async () => {
    if (!isSuperAdmin) return;
    setLoading(true);
    setError('');
    try {
      const [devsList, projectsList] = await Promise.all([
        api.getDevelopers(searchTerm, statusFilter),
        api.getProjects().catch(() => [])
      ]);
      setDevelopers(devsList || []);
      setProjects(projectsList || []);

      // Load assignments for each developer
      const assignMap = {};
      await Promise.all((devsList || []).map(async (d) => {
        try {
          const devProjects = await api.getDeveloperProjects(d.id);
          assignMap[d.id] = devProjects || [];
        } catch {
          assignMap[d.id] = [];
        }
      }));
      setAssignmentsMap(assignMap);
    } catch (err) {
      setError(err.message || 'Failed to load developer directories.');
    } finally {
      setLoading(false);
    }
  }, [isSuperAdmin, searchTerm, statusFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Access Denied Fallback
  if (!isSuperAdmin) {
    return (
      <div className="card text-center" style={{ padding: '60px 20px', maxWidth: '500px', margin: '40px auto' }}>
        <div style={{ margin: '0 auto 20px', width: '56px', height: '56px', borderRadius: '50%', backgroundColor: 'var(--error-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--error)' }}>
          <Lock size={24} />
        </div>
        <h2 className="font-display" style={{ fontSize: '1.4rem', fontWeight: 600, marginBottom: '8px' }}>Security Access Denied</h2>
        <p className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '24px' }}>
          This developer governance and allocation console is restricted exclusively to <strong>Super Administrators</strong>.
        </p>
        <button className="btn btn-primary" onClick={() => window.history.back()}>
          Return to Dashboard
        </button>
      </div>
    );
  }

  const handleOpenCreateModal = () => {
    setEditingDev(null);
    setFormData({
      fullName: '',
      email: '',
      password: '',
      phone: '',
      department: 'Software Engineering',
      organization: 'Academic Development Core',
      status: 'ACTIVE'
    });
    setModalOpen(true);
  };

  const handleOpenEditModal = (dev) => {
    setEditingDev(dev);
    setFormData({
      fullName: dev.fullName || '',
      email: dev.email || '',
      password: '', // Keep blank unless resetting
      phone: dev.phone || dev.mobileNumber || '',
      department: dev.department || '',
      organization: dev.organization || '',
      status: dev.status || 'ACTIVE'
    });
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setEditingDev(null);
  };

  const handleFormChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (editingDev) {
        // Edit Developer
        const updatePayload = {
          fullName: formData.fullName,
          email: formData.email,
          phone: formData.phone,
          department: formData.department,
          organization: formData.organization,
          status: formData.status
        };
        if (formData.password) {
          updatePayload.password = formData.password;
        }

        await api.updateDeveloper(editingDev.id, updatePayload);
        setSuccess(`Developer "${formData.fullName}" updated successfully.`);
      } else {
        // Create Developer
        if (!formData.password) {
          setError('A secure initial password is required for new developers.');
          return;
        }
        await api.createDeveloper(formData);
        setSuccess(`Developer account "${formData.fullName}" created successfully.`);
      }

      handleCloseModal();
      loadData();
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      setError(err.message || 'An error occurred while saving developer profile.');
    }
  };

  const handleToggleStatus = async (dev) => {
    setError('');
    const newStatus = dev.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await api.updateDeveloper(dev.id, { status: newStatus });
      loadData();
      setSuccess(`Status of ${dev.fullName} changed to ${newStatus}.`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to toggle account state.');
    }
  };

  const handleDeleteDev = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete developer "${name}"? This action will remove their project access.`)) {
      return;
    }
    setError('');
    try {
      await api.deleteDeveloper(id);
      loadData();
      setSuccess(`Developer "${name}" successfully deleted.`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to delete developer.');
    }
  };

  // Open Assign Project Modal
  const handleOpenAssignModal = (dev) => {
    setSelectedDevForAssign(dev);
    setAssignFormData({
      projectId: projects.length > 0 ? projects[0].id : '',
      notes: 'Assigned by Super Admin',
      expiredAt: ''
    });
    setAssignModalOpen(true);
  };

  const handleAssignProjectSubmit = async (e) => {
    e.preventDefault();
    if (!assignFormData.projectId) {
      setError('Please select a project to assign.');
      return;
    }

    setAssignLoading(true);
    setError('');
    try {
      await api.assignDeveloperToProject(selectedDevForAssign.id, {
        projectId: assignFormData.projectId,
        notes: assignFormData.notes,
        expiredAt: assignFormData.expiredAt || null
      });

      setSuccess(`Assigned project to ${selectedDevForAssign.fullName} successfully.`);
      setAssignModalOpen(false);
      loadData();
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      setError(err.message || 'Failed to assign project to developer.');
    } finally {
      setAssignLoading(false);
    }
  };

  const activeDevsCount = developers.filter(d => d.status === 'ACTIVE').length;
  const totalAssignmentsCount = Object.values(assignmentsMap).reduce((acc, curr) => acc + (curr?.length || 0), 0);

  return (
    <div className="text-left flex flex-col" style={{ gap: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* 1. Header Banner */}
      <div className="card" style={{ padding: '24px 32px' }}>
        <div className="flex justify-between items-center gap-6 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="badge badge-primary">Super Admin Governance</span>
            </div>
            <h2 className="font-display" style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Developer Management & Project Allocation
            </h2>
            <p className="text-muted" style={{ fontSize: '0.9rem', marginTop: '4px', maxWidth: '650px' }}>
              Provision developer credentials, assign developers to project repositories, and monitor source code permissions.
            </p>
          </div>

          <button onClick={handleOpenCreateModal} className="btn btn-primary flex items-center gap-2">
            <UserPlus size={16} />
            <span>Add Developer</span>
          </button>
        </div>
      </div>

      {/* 2. KPI Metrics Section */}
      <div className="grid grid-cols-3 gap-6">
        <div className="card dashboard-kpi-card">
          <div className="kpi-icon-box bg-primary-light text-primary">
            <Code2 size={24} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label text-muted">Project Developers</span>
            <h3 className="kpi-value font-display">{loading ? '...' : developers.length}</h3>
            <span className="kpi-trend text-success flex items-center gap-1">
              <CheckCircle2 size={12} />
              <span>{activeDevsCount} Active Engineers</span>
            </span>
          </div>
        </div>

        <div className="card dashboard-kpi-card" style={{ borderLeft: '4px solid var(--success)' }}>
          <div className="kpi-icon-box bg-success-light text-success">
            <FolderKanban size={24} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label text-muted">Active Assignments</span>
            <h3 className="kpi-value font-display text-success">{loading ? '...' : totalAssignmentsCount}</h3>
            <span className="kpi-trend text-primary flex items-center gap-1">
              <Layers size={12} />
              <span>Assigned Projects</span>
            </span>
          </div>
        </div>

        <div className="card dashboard-kpi-card" style={{ borderLeft: '4px solid var(--warning)' }}>
          <div className="kpi-icon-box bg-warning-light text-warning">
            <Clock size={24} />
          </div>
          <div className="kpi-content">
            <span className="kpi-label text-muted">Available Projects</span>
            <h3 className="kpi-value font-display text-warning">{loading ? '...' : projects.length}</h3>
            <span className="kpi-trend text-warning flex items-center gap-1">
              <FolderKanban size={12} />
              <span>Repository Catalog</span>
            </span>
          </div>
        </div>
      </div>

      {/* Alert Banners */}
      {success && (
        <div className="alert alert-success flex items-center gap-2" style={{ padding: '12px 16px', borderRadius: '8px' }}>
          <Check size={16} />
          <span>{success}</span>
        </div>
      )}
      {error && (
        <div className="alert alert-danger flex items-center gap-2" style={{ padding: '12px 16px', borderRadius: '8px' }}>
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* 3. Search & Filter Bar */}
      <div className="card flex justify-between items-center gap-4 flex-wrap" style={{ padding: '16px 24px' }}>
        <div className="search-box" style={{ flex: 1, maxWidth: '450px', position: 'relative' }}>
          <Search size={18} className="search-icon" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="form-control"
            placeholder="Search developer by name or email address..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ paddingLeft: '42px', width: '100%' }}
          />
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Filter size={14} className="text-muted" />
            <select 
              value={statusFilter} 
              onChange={(e) => setStatusFilter(e.target.value)}
              className="form-control form-select"
              style={{ minWidth: '150px' }}
            >
              <option value="">All Statuses</option>
              <option value="ACTIVE">Active Developers</option>
              <option value="INACTIVE">Inactive Developers</option>
            </select>
          </div>
        </div>
      </div>

      {/* 4. Developer Directory Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-responsive">
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
            <thead style={{ backgroundColor: 'var(--bg-main)', borderBottom: '1px solid var(--border-color)' }}>
              <tr>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600 }}>Developer</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600 }}>Organization / Dept</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: 600 }}>Assigned Projects</th>
                <th style={{ padding: '12px 16px', textAlign: 'center', fontWeight: 600 }}>Status</th>
                <th style={{ padding: '12px 16px', textAlign: 'right', fontWeight: 600 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="5" style={{ padding: '36px', textAlign: 'center', color: 'var(--text-muted)' }}>
                    Loading developer directories...
                  </td>
                </tr>
              ) : developers.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ padding: '48px 16px', textAlign: 'center' }}>
                    <Code2 size={40} className="text-muted mb-2 inline" />
                    <h4 style={{ fontSize: '1rem', fontWeight: 600, margin: '8px 0 4px 0' }}>No developers found</h4>
                    <p className="text-muted" style={{ fontSize: '0.84rem' }}>
                      Click "Add Developer" above to register your first project developer.
                    </p>
                  </td>
                </tr>
              ) : (
                developers.map((dev) => {
                  const devAssignments = assignmentsMap[dev.id] || [];
                  const isDevActive = dev.status === 'ACTIVE';

                  return (
                    <tr key={dev.id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background-color 0.15s' }}>
                      <td style={{ padding: '12px 16px' }}>
                        <div className="flex items-center gap-3">
                          <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.88rem' }}>
                            {dev.fullName ? dev.fullName.substring(0, 2).toUpperCase() : 'DV'}
                          </div>
                          <div>
                            <span style={{ fontWeight: 600, display: 'block', color: 'var(--text-main)' }}>{dev.fullName}</span>
                            <span className="text-muted" style={{ fontSize: '0.78rem' }}>{dev.email}</span>
                          </div>
                        </div>
                      </td>

                      <td style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>
                        <div>{dev.organization || 'Academic Development Team'}</div>
                        {dev.department && <span style={{ fontSize: '0.76rem', color: 'var(--primary)' }}>{dev.department}</span>}
                      </td>

                      <td style={{ padding: '12px 16px' }}>
                        {devAssignments.length > 0 ? (
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span className="badge badge-primary" style={{ fontSize: '0.75rem' }}>
                              {devAssignments.length} Project{devAssignments.length > 1 ? 's' : ''} Assigned
                            </span>
                          </div>
                        ) : (
                          <span className="text-muted" style={{ fontSize: '0.78rem' }}>No projects assigned</span>
                        )}
                      </td>

                      <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                        <button
                          onClick={() => handleToggleStatus(dev)}
                          className={`badge ${isDevActive ? 'badge-success' : 'badge-danger'}`}
                          style={{ cursor: 'pointer', border: 'none', padding: '4px 10px', fontSize: '0.75rem' }}
                          title="Click to toggle status"
                        >
                          {dev.status}
                        </button>
                      </td>

                      <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleOpenAssignModal(dev)}
                            className="btn btn-secondary flex items-center gap-1"
                            style={{ padding: '5px 10px', fontSize: '0.78rem' }}
                            title="Assign developer to project"
                          >
                            <FolderKanban size={14} />
                            <span>Assign Project</span>
                          </button>

                          <button
                            onClick={() => handleOpenEditModal(dev)}
                            className="btn btn-secondary"
                            style={{ padding: '6px 8px' }}
                            title="Edit Profile"
                          >
                            <Edit3 size={14} />
                          </button>

                          <button
                            onClick={() => handleDeleteDev(dev.id, dev.fullName)}
                            className="btn btn-secondary text-error"
                            style={{ padding: '6px 8px', borderColor: 'rgba(239, 68, 68, 0.3)' }}
                            title="Delete Developer"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Create / Edit Developer Modal */}
      {modalOpen && (
        <div className="modal-overlay" style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(15, 23, 42, 0.75)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(6px)', padding: '20px' }}>
          <div className="modal-content" style={{ width: '100%', maxWidth: '520px', backgroundColor: 'var(--bg-card, #ffffff)', borderRadius: '14px', border: '1px solid var(--border-color)', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)', overflow: 'hidden' }}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="flex items-center gap-2.5">
                <Code2 size={20} className="text-primary" />
                <h3 className="font-display" style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0 }}>
                  {editingDev ? 'Edit Developer Account' : 'Provision Project Developer'}
                </h3>
              </div>
              <button onClick={handleCloseModal} className="btn btn-secondary" style={{ padding: '4px', border: 'none', background: 'transparent' }}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSubmit} style={{ padding: '24px' }}>
              <div className="form-group mb-3">
                <label className="form-label" style={{ fontSize: '0.84rem', fontWeight: 600 }}>Full Name *</label>
                <input
                  type="text"
                  name="fullName"
                  className="form-control"
                  placeholder="e.g. Vikramaditya Dev"
                  value={formData.fullName}
                  onChange={handleFormChange}
                  required
                />
              </div>

              <div className="form-group mb-3">
                <label className="form-label" style={{ fontSize: '0.84rem', fontWeight: 600 }}>Email Address *</label>
                <input
                  type="email"
                  name="email"
                  className="form-control"
                  placeholder="e.g. vikram@academic.edu"
                  value={formData.email}
                  onChange={handleFormChange}
                  required
                />
              </div>

              <div className="form-group mb-3">
                <label className="form-label" style={{ fontSize: '0.84rem', fontWeight: 600 }}>
                  Password {editingDev && <span className="text-muted" style={{ fontWeight: 400 }}>(leave blank to keep current)</span>}
                </label>
                <input
                  type="password"
                  name="password"
                  className="form-control"
                  placeholder={editingDev ? "••••••••" : "Choose a secure password"}
                  value={formData.password}
                  onChange={handleFormChange}
                  required={!editingDev}
                />
              </div>

              <div className="grid grid-cols-2 gap-3 mb-3">
                <div className="form-group">
                  <label className="form-label" style={{ fontSize: '0.84rem', fontWeight: 600 }}>Department</label>
                  <input
                    type="text"
                    name="department"
                    className="form-control"
                    placeholder="e.g. Data Science"
                    value={formData.department}
                    onChange={handleFormChange}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" style={{ fontSize: '0.84rem', fontWeight: 600 }}>Phone</label>
                  <input
                    type="text"
                    name="phone"
                    className="form-control"
                    placeholder="9876543210"
                    value={formData.phone}
                    onChange={handleFormChange}
                  />
                </div>
              </div>

              <div className="form-group mb-4">
                <label className="form-label" style={{ fontSize: '0.84rem', fontWeight: 600 }}>Account Status</label>
                <select
                  name="status"
                  className="form-control form-select"
                  value={formData.status}
                  onChange={handleFormChange}
                >
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="INACTIVE">INACTIVE</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-2" style={{ borderTop: '1px solid var(--border-color)' }}>
                <button type="button" onClick={handleCloseModal} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingDev ? 'Save Profile' : 'Create Developer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 6. Assign Developer to Project Modal */}
      {assignModalOpen && selectedDevForAssign && (
        <div className="modal-overlay" style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(15, 23, 42, 0.75)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(6px)', padding: '20px' }}>
          <div className="modal-content" style={{ width: '100%', maxWidth: '540px', backgroundColor: 'var(--bg-card, #ffffff)', borderRadius: '14px', border: '1px solid var(--border-color)', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)', overflow: 'hidden' }}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="flex items-center gap-2.5">
                <FolderKanban size={20} className="text-primary" />
                <h3 className="font-display" style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0 }}>
                  Assign Project to Developer
                </h3>
              </div>
              <button onClick={() => setAssignModalOpen(false)} className="btn btn-secondary" style={{ padding: '4px', border: 'none', background: 'transparent' }}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleAssignProjectSubmit} style={{ padding: '24px' }}>
              <div className="mb-4" style={{ backgroundColor: 'var(--bg-main)', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <span className="text-muted" style={{ fontSize: '0.78rem', display: 'block' }}>Target Developer</span>
                <span style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)' }}>{selectedDevForAssign.fullName}</span>
                <span className="text-muted" style={{ fontSize: '0.78rem', display: 'block' }}>{selectedDevForAssign.email}</span>
              </div>

              <div className="form-group mb-3">
                <label className="form-label" style={{ fontSize: '0.84rem', fontWeight: 600 }}>Select Project Repository *</label>
                <select
                  className="form-control form-select"
                  value={assignFormData.projectId}
                  onChange={(e) => setAssignFormData({ ...assignFormData, projectId: e.target.value })}
                  required
                >
                  <option value="">-- Select a Project --</option>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      #{p.id} - {p.title || p.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group mb-3">
                <label className="form-label" style={{ fontSize: '0.84rem', fontWeight: 600 }}>Assignment Instructions / Notes</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. Lead developer for modules & datasets"
                  value={assignFormData.notes}
                  onChange={(e) => setAssignFormData({ ...assignFormData, notes: e.target.value })}
                />
              </div>

              <div className="form-group mb-4">
                <label className="form-label" style={{ fontSize: '0.84rem', fontWeight: 600 }}>Access Expiry Deadline (Optional)</label>
                <input
                  type="datetime-local"
                  className="form-control"
                  value={assignFormData.expiredAt}
                  onChange={(e) => setAssignFormData({ ...assignFormData, expiredAt: e.target.value })}
                />
              </div>

              <div className="flex justify-end gap-3 pt-2" style={{ borderTop: '1px solid var(--border-color)' }}>
                <button type="button" onClick={() => setAssignModalOpen(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={assignLoading} className="btn btn-primary flex items-center gap-2">
                  <CheckCircle2 size={16} />
                  <span>{assignLoading ? 'Assigning...' : 'Assign Project'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default DeveloperManagement;
