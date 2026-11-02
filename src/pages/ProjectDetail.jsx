import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { 
  ArrowLeft, 
  FolderKanban, 
  UserPlus, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  UserCheck, 
  UserX, 
  FileText, 
  IndianRupee, 
  Code, 
  ShieldCheck, 
  Calendar,
  Folder,
  Layers,
  Users,
  Lock
} from 'lucide-react';
import FolderExplorer from '../components/FolderExplorer';
import { formatDate, toDateInputValue, isDeadlineExpired } from '../utils/dateUtils';

const ProjectDetail = () => {
  const { id, folderId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [project, setProject] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Assign User Modal State
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [usersList, setUsersList] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [assignmentNotes, setAssignmentNotes] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [activeTab, setActiveTab] = useState('folders');
  const [selectedAdminForAssignment, setSelectedAdminForAssignment] = useState(undefined);
  const [adminAssignmentDeadline, setAdminAssignmentDeadline] = useState('');
  const [assignmentStatusModal, setAssignmentStatusModal] = useState(null);
  const isSuperAdmin = user?.role === 'SUPER_ADMIN';
  const isAdmin = user?.role === 'ADMIN';
  const canAssign = isSuperAdmin;
  const canManageStatus = isSuperAdmin;

  const [linkedReq, setLinkedReq] = useState(null);
  const [activeFolder, setActiveFolder] = useState(null);

  useEffect(() => {
    fetchProjectAndAssignments();
  }, [id]);

  const fetchProjectAndAssignments = async () => {
    try {
      setLoading(true);
      setError('');

      const [proj, assignList] = await Promise.all([
        api.getProjectById(id),
        api.getProjectAssignments(id)
      ]);

      setProject(proj);
      setAssignments(assignList);

      // Find active admin assignment from assignList or proj.assignedUserId
      const activeAdminAssignment = assignList.find(a => a.active && (a.user?.role === 'ADMIN' || a.user?.role === 'SUPER_ADMIN'));
      const activeAdminId = activeAdminAssignment ? activeAdminAssignment.user.id : (proj.assignedUserId || '');
      setSelectedAdminForAssignment(activeAdminId ? String(activeAdminId) : '');
      if (activeAdminAssignment && activeAdminAssignment.expiredAt) {
        setAdminAssignmentDeadline(toDateInputValue(activeAdminAssignment.expiredAt));
      } else {
        setAdminAssignmentDeadline('');
      }

      if (proj && proj.linkedRequirementId) {
        try {
          const reqData = await api.getRequirementById(proj.linkedRequirementId);
          setLinkedReq(reqData);
        } catch (e) {
          console.warn('Could not fetch linked requirement details', e);
        }
      }

      if (canAssign) {
        const uList = await api.getAdmins();
        setUsersList(uList.filter(u => u.role === 'ADMIN' || u.role === 'SUPER_ADMIN'));
      }
    } catch (err) {
      setError(err.message || 'Failed to load project details');
    } finally {
      setLoading(false);
    }
  };

  const [paying, setPaying] = useState(false);

  const handlePayRemaining = async () => {
    if (!project) return;
    setPaying(true);
    setError('');
    setSuccess('');
    try {
      const idempotencyKey = 'rem_' + project.id + '_' + Date.now();
      await api.payProjectRemaining(project.id, project.remainingAmount || (project.budget ? project.budget * 0.5 : 200.0), idempotencyKey);
      setSuccess('Remaining balance payment verified! Full project deliverables and source files are now unlocked.');
      await fetchProjectAndAssignments();
    } catch (err) {
      setError(err.message || 'Failed to process remaining payment.');
    } finally {
      setPaying(false);
    }
  };

  const handleOpenAssignModal = async () => {
    try {
      const uList = await api.getAdmins();
      setUsersList(uList.filter(u => u.role === 'ADMIN'));
      setIsAssignModalOpen(true);
    } catch (err) {
      setError(err.message || 'Failed to load administrator accounts');
    }
  };

  const handleStatusChange = async (targetStatus) => {
    try {
      setError('');
      setSuccess('');
      const updated = await api.updateProjectStatus(id, targetStatus);
      setProject(updated);
      setSuccess(`Project status successfully transitioned to ${targetStatus}!`);
    } catch (err) {
      setError(err.message || `Failed to transition status to ${targetStatus}`);
    }
  };

  const handleAssignSubmit = async (e) => {
    e.preventDefault();
    if (!selectedUserId) return;

    try {
      setError('');
      setSuccess('');

      const payload = {
        userId: Number(selectedUserId),
        notes: assignmentNotes,
        expiredAt: expiryDate || null
      };

      await api.assignUserToProject(id, payload);
      setSuccess('Administrator successfully assigned to project!');
      setIsAssignModalOpen(false);
      setSelectedUserId('');
      setAssignmentNotes('');
      setExpiryDate('');
      fetchProjectAndAssignments();
    } catch (err) {
      setError(err.message || 'Failed to assign administrator');
    }
  };

  const handleRevokeAssignment = async (assignmentId) => {
    if (!window.confirm('Are you sure you want to revoke this administrator assignment?')) return;

    try {
      setError('');
      setSuccess('');
      await api.deleteAssignment(id, assignmentId);
      setSuccess('Project assignment revoked successfully.');
      fetchProjectAndAssignments();
    } catch (err) {
      setError(err.message || 'Failed to revoke assignment');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'DRAFT': return <span className="badge badge-secondary">DRAFT</span>;
      case 'APPROVED': return <span className="badge badge-primary">APPROVED</span>;
      case 'IN_PROGRESS': return <span className="badge badge-warning">IN PROGRESS</span>;
      case 'COMPLETED': return <span className="badge badge-success">COMPLETED</span>;
      case 'REJECTED': return <span className="badge badge-danger">REJECTED</span>;
      case 'INACTIVE': return <span className="badge" style={{ backgroundColor: 'var(--text-muted)', color: '#fff' }}>INACTIVE</span>;
      default: return <span className="badge">{status}</span>;
    }
  };

  if (loading) {
    return (
      <div className="card text-center" style={{ padding: '60px' }}>
        <div style={{ border: '3px solid var(--border-color)', borderTop: '3px solid var(--primary)', borderRadius: '50%', width: '32px', height: '32px', animation: 'spin 1s linear infinite', margin: '0 auto 12px' }}></div>
        <p className="text-muted">Loading project workspace...</p>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="card text-center" style={{ padding: '40px' }}>
        <AlertCircle size={36} style={{ color: 'var(--error)', margin: '0 auto 12px' }} />
        <h4 className="font-display">Project Not Found</h4>
        <button className="btn btn-secondary" style={{ marginTop: '16px' }} onClick={() => navigate('/projects')}>
          Back to Projects
        </button>
      </div>
    );
  }

  const isAssignedAdmin = assignments.some(
    a => a.active && (a.user?.id === user?.id || a.user?.email === user?.email)
  );

  return (
    <div className="project-detail-wrapper flex flex-col gap-4">
      {/* Alert Banners */}
      {success && (
        <div className="alert alert-success">
          <CheckCircle2 size={16} />
          <span>{success}</span>
        </div>
      )}
      {error && (
        <div className="alert alert-danger">
          <XCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Header Bar */}
      <div className="flex justify-between items-center card" style={{ padding: '20px' }}>
        <div className="flex items-center gap-3">
          <button className="btn btn-secondary flex items-center gap-1" onClick={() => navigate('/projects')}>
            <ArrowLeft size={16} />
            <span>Back to Projects</span>
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-muted font-mono" style={{ fontSize: '0.85rem' }}>{project.projectCode}</span>
              {getStatusBadge(project.status)}
            </div>
            <h2 className="font-display" style={{ fontSize: '1.4rem', fontWeight: 700, marginTop: '2px' }}>
              {project.projectName}
            </h2>
          </div>
        </div>
      </div>

      {/* Project Specifications & Associated Requirements (Only visible on Project Root, hidden inside folder view) */}
      {!folderId && !activeFolder && (
        <div className="card" style={{ padding: '24px' }}>
          <h3 className="font-display" style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px' }}>
            Project Specifications
          </h3>

          <p className="text-muted" style={{ fontSize: '0.95rem', lineHeight: '1.6', marginBottom: '24px' }}>
            {project.description || 'No detailed description provided.'}
          </p>

          <div className="grid grid-cols-3 gap-4" style={{ paddingTop: '16px', borderTop: '1px solid var(--border-color)', marginBottom: '16px' }}>
            <div>
              <span className="text-muted" style={{ fontSize: '0.8rem', display: 'block' }}>Project Budget</span>
              <strong style={{ fontSize: '1.1rem', color: 'var(--primary)' }}>
                Rs. {project.budget != null ? project.budget.toLocaleString(undefined, { minimumFractionDigits: 2 }) : '0.00'}
              </strong>
            </div>
            <div>
              <span className="text-muted" style={{ fontSize: '0.8rem', display: 'block' }}>Technology Stack</span>
              <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{project.technologyStack || 'Not specified'}</span>
            </div>
            <div>
              <span className="text-muted" style={{ fontSize: '0.8rem', display: 'block' }}>Linked Requirement</span>
              {project.linkedRequirementId ? (
                <Link to={`/requirements/${project.linkedRequirementId}`} className="text-primary font-semibold hover:underline" style={{ fontSize: '0.9rem' }}>
                  Requirement #{project.linkedRequirementId} &rarr;
                </Link>
              ) : (
                <span style={{ fontSize: '0.9rem', fontWeight: 600 }} className="text-muted">Direct Creation (None)</span>
              )}
            </div>
          </div>

          {/* Super Admin Exclusive: Assign Managing Administrator Section */}
          {user?.role === 'SUPER_ADMIN' && (
            <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', padding: '20px', borderRadius: 'var(--radius-md)' }}>
              <div className="flex justify-between items-center gap-6 flex-wrap">
                <div style={{ flex: '1 1 280px' }}>
                  <div style={{ marginBottom: '4px' }}>
                    <span style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.6px', color: 'var(--primary)' }}>
                      Super Admin Clearance
                    </span>
                  </div>
                  <h4 className="font-display" style={{ fontSize: '1.05rem', fontWeight: 700, margin: '0 0 4px 0' }}>
                    Managing Administrator Assignment
                  </h4>
                  <p className="text-muted" style={{ fontSize: '0.82rem', margin: 0, lineHeight: '1.4' }}>
                    Assign an Administrator to manage folder structure and user access for this project.
                  </p>
                </div>

                <div className="flex items-end gap-3 flex-wrap">
                  <div style={{ width: '220px' }}>
                    <label style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: '6px' }}>
                      Select Administrator
                    </label>
                    <select
                      className="form-control form-select"
                      style={{ fontSize: '0.85rem', height: '38px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}
                      value={selectedAdminForAssignment !== undefined ? selectedAdminForAssignment : (project.assignedUserId || '')}
                      onChange={(e) => setSelectedAdminForAssignment(e.target.value)}
                    >
                      <option value="">Unassigned (No Admin)</option>
                      {usersList.map(u => (
                        <option key={u.id} value={u.id}>{u.fullName} ({u.email})</option>
                      ))}
                    </select>
                  </div>

                  <div style={{ width: '160px' }}>
                    <label style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: '6px' }}>
                      Assignment Deadline
                    </label>
                    <input
                      type="date"
                      className="form-control"
                      style={{ fontSize: '0.85rem', height: '38px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}
                      value={adminAssignmentDeadline}
                      onChange={(e) => setAdminAssignmentDeadline(e.target.value)}
                    />
                  </div>

                  <div>
                    <button
                      type="button"
                      className="btn btn-primary flex items-center justify-center gap-1.5"
                      style={{ padding: '0 18px', fontSize: '0.85rem', fontWeight: 600, whiteSpace: 'nowrap', height: '38px', borderRadius: 'var(--radius-md)' }}
                      onClick={async () => {
                        try {
                          setError('');
                          setSuccess('');
                          const targetId = selectedAdminForAssignment !== undefined ? selectedAdminForAssignment : project.assignedUserId;
                          if (!targetId) {
                            setAssignmentStatusModal({
                              show: true,
                              type: 'error',
                              title: 'Assignment Status Failed',
                              message: 'Please select an Administrator from the dropdown before clicking Assign Project.',
                              details: null
                            });
                            return;
                          }
                          const targetAdminId = Number(targetId);
                          const assignedAdminObj = usersList.find(u => u.id === targetAdminId);

                          await api.assignProjectAdmin(project.id, targetAdminId, adminAssignmentDeadline || null);
                          await fetchProjectAndAssignments();

                          setAssignmentStatusModal({
                            show: true,
                            type: 'success',
                            title: 'Project Assignment Status',
                            message: targetAdminId 
                              ? `Project '${project.projectName}' (${project.projectCode}) has been successfully assigned!` 
                              : `Project assignment for '${project.projectName}' has been cleared (Unassigned).`,
                            details: {
                              projectCode: project.projectCode,
                              projectName: project.projectName,
                              assignedAdmin: assignedAdminObj ? `${assignedAdminObj.fullName} (${assignedAdminObj.email})` : 'Unassigned (No Admin)',
                              deadline: adminAssignmentDeadline ? formatDate(adminAssignmentDeadline) : 'Permanent (No Deadline)',
                              assignedBy: user?.email || 'superadmin@academic.com',
                              targetTable: 'project_assignments',
                              status: targetAdminId ? 'ACTIVE_ASSIGNMENT' : 'UNASSIGNED',
                              assignedAt: new Date().toLocaleString()
                            }
                          });
                        } catch (err) {
                          setAssignmentStatusModal({
                            show: true,
                            type: 'error',
                            title: 'Assignment Status Failed',
                            message: err.message || 'Failed to update project assignment in database.',
                            details: null
                          });
                        }
                      }}
                    >
                      <ShieldCheck size={16} />
                      <span>Assign Project</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Locked Deliverables Banner for Users */}
      {user?.role === 'USER' && (
        (project.isMarketplace && !project.purchasedByUserId) ||
        (!project.isMarketplace && project.remainingPaymentStatus !== 'COMPLETED')
      ) ? (
        <div className="card" style={{
          padding: '36px 28px',
          background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(245, 158, 11, 0.08))',
          border: '1px solid rgba(245, 158, 11, 0.35)',
          borderRadius: 'var(--radius-xl)',
          textAlign: 'center',
          boxShadow: '0 12px 28px rgba(0,0,0,0.2)'
        }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '16px',
            background: 'rgba(245, 158, 11, 0.15)',
            color: '#f59e0b',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px auto'
          }}>
            <Lock size={28} />
          </div>

          <h3 style={{ fontSize: '1.3rem', fontWeight: 700, margin: '0 0 8px 0', color: 'var(--text-main)' }}>
            Project Deliverables & Repository Locked
          </h3>

          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', maxWidth: '540px', margin: '0 auto 24px auto', lineHeight: 1.6 }}>
            {project.isMarketplace 
              ? 'This marketplace project requires full purchase payment before repository files and source code can be accessed.'
              : 'Project development and review have been completed. Complete the remaining balance payment to unlock full repository source files and deliverables.'}
          </p>

          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px' }}>
            <button
              onClick={handlePayRemaining}
              disabled={paying}
              className="btn btn-primary"
              style={{
                background: 'linear-gradient(135deg, #10b981, #059669)',
                border: 'none',
                padding: '12px 24px',
                fontSize: '0.95rem',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <IndianRupee size={18} />
              {paying ? 'Verifying Payment...' : `Pay Remaining Balance (Rs. ${project.remainingAmount != null ? project.remainingAmount.toFixed(2) : (project.budget != null ? (project.budget * 0.5).toFixed(2) : '200.00')}) & Unlock`}
            </button>
          </div>
        </div>
      ) : (
        /* Project Root Folders & Secure Repository Explorer */
        <FolderExplorer 
          project={project} 
          onFolderChange={(folder) => setActiveFolder(folder)}
        />
      )}

      {/* TAB 2: Project Assignments Section */}
      {activeTab === 'team' && (
        <div className="card" style={{ padding: '24px' }}>

          <div className="flex justify-between items-center" style={{ marginBottom: '20px' }}>
            <div>
              <h3 className="font-display" style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                Team Assignments & Access Control
              </h3>
              <p className="text-muted" style={{ fontSize: '0.8rem' }}>
                `PROJECT_ASSIGNMENT` table records defining active user and administrator access for this project.
              </p>
            </div>

            {canAssign && (
              <button className="btn btn-primary flex items-center gap-2" onClick={handleOpenAssignModal}>
                <UserPlus size={16} />
                <span>Assign User</span>
              </button>
            )}
          </div>

          {assignments.length === 0 ? (
            <div className="text-center" style={{ padding: '32px 16px', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-md)' }}>
              <UserX size={32} style={{ color: 'var(--text-muted)', margin: '0 auto 8px' }} />
              <p className="text-muted" style={{ fontSize: '0.9rem' }}>No users are currently assigned to this project.</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table" style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border-color)', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px' }}>Assigned User</th>
                    <th style={{ padding: '12px' }}>Role / Notes</th>
                    <th style={{ padding: '12px' }}>Assigned Date</th>
                    <th style={{ padding: '12px' }}>Expiry Date</th>
                    <th style={{ padding: '12px' }}>Access Status</th>
                    {canAssign && <th style={{ padding: '12px', textAlign: 'right' }}>Actions</th>}
                  </tr>
                </thead>
                <tbody>
                  {assignments.map((assignment) => {
                    const isExpired = isDeadlineExpired(assignment.expiredAt);
                    const isCurrentlyActive = assignment.active && !isExpired;

                    return (
                      <tr key={assignment.id} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.9rem', backgroundColor: isExpired && assignment.active ? 'rgba(239, 68, 68, 0.05)' : 'transparent' }}>
                        <td style={{ padding: '12px' }}>
                          <div style={{ fontWeight: 600 }}>{assignment.user?.fullName}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{assignment.user?.email}</div>
                        </td>

                        <td style={{ padding: '12px' }}>
                          {assignment.notes || 'Project Member'}
                        </td>

                        <td style={{ padding: '12px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          {formatDate(assignment.assignedAt)}
                        </td>

                        <td style={{ padding: '12px', fontSize: '0.8rem', color: isExpired ? 'var(--error)' : 'var(--text-muted)', fontWeight: isExpired ? 600 : 400 }}>
                          {formatDate(assignment.expiredAt, 'Never (Permanent)')}
                        </td>

                        <td style={{ padding: '12px' }}>
                          {isCurrentlyActive ? (
                            <span className="badge badge-success"><ShieldCheck size={12} /> ACTIVE</span>
                          ) : isExpired && assignment.active ? (
                            <span className="badge badge-danger"><Clock size={12} /> EXPIRED (PENDING REVOCATION)</span>
                          ) : (
                            <span className="badge badge-secondary">REVOKED</span>
                          )}
                        </td>

                        {canAssign && (
                          <td style={{ padding: '12px', textAlign: 'right' }}>
                            {assignment.active && (
                              <button 
                                className="btn btn-secondary btn-sm" 
                                style={{ color: 'var(--error)', borderColor: 'var(--error)', padding: '6px 12px', fontSize: '0.75rem', fontWeight: 600 }}
                                onClick={() => handleRevokeAssignment(assignment.id)}
                                title="Revoke and deactivate access for this project assignment"
                              >
                                Revoke Access
                              </button>
                            )}
                          </td>
                        )}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: State Machine Lifecycle Actions */}
      {activeTab === 'lifecycle' && canManageStatus && (
        <div className="card" style={{ padding: '20px', marginBottom: '24px', backgroundColor: 'var(--bg-main)' }}>
          <h4 className="font-display" style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>
            Project Lifecycle & State Machine Actions
          </h4>

          <p className="text-muted" style={{ fontSize: '0.8rem', marginBottom: '16px' }}>
            Current Status: <strong>{project.status}</strong>. Click an allowed target status button below to execute a valid state transition:
          </p>

          <div className="flex flex-wrap gap-2">
            {(project.status === 'DRAFT' || project.status === 'APPROVED') && (
              <>
                <button className="btn btn-primary" onClick={() => handleStatusChange('IN_PROGRESS')}>
                  Start Development (IN PROGRESS)
                </button>
                <button className="btn btn-secondary" onClick={() => handleStatusChange('INACTIVE')}>
                  Deactivate Project
                </button>
              </>
            )}

            {project.status === 'IN_PROGRESS' && (
              <>
                <button className="btn btn-success" onClick={() => handleStatusChange('COMPLETED')}>
                  Mark as COMPLETED
                </button>
                <button className="btn btn-secondary" onClick={() => handleStatusChange('INACTIVE')}>
                  Deactivate Project
                </button>
              </>
            )}

            {project.status === 'COMPLETED' && (
              <>
                <button className="btn btn-primary" onClick={() => handleStatusChange('IN_PROGRESS')}>
                  Reopen Development
                </button>
                <button className="btn btn-secondary" onClick={() => handleStatusChange('INACTIVE')}>
                  Deactivate Project
                </button>
              </>
            )}

            {project.status === 'INACTIVE' && (
              <button className="btn btn-primary" onClick={() => handleStatusChange('IN_PROGRESS')}>
                Reactivate Project
              </button>
            )}
          </div>
        </div>
      )}
      {isAssignModalOpen && (
        <div className="modal-backdrop">
          <div className="modal-card card" style={{ maxWidth: '500px', width: '100%', padding: '24px' }}>
            <div className="flex justify-between items-center" style={{ marginBottom: '20px' }}>
              <h3 className="font-display" style={{ fontSize: '1.2rem', fontWeight: 700 }}>Assign Administrator to Project</h3>
              <button className="btn-close" onClick={() => setIsAssignModalOpen(false)}>×</button>
            </div>

            <form onSubmit={handleAssignSubmit}>
              <div className="form-group" style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Select Administrator Account *
                </label>
                <select 
                  className="form-control" 
                  value={selectedUserId} 
                  onChange={(e) => setSelectedUserId(e.target.value)}
                  required
                >
                  <option value="">-- Choose Administrator --</option>
                  {usersList.map(u => (
                    <option key={u.id} value={u.id}>{u.fullName} ({u.email}) - Role: {u.role}</option>
                  ))}
                </select>
              </div>

              <div className="form-group" style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Role / Notes on Project
                </label>
                <input 
                  type="text" 
                  className="form-control" 
                  value={assignmentNotes} 
                  onChange={(e) => setAssignmentNotes(e.target.value)}
                  placeholder="e.g. Lead Project Coordinator" 
                />
              </div>

              <div className="form-group" style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Expiration Date (Optional)
                </label>
                <input 
                  type="date" 
                  className="form-control" 
                  value={expiryDate} 
                  onChange={(e) => setExpiryDate(e.target.value)}
                />
                <small className="text-muted" style={{ fontSize: '0.75rem', display: 'block', marginTop: '4px' }}>
                  Leave empty for permanent access until manually revoked.
                </small>
              </div>

              <div className="flex justify-end gap-3">
                <button type="button" className="btn btn-secondary" onClick={() => setIsAssignModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Confirm Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Super Admin Project Assignment Status Pop-up Modal */}
      {assignmentStatusModal?.show && (
        <div className="modal-backdrop" onClick={() => setAssignmentStatusModal(null)}>
          <div className="card modal-card" style={{ width: '100%', maxWidth: '520px', padding: '24px' }} onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4 pb-2" style={{ borderBottom: '1px solid var(--border-color)' }}>
              <div className="flex items-center gap-2">
                {assignmentStatusModal.type === 'success' ? (
                  <CheckCircle2 size={24} style={{ color: 'var(--success)' }} />
                ) : (
                  <XCircle size={24} style={{ color: 'var(--error)' }} />
                )}
                <h3 className="font-display" style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0 }}>
                  {assignmentStatusModal.title}
                </h3>
              </div>
              <button className="btn-close" onClick={() => setAssignmentStatusModal(null)}>&times;</button>
            </div>

            <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginBottom: '16px' }}>
              {assignmentStatusModal.message}
            </p>

            {assignmentStatusModal.details && (
              <div style={{ backgroundColor: 'var(--bg-main)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '20px' }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--text-muted)', marginBottom: '12px' }}>
                  Recorded Database Assignment Details
                </h4>

                <div className="grid grid-cols-2 gap-3" style={{ fontSize: '0.82rem' }}>
                  <div>
                    <span className="text-muted" style={{ display: 'block' }}>Project Code:</span>
                    <strong>{assignmentStatusModal.details.projectCode}</strong>
                  </div>

                  <div>
                    <span className="text-muted" style={{ display: 'block' }}>Target Table:</span>
                    <strong className="font-mono text-primary">{assignmentStatusModal.details.targetTable}</strong>
                  </div>

                  <div style={{ gridColumn: 'span 2' }}>
                    <span className="text-muted" style={{ display: 'block' }}>Assigned Managing Administrator:</span>
                    <strong style={{ color: 'var(--primary)' }}>{assignmentStatusModal.details.assignedAdmin}</strong>
                  </div>

                  <div>
                    <span className="text-muted" style={{ display: 'block' }}>Assignment Status:</span>
                    <span className="badge badge-success" style={{ fontSize: '0.75rem', marginTop: '2px' }}>
                      {assignmentStatusModal.details.status}
                    </span>
                  </div>

                  <div>
                    <span className="text-muted" style={{ display: 'block' }}>Assigned By (Super Admin):</span>
                    <span>{assignmentStatusModal.details.assignedBy}</span>
                  </div>

                  <div style={{ gridColumn: 'span 2' }}>
                    <span className="text-muted" style={{ display: 'block' }}>Timestamp:</span>
                    <span className="font-mono" style={{ fontSize: '0.78rem' }}>{assignmentStatusModal.details.assignedAt}</span>
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-end">
              <button className="btn btn-primary" onClick={() => setAssignmentStatusModal(null)}>
                Close & Continue
              </button>
            </div>
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
      `}</style>
    </div>
  );
};

export default ProjectDetail;
