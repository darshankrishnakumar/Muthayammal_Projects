import { useCallback, useEffect, useRef, useState } from 'react';
import { AlertTriangle, Eye, FileText, Lock, Music, RotateCw, ShieldAlert, X, ZoomIn, ZoomOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { Badge, Spinner } from './ui';
import { bytes } from '../utils/format';

const IMAGE_EXTS = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'ico'];
const VIDEO_EXTS = ['mp4', 'webm', 'mkv', 'mov', 'avi'];
const AUDIO_EXTS = ['mp3', 'wav', 'ogg', 'aac', 'm4a'];
const CODE_EXTS = ['java', 'js', 'jsx', 'ts', 'tsx', 'py', 'sql', 'json', 'xml', 'css', 'scss', 'html', 'htm', 'txt', 'md', 'csv', 'sh', 'bat', 'c', 'cpp', 'h', 'hpp', 'cs', 'go', 'yaml', 'yml', 'properties'];
const OFFICE_EXTS = ['docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'odt', 'ods'];

const MEDIA_LABELS = { PDF: 'PDF', IMAGE: 'Image', VIDEO: 'Video', AUDIO: 'Audio', CODE: 'Text', OFFICE_DOC: 'Office document', DOCUMENT: 'File' };

const getMediaType = (asset, mimeFromServer) => {
  const ext = (asset?.extension || asset?.originalFileName?.split('.').pop() || '').toLowerCase();
  const mime = (mimeFromServer || asset?.mimeType || '').toLowerCase();
  if (ext === 'pdf' || mime.includes('pdf')) return 'PDF';
  if (IMAGE_EXTS.includes(ext) || mime.startsWith('image/')) return 'IMAGE';
  if (VIDEO_EXTS.includes(ext) || mime.startsWith('video/')) return 'VIDEO';
  if (AUDIO_EXTS.includes(ext) || mime.startsWith('audio/')) return 'AUDIO';
  if (CODE_EXTS.includes(ext) || mime.startsWith('text/') || mime.includes('json') || mime.includes('xml')) return 'CODE';
  if (OFFICE_EXTS.includes(ext)) return 'OFFICE_DOC';
  return 'DOCUMENT';
};

const block = (e) => {
  e.preventDefault();
  return false;
};

/**
 * Read-only viewer for protected project files. Content is streamed through the authorized
 * endpoint into an object URL. Deterrents (watermark, blackout on focus loss, copy and shortcut
 * blocking) discourage casual capture; they are not a security boundary — the server decides access.
 */
const SecureFileViewer = ({ asset, versionNo, onClose }) => {
  const { user } = useAuth();
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [isLockedOut, setIsLockedOut] = useState(false);
  const [lockoutReason, setLockoutReason] = useState('');
  const [timestamp, setTimestamp] = useState(() => new Date().toLocaleString('en-IN'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fileData, setFileData] = useState(null);
  const viewportRef = useRef(null);

  // Live timestamp for the watermark.
  useEffect(() => {
    const timer = setInterval(() => setTimestamp(new Date().toLocaleString('en-IN')), 1000);
    return () => clearInterval(timer);
  }, []);

  // Hide content synchronously, before React re-renders.
  const instantBlackout = useCallback(() => {
    const el = viewportRef.current;
    if (el) {
      el.style.visibility = 'hidden';
      el.style.filter = 'blur(60px) brightness(0)';
    }
  }, []);

  const restoreDisplay = useCallback(() => {
    const el = viewportRef.current;
    if (el) {
      el.style.visibility = 'visible';
      el.style.filter = 'none';
    }
  }, []);

  // Capture deterrents.
  useEffect(() => {
    const lockOut = (reason) => {
      instantBlackout();
      setIsLockedOut(true);
      setLockoutReason(reason);
      try {
        navigator.clipboard?.writeText?.('Protected content — copying is not permitted.').catch(() => {});
      } catch {
        /* clipboard unavailable */
      }
    };

    const onBlur = () => lockOut('The window lost focus, so the content was hidden.');
    const onVisibility = () => {
      if (document.hidden || document.visibilityState !== 'visible') lockOut('You switched away from this window.');
    };
    const onMouseLeave = () => lockOut('The pointer left the window.');
    const onKeyDown = (e) => {
      if (e.key === 'Escape') return;
      if (e.key === 'PrintScreen' || e.keyCode === 44) {
        e.preventDefault();
        e.stopPropagation();
        lockOut('A screenshot shortcut was pressed.');
        return;
      }
      const captureCombo =
        ['Meta', 'Alt', 'Control', 'F12'].includes(e.key) ||
        (e.shiftKey && (e.metaKey || e.ctrlKey || e.altKey)) ||
        ((e.ctrlKey || e.metaKey) && ['p', 's', 'u', 'c', 'x', 'a'].includes(e.key.toLowerCase()));
      if (captureCombo) {
        instantBlackout();
        e.preventDefault();
        e.stopPropagation();
        lockOut('A copy, print or capture shortcut was pressed.');
      }
    };
    const onKeyUp = (e) => {
      if (e.key === 'PrintScreen' || e.keyCode === 44) lockOut('A screenshot was attempted.');
    };
    const preventCopy = (e) => {
      e.preventDefault();
      e.stopPropagation();
      lockOut('Copying and selecting text is disabled for this file.');
    };

    const focusGuard = setInterval(() => {
      if (!document.hasFocus() || document.hidden) {
        instantBlackout();
        setIsLockedOut(true);
        setLockoutReason((r) => r || 'The window lost focus, so the content was hidden.');
      }
    }, 30);

    window.addEventListener('blur', onBlur);
    document.addEventListener('visibilitychange', onVisibility);
    document.addEventListener('mouseleave', onMouseLeave);
    window.addEventListener('keydown', onKeyDown, true);
    window.addEventListener('keyup', onKeyUp, true);
    ['copy', 'cut', 'paste', 'selectstart'].forEach((ev) => document.addEventListener(ev, preventCopy, true));

    return () => {
      clearInterval(focusGuard);
      window.removeEventListener('blur', onBlur);
      document.removeEventListener('visibilitychange', onVisibility);
      document.removeEventListener('mouseleave', onMouseLeave);
      window.removeEventListener('keydown', onKeyDown, true);
      window.removeEventListener('keyup', onKeyUp, true);
      ['copy', 'cut', 'paste', 'selectstart'].forEach((ev) => document.removeEventListener(ev, preventCopy, true));
    };
  }, [instantBlackout]);

  // Escape closes the viewer.
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose?.();
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  const resume = (e) => {
    e?.stopPropagation();
    setIsLockedOut(false);
    setLockoutReason('');
    restoreDisplay();
  };

  // Stream the file; revoke the object URL when it is no longer shown.
  const assetId = asset?.id;
  const requestedVersion = versionNo || asset?.versionNo || null;
  useEffect(() => {
    if (!assetId) return undefined;
    let cancelled = false;
    let objectUrl = null;
    setLoading(true);
    setError(null);
    setFileData(null);
    api.viewAsset(assetId, requestedVersion)
      .then((data) => {
        objectUrl = data?.url || null;
        if (cancelled) {
          if (objectUrl) URL.revokeObjectURL(objectUrl);
          return;
        }
        setFileData(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [assetId, requestedVersion]);

  const mediaType = getMediaType(asset, fileData?.mimeType);
  const viewerName = user?.fullName || 'Signed-in user';
  const viewerEmail = user?.email || '';
  const shownVersion = versionNo || asset?.versionNo || 1;

  return (
    <div
      className="overlay secure-viewer-overlay"
      onContextMenu={block}
      onDragStart={block}
      onCopy={block}
      onCut={block}
      onPaste={block}
      onMouseDown={(e) => e.target === e.currentTarget && onClose?.()}
    >
      <div className="modal modal-xl secure-viewer" role="dialog" aria-modal="true" aria-label={asset?.originalFileName}>
        <div className="modal-header items-center">
          <div className="flex items-center gap-3 min-w-0">
            <span className="stat-icon shrink-0"><Lock aria-hidden="true" /></span>
            <div className="min-w-0">
              <div className="flex items-center gap-2 min-w-0">
                <h2 className="modal-title truncate">{asset?.originalFileName}</h2>
                <Badge className="font-mono">v{shownVersion}</Badge>
                <Badge>{MEDIA_LABELS[mediaType]}</Badge>
              </div>
              <p className="modal-description">Protected view. Copying, printing and screen capture are discouraged and watermarked.</p>
            </div>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            {!isLockedOut && mediaType === 'IMAGE' && fileData && (
              <>
                <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))} aria-label="Zoom out"><ZoomOut aria-hidden="true" /></button>
                <span className="text-sm text-muted tabular" style={{ minWidth: 40, textAlign: 'center' }}>{Math.round(zoom * 100)}%</span>
                <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setZoom((z) => Math.min(3, z + 0.25))} aria-label="Zoom in"><ZoomIn aria-hidden="true" /></button>
                <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setRotation((r) => (r + 90) % 360)} aria-label="Rotate"><RotateCw aria-hidden="true" /></button>
                <span className="secure-viewer-sep" aria-hidden="true" />
              </>
            )}
            <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={onClose} aria-label="Close viewer"><X aria-hidden="true" /></button>
          </div>
        </div>

        <div className="secure-viewer-body">
          {isLockedOut && (
            <div className="secure-viewer-curtain">
              <div className="secure-viewer-wm secure-viewer-wm-strong" aria-hidden="true">
                {Array.from({ length: 36 }).map((_, i) => (
                  <div key={i}>{viewerName} · {viewerEmail}<br />{timestamp}</div>
                ))}
              </div>
              <div className="card text-center" style={{ position: 'relative', zIndex: 2, maxWidth: 400 }}>
                <div className="empty-icon mx-auto"><AlertTriangle aria-hidden="true" /></div>
                <div className="font-semibold mb-1">Content hidden</div>
                <p className="text-sm mb-4">{lockoutReason || 'The content was hidden to protect it.'}</p>
                <button type="button" className="btn btn-primary btn-block" onClick={resume}>
                  <Eye aria-hidden="true" /> Resume viewing
                </button>
              </div>
            </div>
          )}

          {!isLockedOut && (
            <div className="secure-viewer-wm" aria-hidden="true">
              {Array.from({ length: 24 }).map((_, i) => (
                <div key={i}>{viewerName} · {viewerEmail}<br />{timestamp}</div>
              ))}
            </div>
          )}

          <div ref={viewportRef} className="secure-viewer-canvas" style={{ visibility: isLockedOut ? 'hidden' : 'visible' }}>
            {loading && (
              <div className="secure-viewer-state">
                <Spinner large />
                <p className="text-sm mt-3">Loading file…</p>
              </div>
            )}

            {!loading && error && (
              <div className="secure-viewer-state">
                <div className="empty-icon mx-auto"><ShieldAlert aria-hidden="true" /></div>
                <div className="font-semibold">{error.status === 403 ? 'You do not have access to this file' : 'The file could not be opened'}</div>
                <p className="text-sm mt-1">{error.message}</p>
              </div>
            )}

            {!loading && !error && fileData && (
              <>
                {mediaType === 'PDF' && (
                  <iframe src={`${fileData.url}#toolbar=0&navpanes=0&scrollbar=1`} title={asset.originalFileName} className="secure-viewer-frame" />
                )}

                {mediaType === 'IMAGE' && (
                  <div className="secure-viewer-center">
                    <img
                      src={fileData.url}
                      alt={asset.originalFileName}
                      draggable="false"
                      className="secure-viewer-image"
                      style={{ transform: `scale(${zoom}) rotate(${rotation}deg)` }}
                    />
                  </div>
                )}

                {mediaType === 'VIDEO' && (
                  <div className="secure-viewer-center" style={{ width: '100%' }}>
                    <div className="media-frame" style={{ width: '100%', maxWidth: 960 }}>
                      <video
                        src={fileData.url}
                        controls
                        autoPlay
                        playsInline
                        controlsList="nodownload noremoteplayback"
                        disablePictureInPicture
                      >
                        Your browser cannot play this video.
                      </video>
                    </div>
                  </div>
                )}

                {mediaType === 'AUDIO' && (
                  <div className="secure-viewer-state">
                    <div className="empty-icon mx-auto"><Music aria-hidden="true" /></div>
                    <div className="font-medium mb-3">{asset.originalFileName}</div>
                    <audio src={fileData.url} controls controlsList="nodownload" />
                  </div>
                )}

                {mediaType === 'OFFICE_DOC' && (
                  <div className="secure-viewer-state" style={{ maxWidth: 420 }}>
                    <div className="empty-icon mx-auto"><FileText aria-hidden="true" /></div>
                    <div className="font-semibold">{asset.originalFileName}</div>
                    <p className="text-sm mt-1">
                      {(asset.extension || '').toUpperCase() || 'Office'} files cannot be previewed in the browser.
                      Use Download if you have access to this file.
                    </p>
                  </div>
                )}

                {(mediaType === 'CODE' || mediaType === 'DOCUMENT') && (
                  fileData.textContent != null ? (
                    <pre className="secure-viewer-code"><code>{fileData.textContent}</code></pre>
                  ) : (
                    <div className="secure-viewer-state" style={{ maxWidth: 420 }}>
                      <div className="empty-icon mx-auto"><FileText aria-hidden="true" /></div>
                      <div className="font-semibold">No preview available</div>
                      <p className="text-sm mt-1">This file type cannot be shown in the browser.</p>
                    </div>
                  )
                )}
              </>
            )}
          </div>
        </div>

        <div className="modal-footer" style={{ justifyContent: 'space-between' }}>
          <span className="text-xs text-muted truncate">
            {[asset?.uploadedBy && `Uploaded by ${asset.uploadedBy}`, (fileData?.size ?? asset?.fileSize) != null && bytes(fileData?.size ?? asset?.fileSize)].filter(Boolean).join(' · ')}
          </span>
          <span className="text-xs text-subtle font-mono tabular shrink-0">{timestamp}</span>
        </div>
      </div>

      <style>{`
        .secure-viewer-overlay { z-index: 90; -webkit-user-select: none; user-select: none; }
        .secure-viewer { height: min(820px, calc(100vh - 32px)); }
        .secure-viewer-sep { width: 1px; height: 18px; background: var(--border); margin: 0 6px; }
        .secure-viewer-body { position: relative; flex: 1; min-height: 0; overflow: hidden; background: var(--surface-2); }
        .secure-viewer-canvas { position: absolute; inset: 0; z-index: 1; display: flex; overflow: auto; }
        .secure-viewer-state { margin: auto; padding: 32px; text-align: center; color: var(--text-2); }
        .secure-viewer-center { margin: auto; padding: 24px; display: flex; align-items: center; justify-content: center; }
        .secure-viewer-frame { width: 100%; height: 100%; border: 0; background: var(--surface); }
        .secure-viewer-image { max-width: 100%; max-height: 68vh; object-fit: contain; border-radius: var(--radius-md); transition: transform var(--duration) var(--ease); -webkit-user-drag: none; }
        .secure-viewer-code { width: 100%; min-height: 100%; margin: 0; padding: 20px 24px; background: var(--surface); color: var(--text); font-family: var(--font-mono); font-size: var(--text-sm); line-height: 1.7; white-space: pre; overflow: visible; }
        .secure-viewer-wm { position: absolute; inset: -20%; z-index: 2; pointer-events: none; display: grid; grid-template-columns: repeat(3, 1fr); gap: 90px 40px; opacity: 0.05; overflow: hidden; }
        .secure-viewer-wm > div { transform: rotate(-20deg); font-family: var(--font-mono); font-size: 12px; font-weight: 600; color: var(--text); text-align: center; white-space: nowrap; }
        .secure-viewer-curtain { position: absolute; inset: 0; z-index: 3; display: flex; align-items: center; justify-content: center; padding: 24px; background: var(--surface-2); overflow: hidden; }
        .secure-viewer-wm-strong { opacity: 0.12; gap: 48px 24px; }
        @media print { body * { display: none !important; } }
      `}</style>
    </div>
  );
};

export default SecureFileViewer;
