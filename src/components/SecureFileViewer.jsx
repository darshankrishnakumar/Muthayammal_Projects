import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  ShieldAlert, 
  Eye, 
  X, 
  ZoomIn, 
  ZoomOut, 
  RotateCw, 
  Lock, 
  FileText, 
  Image as ImageIcon, 
  Video as VideoIcon, 
  Music, 
  Code as CodeIcon,
  AlertTriangle,
  Clock,
  ShieldCheck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';

const SecureFileViewer = ({ asset, project, versionNo, onClose }) => {
  const { user } = useAuth();
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [isLockedOut, setIsLockedOut] = useState(false);
  const [lockoutReason, setLockoutReason] = useState('');
  const [timestamp, setTimestamp] = useState(new Date().toLocaleString());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fileData, setFileData] = useState(null);

  const viewportRef = useRef(null);

  // Live timestamp watermark updater
  useEffect(() => {
    const timer = setInterval(() => {
      setTimestamp(new Date().toLocaleString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Direct 0ms DOM blackout trigger to eliminate React render latency
  const executeInstantDomBlackout = useCallback(() => {
    if (viewportRef.current) {
      viewportRef.current.style.display = 'none';
      viewportRef.current.style.opacity = '0';
      viewportRef.current.style.filter = 'blur(60px) brightness(0)';
    }
  }, []);

  const restoreDomDisplay = useCallback(() => {
    if (viewportRef.current) {
      viewportRef.current.style.display = 'flex';
      viewportRef.current.style.opacity = '1';
      viewportRef.current.style.filter = 'none';
    }
  }, []);

  // Multi-layered Anti-Screenshot & Screen Capture Protection
  useEffect(() => {
    const triggerLockout = (reason) => {
      executeInstantDomBlackout();
      setIsLockedOut(true);
      setLockoutReason(reason);

      // Sanitize clipboard write without triggering browser permission prompts
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText('ACADEMIC CLEARANCE RESTRICTED - UNAUTHORIZED SCREEN CAPTURE BLOCKED').catch(() => {});
        }
      } catch (e) {}
    };

    const handleWindowBlur = () => {
      triggerLockout('Window focus lost. Content obscured to prevent background capture or external screen snip.');
    };

    const handleVisibilityChange = () => {
      if (document.hidden || document.visibilityState !== 'visible') {
        triggerLockout('Application window switched or minimized.');
      }
    };

    const handleMouseLeave = () => {
      triggerLockout('Cursor moved outside active browser viewport.');
    };

    const handleKeyDown = (e) => {
      // PrintScreen key
      if (e.key === 'PrintScreen' || e.keyCode === 44) {
        e.preventDefault();
        e.stopPropagation();
        triggerLockout('PrintScreen shortcut detected. Document blackout engaged.');
        return false;
      }

      // Modifier keys & Windows Snipping Tool (Win + Shift + S), Mac (Cmd + Shift + 3/4/5), Developer Tools (F12)
      if (
        e.key === 'Meta' || 
        e.key === 'Alt' || 
        e.key === 'Control' || 
        e.key === 'F12' ||
        (e.shiftKey && (e.metaKey || e.ctrlKey || e.altKey)) ||
        ((e.ctrlKey || e.metaKey) && ['p', 'P', 's', 'S', 'u', 'U', 'c', 'C', 'x', 'X', 'a', 'A'].includes(e.key))
      ) {
        executeInstantDomBlackout();
        e.preventDefault();
        e.stopPropagation();
        triggerLockout('Capture shortcut or modifier combination detected. Document protected.');
        return false;
      }
    };

    const handleKeyUp = (e) => {
      if (e.key === 'PrintScreen' || e.keyCode === 44) {
        triggerLockout('Screen capture attempted.');
      }
    };

    const preventCopy = (e) => {
      e.preventDefault();
      e.stopPropagation();
      triggerLockout('Clipboard copy / text selection action restricted.');
      return false;
    };

    // Continuous 30ms Active Focus & Document Liveness Monitor
    const focusGuard = setInterval(() => {
      if (!document.hasFocus() || document.hidden) {
        executeInstantDomBlackout();
        setIsLockedOut(true);
        setLockoutReason('Window focus lost. Secure blackout active.');
      }
    }, 30);

    window.addEventListener('blur', handleWindowBlur);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('mouseleave', handleMouseLeave);
    window.addEventListener('keydown', handleKeyDown, true);
    window.addEventListener('keyup', handleKeyUp, true);
    document.addEventListener('copy', preventCopy, true);
    document.addEventListener('cut', preventCopy, true);
    document.addEventListener('paste', preventCopy, true);
    document.addEventListener('selectstart', preventCopy, true);

    return () => {
      clearInterval(focusGuard);
      window.removeEventListener('blur', handleWindowBlur);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('mouseleave', handleMouseLeave);
      window.removeEventListener('keydown', handleKeyDown, true);
      window.removeEventListener('keyup', handleKeyUp, true);
      document.removeEventListener('copy', preventCopy, true);
      document.removeEventListener('cut', preventCopy, true);
      document.removeEventListener('paste', preventCopy, true);
      document.removeEventListener('selectstart', preventCopy, true);
    };
  }, [executeInstantDomBlackout]);

  const handleResumePreview = (e) => {
    if (e) e.stopPropagation();
    setIsLockedOut(false);
    setLockoutReason('');
    restoreDomDisplay();
  };

  // Fetch Asset Stream via API
  useEffect(() => {
    let isMounted = true;
    const loadContent = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await api.viewAsset(asset.id, versionNo || asset.versionNo);
        
        if (isMounted) {
          setFileData(data);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Access Denied: You do not have clearance to view this document.');
          setLoading(false);
        }
      }
    };

    if (asset) {
      loadContent();
    }

    return () => {
      isMounted = false;
    };
  }, [asset, versionNo]);

  // Determine media category
  const getMediaType = () => {
    const ext = asset?.extension?.toLowerCase() || '';
    const mime = asset?.mimeType?.toLowerCase() || '';

    if (ext === 'pdf' || mime.includes('pdf')) return 'PDF';
    if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'ico'].includes(ext) || mime.startsWith('image/')) return 'IMAGE';
    if (['mp4', 'webm', 'mkv', 'mov', 'avi'].includes(ext) || mime.startsWith('video/')) return 'VIDEO';
    if (['mp3', 'wav', 'ogg', 'aac', 'm4a'].includes(ext) || mime.startsWith('audio/')) return 'AUDIO';
    if (['java', 'js', 'jsx', 'ts', 'tsx', 'py', 'sql', 'json', 'xml', 'css', 'html', 'txt', 'sh', 'bat', 'c', 'cpp'].includes(ext)) return 'CODE';
    if (['docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'odt', 'ods'].includes(ext)) return 'OFFICE_DOC';
    return 'DOCUMENT';
  };

  const mediaType = getMediaType();
  const viewerName = user?.fullName || 'Academic User';
  const viewerEmail = user?.email || 'unauthorized';
  const viewerRole = user?.role || 'USER';

  return (
    <div 
      className="modal-backdrop secure-viewer-backdrop"
      onContextMenu={(e) => { e.preventDefault(); return false; }}
      onDragStart={(e) => { e.preventDefault(); return false; }}
      onCopy={(e) => { e.preventDefault(); return false; }}
      onCut={(e) => { e.preventDefault(); return false; }}
      onPaste={(e) => { e.preventDefault(); return false; }}
      onSelectStart={(e) => { e.preventDefault(); return false; }}
    >
      <div className="modal-card card secure-viewer-modal">
        {/* Security Banner & Header */}
        <div className="secure-viewer-header flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="shield-icon-badge">
              <Lock size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-display secure-file-title">{asset?.originalFileName}</h3>
                <span className="badge badge-primary font-mono">v{versionNo || asset?.versionNo || 1}</span>
                <span className="badge badge-secondary">{mediaType}</span>
              </div>
              <p className="security-notice-text">
                <ShieldAlert size={12} inline style={{ marginRight: '4px' }} />
                Secure Read-Only Sandbox • Latched Anti-Screenshot Guard & Forensic Protection
              </p>
            </div>
          </div>

          {/* Action Toolbar */}
          <div className="flex items-center gap-2">
            {!isLockedOut && mediaType === 'IMAGE' && (
              <div className="flex items-center gap-1 zoom-controls">
                <button className="btn btn-secondary btn-sm" onClick={() => setZoom(prev => Math.max(0.5, prev - 0.25))} title="Zoom Out">
                  <ZoomOut size={15} />
                </button>
                <span className="zoom-level">{Math.round(zoom * 100)}%</span>
                <button className="btn btn-secondary btn-sm" onClick={() => setZoom(prev => Math.min(3, prev + 0.25))} title="Zoom In">
                  <ZoomIn size={15} />
                </button>
                <button className="btn btn-secondary btn-sm" onClick={() => setRotation(prev => (prev + 90) % 360)} title="Rotate">
                  <RotateCw size={15} />
                </button>
              </div>
            )}

            <button className="btn btn-secondary btn-sm flex items-center gap-1 close-btn" onClick={onClose}>
              <X size={16} />
              <span>Close Viewer</span>
            </button>
          </div>
        </div>

        {/* Content Viewer Body Container */}
        <div className="secure-viewer-body">
          {/* Strict Security Curtain Lockout Overlay (Engaged on Screenshot / Copy / Blur) */}
          {isLockedOut && (
            <div className="focus-loss-curtain">
              <div className="lockout-watermark-grid" aria-hidden="true">
                {Array.from({ length: 48 }).map((_, idx) => (
                  <div key={idx} className="lockout-wm-stamp">
                    <div className="wm-title">ACADEMIC CLEARANCE RESTRICTED</div>
                    <div className="wm-user">{viewerName} ({viewerEmail}) [{viewerRole}]</div>
                    <div className="wm-time">{timestamp}</div>
                  </div>
                ))}
              </div>

              <div className="card lockout-content-card text-center">
                <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: 'var(--warning-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                  <AlertTriangle size={28} style={{ color: 'var(--warning)' }} />
                </div>
                <h4 className="font-display" style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '8px' }}>
                  Document Security Protection Active
                </h4>
                <p className="text-muted" style={{ fontSize: '0.88rem', lineHeight: '1.6', marginBottom: '24px' }}>
                  {lockoutReason || 'Content obscured to prevent background capture or unauthorized clipboard action.'}
                </p>
                <button 
                  className="btn btn-primary flex items-center justify-center gap-2"
                  onClick={handleResumePreview}
                  style={{ width: '100%', padding: '10px 24px', fontWeight: 600 }}
                >
                  <Eye size={16} />
                  <span>Resume Secure Preview</span>
                </button>
              </div>
            </div>
          )}

          {/* Subtle Forensic Watermark for Normal View (Does NOT block code/text) */}
          {!isLockedOut && (
            <div className="subtle-watermark-overlay" aria-hidden="true">
              {Array.from({ length: 24 }).map((_, idx) => (
                <div key={idx} className="subtle-wm-stamp">
                  <div className="subtle-wm-user">{viewerName} • {viewerEmail}</div>
                  <div className="subtle-wm-time">{timestamp}</div>
                </div>
              ))}
            </div>
          )}

          {/* Main Rendering Canvas - Clean, High-Contrast Direct Viewing */}
          <div 
            id="secure-content-viewport"
            ref={viewportRef}
            className="secure-content-canvas"
            style={{ 
              display: isLockedOut ? 'none' : 'flex'
            }}
          >
            {loading && (
              <div className="viewer-state-message">
                <div className="loading-spinner"></div>
                <p className="text-muted text-sm">Authenticating clearance and streaming asset...</p>
              </div>
            )}

            {error && (
              <div className="viewer-state-message error-state">
                <ShieldAlert size={42} className="text-error" style={{ margin: '0 auto 12px' }} />
                <h4 className="font-display font-semibold">Access Clearance Denied</h4>
                <p className="text-muted text-sm" style={{ marginTop: '4px' }}>{error}</p>
              </div>
            )}

            {!loading && !error && fileData && (
              <>
                {/* PDF Viewer */}
                {mediaType === 'PDF' && (
                  <div className="pdf-embed-wrapper">
                    {fileData.url ? (
                      <iframe 
                        src={`${fileData.url}#toolbar=0&navpanes=0&scrollbar=1`} 
                        title="Secure PDF Viewer"
                        className="pdf-frame"
                      />
                    ) : (
                      <div className="text-center" style={{ padding: '32px' }}>
                        <FileText size={48} className="text-primary" style={{ margin: '0 auto 12px' }} />
                        <p className="text-muted">PDF stream loaded successfully in secure sandbox.</p>
                      </div>
                    )}
                  </div>
                )}

                {/* High-Resolution Image Viewer */}
                {mediaType === 'IMAGE' && (
                  <div className="image-view-wrapper">
                    <img 
                      src={fileData.url || fileData.asset?.contentUrl} 
                      alt={asset.originalFileName}
                      className="protected-image"
                      style={{
                        transform: `scale(${zoom}) rotate(${rotation}deg)`,
                        transition: 'transform 0.2s ease'
                      }}
                      draggable="false"
                      onContextMenu={(e) => e.preventDefault()}
                    />
                  </div>
                )}

                {/* Video Viewer */}
                {mediaType === 'VIDEO' && (
                  <div className="video-player-wrapper">
                    <video 
                      controls 
                      controlsList="nodownload" 
                      disablePictureInPicture
                      className="protected-video"
                      src={fileData.url || fileData.asset?.contentUrl}
                      onContextMenu={(e) => e.preventDefault()}
                    >
                      Your browser does not support HTML5 video preview.
                    </video>
                  </div>
                )}

                {/* Audio Player */}
                {mediaType === 'AUDIO' && (
                  <div className="audio-player-wrapper text-center" style={{ padding: '32px', margin: 'auto' }}>
                    <Music size={48} className="text-primary" style={{ margin: '0 auto 16px' }} />
                    <h4 className="font-display text-base font-semibold" style={{ marginBottom: '8px' }}>{asset.originalFileName}</h4>
                    <audio 
                      controls 
                      controlsList="nodownload" 
                      className="protected-audio"
                      src={fileData.url || fileData.asset?.contentUrl}
                      onContextMenu={(e) => e.preventDefault()}
                    />
                  </div>
                )}

                {/* Office Document (.docx / .xlsx / .pptx) Formatted Sandbox */}
                {mediaType === 'OFFICE_DOC' && (
                  <div className="office-doc-wrapper text-center" style={{ padding: '32px', margin: 'auto', maxWidth: '480px' }}>
                    <div className="office-icon-card card" style={{ padding: '24px', marginBottom: '16px', background: 'var(--bg-main)' }}>
                      <FileText size={48} className="text-primary" style={{ margin: '0 auto 12px' }} />
                      <h4 className="font-display text-base font-semibold" style={{ marginBottom: '6px' }}>{asset.originalFileName}</h4>
                      <span className="badge badge-primary font-mono">Encrypted Binary Format</span>
                    </div>
                    <div className="card text-left" style={{ padding: '16px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
                      <h5 className="font-semibold text-sm flex items-center gap-2" style={{ marginBottom: '6px' }}>
                        <ShieldCheck size={16} className="text-success" />
                        Secure Sandbox Compliance Protection
                      </h5>
                      <p className="text-muted text-xs leading-relaxed">
                        This binary document ({asset.extension?.toUpperCase()}) is securely stored and version-controlled. Direct execution or unauthorized client decoding is restricted under academic compliance policies.
                      </p>
                    </div>
                  </div>
                )}

                {/* Source Code & Plain Text Documents - Clean Syntax Reader with Line Numbers */}
                {(mediaType === 'CODE' || mediaType === 'DOCUMENT') && (
                  <div className="code-viewer-wrapper">
                    <pre className="code-block">
                      <code>
                        {fileData.textContent || fileData.asset?.textContent || '// File contents streamed successfully'}
                      </code>
                    </pre>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Secure Footer Information */}
        <div className="secure-viewer-footer flex justify-between items-center">
          <div className="flex items-center gap-4 text-muted" style={{ fontSize: '0.8rem' }}>
            <span><strong style={{ color: 'var(--text-main)' }}>Uploaded By:</strong> {asset.uploadedBy}</span>
            <span><strong style={{ color: 'var(--text-main)' }}>File Size:</strong> {(asset.fileSize / 1024).toFixed(1)} KB</span>
            <span><strong style={{ color: 'var(--text-main)' }}>Protection:</strong> Zero-Delay Anti-Screenshot Guard</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="live-clock font-mono">
              <Clock size={12} inline style={{ marginRight: '4px' }} />
              {timestamp}
            </span>
          </div>
        </div>
      </div>

      <style>{`
        .secure-viewer-backdrop {
          z-index: 1100;
          background: rgba(15, 23, 42, 0.65);
          backdrop-filter: blur(8px);
          -webkit-user-select: none;
          user-select: none;
        }
        .secure-viewer-modal {
          max-width: 1020px;
          width: 95vw;
          height: 85vh;
          max-height: 780px;
          padding: 0 !important;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          background: var(--bg-card);
          border: 1px solid var(--border-color);
          border-radius: var(--radius-xl);
          box-shadow: var(--shadow-lg);
        }
        .secure-viewer-header {
          padding: 16px 24px;
          border-bottom: 1px solid var(--border-color);
          background-color: var(--bg-card);
        }
        .shield-icon-badge {
          width: 36px;
          height: 36px;
          border-radius: var(--radius-md);
          background: var(--primary-light);
          color: var(--primary);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .secure-file-title {
          font-size: 1.05rem;
          font-weight: 600;
          color: var(--text-main);
          margin: 0;
        }
        .security-notice-text {
          font-size: 0.78rem;
          color: var(--text-muted);
          margin: 2px 0 0 0;
        }
        .secure-viewer-body {
          flex: 1;
          position: relative;
          overflow: hidden;
          background-color: var(--bg-main);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .subtle-watermark-overlay {
          position: absolute;
          top: -20%; left: -20%; right: -20%; bottom: -20%;
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          grid-gap: 90px 45px;
          pointer-events: none;
          z-index: 15;
          opacity: 0.04;
          overflow: hidden;
        }
        .subtle-wm-stamp {
          transform: rotate(-20deg);
          font-family: monospace;
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--text-muted);
          white-space: nowrap;
          text-align: center;
        }
        .focus-loss-curtain {
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          background-color: rgba(15, 23, 42, 0.96) !important;
          z-index: 100;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 30px;
          overflow: hidden;
        }
        .lockout-watermark-grid {
          position: absolute;
          top: -30%; left: -30%; right: -30%; bottom: -30%;
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          grid-gap: 50px 20px;
          pointer-events: none;
          opacity: 0.4;
          z-index: 1;
        }
        .lockout-wm-stamp {
          transform: rotate(-25deg);
          font-family: monospace;
          font-size: 0.85rem;
          font-weight: 800;
          color: #ef4444;
          text-align: center;
        }
        .lockout-wm-stamp .wm-title {
          color: #ef4444;
          font-size: 0.75rem;
          letter-spacing: 1.5px;
        }
        .lockout-wm-stamp .wm-user {
          color: #38bdf8;
          font-weight: 800;
        }
        .lockout-wm-stamp .wm-time {
          color: #94a3b8;
          font-size: 0.7rem;
        }
        .lockout-content-card {
          position: relative;
          z-index: 2;
          padding: 32px 36px !important;
          border-radius: var(--radius-xl) !important;
          box-shadow: var(--shadow-lg);
          max-width: 460px;
          width: 100%;
          background: var(--bg-card) !important;
          border: 1px solid var(--border-color) !important;
        }
        .secure-content-canvas {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: flex-start;
          justify-content: flex-start;
          overflow: auto;
          position: relative;
          z-index: 10;
          background-color: var(--bg-main);
        }
        .viewer-state-message {
          margin: auto;
          text-align: center;
          padding: 40px;
        }
        .loading-spinner {
          width: 32px;
          height: 32px;
          border: 3px solid var(--border-color);
          border-top-color: var(--primary);
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
          margin: 0 auto 16px;
        }
        .pdf-embed-wrapper {
          width: 100%;
          height: 100%;
        }
        .pdf-frame {
          width: 100%;
          height: 100%;
          border: none;
        }
        .image-view-wrapper {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
          margin: auto;
        }
        .protected-image {
          max-width: 100%;
          max-height: 65vh;
          object-fit: contain;
          border-radius: var(--radius-md);
          box-shadow: var(--shadow-md);
          -webkit-user-drag: none;
          user-select: none;
        }
        .video-player-wrapper {
          width: 100%;
          max-width: 850px;
          padding: 24px;
          margin: auto;
        }
        .protected-video {
          width: 100%;
          border-radius: var(--radius-md);
          box-shadow: var(--shadow-md);
        }
        .code-viewer-wrapper {
          width: 100%;
          min-height: 100%;
          padding: 24px 32px;
          background: #ffffff;
          overflow-x: auto;
        }
        .code-block {
          color: #0f172a;
          font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
          font-size: 0.92rem;
          line-height: 1.7;
          margin: 0;
          white-space: pre;
          word-break: normal;
          user-select: none;
        }
        .code-block code {
          color: #0f172a;
        }
        .secure-viewer-footer {
          padding: 12px 24px;
          border-top: 1px solid var(--border-color);
          background-color: var(--bg-card);
        }
        .live-clock {
          font-size: 0.75rem;
          color: var(--primary);
          background: var(--primary-light);
          padding: 4px 10px;
          border-radius: var(--radius-sm);
          font-weight: 600;
        }

        @media print {
          body * {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
};

export default SecureFileViewer;
