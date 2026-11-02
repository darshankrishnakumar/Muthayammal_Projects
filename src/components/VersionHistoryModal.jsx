import React, { useState, useEffect } from 'react';
import { History, X, CheckCircle2, RotateCcw, Eye, Clock, User, FileText, AlertCircle } from 'lucide-react';
import { api } from '../utils/api';

const VersionHistoryModal = ({ asset, project, onClose, onPreviewVersion, onVersionRestored }) => {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionSuccess, setActionSuccess] = useState('');
  const [restoringVersionNo, setRestoringVersionNo] = useState(null);

  useEffect(() => {
    fetchVersions();
  }, [asset.id]);

  const fetchVersions = async () => {
    try {
      setLoading(true);
      setError('');
      const list = await api.getAssetVersions(asset.id);
      setVersions(list);
    } catch (err) {
      setError(err.message || 'Failed to load version history');
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (versionNo) => {
    if (!window.confirm(`Are you sure you want to restore Version v${versionNo} as the current active file?`)) {
      return;
    }

    try {
      setRestoringVersionNo(versionNo);
      setError('');
      setActionSuccess('');

      await api.restoreAssetVersion(asset.id, versionNo);
      setActionSuccess(`Successfully restored Version v${versionNo} as active.`);
      await fetchVersions();
      if (onVersionRestored) onVersionRestored();
    } catch (err) {
      setError(err.message || 'Failed to restore version');
    } finally {
      setRestoringVersionNo(null);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card card" style={{ maxWidth: '650px', width: '100%', padding: '24px', maxHeight: '85vh', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div className="flex justify-between items-center" style={{ marginBottom: '16px' }}>
          <div className="flex items-center gap-3">
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.15)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <History size={20} />
            </div>
            <div>
              <h3 className="font-display" style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0 }}>
                Version History
              </h3>
              <p className="text-muted" style={{ fontSize: '0.8rem', margin: 0 }}>
                {asset.originalFileName} (Total Versions: {versions.length})
              </p>
            </div>
          </div>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>

        {/* Notifications */}
        {error && (
          <div className="card text-error" style={{ padding: '10px 14px', marginBottom: '16px', backgroundColor: 'var(--error-light)' }}>
            <AlertCircle size={15} inline style={{ marginRight: '6px' }} />
            {error}
          </div>
        )}
        {actionSuccess && (
          <div className="card text-success" style={{ padding: '10px 14px', marginBottom: '16px', backgroundColor: 'var(--success-light)' }}>
            <CheckCircle2 size={15} inline style={{ marginRight: '6px' }} />
            {actionSuccess}
          </div>
        )}

        {/* Versions Timeline List */}
        <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
          {loading ? (
            <div className="text-center p-8">
              <div className="loading-spinner-sm" style={{ margin: '0 auto 8px' }}></div>
              <p className="text-muted" style={{ fontSize: '0.85rem' }}>Loading version lineage...</p>
            </div>
          ) : versions.length === 0 ? (
            <div className="text-center p-8 text-muted">No version history available.</div>
          ) : (
            <div className="version-timeline">
              {versions.map((ver) => (
                <div key={ver.id} className={`version-item card ${ver.isCurrentVersion ? 'version-current' : ''}`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`badge ${ver.isCurrentVersion ? 'badge-primary' : 'badge-secondary'}`} style={{ fontWeight: 700 }}>
                          v{ver.versionNo}
                        </span>
                        {ver.isCurrentVersion && (
                          <span className="badge badge-success flex items-center gap-1" style={{ fontSize: '0.7rem' }}>
                            <CheckCircle2 size={11} /> CURRENT ACTIVE
                          </span>
                        )}
                        <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{ver.originalFileName}</span>
                      </div>

                      <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', margin: '6px 0', lineHeight: 1.4 }}>
                        {ver.description || 'No description notes provided for this version.'}
                      </p>

                      <div className="flex items-center gap-4 text-muted" style={{ fontSize: '0.75rem', marginTop: '8px' }}>
                        <span className="flex items-center gap-1">
                          <User size={12} /> {ver.uploadedBy}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock size={12} /> {new Date(ver.createdAt).toLocaleString()}
                        </span>
                        <span>
                          {(ver.fileSize / 1024).toFixed(1)} KB
                        </span>
                      </div>
                    </div>

                    {/* Version Actions */}
                    <div className="flex items-center gap-2">
                      <button 
                        className="btn btn-secondary btn-sm flex items-center gap-1"
                        style={{ fontSize: '0.75rem', padding: '5px 10px' }}
                        onClick={() => onPreviewVersion(ver.versionNo)}
                      >
                        <Eye size={13} />
                        <span>Preview</span>
                      </button>

                      {!ver.isCurrentVersion && (
                        <button 
                          className="btn btn-primary btn-sm flex items-center gap-1"
                          style={{ fontSize: '0.75rem', padding: '5px 10px' }}
                          onClick={() => handleRestore(ver.versionNo)}
                          disabled={restoringVersionNo === ver.versionNo}
                        >
                          <RotateCcw size={13} />
                          <span>{restoringVersionNo === ver.versionNo ? 'Restoring...' : 'Restore'}</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end" style={{ marginTop: '16px', borderTop: '1px solid var(--border-color)', paddingTop: '12px' }}>
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>

      <style>{`
        .version-timeline {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .version-item {
          padding: 14px 16px;
          border: 1px solid var(--border-color);
          background: var(--bg-main);
          border-radius: 8px;
          transition: all 0.2s ease;
        }
        .version-current {
          border-color: var(--primary);
          background: rgba(59, 130, 246, 0.05);
        }
      `}</style>
    </div>
  );
};

export default VersionHistoryModal;
