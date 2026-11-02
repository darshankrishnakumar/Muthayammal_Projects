import { Fragment, useEffect, useMemo, useRef, useState } from 'react';
import {
  Archive, ChevronRight, Database, Download, Eye, File as FileIcon, FileCode, FileText, Folder as FolderIcon,
  FolderPlus, History, Image as ImageIcon, Lock, Music, Pencil, Search, ShieldCheck, Trash2, Upload, Video as VideoIcon,
} from 'lucide-react';
import { api } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { useAsync } from '../hooks/useAsync';
import { Badge, ConfirmDialog, EmptyState, ErrorState, Field, Modal, SkeletonRows, useToast } from './ui';
import { bytes, date } from '../utils/format';
import SecureFileViewer from './SecureFileViewer';
import FileUploadModal from './FileUploadModal';
import VersionHistoryModal from './VersionHistoryModal';
import AdminPermissionManagerModal from './AdminPermissionManagerModal';

const CATEGORY_LABELS = {
  SOURCE_CODE: 'Source code',
  DOCUMENTATION: 'Documentation',
  PRESENTATION: 'Presentation',
  DATABASE: 'Database',
  VIDEO: 'Video',
  SCREENSHOT: 'Screenshot',
  OTHER: 'Other',
};

const LOCKED_TEXT = 'Unlocks after purchase';

const fileIconFor = (file) => {
  const ext = (file.extension || '').toLowerCase();
  const mime = (file.mimeType || '').toLowerCase();
  if (file.category === 'DATABASE' || ext === 'sql') return Database;
  if (file.category === 'VIDEO' || mime.startsWith('video/') || ['mp4', 'webm', 'mkv', 'mov', 'avi'].includes(ext)) return VideoIcon;
  if (file.category === 'SCREENSHOT' || mime.startsWith('image/')) return ImageIcon;
  if (mime.startsWith('audio/')) return Music;
  if (['zip', 'tar', 'gz', '7z', 'rar'].includes(ext)) return Archive;
  if (file.category === 'SOURCE_CODE') return FileCode;
  if (ext === 'pdf' || ['doc', 'docx', 'txt', 'md', 'ppt', 'pptx'].includes(ext)) return FileText;
  return FileIcon;
};

const findFolder = (list, id) => {
  for (const f of list || []) {
    if (String(f.id) === String(id)) return f;
    const sub = findFolder(f.subFolders, id);
    if (sub) return sub;
  }
  return null;
};

const flattenFolders = (list, depth = 0, out = []) => {
  for (const f of list || []) {
    out.push({ id: f.id, label: `${'  '.repeat(depth)}${depth ? '└ ' : ''}${f.name}` });
    flattenFolders(f.subFolders, depth + 1, out);
  }
  return out;
};

/**
 * Folder and file browser for a project.
 * Write actions (folders, uploads, versions) are limited to the Super Admin and the developer who owns a
 * custom project; access rules are Super Admin only. Everyone else browses read-only. The server enforces
 * the same rules — this only hides controls that would be rejected.
 */
const noop = () => {};

