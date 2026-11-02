import { useRef, useState } from 'react';
import { File as FileIcon, Upload, X } from 'lucide-react';
import { api } from '../utils/api';
import { Modal, Field, Alert, useToast } from './ui';
import { bytes } from '../utils/format';

const MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024; // 500 MB
const ALLOWED_EXTS = [
  'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'csv', 'txt', 'rtf', 'md',
  'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'ico',
  'mp4', 'webm', 'mkv', 'mov', 'avi', 'mp3', 'wav', 'ogg', 'aac', 'm4a',
  'zip', 'tar', 'gz', '7z', 'rar',
  'java', 'js', 'jsx', 'ts', 'tsx', 'py', 'c', 'cpp', 'h', 'hpp', 'cs', 'go',
  'html', 'htm', 'css', 'scss', 'json', 'xml', 'yaml', 'yml', 'sql', 'sh', 'bat', 'properties',
];

const validateFile = (file) => {
  if (!file) return 'Choose a file to upload.';
  if (file.size > MAX_FILE_SIZE_BYTES) return `${file.name} is ${bytes(file.size)}; the limit is 500 MB.`;
  const ext = (file.name.split('.').pop() || '').toLowerCase();
  if (!ALLOWED_EXTS.includes(ext)) return `.${ext} files are not supported. Upload documents, media, source code or archives.`;
  return null;
};

/**
 * Uploads new files into a folder, or a replacement version of an existing asset.
 * Only rendered for users with write access (enforced again server-side).
 */
const FileUploadModal = ({ projectId, folderId, folderName, replaceAsset = null, onClose, onUploadSuccess }) => {
  const { notify } = useToast();
  const fileInputRef = useRef(null);
  const isReplace = Boolean(replaceAsset);

  const [files, setFiles] = useState([]);
  const [description, setDescription] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progressText, setProgressText] = useState('');

  const addFiles = (list) => {
    const incoming = Array.from(list || []);
    if (!incoming.length) return;
    if (isReplace) {
      const problem = validateFile(incoming[0]);
      setError(problem || '');
      setFiles(problem ? [] : [incoming[0]]);
      return;
    }
    for (const f of incoming) {
      const problem = validateFile(f);
      if (problem) {
        setError(problem);
        return;
      }
    }
    setError('');
    setFiles((prev) => [...prev, ...incoming.filter((f) => !prev.some((p) => p.name === f.name && p.size === f.size))]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!files.length) {
      setError('Choose at least one file.');
      return;
    }
    if (isReplace && !description.trim()) {
      setError('Describe what changed in this version.');
      return;
    }
    setUploading(true);
    setError('');
    let uploaded = 0;
    try {
      if (isReplace) {
        setProgressText(`Uploading new version of ${replaceAsset.originalFileName}…`);
        await api.replaceAsset(replaceAsset.id, files[0], description.trim());
        notify(`New version of ${replaceAsset.originalFileName} uploaded`);
      } else {
        for (let i = 0; i < files.length; i++) {
          setProgressText(`Uploading ${i + 1} of ${files.length}: ${files[i].name}`);
          await api.uploadAsset(projectId, folderId, files[i], description.trim());
          uploaded++;
        }
        notify(`${uploaded} file${uploaded === 1 ? '' : 's'} uploaded`);
      }
      onUploadSuccess?.();
      onClose();
    } catch (err) {
      if (uploaded > 0) {
        // Keep only the files that did not make it so the user can retry.
        setFiles((prev) => prev.slice(uploaded));
        onUploadSuccess?.();
      }
      setError(err.message);
    } finally {
      setUploading(false);
      setProgressText('');
    }
  };

  return (
    <Modal
      open
      size="lg"
      onClose={() => !uploading && onClose()}
      title={isReplace ? 'Upload a new version' : 'Upload files'}
      description={isReplace ? `${replaceAsset.originalFileName} · currently v${replaceAsset.versionNo}` : `To ${folderName || 'the selected folder'}`}
      footer={
        <>
          <span className="text-sm text-muted truncate" style={{ marginRight: 'auto', alignSelf: 'center' }}>{progressText}</span>
          <button type="button" className="btn btn-secondary" onClick={onClose} disabled={uploading}>Cancel</button>
          <button type="submit" form="upload-form" className="btn btn-primary" disabled={uploading || !files.length}>
            {uploading ? <span className="spinner" /> : <Upload aria-hidden="true" />}
            {isReplace ? 'Upload version' : `Upload ${files.length > 1 ? `${files.length} files` : 'file'}`}
          </button>
        </>
      }
    >
      <form id="upload-form" onSubmit={handleSubmit}>
        {error && <Alert tone="danger">{error}</Alert>}

        <div
          className={`dropzone ${dragActive ? 'is-active' : ''}`}
          role="button"
          tabIndex={0}
          onClick={() => !uploading && fileInputRef.current?.click()}
          onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && fileInputRef.current?.click()}
          onDragEnter={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragLeave={(e) => { e.preventDefault(); setDragActive(false); }}
          onDrop={(e) => { e.preventDefault(); setDragActive(false); addFiles(e.dataTransfer.files); }}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple={!isReplace}
            className="hidden"
            onChange={(e) => { addFiles(e.target.files); e.target.value = ''; }}
          />
          <Upload size={20} aria-hidden="true" className="mx-auto mb-2" />
          <div className="font-medium" style={{ color: 'var(--text)' }}>
            {isReplace ? 'Drop the replacement file, or click to browse' : 'Drop files here, or click to browse'}
          </div>
          <p className="text-sm mt-1">Documents, images, video, audio, archives and source code up to 500 MB each.</p>
        </div>

        {files.length > 0 && (
          <div className="list border rounded mt-3" style={{ maxHeight: 180, overflowY: 'auto' }}>
            {files.map((f, i) => (
              <div key={`${f.name}-${f.size}`} className="list-item" style={{ padding: '8px 12px' }}>
                <FileIcon size={15} aria-hidden="true" className="text-muted shrink-0" />
                <span className="flex-1 truncate text-sm">{f.name}</span>
                <span className="text-xs text-subtle shrink-0">{bytes(f.size)}</span>
                <button
                  type="button"
                  className="btn btn-ghost btn-icon btn-sm"
                  onClick={() => setFiles((prev) => prev.filter((_, idx) => idx !== i))}
                  disabled={uploading}
                  aria-label={`Remove ${f.name}`}
                >
                  <X aria-hidden="true" />
                </button>
              </div>
            ))}
          </div>
        )}

        <Field
          label={isReplace ? 'What changed' : 'Description'}
          hint={isReplace ? 'Shown in the version history.' : 'Optional. Applied to every file in this upload.'}
          className="mt-4"
          htmlFor="upload-description"
        >
          <textarea
            id="upload-description"
            className="textarea"
            rows={2}
            style={{ minHeight: 72 }}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={isReplace ? 'e.g. Updated the database schema in section 3.2' : ''}
            required={isReplace}
            disabled={uploading}
          />
        </Field>
      </form>
    </Modal>
  );
};

export default FileUploadModal;
