import React, { useState, useRef } from 'react';
import { Upload, X, File, AlertCircle, CheckCircle2, ShieldCheck, Trash2 } from 'lucide-react';
import { api } from '../utils/api';

const MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024; // 500MB
const ALLOWED_EXTS = [
  'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'csv', 'txt', 'rtf', 'md',
  'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'ico',
  'mp4', 'webm', 'mkv', 'mov', 'avi', 'mp3', 'wav', 'ogg', 'aac', 'm4a',
  'zip', 'tar', 'gz', '7z', 'rar',
  'java', 'js', 'jsx', 'ts', 'tsx', 'py', 'c', 'cpp', 'h', 'hpp', 'cs', 'go',
  'html', 'htm', 'css', 'scss', 'json', 'xml', 'yaml', 'yml', 'sql', 'sh', 'bat', 'properties'
];

const FileUploadModal = ({ projectId, folderId, folderName, replaceAsset = null, onClose, onUploadSuccess }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [description, setDescription] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadStatusText, setUploadStatusText] = useState('');
  const fileInputRef = useRef(null);

  const isReplaceMode = Boolean(replaceAsset);

  const validateFile = (file) => {
    if (!file) return 'Please choose a file to upload.';
    if (file.size > MAX_FILE_SIZE_BYTES) {
      return `File '${file.name}' exceeds the 500MB limit (${(file.size / (1024 * 1024)).toFixed(1)} MB selected).`;
    }
    const ext = file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTS.includes(ext)) {
      return `File type '.${ext}' is not supported. Supported: documents, media, source code, archives.`;
    }
    return null;
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files || []);
    addValidFiles(files);
  };

  const addValidFiles = (files) => {
    if (!files.length) return;

    if (isReplaceMode) {
      const file = files[0];
      const valError = validateFile(file);
      if (valError) {
        setError(valError);
        setSelectedFiles([]);
      } else {
        setError('');
        setSelectedFiles([file]);
      }
      return;
    }

    let validationError = '';
    const validBatch = [];

    for (const file of files) {
      const err = validateFile(file);
      if (err) {
        validationError = err;
        break;
      }
      if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
        validBatch.push(file);
      }
    }

    if (validationError) {
      setError(validationError);
    } else {
      setError('');
      setSelectedFiles(prev => [...prev, ...validBatch]);
    }
  };

  const handleRemoveFile = (index, e) => {
    e.stopPropagation();
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      addValidFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedFiles.length === 0) {
      setError('Please select at least one file first.');
      return;
    }

    try {
      setUploading(true);
      setError('');

      if (isReplaceMode) {
        setUploadStatusText(`Uploading replacement version for ${replaceAsset.originalFileName}...`);
        await api.replaceAsset(replaceAsset.id, selectedFiles[0], description);
      } else {
        const total = selectedFiles.length;
        for (let i = 0; i < total; i++) {
          const file = selectedFiles[i];
          setUploadStatusText(`Uploading file ${i + 1} of ${total}: ${file.name}...`);
          await api.uploadAsset(projectId, folderId, file, description);
        }
      }

      onUploadSuccess();
      onClose();
    } catch (err) {
      setError(err.message || 'File upload failed');
    } finally {
      setUploading(false);
      setUploadStatusText('');
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card card" style={{ maxWidth: '580px', width: '100%', padding: '24px' }}>
        <div className="flex justify-between items-center" style={{ marginBottom: '16px' }}>
          <div>
            <h3 className="font-display" style={{ fontSize: '1.25rem', fontWeight: 700 }}>
              {isReplaceMode ? `Replace File (Upload New Version)` : `Upload Files to Folder`}
            </h3>
            <p className="text-muted" style={{ fontSize: '0.8rem' }}>
              Target Directory: <strong>{folderName || 'Selected Folder'}</strong>
            </p>
          </div>
          <button className="btn-close" onClick={onClose} disabled={uploading}>×</button>
        </div>

        {error && (
          <div className="card text-error" style={{ padding: '10px 14px', marginBottom: '16px', backgroundColor: 'var(--error-light)' }}>
            <AlertCircle size={15} inline style={{ marginRight: '6px' }} />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Dropzone Area */}
          <div 
            className={`dropzone-container ${dragActive ? 'dropzone-active' : ''} ${selectedFiles.length > 0 ? 'dropzone-selected' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              ref={fileInputRef}
              type="file" 
              multiple={!isReplaceMode}
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />

            <div className="text-center">
              <Upload size={34} style={{ color: 'var(--primary, #3b82f6)', margin: '0 auto 8px' }} />
              <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>
                {isReplaceMode 
                  ? 'Drag & drop replacement file, or browse' 
                  : 'Drag & drop multiple files, or click to browse'}
              </div>
              <div className="text-muted" style={{ fontSize: '0.75rem', marginTop: '4px' }}>
                Supports Documents, Images, Videos, Audio, Archives & Code (Up to 500MB per file)
              </div>
            </div>
          </div>

          {/* Selected Files List */}
          {selectedFiles.length > 0 && (
            <div className="selected-files-container card" style={{ marginTop: '12px', padding: '10px 12px', maxHeight: '160px', overflowY: 'auto' }}>
              <div className="flex justify-between items-center mb-2">
                <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }} className="text-muted">
                  Selected Files ({selectedFiles.length})
                </span>
                {!isReplaceMode && (
                  <button 
                    type="button" 
                    className="text-error" 
                    style={{ background: 'none', border: 'none', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600 }}
                    onClick={() => setSelectedFiles([])}
                  >
                    Clear All
                  </button>
                )}
              </div>
              <div className="flex flex-col gap-2">
                {selectedFiles.map((f, idx) => (
                  <div key={idx} className="file-chip flex items-center justify-between" style={{ padding: '6px 10px', background: 'var(--bg-main)', borderRadius: '6px', fontSize: '0.85rem' }}>
                    <div className="flex items-center gap-2" style={{ overflow: 'hidden' }}>
                      <CheckCircle2 size={16} style={{ color: 'var(--success)', flexShrink: 0 }} />
                      <span style={{ fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{f.name}</span>
                      <span className="text-muted" style={{ fontSize: '0.75rem', flexShrink: 0 }}>
                        ({(f.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                    <button 
                      type="button" 
                      onClick={(e) => handleRemoveFile(idx, e)}
                      style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '2px 4px' }}
                      title="Remove file"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Description / Change Notes */}
          <div className="form-group" style={{ marginTop: '16px', marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
              {isReplaceMode ? 'Version Change Notes *' : 'Description / Metadata Notes'}
            </label>
            <textarea 
              className="form-control"
              rows="2"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={isReplaceMode ? "Describe what changed in this version (e.g. Added section 3.2)" : "Optional notes regarding uploaded files"}
              required={isReplaceMode}
            />
          </div>

          {/* Backend Validation Disclosure */}
          <div className="flex items-center gap-2 text-muted" style={{ fontSize: '0.75rem', marginBottom: '16px', background: 'var(--bg-main)', padding: '8px 12px', borderRadius: '6px' }}>
            <ShieldCheck size={14} style={{ color: 'var(--primary)' }} />
            <span>Files are encrypted in private storage and scanned for project authorization.</span>
          </div>

          <div className="flex justify-between items-center">
            <div className="text-muted" style={{ fontSize: '0.8rem' }}>
              {uploadStatusText && <span style={{ color: 'var(--primary)', fontWeight: 600 }}>{uploadStatusText}</span>}
            </div>
            <div className="flex gap-3">
              <button type="button" className="btn btn-secondary" onClick={onClose} disabled={uploading}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary flex items-center gap-2" disabled={uploading || selectedFiles.length === 0}>
                {uploading ? (
                  <>
                    <div className="loading-spinner-sm"></div>
                    <span>Uploading ({selectedFiles.length})...</span>
                  </>
                ) : (
                  <>
                    <Upload size={16} />
                    <span>{isReplaceMode ? 'Commit New Version' : `Upload ${selectedFiles.length > 1 ? `${selectedFiles.length} Files` : 'File'}`}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>

      <style>{`
        .dropzone-container {
          border: 2px dashed var(--border-color, #2a3655);
          border-radius: 8px;
          padding: 24px 20px;
          background: var(--bg-main, #0f172a);
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .dropzone-container:hover, .dropzone-active {
          border-color: var(--primary, #3b82f6);
          background: rgba(59, 130, 246, 0.05);
        }
        .dropzone-selected {
          border-color: var(--primary, #3b82f6);
        }
        .loading-spinner-sm {
          width: 14px;
          height: 14px;
          border: 2px solid rgba(255,255,255,0.3);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
      `}</style>
    </div>
  );
};

export default FileUploadModal;
