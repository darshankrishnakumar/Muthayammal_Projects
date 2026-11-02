import React, { useState, useEffect } from 'react';
import { CheckCircle2, AlertCircle, FolderKanban, ArrowUpRight, Check, X, MessageSquare, RefreshCw, Clock, Send, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../utils/api';

export default function ProjectReviewWorkspace() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedProject, setSelectedProject] = useState(null);
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [reviewAction, setReviewAction] = useState('APPROVE');
  const [reviewNotes, setReviewNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [actionSuccess, setActionSuccess] = useState('');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const list = await api.getReviewProjects();
      setProjects(list || []);
    } catch (err) {
      setError(err.message || 'Failed to load assigned review projects.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenReviewModal = (project, action) => {
    setSelectedProject(project);
    setReviewAction(action);
    setReviewNotes('');
    setReviewModalOpen(true);
  };

  const handleConfirmReview = async () => {
    if (!selectedProject) return;
    setSubmitting(true);
    try {
      await api.adminReviewProject(selectedProject.id, reviewAction, reviewNotes);
      setActionSuccess(`Project '${selectedProject.projectName}' review decision (${reviewAction}) recorded successfully!`);
      setReviewModalOpen(false);
      loadProjects();
    } catch (err) {
      setError(err.message || 'Failed to submit review decision.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Shield size={26} color="var(--primary)" />
            Project Review Workspace
          </h1>
          <p className="page-subtitle">
            Inspect submitted project deliverables, verify compliance against requirements, and approve for final customer release or request changes.
          </p>
        </div>
        <button onClick={loadProjects} className="btn btn-secondary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <RefreshCw size={14} /> Refresh Queue
        </button>
      </div>

      {/* Alerts */}
      {actionSuccess && (
        <div style={{
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#34d399',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.9rem'
        }}>
          <CheckCircle2 size={18} />
          <span>{actionSuccess}</span>
        </div>
      )}

      {error && (
        <div style={{
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          color: '#f87171',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.9rem'
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Projects List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
          Loading review queue...
        </div>
      ) : projects.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', background: 'var(--bg-card)' }}>
          <CheckCircle2 size={48} color="#34d399" style={{ margin: '0 auto 16px auto', opacity: 0.8 }} />
          <h3 style={{ margin: '0 0 8px 0', fontSize: '1.2rem', color: 'var(--text-main)' }}>
            Review Queue Clean
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '460px', margin: '0 auto' }}>
            There are currently no projects assigned to you awaiting review. New submissions will appear here automatically.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {projects.map((p) => {
            const isReadyForReview = p.status === 'READY_FOR_REVIEW';

            return (
              <div key={p.id} className="card" style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-xl)',
                padding: '24px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '20px',
                boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)'
              }}>
                <div style={{ flex: 1, minWidth: '280px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.8rem', fontFamily: 'monospace', fontWeight: 600, color: 'var(--primary-light)' }}>
                      {p.projectCode}
                    </span>
                    <span className={`badge ${isReadyForReview ? 'badge-warning' : 'badge-info'}`}>
                      {p.status}
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: '0 0 6px 0', color: 'var(--text-main)' }}>
                    {p.projectName}
                  </h3>

                  <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', margin: '0 0 12px 0' }}>
                    {p.description || 'No description provided.'}
                  </p>

                  {p.reviewNotes && (
                    <div style={{
                      padding: '10px 14px',
                      background: 'rgba(99, 102, 241, 0.08)',
                      border: '1px solid rgba(99, 102, 241, 0.2)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '0.84rem',
                      color: 'var(--text-main)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <MessageSquare size={14} color="var(--primary-light)" />
                      <span><strong>Developer Submission Note:</strong> {p.reviewNotes}</span>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                  <Link
                    to={`/projects/${p.id}`}
                    className="btn btn-secondary btn-sm"
                    style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                  >
                    Inspect Files <ArrowUpRight size={14} />
                  </Link>

                  <button
                    onClick={() => handleOpenReviewModal(p, 'REQUEST_CHANGES')}
                    className="btn btn-secondary btn-sm"
                    style={{ color: '#f87171', borderColor: 'rgba(239, 68, 68, 0.3)', display: 'flex', alignItems: 'center', gap: '6px' }}
                  >
                    <X size={14} /> Request Changes
                  </button>

                  <button
                    onClick={() => handleOpenReviewModal(p, 'APPROVE')}
                    className="btn btn-primary btn-sm"
                    style={{ background: 'linear-gradient(135deg, #10b981, #059669)', border: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
                  >
                    <Check size={14} /> Approve Deliverables
                  </button>
                </div>

              </div>
            );
          })}
        </div>
      )}

      {/* Review Confirmation Modal */}
      {reviewModalOpen && selectedProject && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '20px'
        }}>
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-xl)',
            width: '100%',
            maxWidth: '540px',
            padding: '28px',
            boxShadow: '0 20px 40px rgba(0,0,0,0.3)'
          }}>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, margin: '0 0 8px 0', color: 'var(--text-main)' }}>
              {reviewAction === 'APPROVE' ? 'Approve Project Deliverables' : 'Request Deliverable Revisions'}
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: '0 0 20px 0' }}>
              Project: <strong>{selectedProject.projectName}</strong> ({selectedProject.projectCode})
            </p>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>
                {reviewAction === 'APPROVE' ? 'Approval Notes (Optional)' : 'Revision Instructions for Developer *'}
              </label>
              <textarea
                required={reviewAction === 'REQUEST_CHANGES'}
                rows={4}
                placeholder={reviewAction === 'APPROVE' ? 'e.g. All requirements met. Project is ready for customer final payment.' : 'Specify what needs to be fixed or adjusted...'}
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px',
                  background: 'var(--bg-main)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-main)',
                  fontSize: '0.88rem',
                  resize: 'vertical'
                }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button
                type="button"
                onClick={() => setReviewModalOpen(false)}
                disabled={submitting}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmReview}
                disabled={submitting || (reviewAction === 'REQUEST_CHANGES' && !reviewNotes.trim())}
                className="btn btn-primary"
                style={{
                  background: reviewAction === 'APPROVE' ? 'linear-gradient(135deg, #10b981, #059669)' : undefined,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                {reviewAction === 'APPROVE' ? <Check size={16} /> : <Send size={16} />}
                {submitting ? 'Processing...' : (reviewAction === 'APPROVE' ? 'Approve & Release to Customer' : 'Send Revision Request')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
