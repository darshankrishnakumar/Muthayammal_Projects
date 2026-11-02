import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { 
  ArrowLeft, 
  Send, 
  CheckCircle2, 
  XCircle, 
  Edit, 
  Clock, 
  IndianRupee, 
  Code, 
  User as UserIcon, 
  Calendar, 
  FileText, 
  Image as ImageIcon, 
  Mic, 
  AlertCircle,
  FolderPlus
} from 'lucide-react';

const RequirementDetail = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [requirement, setRequirement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [linkedProject, setLinkedProject] = useState(null);

  const fetchRequirement = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRequirementById(id);
      setRequirement(data);

      if (data && data.status === 'APPROVED') {
        const proj = await api.getProjectByRequirementId(id);
        setLinkedProject(proj);
      }
    } catch (err) {
      console.error('Error loading requirement details:', err);
      setError(err.message || 'Failed to load requirement details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequirement();
  }, [id]);

  const handleSubmit = async () => {
    setActionLoading(true);
    setError(null);
    try {
      const updated = await api.submitRequirement(id);
      setRequirement(updated);
      setMessage('Requirement submitted successfully for admin review.');
    } catch (err) {
      console.error('Error submitting requirement:', err);
      setError(err.message || 'Failed to submit requirement.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleApprove = async () => {
    setActionLoading(true);
    setError(null);
    try {
      const updated = await api.approveRequirement(id);
      setRequirement(updated);
      setMessage('Requirement approved successfully! Ready for Developer 3 Project Creation.');
    } catch (err) {
      console.error('Error approving requirement:', err);
      setError(err.message || 'Failed to approve requirement.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    setActionLoading(true);
    setError(null);
    try {
      const updated = await api.rejectRequirement(id);
      setRequirement(updated);
      setMessage('Requirement has been rejected.');
    } catch (err) {
      console.error('Error rejecting requirement:', err);
      setError(err.message || 'Failed to reject requirement.');
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'DRAFT':
        return <span className="badge badge-secondary" style={{ fontSize: '0.85rem', padding: '6px 12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}><Clock size={14}/> DRAFT</span>;
      case 'SUBMITTED':
        return <span className="badge badge-primary" style={{ fontSize: '0.85rem', padding: '6px 12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}><Send size={14}/> SUBMITTED FOR REVIEW</span>;
      case 'APPROVED':
        return <span className="badge badge-success" style={{ fontSize: '0.85rem', padding: '6px 12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}><CheckCircle2 size={14}/> APPROVED</span>;
      case 'REJECTED':
        return <span className="badge badge-danger" style={{ fontSize: '0.85rem', padding: '6px 12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}><XCircle size={14}/> REJECTED</span>;
      default:
        return <span className="badge badge-secondary">{status}</span>;
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center' }}>
        <div style={{ border: '4px solid var(--border-color)', borderTop: '4px solid var(--primary)', borderRadius: '50%', width: '36px', height: '36px', animation: 'spin 1s linear infinite', margin: '0 auto 12px' }}></div>
        <p className="text-muted">Loading requirement from database...</p>
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error || !requirement) {
    return (
      <div className="card text-left flex flex-col gap-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/requirements')} className="btn btn-secondary" style={{ padding: '8px' }}>
            <ArrowLeft size={18} />
          </button>
          <h2 className="font-display text-xl font-semibold text-error">Error Loading Requirement</h2>
        </div>
        <div className="card" style={{ borderLeft: '4px solid var(--error)', backgroundColor: 'var(--error-light)' }}>
          <p style={{ fontWeight: 600, color: 'var(--error)' }}>{error || 'Requirement not found.'}</p>
        </div>
      </div>
    );
  }

  const isOwner = user && requirement.user && user.id === requirement.user.id;
  const isAdminOrSuper = user && (user.role === 'ADMIN' || user.role === 'SUPER_ADMIN');

  return (
    <div className="requirement-detail-page text-left flex flex-col gap-4">
      {/* Action Header */}
      <div className="card flex justify-between items-center flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/requirements')} className="btn btn-secondary" style={{ padding: '8px' }}>
            <ArrowLeft size={18} />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="font-display text-xl font-semibold">{requirement.title}</h2>
              {getStatusBadge(requirement.status)}
            </div>
            <p className="text-muted text-sm" style={{ marginTop: '2px' }}>
              Requirement ID #{requirement.id} &bull; Created by {requirement.user?.fullName} ({requirement.user?.email})
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {isOwner && requirement.status === 'DRAFT' && (
            <>
              <Link to={`/requirements/${requirement.id}/edit`} className="btn btn-secondary flex items-center gap-2">
                <Edit size={16} />
                <span>Edit</span>
              </Link>
              <button 
                onClick={handleSubmit} 
                className="btn btn-primary flex items-center gap-2"
                disabled={actionLoading}
              >
                <Send size={16} />
                <span>Submit Requirement</span>
              </button>
            </>
          )}

          {isAdminOrSuper && requirement.status === 'SUBMITTED' && (
            <>
              <button 
                onClick={handleReject} 
                className="btn btn-danger flex items-center gap-2"
                disabled={actionLoading}
              >
                <XCircle size={16} />
                <span>Reject</span>
              </button>
              <button 
                onClick={handleApprove} 
                className="btn btn-success flex items-center gap-2"
                disabled={actionLoading}
                style={{ backgroundColor: 'var(--success)', color: 'white' }}
              >
                <CheckCircle2 size={16} />
                <span>Approve Requirement</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Success Notification */}
      {message && (
        <div className="card" style={{ borderLeft: '4px solid var(--success)', backgroundColor: 'var(--success-light)' }}>
          <div className="flex items-center gap-2 text-success">
            <CheckCircle2 size={18} />
            <span style={{ fontWeight: 600 }}>{message}</span>
          </div>
        </div>
      )}

      {/* Developer 3 Workflow Integration Banner */}
      {requirement.status === 'APPROVED' && (
        <div className="card" style={{ borderLeft: '4px solid var(--primary)', backgroundColor: 'var(--primary-light)' }}>
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2 text-primary">
              <FolderPlus size={20} />
              <div>
                <strong style={{ fontSize: '0.95rem' }}>Requirement Approved & Validated</strong>
                <p style={{ fontSize: '0.8rem' }} className="text-muted">
                  {linkedProject 
                    ? `Linked to Active Project ${linkedProject.projectCode} (${linkedProject.projectName}).` 
                    : 'This requirement is ready for Project Creation & Assignment.'}
                </p>
              </div>
            </div>

            {linkedProject ? (
              <Link to={`/projects/${linkedProject.id}`} className="btn btn-primary flex items-center gap-2">
                <FileText size={16} />
                <span>View Linked Project ({linkedProject.projectCode})</span>
              </Link>
            ) : (
              user?.role === 'SUPER_ADMIN' && (
                <Link to={`/projects?createFromReq=${requirement.id}`} className="btn btn-primary flex items-center gap-2">
                  <FolderPlus size={16} />
                  <span>🚀 Initialize Project</span>
                </Link>
              )
            )}
          </div>
        </div>
      )}

      {/* Detail Body Grid */}
      <div className="grid grid-cols-3 gap-4">
        {/* Left 2 Cols: Main Content */}
        <div className="col-span-2 flex flex-col gap-4">
          <div className="card">
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '12px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              Problem Statement
            </h3>
            <p style={{ fontSize: '0.95rem', lineHeight: '1.6', whiteSpace: 'pre-wrap', color: 'var(--text-main)' }}>
              {requirement.problemStatement}
            </p>
          </div>

          {requirement.description && (
            <div className="card">
              <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '12px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
                Detailed Description
              </h3>
              <p style={{ fontSize: '0.95rem', lineHeight: '1.6', whiteSpace: 'pre-wrap', color: 'var(--text-main)' }}>
                {requirement.description}
              </p>
            </div>
          )}
        </div>

        {/* Right 1 Col: Metadata Sidebar */}
        <div className="flex flex-col gap-4">
          <div className="card">
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              Requirement Metadata
            </h3>

            <div className="flex flex-col gap-3" style={{ fontSize: '0.9rem' }}>
              <div className="flex items-center justify-between">
                <span className="text-muted flex items-center gap-2"><IndianRupee size={16} /> Budget</span>
                <span style={{ fontWeight: 600 }}>{requirement.budget ? `Rs. ${Number(requirement.budget).toLocaleString()}` : 'N/A'}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-muted flex items-center gap-2"><Code size={16} /> Tech Stack</span>
                <span style={{ fontWeight: 500 }}>{requirement.technologyStack || 'Unspecified'}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-muted flex items-center gap-2"><UserIcon size={16} /> Owner</span>
                <span style={{ fontWeight: 500 }}>{requirement.user?.fullName}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-muted flex items-center gap-2"><Calendar size={16} /> Created At</span>
                <span style={{ fontSize: '0.8rem' }}>{new Date(requirement.createdAt).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          {/* Media Attachments Card */}
          <div className="card">
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '12px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              Requirement Media Attachments
            </h3>

            <div className="flex flex-col gap-4">
              {/* Image Preview */}
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <ImageIcon size={16} className="text-primary" />
                  <span>Image Attachment</span>
                </div>
                {requirement.imageUrl ? (
                  <div style={{ borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border-color)', backgroundColor: '#000' }}>
                    <img 
                      src={requirement.imageUrl} 
                      alt="Requirement Diagram" 
                      style={{ width: '100%', maxHeight: '200px', objectFit: 'contain', display: 'block' }} 
                    />
                  </div>
                ) : (
                  <p className="text-muted" style={{ fontSize: '0.8rem' }}>No image attachment uploaded.</p>
                )}
              </div>

              {/* Audio Preview */}
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Mic size={16} className="text-primary" />
                  <span>Audio Voice Note</span>
                </div>
                {requirement.audioUrl ? (
                  <div style={{ padding: '8px', border: '1px solid var(--border-color)', borderRadius: '8px', backgroundColor: 'var(--bg-card)' }}>
                    <audio controls src={requirement.audioUrl} style={{ width: '100%', height: '36px' }} />
                  </div>
                ) : (
                  <p className="text-muted" style={{ fontSize: '0.8rem' }}>No audio recording uploaded.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RequirementDetail;
