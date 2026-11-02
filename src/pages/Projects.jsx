import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { 
  FolderKanban, 
  Plus, 
  Search, 
  Filter, 
  FileCheck2, 
  ArrowUpRight, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  XCircle,
  Code,
  IndianRupee,
  UserCheck,
  Folder,
  UserPlus,
  Users,
  Trash2,
  Lock,
  ShieldAlert,
  ShieldCheck
} from 'lucide-react';

const Projects = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [projects, setProjects] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [techFilter, setTechFilter] = useState('');
  const [assignedUserFilter, setAssignedUserFilter] = useState('');
  const [allUsers, setAllUsers] = useState([]);

  // Create Project Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [createMode, setCreateMode] = useState('DIRECT'); // 'DIRECT' or 'REQUIREMENT'
  const [approvedReqs, setApprovedReqs] = useState([]);
  const [selectedReqId, setSelectedReqId] = useState('');

  const [formData, setFormData] = useState({
    projectName: '',
    description: '',
    budget: '',
    technologyStack: '',
    status: 'DRAFT'
  });

  // Assign Project Modal State
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [selectedProjectForAssignment, setSelectedProjectForAssignment] = useState(null);
  const [assignTargetRole, setAssignTargetRole] = useState('ADMIN'); // 'ADMIN' or 'USER'
  const [assignableUsers, setAssignableUsers] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [assignmentNotes, setAssignmentNotes] = useState('');
  const [projectAssignments, setProjectAssignments] = useState([]);
  const [loadingAssignments, setLoadingAssignments] = useState(false);
  const [assignModalError, setAssignModalError] = useState('');
  const [assignModalSuccess, setAssignModalSuccess] = useState('');

  const isSuperAdmin = user?.role === 'SUPER_ADMIN';
  const isAdmin = user?.role === 'ADMIN';
  const canManage = isSuperAdmin || isAdmin;
  const isRegularUser = user?.role === 'USER';

  useEffect(() => {
    fetchData();
  }, [searchQuery, statusFilter, techFilter, assignedUserFilter]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const reqId = params.get('createFromReq');
    if (reqId && isSuperAdmin) {
      handleOpenCreateModalWithReq(reqId);
    }
  }, [isSuperAdmin]);

  const handleOpenCreateModalWithReq = async (reqId) => {
    setIsModalOpen(true);
    setCreateMode('REQUIREMENT');
    setSelectedReqId(String(reqId));

    try {
      const reqs = await api.getApprovedRequirements();
      setApprovedReqs(reqs);
      const req = reqs.find(r => r.id === Number(reqId));
      if (req) {
        setFormData({
          projectName: req.title,
          description: req.description || req.problemStatement,
          budget: req.budget || '',
          technologyStack: req.technologyStack || '',
          status: 'APPROVED'
        });
      }
    } catch (e) {
      console.warn('Failed to auto-select approved requirement', e);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');

      const projectsData = await api.getProjects(searchQuery, statusFilter, techFilter, assignedUserFilter || null);
      setProjects(projectsData || []);

      try {
        const statsData = await api.getProjectDashboard();
        setDashboardStats(statsData?.statusCounts || null);
      } catch (e) {
        console.warn('Dashboard stats load skipped', e);
      }

      if (isSuperAdmin) {
        try {
          const usersData = await api.getAdmins();
          setAllUsers(usersData.filter(u => u.role === 'ADMIN' || u.role === 'SUPER_ADMIN'));
        } catch (e) {
          console.warn('Admins list load skipped', e);
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const loadAssignableUsersForRole = async (targetRole) => {
    try {
      const users = await api.getAssignableUsers(targetRole);
      setAssignableUsers(users || []);
    } catch (err) {
      console.warn('Failed to load assignable users', err);
    }
  };

  const handleOpenAssignModal = async (project, e) => {
    if (e) e.stopPropagation();
    setSelectedProjectForAssignment(project);
    setSelectedUserId('');
    setAssignmentNotes('');
    setAssignModalError('');
    setAssignModalSuccess('');
    
    // Default assignment target: SuperAdmin defaults to ADMIN assignment; Admin can only assign USER
    const initialRole = isSuperAdmin ? 'ADMIN' : 'USER';
    setAssignTargetRole(initialRole);
    setIsAssignModalOpen(true);
    setLoadingAssignments(true);

    try {
      const [users, assignments] = await Promise.all([
        api.getAssignableUsers(initialRole).catch(() => []),
        api.getProjectAssignments(project.id).catch(() => [])
      ]);
      setAssignableUsers(users || []);
      setProjectAssignments(assignments || []);
    } catch (err) {
      setAssignModalError('Failed to load users or assignments');
    } finally {
      setLoadingAssignments(false);
    }
  };

  const handleTargetRoleChange = async (newRole) => {
    setAssignTargetRole(newRole);
    setSelectedUserId('');
    await loadAssignableUsersForRole(newRole);
  };

  const handleAssignSubmit = async (e) => {
    e.preventDefault();
    if (!selectedUserId || !selectedProjectForAssignment) return;

    try {
      setAssignModalError('');
      setAssignModalSuccess('');

      const defaultNote = isSuperAdmin && assignTargetRole === 'ADMIN'
        ? 'Managing Administrator assigned by Super Admin'
        : (assignmentNotes || 'Project assignment');

      await api.assignProjectUser(selectedProjectForAssignment.id, selectedUserId, defaultNote);
      setAssignModalSuccess(
        isSuperAdmin && assignTargetRole === 'ADMIN'
          ? 'Project assigned to Administrator successfully!'
          : 'User assigned to project successfully!'
      );
      setSelectedUserId('');
      setAssignmentNotes('');

      // Refresh assignments list
      const updatedAssignments = await api.getProjectAssignments(selectedProjectForAssignment.id);
      setProjectAssignments(updatedAssignments || []);
      fetchData();
    } catch (err) {
      setAssignModalError(err.message || 'Failed to assign project');
    }
  };

  const handleRemoveAssignment = async (userId) => {
    if (!selectedProjectForAssignment) return;
    try {
      setAssignModalError('');
      setAssignModalSuccess('');

      await api.removeProjectUserAssignment(selectedProjectForAssignment.id, userId);
      setAssignModalSuccess('Assignment removed successfully.');

      // Refresh assignments list
      const updatedAssignments = await api.getProjectAssignments(selectedProjectForAssignment.id);
      setProjectAssignments(updatedAssignments || []);
      fetchData();
    } catch (err) {
      setAssignModalError(err.message || 'Failed to remove assignment');
    }
  };

  const selectedUserObject = assignableUsers.find(u => u.id === Number(selectedUserId));

  const handleOpenCreateModal = async () => {
    setIsModalOpen(true);
    setCreateMode('DIRECT');
    setSelectedReqId('');
    setFormData({
      projectName: '',
      description: '',
      budget: '',
      technologyStack: '',
      status: 'DRAFT',
      assignedUserId: '',
      deadline: ''
    });

    try {
      const reqs = await api.getApprovedRequirements();
      setApprovedReqs(reqs);
    } catch (e) {
      console.warn('Failed to load approved requirements stub', e);
    }
  };

  const handleRequirementSelect = (reqId) => {
    setSelectedReqId(reqId);
    if (!reqId) return;

    const selectedReq = approvedReqs.find(r => r.id === Number(reqId));
    if (selectedReq) {
      setFormData({
        projectName: selectedReq.title,
        description: selectedReq.description,
        budget: selectedReq.budget,
        technologyStack: selectedReq.technologyStack,
        status: 'APPROVED',
        assignedUserId: '',
        deadline: ''
      });
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    try {
      setError('');
      setSuccess('');

      const payload = {
        ...formData,
        budget: formData.budget ? parseFloat(formData.budget) : 0,
        linkedRequirementId: selectedReqId ? Number(selectedReqId) : null
      };

      const created = await api.createProject(payload);

      if (formData.assignedUserId) {
        await api.assignProjectAdmin(created.id, Number(formData.assignedUserId), formData.deadline || null);
      }

      setSuccess(`Project ${created.projectCode} created successfully!`);
      setIsModalOpen(false);
      fetchData();
    } catch (err) {
      setError(err.message || 'Failed to create project');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'DRAFT':
        return <span className="badge badge-secondary"><Clock size={12} /> DRAFT</span>;
      case 'APPROVED':
        return <span className="badge badge-primary"><FileCheck2 size={12} /> APPROVED</span>;
      case 'IN_PROGRESS':
        return <span className="badge badge-warning"><Code size={12} /> IN PROGRESS</span>;
      case 'COMPLETED':
        return <span className="badge badge-success"><CheckCircle2 size={12} /> COMPLETED</span>;
      case 'REJECTED':
        return <span className="badge badge-danger"><XCircle size={12} /> REJECTED</span>;
      case 'INACTIVE':
        return <span className="badge" style={{ backgroundColor: 'var(--text-muted)', color: '#fff' }}>INACTIVE</span>;
      default:
        return <span className="badge">{status}</span>;
    }
  };

  return (
    <div className="projects-container text-left">
      {/* Top Banner / Notification */}
      {error && (
        <div className="card text-error" style={{ padding: '12px 16px', marginBottom: '20px', backgroundColor: 'var(--error-light)', borderColor: 'transparent' }}>
          <AlertCircle size={16} inline style={{ marginRight: '8px' }} />
          {error}
        </div>
      )}
      {success && (
        <div className="card text-success" style={{ padding: '12px 16px', marginBottom: '20px', backgroundColor: 'var(--success-light)', borderColor: 'transparent' }}>
          <CheckCircle2 size={16} inline style={{ marginRight: '8px' }} />
          {success}
        </div>
      )}

      {/* Dashboard Summary Cards */}
      {dashboardStats && (
        <div className="grid grid-cols-4 gap-4" style={{ marginBottom: '24px' }}>
          <div className="card text-left" style={{ padding: '16px' }}>
            <p className="text-muted" style={{ fontSize: '0.8rem', fontWeight: 500 }}>Total Projects</p>
            <h2 className="font-display" style={{ fontSize: '1.8rem', fontWeight: 700, margin: '4px 0' }}>
              {dashboardStats.TOTAL || 0}
            </h2>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {isSuperAdmin ? 'All projects in system' : 'Assigned to your account'}
            </span>
          </div>

          <div className="card text-left" style={{ padding: '16px', borderLeft: '4px solid var(--warning)' }}>
            <p className="text-muted" style={{ fontSize: '0.8rem', fontWeight: 500 }}>Active / In Progress</p>
            <h2 className="font-display" style={{ fontSize: '1.8rem', fontWeight: 700, margin: '4px 0', color: 'var(--warning)' }}>
              {dashboardStats.IN_PROGRESS || 0}
            </h2>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Under development</span>
          </div>

          <div className="card text-left" style={{ padding: '16px', borderLeft: '4px solid var(--primary)' }}>
            <p className="text-muted" style={{ fontSize: '0.8rem', fontWeight: 500 }}>Approved / Ready</p>
            <h2 className="font-display" style={{ fontSize: '1.8rem', fontWeight: 700, margin: '4px 0', color: 'var(--primary)' }}>
              {dashboardStats.APPROVED || 0}
            </h2>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Approved requirements</span>
          </div>

          <div className="card text-left" style={{ padding: '16px', borderLeft: '4px solid var(--success)' }}>
            <p className="text-muted" style={{ fontSize: '0.8rem', fontWeight: 500 }}>Completed</p>
            <h2 className="font-display" style={{ fontSize: '1.8rem', fontWeight: 700, margin: '4px 0', color: 'var(--success)' }}>
              {dashboardStats.COMPLETED || 0}
            </h2>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Delivered projects</span>
          </div>
        </div>
      )}

      {/* Action Header */}
      <div className="flex justify-between items-center flex-wrap gap-4 card" style={{ marginBottom: '24px' }}>
        <div>
          <h2 className="font-display text-xl font-semibold">
            {isSuperAdmin 
              ? 'Academic Projects Directory (Super Admin)' 
              : isAdmin 
                ? 'Assigned Projects Management (Admin)' 
                : 'My Assigned Projects'}
          </h2>
          <p className="text-muted text-sm">
            {isSuperAdmin 
              ? 'Full management: create new projects, assign projects to managing Administrators, and monitor progress.' 
              : isAdmin 
                ? 'Manage projects assigned to you by the Super Admin and assign projects to Users.' 
                : 'View projects that have been assigned to your account.'}
          </p>
        </div>

        {/* ONLY Super Admin can create projects */}
        {isSuperAdmin && (
          <button className="btn btn-primary flex items-center gap-2" onClick={handleOpenCreateModal}>
            <Plus size={18} />
            <span>Create New Project</span>
          </button>
        )}
      </div>

      {/* Filter & Search Bar */}
      <div className="filter-toolbar card" style={{ padding: '16px', marginBottom: '24px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <div className="search-input-wrapper flex-1" style={{ minWidth: '240px', position: 'relative' }}>
          <Search size={16} className="search-icon" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            className="form-control" 
            placeholder="Search projects by name, code, or description..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '36px', width: '100%' }}
          />
        </div>

        <select 
          className="form-control" 
          value={statusFilter} 
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ minWidth: '150px' }}
        >
          <option value="">All Statuses</option>
          <option value="DRAFT">Draft</option>
          <option value="APPROVED">Approved</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="COMPLETED">Completed</option>
          <option value="REJECTED">Rejected</option>
        </select>

        <input 
          type="text" 
          className="form-control" 
          placeholder="Filter by Tech Stack..." 
          value={techFilter}
          onChange={(e) => setTechFilter(e.target.value)}
          style={{ minWidth: '160px' }}
        />
      </div>

      {/* Project Grid / Table */}
      {loading ? (
        <div className="card text-center" style={{ padding: '60px 20px' }}>
          <div style={{ border: '3px solid var(--border-color)', borderTop: '3px solid var(--primary)', borderRadius: '50%', width: '32px', height: '32px', animation: 'spin 1s linear infinite', margin: '0 auto 12px' }}></div>
          <p className="text-muted">Loading projects...</p>
        </div>
      ) : projects.length === 0 ? (
        <div className="card text-center" style={{ padding: '56px 24px' }}>
          <FolderKanban size={48} style={{ margin: '0 auto 16px', color: 'var(--text-muted)', opacity: 0.6 }} />
          <h4 className="font-display" style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '6px' }}>
            {isSuperAdmin 
              ? 'No Projects Found' 
              : isAdmin 
                ? 'No Projects Assigned to You' 
                : 'No Projects Assigned Yet'}
          </h4>
          <p className="text-muted" style={{ fontSize: '0.88rem', maxWidth: '460px', margin: '0 auto 20px', lineHeight: 1.5 }}>
            {isSuperAdmin 
              ? 'No projects matched your search criteria. Click "Create New Project" to register one.' 
              : isAdmin 
                ? 'The Super Admin has not assigned any projects to your Admin account yet. Once assigned, you will be able to manage them and assign Users.' 
                : 'You currently have no assigned projects. Please contact your project administrator to assign access to your account.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {projects.map((project) => (
            <div 
              key={project.id} 
              className="card project-card card-hover" 
              style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', textAlign: 'left' }}
            >
              <div>
                <div className="flex justify-between items-center" style={{ marginBottom: '10px' }}>
                  <span className="code-tag" style={{ background: 'var(--bg-main)', border: '1px solid var(--border-color)', padding: '2px 8px', borderRadius: '4px', fontFamily: 'monospace', fontWeight: 700, fontSize: '0.85rem' }}>
                    {project.projectCode}
                  </span>
                  {getStatusBadge(project.status)}
                </div>

                <h4 className="font-display" style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '6px' }}>
                  {project.projectName}
                </h4>

                <p className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '14px', lineClamp: 2, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {project.description || 'No description provided.'}
                </p>
              </div>

              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '12px', marginTop: '12px' }}>
                <div className="flex justify-between items-center" style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                  <span className="flex items-center gap-1">
                    <IndianRupee size={14} /> Rs. {project.budget ? Number(project.budget).toLocaleString(undefined, { minimumFractionDigits: 2 }) : '0.00'}
                  </span>
                  {project.linkedRequirementId && (
                    <span className="badge badge-info" title="Linked to Requirement">
                      Req #{project.linkedRequirementId}
                    </span>
                  )}
                </div>

                {project.technologyStack && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
                    <strong>Tech:</strong> {project.technologyStack}
                  </div>
                )}

                <div className="flex gap-2 items-center flex-wrap">
                  <button 
                    className="btn btn-primary flex-1 flex items-center justify-center gap-1" 
                    onClick={() => navigate(`/projects/${project.id}`)}
                  >
                    <span>Open Project Folders</span>
                    <ArrowUpRight size={14} />
                  </button>

                  {canManage && (
                    <button 
                      className="btn btn-secondary flex items-center justify-center gap-1"
                      onClick={(e) => handleOpenAssignModal(project, e)}
                      title={isSuperAdmin ? 'Assign Admin or User' : 'Assign to Users'}
                      style={{ padding: '8px 14px', fontSize: '0.85rem' }}
                    >
                      <UserPlus size={15} />
                      <span>{isSuperAdmin ? 'Assign Admin/User' : 'Assign to User'}</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Assign Project Modal */}
      {isAssignModalOpen && selectedProjectForAssignment && (
        <div className="modal-backdrop">
          <div className="modal-card card" style={{ maxWidth: '640px', width: '100%', margin: '40px auto', padding: '24px' }}>
            <div className="flex justify-between items-center" style={{ marginBottom: '18px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
              <div>
                <h3 className="font-display" style={{ fontSize: '1.25rem', fontWeight: 700 }}>
                  {isSuperAdmin ? 'Project Assignment (Super Admin)' : 'Assign Project to Users (Admin)'}
                </h3>
                <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '2px' }}>
                  Project: <strong style={{ color: 'var(--text-main)' }}>{selectedProjectForAssignment.projectName}</strong> ({selectedProjectForAssignment.projectCode})
                </p>
              </div>
              <button className="btn-close" onClick={() => setIsAssignModalOpen(false)}>×</button>
            </div>

            {/* Super Admin Assignment Target Switcher */}
            {isSuperAdmin && (
              <div className="flex gap-2" style={{ marginBottom: '16px', background: 'var(--bg-main)', padding: '6px', borderRadius: '8px' }}>
                <button
                  type="button"
                  className={`btn ${assignTargetRole === 'ADMIN' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ flex: 1, fontSize: '0.85rem', padding: '8px' }}
                  onClick={() => handleTargetRoleChange('ADMIN')}
                >
                  <ShieldCheck size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                  <span>Assign to Admin (Managing)</span>
                </button>
                <button
                  type="button"
                  className={`btn ${assignTargetRole === 'USER' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ flex: 1, fontSize: '0.85rem', padding: '8px' }}
                  onClick={() => handleTargetRoleChange('USER')}
                >
                  <Users size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                  <span>Assign to User</span>
                </button>
              </div>
            )}

            {assignModalError && (
              <div className="card text-error" style={{ padding: '10px 14px', marginBottom: '16px', backgroundColor: 'var(--error-light)', borderColor: 'transparent', fontSize: '0.85rem' }}>
                <AlertCircle size={14} inline style={{ marginRight: '6px' }} />
                {assignModalError}
              </div>
            )}

            {assignModalSuccess && (
              <div className="card text-success" style={{ padding: '10px 14px', marginBottom: '16px', backgroundColor: 'var(--success-light)', borderColor: 'transparent', fontSize: '0.85rem' }}>
                <CheckCircle2 size={14} inline style={{ marginRight: '6px' }} />
                {assignModalSuccess}
              </div>
            )}

            {/* Assignment Form */}
            <form onSubmit={handleAssignSubmit} style={{ marginBottom: '24px' }}>
              <div className="form-group" style={{ marginBottom: '14px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Select {assignTargetRole === 'ADMIN' ? 'Administrator (Role = ADMIN)' : 'User (Role = USER)'} *
                </label>
                <select 
                  className="form-control"
                  value={selectedUserId}
                  onChange={(e) => setSelectedUserId(e.target.value)}
                  required
                >
                  <option value="">-- Select {assignTargetRole === 'ADMIN' ? 'an Administrator' : 'a User'} --</option>
                  {assignableUsers.map(u => (
                    <option key={u.id} value={u.id}>
                      {u.fullName || u.name} ({u.email}) - [{u.role}]
                    </option>
                  ))}
                </select>
              </div>

              {selectedUserObject && (
                <div className="card" style={{ padding: '12px 16px', marginBottom: '14px', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px' }}>SELECTED RECIPIENT</div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>Name: {selectedUserObject.fullName || selectedUserObject.name}</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Email: {selectedUserObject.email}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--success)', marginTop: '2px' }}>Role: {selectedUserObject.role} • Status: ACTIVE</div>
                </div>
              )}

              <div className="form-group" style={{ marginBottom: '18px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Assignment Notes (Optional)
                </label>
                <input 
                  type="text" 
                  className="form-control"
                  placeholder="e.g. Lead Managing Admin / Research access"
                  value={assignmentNotes}
                  onChange={(e) => setAssignmentNotes(e.target.value)}
                />
              </div>

              <div className="flex justify-end gap-2">
                <button type="button" className="btn btn-secondary" onClick={() => setIsAssignModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary flex items-center gap-1">
                  <UserPlus size={15} />
                  <span>Assign Project</span>
                </button>
              </div>
            </form>

            {/* Currently Assigned Users Table */}
            <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Users size={16} />
                <span>Currently Assigned Members ({projectAssignments.length})</span>
              </h4>

              {loadingAssignments ? (
                <p className="text-muted text-sm">Loading assignments...</p>
              ) : projectAssignments.length === 0 ? (
                <p className="text-muted text-sm" style={{ padding: '12px', background: 'var(--bg-main)', borderRadius: '6px' }}>
                  No members are currently assigned to this project.
                </p>
              ) : (
                <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                  <table className="table" style={{ width: '100%', fontSize: '0.85rem', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '8px 4px' }}>NAME</th>
                        <th style={{ padding: '8px 4px' }}>EMAIL</th>
                        <th style={{ padding: '8px 4px' }}>ROLE</th>
                        <th style={{ padding: '8px 4px', textAlign: 'right' }}>ACTION</th>
                      </tr>
                    </thead>
                    <tbody>
                      {projectAssignments.map(a => (
                        <tr key={a.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                          <td style={{ padding: '10px 4px', fontWeight: 600 }}>{a.user?.fullName || a.user?.name || 'Member'}</td>
                          <td style={{ padding: '10px 4px', color: 'var(--text-muted)' }}>{a.user?.email}</td>
                          <td style={{ padding: '10px 4px' }}>
                            <span className={`badge ${a.user?.role === 'ADMIN' ? 'badge-warning' : 'badge-primary'}`} style={{ fontSize: '0.7rem' }}>
                              {a.user?.role || 'USER'}
                            </span>
                          </td>
                          <td style={{ padding: '10px 4px', textAlign: 'right' }}>
                            {/* SuperAdmin can remove any; Admin can only remove USER assignments */}
                            {(isSuperAdmin || (isAdmin && a.user?.role === 'USER')) && (
                              <button 
                                type="button"
                                className="btn btn-secondary btn-sm text-error" 
                                onClick={() => handleRemoveAssignment(a.user?.id)}
                                title="Remove assignment"
                                style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                              >
                                <Trash2 size={13} />
                                <span>Remove</span>
                              </button>
                            )}
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
      )}

      {/* Create Project Modal (SUPER ADMIN ONLY) */}
      {isModalOpen && isSuperAdmin && (
        <div className="modal-backdrop">
          <div className="modal-card card" style={{ maxWidth: '600px', width: '100%', margin: '40px auto', padding: '24px' }}>
            <div className="flex justify-between items-center" style={{ marginBottom: '20px' }}>
              <h3 className="font-display" style={{ fontSize: '1.2rem', fontWeight: 700 }}>Create New Project</h3>
              <button className="btn-close" onClick={() => setIsModalOpen(false)}>×</button>
            </div>

            {/* Creation Method Switcher */}
            <div className="flex gap-2" style={{ marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
              <button 
                type="button"
                className={`btn ${createMode === 'DIRECT' ? 'btn-primary' : 'btn-secondary'}`} 
                style={{ flex: 1, fontSize: '0.85rem' }}
                onClick={() => {
                  setCreateMode('DIRECT');
                  setSelectedReqId('');
                }}
              >
                Direct Creation
              </button>
              <button 
                type="button"
                className={`btn ${createMode === 'REQUIREMENT' ? 'btn-primary' : 'btn-secondary'}`} 
                style={{ flex: 1, fontSize: '0.85rem' }}
                onClick={() => setCreateMode('REQUIREMENT')}
              >
                Import Approved Requirement
              </button>
            </div>

            <form onSubmit={handleCreateSubmit}>
              {createMode === 'REQUIREMENT' && (
                <div className="form-group" style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                    Select Approved Requirement (Developer 2 Stub)
                  </label>
                  <select 
                    className="form-control" 
                    value={selectedReqId} 
                    onChange={(e) => handleRequirementSelect(e.target.value)}
                    required={createMode === 'REQUIREMENT'}
                  >
                    <option value="">-- Choose Approved Requirement --</option>
                    {approvedReqs.map(r => (
                      <option key={r.id} value={r.id}>
                        [Req #{r.id}] {r.title} - Rs. {r.budget} ({r.technologyStack})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="form-group" style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Project Name *
                </label>
                <input 
                  type="text" 
                  className="form-control" 
                  value={formData.projectName} 
                  onChange={(e) => setFormData({ ...formData, projectName: e.target.value })}
                  placeholder="e.g. Automated Grading & Feedback System" 
                  required 
                />
              </div>

              <div className="form-group" style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Description
                </label>
                <textarea 
                  className="form-control" 
                  rows="3" 
                  value={formData.description} 
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Detailed project summary..." 
                />
              </div>

              <div className="grid grid-cols-2 gap-3" style={{ marginBottom: '16px' }}>
                <div className="form-group">
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                    Budget (Rs.)
                  </label>
                  <input 
                    type="number" 
                    step="0.01"
                    className="form-control" 
                    value={formData.budget} 
                    onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                    placeholder="15000.00" 
                  />
                </div>

                <div className="form-group">
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                    Initial Status
                  </label>
                  <select 
                    className="form-control" 
                    value={formData.status} 
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  >
                    <option value="DRAFT">DRAFT</option>
                    <option value="APPROVED">APPROVED</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3" style={{ marginBottom: '16px' }}>
                <div className="form-group">
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                    Assign Managing Administrator
                  </label>
                  <select 
                    className="form-control form-select" 
                    value={formData.assignedUserId || ''} 
                    onChange={(e) => setFormData({ ...formData, assignedUserId: e.target.value ? Number(e.target.value) : null })}
                  >
                    <option value="">-- Select Admin User --</option>
                    {allUsers.map(u => (
                      <option key={u.id} value={u.id}>{u.fullName} ({u.email})</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                    Assignment Deadline
                  </label>
                  <input 
                    type="date"
                    className="form-control" 
                    value={formData.deadline || ''} 
                    onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Technology Stack
                </label>
                <input 
                  type="text" 
                  className="form-control" 
                  value={formData.technologyStack} 
                  onChange={(e) => setFormData({ ...formData, technologyStack: e.target.value })}
                  placeholder="e.g. Java, Spring Boot, React, MySQL" 
                />
              </div>

              <div className="flex justify-end gap-3">
                <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <style>{`
        .modal-backdrop {
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(0, 0, 0, 0.6);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 20px;
        }
        .btn-close {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          color: var(--text-muted);
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Projects;
