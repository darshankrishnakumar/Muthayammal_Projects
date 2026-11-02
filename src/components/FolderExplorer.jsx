import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Folder as FolderIcon, 
  FolderPlus, 
  ChevronRight, 
  ChevronDown, 
  FileText, 
  Image as ImageIcon, 
  Video as VideoIcon, 
  Music, 
  Code as CodeIcon, 
  Archive, 
  Eye, 
  Upload, 
  History, 
  Search, 
  ShieldCheck, 
  Lock, 
  Plus, 
  Trash2, 
  Edit2, 
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  FolderOpen,
  ArrowLeft
} from 'lucide-react';
import { api } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import SecureFileViewer from './SecureFileViewer';
import FileUploadModal from './FileUploadModal';
import VersionHistoryModal from './VersionHistoryModal';
import AdminPermissionManagerModal from './AdminPermissionManagerModal';

const FolderExplorer = ({ project, projects = [], selectedProject = null, onSelectProject = () => {}, onFolderChange = () => {} }) => {
  const { id: routeProjectId, folderId: routeFolderId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const currentProject = project || selectedProject;
  const [folders, setFolders] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [expandedFolders, setExpandedFolders] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Modals state
  const [isCreateFolderModalOpen, setIsCreateFolderModalOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderParentId, setNewFolderParentId] = useState('');

  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [replaceAssetTarget, setReplaceAssetTarget] = useState(null);

  const [viewingAsset, setViewingAsset] = useState(null);
  const [viewingVersionNo, setViewingVersionNo] = useState(null);

  const [historyAsset, setHistoryAsset] = useState(null);

  // Access Control Manager Modal state
  const [permissionTarget, setPermissionTarget] = useState(null); // { folder, asset }
  const [usersList, setUsersList] = useState([]);

  const isManagement = user?.role === 'SUPER_ADMIN' || user?.role === 'ADMIN';

  useEffect(() => {
    if (isManagement) {
      api.getUsers().then(setUsersList).catch(console.warn);
    }
  }, [isManagement]);

  useEffect(() => {
    if (currentProject?.id) {
      loadFolders();
    }
  }, [currentProject?.id]);

  const loadFolders = async (preserveSelectedId = null) => {
    try {
      setLoading(true);
      setError('');
      if (!currentProject?.id) return;
      const data = await api.getProjectFolders(currentProject.id);
      setFolders(data);

      // Auto expand top-level folders by default
      const expandMap = {};
      for (const item of data) {
        expandMap[item.id] = true;
      }
      setExpandedFolders(prev => ({ ...expandMap, ...prev }));

      const targetFolderId = preserveSelectedId || routeFolderId;
      if (targetFolderId) {
        const found = findFolderRecursive(data, targetFolderId);
        if (found) setSelectedFolder(found);
        else setSelectedFolder(null);
      } else {
        setSelectedFolder(null);
      }
    } catch (err) {
      setError(err.message || 'Failed to load project folders');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (folders.length > 0 && routeFolderId) {
      const found = findFolderRecursive(folders, routeFolderId);
      if (found) setSelectedFolder(found);
    } else if (!routeFolderId) {
      setSelectedFolder(null);
    }
  }, [routeFolderId, folders]);

  useEffect(() => {
    onFolderChange(selectedFolder);
  }, [selectedFolder]);

  const findFolderRecursive = (list, id) => {
    for (const f of list) {
      if (f.id === Number(id)) return f;
      if (f.subFolders && f.subFolders.length > 0) {
        const sub = findFolderRecursive(f.subFolders, id);
        if (sub) return sub;
      }
    }
    return null;
  };

  const toggleExpand = (folderId, e) => {
    e.stopPropagation();
    setExpandedFolders(prev => ({
      ...prev,
      [folderId]: !prev[folderId]
    }));
  };

  const handleSelectFolder = (folder) => {
    setSelectedFolder(folder);
    if (currentProject?.id && folder?.id) {
      navigate(`/projects/${currentProject.id}/folders/${folder.id}`);
    }
  };

  const handleBackToProjectRoot = () => {
    setSelectedFolder(null);
    if (currentProject?.id) {
      navigate(`/projects/${currentProject.id}`);
    }
  };

  const handleCreateFolderSubmit = async (e) => {
    e.preventDefault();
    if (!newFolderName.trim()) return;

    if (user?.role !== 'ADMIN' && user?.role !== 'SUPER_ADMIN') {
      setError('Access Denied: Only Administrator and Superadmin accounts are authorized to create new folders.');
      return;
    }

    try {
      setError('');
      setSuccess('');
      const parentId = newFolderParentId ? Number(newFolderParentId) : null;
      await api.createFolder(project.id, {
        name: newFolderName.trim(),
        parentFolderId: parentId
      });

      setSuccess(`Folder '${newFolderName}' created successfully!`);
      setIsCreateFolderModalOpen(false);
      setNewFolderName('');
      setNewFolderParentId('');
      loadFolders(selectedFolder?.id);
    } catch (err) {
      setError(err.message || 'Failed to create folder');
    }
  };

  const handleDeleteFolder = async (folder) => {
    if (!window.confirm(`Are you sure you want to delete folder '${folder.name}'?`)) return;

    try {
      setError('');
      setSuccess('');
      await api.deleteFolder(project.id, folder.id);
      setSuccess(`Folder '${folder.name}' deleted successfully.`);
      setSelectedFolder(null);
      loadFolders();
    } catch (err) {
      setError(err.message || 'Failed to delete folder');
    }
  };

  // Helper to get flatten folder options for parent dropdown
  const getFlattenFolders = (list, depth = 0) => {
    let result = [];
    for (const f of list) {
      result.push({ id: f.id, name: `${'—'.repeat(depth)} ${f.name}` });
      if (f.subFolders && f.subFolders.length > 0) {
        result = result.concat(getFlattenFolders(f.subFolders, depth + 1));
      }
    }
    return result;
  };

  const getFileIcon = (mimeType, ext) => {
    ext = (ext || '').toLowerCase();
    mimeType = (mimeType || '').toLowerCase();

    if (ext === 'pdf' || mimeType.includes('pdf')) return <FileText size={22} style={{ color: '#ef4444' }} />;
    if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'].includes(ext) || mimeType.startsWith('image/')) return <ImageIcon size={22} style={{ color: '#3b82f6' }} />;
    if (['mp4', 'webm', 'mkv', 'mov'].includes(ext) || mimeType.startsWith('video/')) return <VideoIcon size={22} style={{ color: '#8b5cf6' }} />;
    if (['mp3', 'wav', 'ogg'].includes(ext) || mimeType.startsWith('audio/')) return <Music size={22} style={{ color: '#ec4899' }} />;
    if (['zip', 'tar', 'gz', '7z', 'rar'].includes(ext)) return <Archive size={22} style={{ color: '#f59e0b' }} />;
    return <CodeIcon size={22} style={{ color: '#10b981' }} />;
  };

  // Render recursive folder tree node
  const renderTreeNode = (folder, depth = 0) => {
    const isExpanded = Boolean(expandedFolders[folder.id]);
    const isSelected = selectedFolder?.id === folder.id;
    const hasChildren = folder.subFolders && folder.subFolders.length > 0;
    const assetCount = folder.assets?.length || 0;

    return (
      <div key={folder.id} className="folder-tree-node">
        <div 
          className={`folder-tree-item ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${12 + depth * 16}px` }}
          onClick={() => handleSelectFolder(folder)}
        >
          <button 
            className="btn-tree-toggle"
            onClick={(e) => toggleExpand(folder.id, e)}
            style={{ visibility: hasChildren ? 'visible' : 'hidden' }}
          >
            {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </button>

          <span className="folder-icon-wrapper">
            {isSelected ? (
              <FolderOpen size={16} style={{ color: 'var(--primary)' }} />
            ) : (
              <FolderIcon size={16} style={{ color: 'var(--text-muted)' }} />
            )}
          </span>

          <span className="folder-name-label">{folder.name}</span>

          {assetCount > 0 && (
            <span className="asset-count-pill">{assetCount}</span>
          )}
        </div>

        {hasChildren && isExpanded && (
          <div className="folder-sub-tree">
            {folder.subFolders.map(child => renderTreeNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  // Filter files in current folder
  const currentFiles = (selectedFolder?.assets || []).filter(a => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return a.originalFileName.toLowerCase().includes(q) || (a.description && a.description.toLowerCase().includes(q));
  });

  return (
    <div className="folder-explorer-card card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Top Header & Breadcrumbs Bar */}
      <div className="explorer-topbar flex justify-between items-center">
        <div className="flex items-center gap-3" style={{ flex: 1, overflow: 'hidden' }}>
          <div className="breadcrumbs-trail flex items-center gap-1 font-sans">
            <span className="breadcrumb-root" onClick={() => navigate('/projects')}>
              Projects
            </span>
            <ChevronRight size={13} className="text-muted" />
            <span 
              className={`breadcrumb-item ${!selectedFolder ? 'active' : ''}`}
              onClick={handleBackToProjectRoot}
            >
              {currentProject?.projectName || currentProject?.projectCode || 'Project'}
            </span>
            {selectedFolder?.breadcrumbs?.map((crumb, idx) => (
              <React.Fragment key={crumb.id || idx}>
                <ChevronRight size={13} className="text-muted" />
                <span 
                  className={`breadcrumb-item ${idx === selectedFolder.breadcrumbs.length - 1 ? 'active' : ''}`}
                  onClick={() => {
                    const f = findFolderRecursive(folders, crumb.id);
                    if (f) handleSelectFolder(f);
                  }}
                >
                  {crumb.name}
                </span>
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Global Explorer Actions */}
        <div className="flex items-center gap-2">
          {selectedFolder && isManagement && (
            <button 
              className="btn btn-primary btn-sm flex items-center gap-1"
              onClick={() => {
                setReplaceAssetTarget(null);
                setIsUploadModalOpen(true);
              }}
            >
              <Upload size={14} />
              <span>Upload File</span>
            </button>
          )}

          {isManagement && (
            <button 
              className="btn btn-secondary btn-sm flex items-center gap-1"
              onClick={() => {
                setNewFolderParentId(selectedFolder ? selectedFolder.id : '');
                setIsCreateFolderModalOpen(true);
              }}
            >
              <FolderPlus size={14} />
              <span>New Folder</span>
            </button>
          )}
        </div>
      </div>

      {/* Notifications */}
      {error && (
        <div className="card text-error" style={{ margin: '16px', padding: '10px 14px', backgroundColor: 'var(--error-light)' }}>
          <AlertCircle size={15} inline style={{ marginRight: '6px' }} />
          {error}
        </div>
      )}
      {success && (
        <div className="card text-success" style={{ margin: '16px', padding: '10px 14px', backgroundColor: 'var(--success-light)' }}>
          <CheckCircle2 size={15} inline style={{ marginRight: '6px' }} />
          {success}
        </div>
      )}

      {/* Main Single Column Workspace */}
      <div className="explorer-layout-single">
        {/* Right Active Folder Files Workspace */}
        <div className="folder-content-workspace">
          {selectedFolder ? (
            <div>
              {/* Workspace Action Toolbar */}
              <div className="workspace-toolbar flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <h3 className="folder-workspace-title">{selectedFolder.name}</h3>
                  <span className="badge badge-secondary" style={{ fontSize: '0.75rem' }}>
                    {currentFiles.length} file{currentFiles.length === 1 ? '' : 's'}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  {isManagement && (
                    <button 
                      className="btn btn-secondary btn-sm" 
                      style={{ color: 'var(--error)' }}
                      onClick={() => handleDeleteFolder(selectedFolder)}
                      title="Delete folder"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              </div>

              {/* Files Table / Grid */}
              {currentFiles.length === 0 ? (
                <div className="empty-files-placeholder text-center">
                  <FileText size={40} style={{ color: 'var(--text-muted)', margin: '0 auto 12px', opacity: 0.6 }} />
                  <h4 className="font-display" style={{ fontSize: '1rem', fontWeight: 600 }}>No Files in this Folder</h4>
                  <p className="text-muted" style={{ fontSize: '0.8rem', maxWidth: '360px', margin: '4px auto 16px' }}>
                    This directory is currently empty. {isManagement ? 'Click upload below to add project documentation, source code, or assets.' : 'No repository files have been uploaded to this folder yet.'}
                  </p>
                  {isManagement && (
                    <button 
                      className="btn btn-primary btn-sm flex items-center gap-1"
                      style={{ margin: '0 auto' }}
                      onClick={() => {
                        setReplaceAssetTarget(null);
                        setIsUploadModalOpen(true);
                      }}
                    >
                      <Upload size={14} />
                      <span>Upload First File</span>
                    </button>
                  )}
                </div>
              ) : (
                <div className="files-table-container">
                  <table className="table" style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '2px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '12px' }}>File Name & Description</th>
                        <th style={{ padding: '12px' }}>Version</th>
                        <th style={{ padding: '12px' }}>Size</th>
                        <th style={{ padding: '12px' }}>Uploaded By</th>
                        <th style={{ padding: '12px' }}>Date</th>
                        <th style={{ padding: '12px', textAlign: 'right' }}>Security Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {currentFiles.map((file) => {
                        const isFileRestricted = file.restricted;

                        return (
                          <tr key={file.id} className="file-row" style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.85rem', opacity: isFileRestricted && !isManagement ? 0.7 : 1 }}>
                            <td style={{ padding: '12px' }}>
                              <div className="flex items-center gap-3">
                                {getFileIcon(file.mimeType, file.extension)}
                                <div>
                                  <div 
                                    className="file-title-link flex items-center gap-1"
                                    onClick={() => {
                                      if (isFileRestricted && !isManagement) {
                                        setError(`Access Denied: File '${file.originalFileName}' is restricted.`);
                                        return;
                                      }
                                      setViewingAsset(file);
                                      setViewingVersionNo(file.versionNo);
                                    }}
                                  >
                                    {isFileRestricted ? (
                                      <Lock size={13} style={{ color: 'var(--error)' }} />
                                    ) : (
                                      <Lock size={12} style={{ color: 'var(--primary)' }} />
                                    )}
                                    <span style={{ textDecoration: isFileRestricted ? 'line-through' : 'none' }}>{file.originalFileName}</span>
                                    {isFileRestricted && (
                                      <span className="badge badge-danger" style={{ fontSize: '0.65rem', padding: '1px 5px' }}>
                                        🔒 Restricted
                                      </span>
                                    )}
                                  </div>
                                  {file.description && (
                                    <div className="text-muted" style={{ fontSize: '0.75rem', marginTop: '2px' }}>
                                      {file.description}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </td>

                            <td style={{ padding: '12px' }}>
                              <span className="badge badge-primary font-mono" style={{ fontSize: '0.75rem', fontWeight: 700 }}>
                                v{file.versionNo}
                              </span>
                            </td>

                            <td style={{ padding: '12px', color: 'var(--text-muted)' }}>
                              {(file.fileSize / 1024).toFixed(1)} KB
                            </td>

                            <td style={{ padding: '12px', color: 'var(--text-muted)' }}>
                              {file.uploadedBy}
                            </td>

                            <td style={{ padding: '12px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                              {new Date(file.updatedAt || file.createdAt).toLocaleDateString()}
                            </td>

                            <td style={{ padding: '12px', textAlign: 'right' }}>
                              <div className="flex items-center justify-end gap-2">
                                {/* Admin Access Management Button */}
                                {isManagement && (
                                  <button
                                    className="btn btn-secondary btn-sm flex items-center gap-1 action-btn"
                                    onClick={() => setPermissionTarget({ folder: selectedFolder, asset: file })}
                                    title="Manage Access Control for this file"
                                  >
                                    <ShieldCheck size={13} style={{ color: 'var(--primary)' }} />
                                    <span>Access</span>
                                  </button>
                                )}

                                {/* 1. Secure View Action */}
                                <button 
                                  className="btn btn-primary btn-sm flex items-center gap-1 action-btn"
                                  disabled={isFileRestricted && !isManagement}
                                  onClick={() => {
                                    if (isFileRestricted && !isManagement) return;
                                    setViewingAsset(file);
                                    setViewingVersionNo(file.versionNo);
                                  }}
                                  title="Open in DRM Secure Viewer"
                                >
                                  <Eye size={13} />
                                  <span>Secure View</span>
                                </button>

                                {/* 2. Version History Action */}
                                <button 
                                  className="btn btn-secondary btn-sm flex items-center gap-1 action-btn"
                                  disabled={isFileRestricted && !isManagement}
                                  onClick={() => setHistoryAsset(file)}
                                  title="View Version Lineage"
                                >
                                  <History size={13} />
                                  <span>History</span>
                                </button>

                                {/* 3. Replace Action */}
                                {isManagement && (
                                  <button 
                                    className="btn btn-secondary btn-sm flex items-center gap-1 action-btn"
                                    onClick={() => {
                                      setReplaceAssetTarget(file);
                                      setIsUploadModalOpen(true);
                                    }}
                                    title="Upload replacement (v2+)"
                                  >
                                    <Upload size={13} />
                                    <span>Replace</span>
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
            </div>
          ) : (
            <div style={{ padding: '8px' }}>
              <div className="flex items-center gap-2 mb-4 pb-2" style={{ borderBottom: '1px solid var(--border-color)' }}>
                <FolderOpen size={20} style={{ color: 'var(--primary)' }} />
                <h3 className="font-display" style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                  Project Folders ({folders.length})
                </h3>
              </div>
              <p className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '20px' }}>
                Click any folder below to open and view its files and repository contents.
              </p>
              
              {folders.length === 0 ? (
                <div className="text-center p-8 text-muted">
                  <FolderIcon size={40} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
                  <p>No folders created for this project yet.</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  {folders.map(folder => {
                    const isFolderRestricted = folder.restricted;
                    const accessibleCount = (folder.assets || []).filter(a => !a.restricted).length;

                    return (
                      <div 
                        key={folder.id}
                        className="card card-hover flex items-center justify-between"
                        style={{ 
                          padding: '20px', 
                          cursor: isFolderRestricted && !isManagement ? 'not-allowed' : 'pointer', 
                          borderLeft: `4px solid ${isFolderRestricted ? 'var(--error)' : 'var(--primary)'}`, 
                          opacity: isFolderRestricted && !isManagement ? 0.75 : 1,
                          transition: 'all 0.2s ease' 
                        }}
                        onClick={() => {
                          if (isFolderRestricted && !isManagement) {
                            setError(`Access Denied: Folder '${folder.name}' is restricted.`);
                            return;
                          }
                          handleSelectFolder(folder);
                        }}
                      >
                        <div className="flex items-center gap-3" style={{ overflow: 'hidden' }}>
                          {isFolderRestricted ? (
                            <Lock size={36} style={{ color: 'var(--error)', flexShrink: 0 }} />
                          ) : (
                            <FolderIcon size={36} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                          )}
                          <div style={{ overflow: 'hidden' }}>
                            <div className="flex items-center gap-2">
                              <h4 className="font-display" style={{ fontWeight: 700, fontSize: '1.05rem', margin: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {folder.name}
                              </h4>
                              {isFolderRestricted && (
                                <span className="badge badge-danger" style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                                  🔒 Restricted
                                </span>
                              )}
                            </div>
                            <span className="text-muted" style={{ fontSize: '0.8rem' }}>
                              {accessibleCount} accessible file{accessibleCount === 1 ? '' : 's'}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                          {isManagement && (
                            <button
                              className="btn btn-secondary btn-sm flex items-center gap-1"
                              style={{ fontSize: '0.75rem', padding: '4px 8px' }}
                              onClick={() => setPermissionTarget({ folder, asset: null })}
                              title="Manage Folder Access Permissions"
                            >
                              <ShieldCheck size={13} style={{ color: 'var(--primary)' }} />
                              <span>Access</span>
                            </button>
                          )}
                          <ChevronRight size={18} className="text-muted" />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Modal: Create Folder */}
      {isCreateFolderModalOpen && (
        <div className="modal-backdrop">
          <div className="modal-card card" style={{ maxWidth: '440px', width: '100%', padding: '24px' }}>
            <div className="flex justify-between items-center" style={{ marginBottom: '16px' }}>
              <h3 className="font-display" style={{ fontSize: '1.15rem', fontWeight: 700 }}>Create New Folder</h3>
              <button className="btn-close" onClick={() => setIsCreateFolderModalOpen(false)}>×</button>
            </div>

            <form onSubmit={handleCreateFolderSubmit}>
              <div className="form-group" style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Folder Name *
                </label>
                <input 
                  type="text"
                  className="form-control"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="e.g. Architecture Diagrams"
                  required
                />
              </div>

              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                  Parent Folder Location
                </label>
                <select 
                  className="form-control"
                  value={newFolderParentId}
                  onChange={(e) => setNewFolderParentId(e.target.value)}
                >
                  <option value="">-- Project Root (Top Level) --</option>
                  {getFlattenFolders(folders).map(item => (
                    <option key={item.id} value={item.id}>{item.name}</option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-3">
                <button type="button" className="btn btn-secondary" onClick={() => setIsCreateFolderModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Folder
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Upload / Replace File */}
      {isUploadModalOpen && (
        <FileUploadModal 
          projectId={project.id}
          folderId={selectedFolder?.id}
          folderName={selectedFolder?.name}
          replaceAsset={replaceAssetTarget}
          onClose={() => {
            setIsUploadModalOpen(false);
            setReplaceAssetTarget(null);
          }}
          onUploadSuccess={() => {
            loadFolders(selectedFolder?.id);
          }}
        />
      )}

      {/* Modal: Version History */}
      {historyAsset && (
        <VersionHistoryModal 
          asset={historyAsset}
          project={project}
          onClose={() => setHistoryAsset(null)}
          onPreviewVersion={(versionNo) => {
            setViewingAsset(historyAsset);
            setViewingVersionNo(versionNo);
          }}
          onVersionRestored={() => {
            loadFolders(selectedFolder?.id);
          }}
        />
      )}

      {/* Modal: Secure DRM File Viewer */}
      {viewingAsset && (
        <SecureFileViewer 
          asset={viewingAsset}
          project={project}
          versionNo={viewingVersionNo}
          onClose={() => {
            setViewingAsset(null);
            setViewingVersionNo(null);
          }}
        />
      )}

      {/* Modal: Admin Access Management & Permission Manager */}
      {permissionTarget && (
        <AdminPermissionManagerModal
          folder={permissionTarget.folder}
          asset={permissionTarget.asset}
          project={project || currentProject}
          usersList={usersList}
          onClose={() => setPermissionTarget(null)}
          onPermissionUpdated={() => loadFolders(selectedFolder?.id)}
        />
      )}

      <style>{`
        .explorer-topbar {
          padding: 12px 20px;
          border-bottom: 1px solid var(--border-color, #2a3655);
          background: var(--bg-main, #0f172a);
        }
        .breadcrumbs-trail {
          font-size: 0.85rem;
          font-weight: 500;
        }
        .breadcrumb-root, .breadcrumb-item {
          cursor: pointer;
          color: var(--text-muted);
          transition: color 0.15s ease;
        }
        .breadcrumb-root:hover, .breadcrumb-item:hover {
          color: var(--primary);
        }
        .breadcrumb-item.active {
          color: var(--text-main);
          font-weight: 700;
        }
        .explorer-layout-single {
          width: 100%;
          min-height: 440px;
        }
        .folder-tree-sidebar {
          border-right: 1px solid var(--border-color);
          background: var(--bg-sidebar);
          display: flex;
          flex-direction: column;
        }
        .sidebar-header {
          padding: 12px 16px;
          border-bottom: 1px solid var(--border-color);
          background: var(--bg-card);
        }
        .sidebar-title {
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-muted);
        }
        .folder-tree-scroll {
          flex: 1;
          overflow-y: auto;
          padding: 8px 0;
        }
        .folder-tree-item {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          cursor: pointer;
          font-size: 0.85rem;
          color: var(--text-main);
          transition: all 0.15s ease;
          border-left: 3px solid transparent;
        }
        .folder-tree-item:hover {
          background: var(--primary-light);
        }
        .folder-tree-item.selected {
          background: var(--primary-light);
          border-left-color: var(--primary);
          color: var(--primary);
          font-weight: 600;
        }
        .btn-tree-toggle {
          background: none;
          border: none;
          color: var(--text-muted);
          padding: 0;
          cursor: pointer;
          display: flex;
          align-items: center;
        }
        .folder-name-label {
          flex: 1;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .asset-count-pill {
          font-size: 0.7rem;
          background: hsl(220, 20%, 92%);
          color: var(--text-muted);
          padding: 2px 6px;
          border-radius: 10px;
        }
        .folder-content-workspace {
          padding: 20px;
          background: var(--bg-card);
        }
        .workspace-toolbar {
          margin-bottom: 20px;
        }
        .folder-workspace-title {
          font-size: 1.25rem;
          font-weight: 700;
          margin: 0;
        }
        .search-input-wrapper {
          position: relative;
        }
        .search-icon {
          position: absolute;
          left: 10px;
          top: 50%;
          transform: translateY(-50%);
        }
        .search-input {
          padding: 6px 12px 6px 30px;
          border-radius: 6px;
          border: 1px solid var(--border-color);
          background: var(--bg-main);
          color: var(--text-main);
          font-size: 0.8rem;
          width: 180px;
        }
        .file-row:hover {
          background: var(--primary-light);
        }
        .file-title-link {
          font-weight: 600;
          cursor: pointer;
          color: var(--text-main);
          transition: color 0.15s ease;
        }
        .file-title-link:hover {
          color: var(--primary);
        }
        .action-btn {
          padding: 4px 8px;
          font-size: 0.75rem;
        }
        .empty-files-placeholder {
          padding: 60px 20px;
          background: var(--bg-main);
          border-radius: 8px;
          border: 1px dashed var(--border-color);
        }
      `}</style>
    </div>
  );
};

export default FolderExplorer;