const FolderExplorer = ({ project, selectedProject = null, onFolderChange = noop }) => {
  const currentProject = project || selectedProject;
  const projectId = currentProject?.id;
  const { user } = useAuth();
  const { notify } = useToast();

  const isSuperAdmin = user?.role === 'SUPER_ADMIN';
  const isOwningDeveloper =
    user?.role === 'PROJECT_DEVELOPER' &&
    currentProject?.projectType === 'CUSTOM' &&
    currentProject?.developer?.id != null &&
    currentProject.developer.id === user?.id;
  const canWrite = isSuperAdmin || isOwningDeveloper;
  const canManagePermissions = isSuperAdmin;

  // Folder navigation is local state: the app has no folder-level route.
  const [selectedFolderId, setSelectedFolderId] = useState(null);
  useEffect(() => {
    setSelectedFolderId(null);
  }, [projectId]);

  const { data, loading, error, reload } = useAsync(
    () => (projectId ? api.getProjectFolders(projectId) : Promise.resolve([])),
    [projectId],
  );
  const folders = useMemo(() => data || [], [data]);
  const selectedFolder = useMemo(
    () => (selectedFolderId ? findFolder(folders, selectedFolderId) : null),
    [folders, selectedFolderId],
  );

  const onFolderChangeRef = useRef(onFolderChange);
  useEffect(() => {
    onFolderChangeRef.current = onFolderChange;
  });
  useEffect(() => {
    onFolderChangeRef.current?.(selectedFolder);
  }, [selectedFolder]);

  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Dialog state
  const [folderDialog, setFolderDialog] = useState(null); // { mode: 'create' | 'rename', folder? }
  const [folderName, setFolderName] = useState('');
  const [folderParentId, setFolderParentId] = useState('');
  const [folderError, setFolderError] = useState('');
  const [folderSaving, setFolderSaving] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [uploadState, setUploadState] = useState(null); // { replaceAsset }
  const [viewing, setViewing] = useState(null); // { asset, versionNo }
  const [historyAsset, setHistoryAsset] = useState(null);
  const [permissionTarget, setPermissionTarget] = useState(null); // { folder, asset }
  const [downloadingId, setDownloadingId] = useState(null);

  const openFolder = (folder) => {
    setSearchQuery('');
    setCategoryFilter('');
    setSelectedFolderId(folder.id);
  };

  const openRoot = () => {
    setSearchQuery('');
    setCategoryFilter('');
    setSelectedFolderId(null);
  };

  const openCreateFolder = () => {
    setFolderDialog({ mode: 'create' });
    setFolderName('');
    setFolderParentId(selectedFolder ? String(selectedFolder.id) : '');
    setFolderError('');
  };

  const openRenameFolder = (folder) => {
    setFolderDialog({ mode: 'rename', folder });
    setFolderName(folder.name);
    setFolderError('');
  };

  const submitFolderDialog = async (e) => {
    e.preventDefault();
    const name = folderName.trim();
    if (!name) {
      setFolderError('Enter a folder name.');
      return;
    }
    setFolderSaving(true);
    setFolderError('');
    try {
      if (folderDialog.mode === 'create') {
        await api.createFolder(projectId, { name, parentFolderId: folderParentId ? Number(folderParentId) : null });
        notify(`Folder “${name}” created`);
      } else {
        await api.updateFolder(projectId, folderDialog.folder.id, { name });
        notify(`Renamed to “${name}”`);
      }
      setFolderDialog(null);
      reload();
    } catch (err) {
      setFolderError(err.message);
    } finally {
      setFolderSaving(false);
    }
  };

  const confirmDeleteFolder = async () => {
    if (!deleteTarget) return;
    setDeleteBusy(true);
    try {
      await api.deleteFolder(projectId, deleteTarget.id);
      notify(`Folder “${deleteTarget.name}” deleted`);
      const wasOpen = selectedFolder && (selectedFolder.id === deleteTarget.id || selectedFolder.breadcrumbs?.some((c) => c.id === deleteTarget.id));
      setDeleteTarget(null);
      if (wasOpen) {
        const parent = deleteTarget.parentFolderId ? findFolder(folders, deleteTarget.parentFolderId) : null;
        if (parent) openFolder(parent);
        else openRoot();
      }
      reload();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setDeleteBusy(false);
    }
  };

  const handleDownload = async (file) => {
    setDownloadingId(file.id);
    try {
      await api.downloadAsset(file.id, file.originalFileName);
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setDownloadingId(null);
    }
  };

  const openViewer = (file, versionNo = file.versionNo) => {
    if (file.restricted) return;
    setViewing({ asset: file, versionNo });
  };

  const breadcrumbTrail = selectedFolder
    ? (selectedFolder.breadcrumbs?.length ? selectedFolder.breadcrumbs : [{ id: selectedFolder.id, name: selectedFolder.name }])
    : [];

  const currentFiles = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return (selectedFolder?.assets || []).filter((a) => {
      if (categoryFilter && a.category !== categoryFilter) return false;
      if (!q) return true;
      return (a.originalFileName || '').toLowerCase().includes(q) || (a.description || '').toLowerCase().includes(q);
    });
  }, [selectedFolder, searchQuery, categoryFilter]);

  const availableCategories = useMemo(
    () => [...new Set((selectedFolder?.assets || []).map((a) => a.category).filter(Boolean))],
    [selectedFolder],
  );

  const childFolders = selectedFolder ? selectedFolder.subFolders || [] : folders;
  const lockedCount = (selectedFolder?.assets || []).filter((a) => a.restricted).length;

  if (!projectId) return null;
  if (error) return <ErrorState error={error} onRetry={reload} />;

  const renderFolderRow = (folder) => {
    const locked = folder.restricted && !canWrite;
    const fileCount = folder.assets?.length || 0;
    const subCount = folder.subFolders?.length || 0;
    return (
      <div
        key={folder.id}
        className={`list-item ${locked ? '' : 'cursor-pointer'}`}
        role={locked ? undefined : 'button'}
        tabIndex={locked ? undefined : 0}
        onClick={() => !locked && openFolder(folder)}
        onKeyDown={(e) => !locked && e.key === 'Enter' && openFolder(folder)}
        style={locked ? { opacity: 0.7 } : undefined}
      >
        <span className="stat-icon shrink-0">
          {folder.restricted ? <Lock aria-hidden="true" /> : <FolderIcon aria-hidden="true" />}
        </span>
        <div className="flex-1 min-w-0">
          <div className="font-medium truncate">{folder.name}</div>
          <div className="text-xs text-subtle">
            {locked
              ? 'You do not have access to this folder'
              : [`${fileCount} file${fileCount === 1 ? '' : 's'}`, subCount ? `${subCount} folder${subCount === 1 ? '' : 's'}` : null].filter(Boolean).join(' · ')}
          </div>
        </div>
        {folder.restricted && <Badge tone="warning">Restricted</Badge>}
        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
          {canManagePermissions && (
            <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setPermissionTarget({ folder, asset: null })} title="Access rules" aria-label="Access rules">
              <ShieldCheck aria-hidden="true" />
            </button>
          )}
          {canWrite && (
            <>
              <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => openRenameFolder(folder)} title="Rename" aria-label="Rename">
                <Pencil aria-hidden="true" />
              </button>
              <button type="button" className="btn btn-danger-ghost btn-icon btn-sm" onClick={() => setDeleteTarget(folder)} title="Delete" aria-label="Delete">
                <Trash2 aria-hidden="true" />
              </button>
            </>
          )}
        </div>
        {!locked && <ChevronRight size={16} className="text-subtle shrink-0" aria-hidden="true" />}
      </div>
    );
  };

  return (
    <>
      <section className="card card-flush">
        <header className="card-header flex-wrap">
          <nav className="breadcrumbs" aria-label="Folder path" style={{ marginBottom: 0 }}>
            <button type="button" className={selectedFolder ? 'text-muted' : 'font-medium'} onClick={openRoot}>
              {currentProject?.projectName || currentProject?.projectCode || 'Files'}
            </button>
            {breadcrumbTrail.map((crumb, idx) => {
              const last = idx === breadcrumbTrail.length - 1;
              return (
                <Fragment key={crumb.id ?? idx}>
                  <ChevronRight aria-hidden="true" />
                  {last ? (
                    <span className="font-medium" style={{ color: 'var(--text)' }}>{crumb.name}</span>
                  ) : (
                    <button
                      type="button"
                      className="text-muted"
                      onClick={() => {
                        const f = findFolder(folders, crumb.id);
                        if (f) openFolder(f);
                      }}
                    >
                      {crumb.name}
                    </button>
                  )}
                </Fragment>
              );
            })}
          </nav>
          <div className="flex items-center gap-2">
            {canWrite && (
              <button type="button" className="btn btn-secondary btn-sm" onClick={openCreateFolder}>
                <FolderPlus aria-hidden="true" /> New folder
              </button>
            )}
            {canWrite && selectedFolder && (
              <button type="button" className="btn btn-primary btn-sm" onClick={() => setUploadState({ replaceAsset: null })}>
                <Upload aria-hidden="true" /> Upload
              </button>
            )}
          </div>
        </header>

        {loading && !data ? (
          <div className="p-4"><SkeletonRows rows={4} /></div>
        ) : !selectedFolder ? (
          folders.length === 0 ? (
            <EmptyState
              icon={FolderIcon}
              title="No folders yet"
              text={canWrite ? 'Create a folder to start organizing this project’s files.' : 'Files will appear here once they are added.'}
              action={canWrite && (
                <button type="button" className="btn btn-primary" onClick={openCreateFolder}><FolderPlus aria-hidden="true" /> New folder</button>
              )}
            />
          ) : (
            <div className="list">{folders.map(renderFolderRow)}</div>
          )
        ) : (
          <>
            <div className="flex items-center justify-between gap-3 flex-wrap" style={{ padding: '14px 20px', borderBottom: '1px solid var(--border)' }}>
              <div className="flex items-center gap-2 min-w-0">
                <h3 className="section-title truncate">{selectedFolder.name}</h3>
                <Badge>{selectedFolder.assets?.length || 0} file{selectedFolder.assets?.length === 1 ? '' : 's'}</Badge>
                {lockedCount > 0 && <Badge tone="warning"><Lock aria-hidden="true" /> {lockedCount} locked</Badge>}
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                {(selectedFolder.assets?.length || 0) > 0 && (
                  <>
                    <div className="input-with-icon" style={{ width: 220 }}>
                      <Search aria-hidden="true" />
                      <input className="input input-sm" placeholder="Search files" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
                    </div>
                    {availableCategories.length > 1 && (
                      <select className="select input-sm" style={{ width: 160 }} value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} aria-label="Category">
                        <option value="">All categories</option>
                        {availableCategories.map((c) => <option key={c} value={c}>{CATEGORY_LABELS[c] || c}</option>)}
                      </select>
                    )}
                  </>
                )}
                {canManagePermissions && (
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => setPermissionTarget({ folder: selectedFolder, asset: null })}>
                    <ShieldCheck aria-hidden="true" /> Access
                  </button>
                )}
                {canWrite && (
                  <>
                    <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => openRenameFolder(selectedFolder)} title="Rename folder" aria-label="Rename folder">
                      <Pencil aria-hidden="true" />
                    </button>
                    <button type="button" className="btn btn-danger-ghost btn-icon btn-sm" onClick={() => setDeleteTarget(selectedFolder)} title="Delete folder" aria-label="Delete folder">
                      <Trash2 aria-hidden="true" />
                    </button>
                  </>
                )}
              </div>
            </div>

            {childFolders.length > 0 && <div className="list border-b">{childFolders.map(renderFolderRow)}</div>}

            {(selectedFolder.assets?.length || 0) === 0 ? (
              childFolders.length === 0 && (
                <EmptyState
                  icon={FileText}
                  title="This folder is empty"
                  text={canWrite ? 'Upload documentation, source code or media.' : 'No files have been added to this folder yet.'}
                  action={canWrite && (
                    <button type="button" className="btn btn-primary" onClick={() => setUploadState({ replaceAsset: null })}>
                      <Upload aria-hidden="true" /> Upload files
                    </button>
                  )}
                />
              )
            ) : currentFiles.length === 0 ? (
              <EmptyState icon={Search} title="No files match" text="Try a different search or category." />
            ) : (
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th className="hide-lg">Version</th>
                      <th>Size</th>
                      <th className="hide-lg">Updated</th>
                      <th className="text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentFiles.map((file) => {
                      const locked = Boolean(file.restricted);
                      const Icon = locked ? Lock : fileIconFor(file);
                      return (
                        <tr key={file.id}>
                          <td style={{ minWidth: 220 }}>
                            <div className="flex items-center gap-3">
                              <span className="stat-icon shrink-0"><Icon aria-hidden="true" /></span>
                              <div className="min-w-0">
                                {locked ? (
                                  <span className="font-medium text-muted">{file.originalFileName}</span>
                                ) : (
                                  <button type="button" className="font-medium text-left" onClick={() => openViewer(file)} style={{ color: 'var(--text)' }}>
                                    {file.originalFileName}
                                  </button>
                                )}
                                <div className="flex items-center gap-2 flex-wrap mt-1">
                                  {file.category && <Badge>{CATEGORY_LABELS[file.category] || file.category}</Badge>}
                                  {file.previewable && currentProject?.accessLevel === 'PREVIEW' && !locked && <Badge tone="info">Preview</Badge>}
                                  {locked && <span className="text-xs text-warning flex items-center gap-1"><Lock size={12} aria-hidden="true" /> {LOCKED_TEXT}</span>}
                                </div>
                                {file.description && <div className="text-xs text-subtle mt-1 truncate" style={{ maxWidth: 360 }}>{file.description}</div>}
                              </div>
                            </div>
                          </td>
                          <td className="hide-lg"><Badge className="font-mono">v{file.versionNo}</Badge></td>
                          <td className="cell-muted nowrap">{bytes(file.fileSize)}</td>
                          <td className="cell-muted nowrap hide-lg">
                            <div>{date(file.updatedAt || file.createdAt)}</div>
                            {file.uploadedBy && <div className="text-xs text-subtle">{file.uploadedBy}</div>}
                          </td>
                          <td>
                            <div className="flex items-center justify-end gap-1">
                              {!locked && (
                                <>
                                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => openViewer(file)}>
                                    <Eye aria-hidden="true" /> View
                                  </button>
                                  <button
                                    type="button"
                                    className="btn btn-ghost btn-icon btn-sm"
                                    onClick={() => handleDownload(file)}
                                    disabled={downloadingId === file.id}
                                    title="Download"
                                    aria-label="Download"
                                  >
                                    {downloadingId === file.id ? <span className="spinner" /> : <Download aria-hidden="true" />}
                                  </button>
                                  <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setHistoryAsset(file)} title="Version history" aria-label="Version history">
                                    <History aria-hidden="true" />
                                  </button>
                                </>
                              )}
                              {canWrite && (
                                <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setUploadState({ replaceAsset: file })} title="Upload new version" aria-label="Upload new version">
                                  <Upload aria-hidden="true" />
                                </button>
                              )}
                              {canManagePermissions && (
                                <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setPermissionTarget({ folder: selectedFolder, asset: file })} title="Access rules" aria-label="Access rules">
                                  <ShieldCheck aria-hidden="true" />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </section>

      <Modal
        open={Boolean(folderDialog)}
        onClose={() => !folderSaving && setFolderDialog(null)}
        title={folderDialog?.mode === 'rename' ? 'Rename folder' : 'New folder'}
        footer={
          <>
            <button type="button" className="btn btn-secondary" onClick={() => setFolderDialog(null)} disabled={folderSaving}>Cancel</button>
            <button type="submit" form="folder-form" className="btn btn-primary" disabled={folderSaving || !folderName.trim()}>
              {folderSaving && <span className="spinner" />} {folderDialog?.mode === 'rename' ? 'Rename' : 'Create folder'}
            </button>
          </>
        }
      >
        <form id="folder-form" onSubmit={submitFolderDialog}>
          {folderError && <div className="alert alert-danger">{folderError}</div>}
          <Field label="Name" htmlFor="folder-name">
            <input
              id="folder-name"
              className="input"
              value={folderName}
              onChange={(e) => setFolderName(e.target.value)}
              placeholder="e.g. Architecture diagrams"
              autoFocus
              required
            />
          </Field>
          {folderDialog?.mode === 'create' && (
            <Field label="Location" htmlFor="folder-parent">
              <select id="folder-parent" className="select" value={folderParentId} onChange={(e) => setFolderParentId(e.target.value)}>
                <option value="">Project root</option>
                {flattenFolders(folders).map((f) => <option key={f.id} value={String(f.id)}>{f.label}</option>)}
              </select>
            </Field>
          )}
        </form>
      </Modal>

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        title="Delete folder"
        text={deleteTarget ? `“${deleteTarget.name}” and everything inside it will be removed from this project.` : ''}
        confirmLabel="Delete"
        tone="danger"
        busy={deleteBusy}
        onConfirm={confirmDeleteFolder}
        onClose={() => !deleteBusy && setDeleteTarget(null)}
      />

      {uploadState && canWrite && (
        <FileUploadModal
          projectId={projectId}
          folderId={selectedFolder?.id}
          folderName={selectedFolder?.name}
          replaceAsset={uploadState.replaceAsset}
          onClose={() => setUploadState(null)}
          onUploadSuccess={reload}
        />
      )}

      {historyAsset && (
        <VersionHistoryModal
          asset={historyAsset}
          canRestore={canWrite}
          onClose={() => setHistoryAsset(null)}
          onPreviewVersion={(versionNo) => openViewer(historyAsset, versionNo)}
          onVersionRestored={reload}
        />
      )}

      {viewing && (
        <SecureFileViewer
          asset={viewing.asset}
          versionNo={viewing.versionNo}
          onClose={() => setViewing(null)}
        />
      )}

      {permissionTarget && canManagePermissions && (
        <AdminPermissionManagerModal
          folder={permissionTarget.folder}
          asset={permissionTarget.asset}
          onClose={() => setPermissionTarget(null)}
          onPermissionUpdated={reload}
        />
      )}
    </>
  );
};

export default FolderExplorer;
