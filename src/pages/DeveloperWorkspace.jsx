import React, { useState, useEffect } from 'react';
import { Code2, FolderKanban, CheckCircle2, Clock, AlertCircle, ArrowUpRight, Send, FileCode, Check, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../utils/api';

export default function DeveloperWorkspace() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedProject, setSelectedProject] = useState(null);
  const [submitModalOpen, setSubmitModalOpen] = useState(false);
  const [deliverablesNotes, setDeliverablesNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [actionSuccess, setActionSuccess] = useState('');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const list = await api.getDeveloperProjects();
      setProjects(list || []);
    } catch (err) {
      setError(err.message || 'Failed to load assigned developer projects.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartDev = async (p) => {
    try {
      await api.updateProjectStatus(p.id, 'IN_PROGRESS');
      setActionSuccess(`Project '${p.projectName}' marked IN PROGRESS.`);
      loadProjects();
    } catch (err) {
      setError(err.message || 'Failed to update project status.');
    }
  };

  const handleSubmitForReview = async () => {
    if (!selectedProject) return;
    setSubmitting(true);
    try {
      await api.developerSubmitReview(selectedProject.id, deliverablesNotes);
      setActionSuccess(`Project '${selectedProject.projectName}' successfully submitted for Admin Review!`);
      setSubmitModalOpen(false);
      setDeliverablesNotes('');
      loadProjects();
    } catch (err) {
      setError(err.message || 'Failed to submit project for review.');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'DEVELOPER_ASSIGNED':
        return <span className="badge badge-warning"><Clock size={12} /> Assigned</span>;
      case 'IN_PROGRESS':
        return <span className="badge badge-primary"><Code2 size={12} /> In Development</span>;
      case 'TESTING':
        return <span className="badge badge-info"><FileCode size={12} /> Testing</span>;
      case 'READY_FOR_REVIEW':
        return <span className="badge badge-info"><Send size={12} /> Awaiting Review</span>;
      case 'CHANGES_REQUESTED':
        return <span className="badge badge-danger"><AlertCircle size={12} /> Changes Requested</span>;
      case 'REVIEW_APPROVED':
      case 'READY_FOR_FINAL_PAYMENT':
      case 'ACCESS_GRANTED':
      case 'COMPLETED':
        return <span className="badge badge-success"><CheckCircle2 size={12} /> Approved</span>;
      default:
        return <span className="badge badge-secondary">{status}</span>;
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Code2 size={26} color="var(--primary)" />
            Developer Workspace
          </h1>
          <p className="page-subtitle">
            Manage your assigned academic development projects, track specifications, and submit deliverables for Admin Review.
          </p>
        </div>
        <button onClick={loadProjects} className="btn btn-secondary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <RefreshCw size={14} /> Refresh
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
          Loading your assigned projects...
        </div>
      ) : projects.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', background: 'var(--bg-card)' }}>
          <FolderKanban size={48} color="var(--text-muted)" style={{ margin: '0 auto 16px auto', opacity: 0.5 }} />
          <h3 style={{ margin: '0 0 8px 0', fontSize: '1.2rem', color: 'var(--text-main)' }}>
            No Assigned Projects Found
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '460px', margin: '0 auto' }}>
            You do not currently have any projects assigned. When the Super Admin assigns a development project to your account, it will appear here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
          {projects.map((p) => {
            const isAssigned = p.status === 'DEVELOPER_ASSIGNED';
            const inDev = p.status === 'IN_PROGRESS' || p.status === 'TESTING';
            const isChanges = p.status === 'CHANGES_REQUESTED';
            const isReview = p.status === 'READY_FOR_REVIEW';

            return (
              <div key={p.id} className="card" style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-xl)',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)'
              }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <span style={{ fontSize: '0.78rem', fontFamily: 'monospace', fontWeight: 600, color: 'var(--primary-light)' }}>
                      {p.projectCode}
                    </span>
                    {getStatusBadge(p.status)}
                  </div>

                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: '0 0 8px 0', color: 'var(--text-main)' }}>
                    {p.projectName}
                  </h3>

                  <p style={{
                    fontSize: '0.86rem',
                    color: 'var(--text-muted)',
                    margin: '0 0 16px 0',
                    lineHeight: 1.5,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}>
                    {p.description || 'No detailed specifications provided.'}
                  </p>

                  {p.technologyStack && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
                      {p.technologyStack.split(',').map((tech, idx) => (
                        <span key={idx} style={{
                          fontSize: '0.72rem',
                          padding: '3px 8px',
                          background: 'rgba(255,255,255,0.05)',
                          border: '1px solid var(--border-color)',
                          borderRadius: '4px',
                          color: 'var(--text-muted)'
                        }}>
                          {tech.trim()}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Changes Requested Feedback Box */}
                  {isChanges && p.changeRequestNotes && (
                    <div style={{
                      padding: '12px 14px',
                      background: 'rgba(239, 68, 68, 0.08)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      borderRadius: 'var(--radius-md)',
                      marginBottom: '16px'
                    }}>
                      <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#f87171', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <AlertCircle size={14} /> Reviewer Revision Feedback:
                      </div>
                      <div style={{ fontSize: '0.84rem', color: 'var(--text-main)', fontStyle: 'italic' }}>
                        "{p.changeRequestNotes}"
                      </div>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div style={{
                  borderTop: '1px solid var(--border-color)',
                  paddingTop: '16px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '10px'
                }}>
                  <Link
                    to={`/projects/${p.id}`}
                    className="btn btn-secondary btn-sm"
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem' }}
                  >
                    Open Files <ArrowUpRight size={14} />
                  </Link>

                  {isAssigned && (
                    <button
                      onClick={() => handleStartDev(p)}
                      className="btn btn-primary btn-sm"
                      style={{ fontSize: '0.82rem' }}
                    >
                      Start Development
                    </button>
                  )}

                  {(inDev || isChanges) && (
                    <button
                      onClick={() => {
                        setSelectedProject(p);
                        setSubmitModalOpen(true);
                      }}
                      className="btn btn-primary btn-sm"
                      style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem' }}
                    >
                      <Send size={14} /> Submit for Review
                    </button>
                  )}

                  {isReview && (
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                      In Review by Admin
                    </span>
                  )}
                </div>

              </div>
            );
          })}
        </div>
      )}

      {/* Submit for Review Modal */}
      {submitModalOpen && selectedProject && (
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
              Submit Project for Admin Review
            </h2>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', margin: '0 0 20px 0' }}>
              Submitting <strong>{selectedProject.projectName}</strong> ({selectedProject.projectCode}) to the Reviewer Admin.
            </p>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>
                Deliverables & Completion Summary *
              </label>
              <textarea
                required
                rows={4}
                placeholder="Describe completed features, architecture, test results, and file locations..."
                value={deliverablesNotes}
                onChange={(e) => setDeliverablesNotes(e.target.value)}
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
                onClick={() => setSubmitModalOpen(false)}
                disabled={submitting}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSubmitForReview}
                disabled={submitting || !deliverablesNotes.trim()}
                className="btn btn-primary"
                style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <Send size={16} /> {submitting ? 'Submitting...' : 'Confirm Submission'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
