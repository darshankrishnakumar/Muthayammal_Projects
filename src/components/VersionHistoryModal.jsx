import { useState } from 'react';
import { Eye, History, RotateCcw } from 'lucide-react';
import { api } from '../utils/api';
import { useAsync } from '../hooks/useAsync';
import { Modal, ConfirmDialog, Badge, EmptyState, Alert, SkeletonRows, useToast } from './ui';
import { bytes, dateTime } from '../utils/format';

const isCurrent = (v) => Boolean(v.currentVersion ?? v.isCurrentVersion);

/**
 * Lists every stored version of an asset. Previewing is available to anyone who can open the file;
 * restoring is a write action and only offered when `canRestore` is true.
 */
const VersionHistoryModal = ({ asset, canRestore = false, onClose, onPreviewVersion, onVersionRestored }) => {
  const { notify } = useToast();
  const { data, loading, error, reload } = useAsync(() => api.getAssetVersions(asset.id), [asset.id]);
  const versions = (data || []).slice().sort((a, b) => b.versionNo - a.versionNo);

  const [restoreTarget, setRestoreTarget] = useState(null);
  const [restoring, setRestoring] = useState(false);

  const confirmRestore = async () => {
    if (!restoreTarget) return;
    setRestoring(true);
    try {
      await api.restoreAssetVersion(asset.id, restoreTarget.versionNo);
      notify(`Version ${restoreTarget.versionNo} is now current`);
      setRestoreTarget(null);
      await reload();
      onVersionRestored?.();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setRestoring(false);
    }
  };

  return (
    <>
      <Modal
        open
        size="lg"
        onClose={onClose}
        title="Version history"
        description={`${asset.originalFileName}${versions.length ? ` · ${versions.length} version${versions.length === 1 ? '' : 's'}` : ''}`}
        footer={<button type="button" className="btn btn-secondary" onClick={onClose}>Close</button>}
      >
        {loading && !data ? (
          <SkeletonRows rows={3} height={64} />
        ) : error ? (
          <Alert tone="danger" title="Could not load versions">{error.message}</Alert>
        ) : versions.length === 0 ? (
          <EmptyState icon={History} title="No versions recorded" />
        ) : (
          <div className="list border rounded">
            {versions.map((v) => {
              const current = isCurrent(v);
              return (
                <div key={v.id ?? v.versionNo} className="list-item items-start" style={current ? { background: 'var(--accent-soft)' } : undefined}>
                  <Badge tone={current ? 'accent' : 'neutral'} className="font-mono shrink-0">v{v.versionNo}</Badge>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium truncate">{v.originalFileName}</span>
                      {current && <Badge tone="success" dot>Current</Badge>}
                    </div>
                    <p className="text-sm mt-1">{v.description || 'No change notes.'}</p>
                    <div className="text-xs text-subtle mt-1">
                      {[v.uploadedBy, dateTime(v.createdAt), v.fileSize != null ? bytes(v.fileSize) : null].filter(Boolean).join(' · ')}
                    </div>
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    <button type="button" className="btn btn-ghost btn-sm" onClick={() => onPreviewVersion?.(v.versionNo)}>
                      <Eye aria-hidden="true" /> Preview
                    </button>
                    {canRestore && !current && (
                      <button type="button" className="btn btn-secondary btn-sm" onClick={() => setRestoreTarget(v)}>
                        <RotateCcw aria-hidden="true" /> Restore
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Modal>

      <ConfirmDialog
        open={Boolean(restoreTarget)}
        title={restoreTarget ? `Restore version ${restoreTarget.versionNo}?` : ''}
        text="The restored version becomes the current file. Newer versions stay in the history."
        confirmLabel="Restore"
        busy={restoring}
        onConfirm={confirmRestore}
        onClose={() => !restoring && setRestoreTarget(null)}
      />
    </>
  );
};

export default VersionHistoryModal;
