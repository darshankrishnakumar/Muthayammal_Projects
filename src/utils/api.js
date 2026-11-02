import { normalizeDeadline } from './dateUtils';

/**
 * API client for the Spring Boot backend.
 *
 * Every call goes to the real backend. There is no mock data and no silent fallback:
 * failures surface as ApiError with the server's message so screens can show them.
 * All authorization is enforced by the backend; nothing here is a security control.
 */

const DEV_DEFAULT_URL = 'http://localhost:8080';
const OVERRIDE_KEY = 'CUSTOM_API_URL';

export class ApiError extends Error {
  constructor(message, status, body) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

/** Base URL ending in /api. Production builds require VITE_API_URL. */
export const getApiBaseUrl = () => {
  let raw = '';
  if (import.meta.env.DEV) {
    try {
      raw = (localStorage.getItem(OVERRIDE_KEY) || '').trim();
    } catch {
      raw = '';
    }
  }
  if (!raw) raw = (import.meta.env.VITE_API_URL || '').trim();
  if (!raw) {
    if (import.meta.env.PROD) {
      console.error('VITE_API_URL is not configured for this build.');
    }
    raw = DEV_DEFAULT_URL;
  }
  raw = raw.replace(/\/+$/, '');
  return raw.endsWith('/api') ? raw : `${raw}/api`;
};

/** Development-only override for pointing the UI at another backend. Ignored in production builds. */
export const setCustomApiUrl = (url) => {
  if (!import.meta.env.DEV) return;
  try {
    if (url && url.trim()) localStorage.setItem(OVERRIDE_KEY, url.trim());
    else localStorage.removeItem(OVERRIDE_KEY);
  } catch {
    /* storage unavailable */
  }
};

const token = () => {
  try {
    return localStorage.getItem('token');
  } catch {
    return null;
  }
};

const clearSession = () => {
  try {
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
  } catch {
    /* storage unavailable */
  }
};

const buildUrl = (path, params) => {
  const url = new URL(`${getApiBaseUrl()}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') url.searchParams.append(k, v);
    });
  }
  return url.toString();
};

/**
 * Low-level request helper.
 * @param {string} path  path below /api, e.g. '/projects'
 * @param {object} opts  { method, body, params, form, headers, raw }
 */
export async function request(path, { method = 'GET', body, params, form, headers = {}, raw = false } = {}) {
  const h = { Accept: 'application/json', 'bypass-tunnel-reminder': 'true', ...headers };
  const t = token();
  if (t) h.Authorization = `Bearer ${t}`;
  let payload;
  if (form) {
    payload = form;
  } else if (body !== undefined) {
    h['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(buildUrl(path, params), { method, headers: h, body: payload });
  } catch {
    throw new ApiError('Cannot reach the server. Check your connection and try again.', 0);
  }

  if (response.status === 401 && !path.startsWith('/auth/login')) {
    clearSession();
    window.dispatchEvent(new CustomEvent('auth:expired'));
  }

  if (!response.ok) {
    let data = null;
    try {
      data = await response.json();
    } catch {
      /* non-JSON error */
    }
    const message = data?.message || data?.error || defaultMessage(response.status);
    throw new ApiError(message, response.status, data);
  }

  if (raw) return response;
  if (response.status === 204) return null;
  const text = await response.text();
  return text ? JSON.parse(text) : null;
}

const defaultMessage = (status) => {
  switch (status) {
    case 400: return 'The request was invalid.';
    case 401: return 'Your session has expired. Please sign in again.';
    case 403: return 'You do not have access to this.';
    case 404: return 'Not found.';
    case 409: return 'This conflicts with existing data.';
    case 413: return 'The file is too large.';
    case 429: return 'Too many attempts. Please wait and try again.';
    case 503: return 'This service is temporarily unavailable.';
    default: return 'Something went wrong. Please try again.';
  }
};

const idempotencyKey = () =>
  (crypto?.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`);

const get = (path, params) => request(path, { params });
const post = (path, body) => request(path, { method: 'POST', body });
const put = (path, body) => request(path, { method: 'PUT', body });
const patch = (path, body) => request(path, { method: 'PATCH', body });
const del = (path) => request(path, { method: 'DELETE' });

export const api = {
  // ------------------------------------------------------------------
  // Authentication
  // ------------------------------------------------------------------
  login: async (email, password) => {
    const data = await post('/auth/login', { email, password });
    localStorage.setItem('token', data.token);
    localStorage.setItem('currentUser', JSON.stringify(data.user));
    return data;
  },
  register: (data) => post('/auth/register', data),
  registrationColleges: () => get('/auth/colleges'),
  logout: async () => {
    try {
      await post('/auth/logout');
    } finally {
      clearSession();
    }
  },
  getCurrentUser: async () => {
    const user = await get('/auth/me');
    localStorage.setItem('currentUser', JSON.stringify(user));
    return user;
  },

  // ------------------------------------------------------------------
  // Dashboards
  // ------------------------------------------------------------------
  getDashboard: () => get('/dashboard'),

  // ------------------------------------------------------------------
  // Colleges (Super Admin)
  // ------------------------------------------------------------------
  getColleges: () => get('/colleges'),
  getCollege: (id) => get(`/colleges/${id}`),
  createCollege: (data) => post('/colleges', data),
  updateCollege: (id, data) => put(`/colleges/${id}`, data),
  setCollegeActive: (id, active) => patch(`/colleges/${id}/status`, { active }),
  createCollegeAdmin: (id, data) => post(`/colleges/${id}/admins`, data),
  getCollegeStudents: (id, search) => get(`/colleges/${id}/students`, { search }),

  // ------------------------------------------------------------------
  // Central library (Super Admin)
  // ------------------------------------------------------------------
  getLibrary: (filters = {}) => get('/library', filters),
  getLibraryStats: () => get('/library/stats'),
  getLibraryProject: (id) => get(`/library/${id}`),
  createLibraryProject: (data) => post('/library', data),
  updateLibraryProject: (id, data) => put(`/library/${id}`, data),
  setCatalogStatus: (id, status) => patch(`/library/${id}/catalog-status`, { status }),
  bulkCatalogStatus: (projectIds, status) => post('/library/bulk-status', { projectIds, status }),
  uploadLibraryFile: (id, file, { category = 'OTHER', previewable = false, description } = {}) => {
    const form = new FormData();
    form.append('file', file);
    form.append('category', category);
    form.append('previewable', String(previewable));
    if (description) form.append('description', description);
    return request(`/library/${id}/files`, { method: 'POST', form });
  },
  updateAssetMetadata: (assetId, data) => patch(`/library/assets/${assetId}`, data),
  scanLibraryImport: () => get('/library/import/scan'),
  startLibraryImport: (data) => post('/library/import', data),
  getLibraryImportStatus: () => get('/library/import/status'),

  // ------------------------------------------------------------------
  // Allocations
  // ------------------------------------------------------------------
  getMyAllocations: () => get('/allocations/mine'),
  getCollegeAllocations: (collegeId) => get(`/allocations/colleges/${collegeId}`),
  getAllocationBoard: (collegeId, search) => get(`/allocations/colleges/${collegeId}/board`, { search }),
  allocateProjects: (collegeId, projectIds, priceOverride, notes) =>
    post('/allocations', { collegeId, projectIds, priceOverride: priceOverride ?? null, notes }),
  updateAllocation: (id, data) => patch(`/allocations/${id}`, data),
  revokeAllocations: (allocationIds) => post('/allocations/revoke', { allocationIds }),

  // ------------------------------------------------------------------
  // Marketplace
  // ------------------------------------------------------------------
  browseMarketplace: (filters = {}) => get('/marketplace', filters),
  getMarketplaceFilters: () => get('/marketplace/filters'),
  getMarketplaceProject: (id) => get(`/marketplace/${id}`),
  getPurchasedProjects: () => get('/marketplace/purchased'),
  purchaseProject: (id) =>
    request(`/marketplace/${id}/purchase`, { method: 'POST', headers: { 'Idempotency-Key': idempotencyKey() } }),

  // ------------------------------------------------------------------
  // Orders and payments
  // ------------------------------------------------------------------
  getOrders: () => get('/orders'),
  getMyOrders: () => get('/orders/my-orders'),
  getInvoice: (orderId) => get(`/orders/${orderId}/invoice`),
  getOrderTransactions: (orderId) => get(`/orders/${orderId}/transactions`),
  getPaymentConfig: () => get('/orders/payment-config'),

  // ------------------------------------------------------------------
  // Requirements and custom development
  // ------------------------------------------------------------------
  getRequirements: (search = '', status = '') => get('/requirements', { search, status }),
  getRequirementById: (id) => get(`/requirements/${id}`),
  getRequirementTimeline: (id) => get(`/requirements/${id}/timeline`),
  getRequirementStats: () => get('/requirements/stats'),
  createRequirement: (data) => post('/requirements', data),
  updateRequirement: (id, data) => put(`/requirements/${id}`, data),
  submitRequirement: (id) => post(`/requirements/${id}/submit`),
  collegeReviewRequirement: (id, action, notes) => post(`/requirements/${id}/college-review`, { action, notes }),
  superAdminReviewRequirement: (id, action, { notes, budget, advanceAmount } = {}) =>
    post(`/requirements/${id}/review`, { action, notes, budget, advanceAmount }),
  payRequirementAdvance: (id) =>
    request(`/requirements/${id}/pay-advance`, { method: 'POST', headers: { 'Idempotency-Key': idempotencyKey() } }),
  startDevelopment: (id, developerId, reviewerId, notes) =>
    post(`/requirements/${id}/start-development`, { developerId, reviewerId: reviewerId || null, notes }),
  deleteRequirement: (id) => del(`/requirements/${id}`),

  // ------------------------------------------------------------------
  // Projects
  // ------------------------------------------------------------------
  getProjects: (search = '', status = '', type = '') => get('/projects', { search, status, type }),
  getProjectById: (id) => get(`/projects/${id}`),
  getProjectTimeline: (id) => get(`/projects/${id}/timeline`),
  getProjectByRequirementId: (reqId) => get(`/projects/by-requirement/${reqId}`),
  createProject: (data) => post('/projects', data),
  updateProject: (id, data) => put(`/projects/${id}`, data),
  updateProjectStatus: (id, status) => patch(`/projects/${id}/status`, { status }),
  deleteProject: (id) => del(`/projects/${id}`),
  getDeveloperProjects: () => get('/projects/my-developer-projects'),
  getReviewProjects: () => get('/projects/my-review-projects'),
  getWorkflowDevelopers: () => get('/projects/workflow/developers'),
  getWorkflowReviewers: () => get('/projects/workflow/reviewers'),
  acceptAssignment: (id) => post(`/projects/${id}/accept`),
  updateProgress: (id, percent, note) => post(`/projects/${id}/progress`, { percent, note }),
  developerSubmitReview: (id, notes) => post(`/projects/${id}/developer-submit-review`, { notes }),
  adminReviewProject: (id, action, notes) => post(`/projects/${id}/admin-review`, { action, notes }),
  assignDeveloperToProject: (projectId, developerId) => post(`/projects/${projectId}/assign-developer`, { developerId }),
  assignReviewerToProject: (projectId, reviewerId) => post(`/projects/${projectId}/assign-reviewer`, { reviewerId }),
  payProjectRemaining: (id) =>
    request(`/projects/${id}/pay-remaining`, { method: 'POST', headers: { 'Idempotency-Key': idempotencyKey() } }),

  // Manual access grants (Super Admin)
  getProjectAssignments: (projectId) => get(`/projects/${projectId}/assignments`),
  assignUserToProject: (projectId, userId, expiredAt = null, notes = '') =>
    post(`/projects/${projectId}/assignments`, { userId, expiredAt: normalizeDeadline(expiredAt), notes }),
  removeProjectUserAssignment: (projectId, userId) => del(`/projects/${projectId}/assignments/user/${userId}`),

  // ------------------------------------------------------------------
  // Folders, files and permissions
  // ------------------------------------------------------------------
  getProjectFolders: (projectId) => get(`/projects/${projectId}/folders`),
  createFolder: (projectId, data) => post(`/projects/${projectId}/folders`, data),
  updateFolder: (projectId, folderId, data) => put(`/projects/${projectId}/folders/${folderId}`, data),
  deleteFolder: (projectId, folderId) => del(`/projects/${projectId}/folders/${folderId}`),
  uploadAsset: (projectId, folderId, file, description) => {
    const form = new FormData();
    form.append('projectId', projectId);
    form.append('folderId', folderId);
    form.append('file', file);
    if (description) form.append('description', description);
    return request('/assets/upload', { method: 'POST', form });
  },
  replaceAsset: (assetId, file, changeNotes) => {
    const form = new FormData();
    form.append('file', file);
    if (changeNotes) form.append('changeNotes', changeNotes);
    return request(`/assets/${assetId}/replace`, { method: 'PUT', form });
  },
  getAssetVersions: (assetId) => get(`/assets/${assetId}/versions`),
  restoreAssetVersion: (assetId, versionNo) => post(`/assets/${assetId}/restore/${versionNo}`),
  /** Streams a protected file through the authorized endpoint and returns an object URL. */
  viewAsset: async (assetId, versionNo = null) => {
    const response = await request(`/assets/${assetId}/view`, { params: { version: versionNo }, raw: true });
    const mimeType = response.headers.get('Content-Type') || 'application/octet-stream';
    const disposition = response.headers.get('Content-Disposition') || '';
    const match = /filename="?([^";]+)"?/i.exec(disposition);
    const blob = await response.blob();
    let textContent = null;
    if (mimeType.startsWith('text/') || mimeType.includes('json') || mimeType.includes('xml')) {
      textContent = await blob.text();
    }
    return { url: URL.createObjectURL(blob), textContent, mimeType, fileName: match ? match[1] : 'Document', size: blob.size };
  },
  /** Downloads a protected file (audited server-side). */
  downloadAsset: async (assetId, fallbackName = 'download') => {
    const response = await request(`/assets/${assetId}/view`, { params: { download: 'true' }, raw: true });
    const disposition = response.headers.get('Content-Disposition') || '';
    const match = /filename="?([^";]+)"?/i.exec(disposition);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = match ? match[1] : fallbackName;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  },
  getFolderPermissions: (folderId) => get(`/permissions/folders/${folderId}`),
  setFolderPermission: (folderId, userId, role, status) => post('/permissions/folders', { folderId, userId, role, status }),
  deleteFolderPermission: (permissionId) => del(`/permissions/folders/${permissionId}`),
  getFilePermissions: (assetId) => get(`/permissions/files/${assetId}`),
  setFilePermission: (assetId, userId, role, status) => post('/permissions/files', { assetId, userId, role, status }),
  deleteFilePermission: (permissionId) => del(`/permissions/files/${permissionId}`),

  // ------------------------------------------------------------------
  // Users, administrators, developers
  // ------------------------------------------------------------------
  getUsers: (search = '', status = '', role = '') => get('/users', { search, status, role }),
  getAssignableUsers: (role = null) => get('/users/assignable', { role }),
  createUser: (data) => post('/users', data),
  updateUser: (id, data) => put(`/users/${id}`, data),
  deleteUser: (id) => del(`/users/${id}`),
  bulkCreateUsers: (users, collegeId = null) => post('/users/bulk', { users, collegeId }),

  getAdmins: (search = '', status = '') => get('/admins', { search, status }),
  createAdmin: (data) => post('/admins', data),
  updateAdmin: (id, data) => put(`/admins/${id}`, data),
  deleteAdmin: (id) => del(`/admins/${id}`),

  getDevelopers: (search = '', status = '') => get('/developers', { search, status }),
  createDeveloper: (data) => post('/developers', data),
  updateDeveloper: (id, data) => put(`/developers/${id}`, data),
  deleteDeveloper: (id) => del(`/developers/${id}`),
  getDeveloperAssignments: (developerId) => get(`/developers/${developerId}/projects`),

  // Granular admin permissions (Super Admin)
  getAdminPermissions: (adminId) => get(`/access-control/admin/${adminId}/permissions`),
  updateAdminPermissions: (adminId, permissions) => post(`/access-control/admin/${adminId}/permissions`, permissions),
  applyAdminPreset: (adminId, preset) => post(`/access-control/admins/${adminId}/apply-preset`, { preset }),
  getAssignedUsers: (adminId) => get(`/access-control/admin/${adminId}/users`),
  assignUsersToAdmin: (adminId, userIds) => post(`/access-control/admin/${adminId}/users`, { userIds }),
  getAccessControlOverview: () => get('/access-control/overview'),
  updateUserRole: (userId, role, collegeId) => post(`/access-control/users/${userId}/role`, { role, collegeId }),

  // ------------------------------------------------------------------
  // Audit and notifications
  // ------------------------------------------------------------------
  getAuditLogs: (date = '') => get('/audit-logs', { date }),
  getNotifications: () => get('/notifications'),
  markNotificationRead: (id) => post(`/notifications/${id}/read`),
  markAllNotificationsRead: () => post('/notifications/read-all'),
};

export default api;
