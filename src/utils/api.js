import { normalizeDeadline } from './dateUtils';

// API Client with Mock Fallback System
// Allows full interactive testing on the frontend without running the backend.

// Active Live Tunnel Endpoints
export const ACTIVE_LIVE_TUNNEL_URL = 'https://bite-restricted-logistics-improving.trycloudflare.com';
export const FALLBACK_LOCALTUNNEL_URL = 'https://academic-integration-backend.loca.lt';

// List of dead/expired tunnels to automatically sanitize if cached or injected by Vercel env
const OBSOLETE_TUNNELS = [
  'bite-restricted-logistics-improving.trycloudflare.com',
  'people-comparative-desirable-inform.trycloudflare.com',
  'grande-photography-moon-capital.trycloudflare.com',
  'align-inquiries-rebound-developers.trycloudflare.com',
  'creator-grants-leaders-delhi.trycloudflare.com'
];

// Dynamic API URL from localStorage override or environment variables
export const getApiBaseUrl = () => {
  const isHttps = typeof window !== 'undefined' && window.location.protocol === 'https:';

  try {
    const custom = typeof window !== 'undefined' ? localStorage.getItem('CUSTOM_API_URL') : null;
    if (custom && custom.trim()) {
      const trimmed = custom.trim();
      const isObsolete = OBSOLETE_TUNNELS.some(obs => trimmed.includes(obs));
      const isInsecure = isHttps && (trimmed.startsWith('http://localhost') || trimmed.startsWith('http://127.0.0.1') || (trimmed.startsWith('http://') && !trimmed.startsWith('https://')));
      
      if (isObsolete || isInsecure) {
        console.warn('Sanitized obsolete/insecure custom API URL from storage:', trimmed);
        localStorage.removeItem('CUSTOM_API_URL');
      } else {
        return trimmed.endsWith('/api') ? trimmed : `${trimmed.replace(/\/+$/, '')}/api`;
      }
    }
  } catch (e) {
    console.warn('Could not read custom API URL from storage:', e);
  }

  let envUrl = (import.meta.env.VITE_API_URL || '').trim();
  const isEnvObsolete = OBSOLETE_TUNNELS.some(obs => envUrl.includes(obs));
  
  let raw;
  if (!envUrl || isEnvObsolete || (isHttps && (envUrl.startsWith('http://localhost') || envUrl.startsWith('http://127.0.0.1') || envUrl.startsWith('http://')))) {
    raw = isHttps ? ACTIVE_LIVE_TUNNEL_URL : (envUrl && !isEnvObsolete ? envUrl : 'http://localhost:8080');
  } else {
    raw = envUrl;
  }

  return raw.endsWith('/api') ? raw : `${raw.replace(/\/+$/, '')}/api`;
};

export const setCustomApiUrl = (url) => {
  if (url && url.trim()) {
    localStorage.setItem('CUSTOM_API_URL', url.trim());
  } else {
    localStorage.removeItem('CUSTOM_API_URL');
  }
};

// Dynamic getter for BASE_URL so runtime overrides take effect immediately
export const getBaseUrl = () => getApiBaseUrl();
const BASE_URL_PROXY = {
  toString: () => getApiBaseUrl(),
  valueOf: () => getApiBaseUrl()
};
const BASE_URL = BASE_URL_PROXY;

// Initialize mock database in localStorage if empty
const initMockDB = () => {
  if (!localStorage.getItem('users')) {
    const initialUsers = [
      {
        id: 1,
        email: 'superadmin@academic.com',
        fullName: 'Super Admin User',
        role: 'SUPER_ADMIN',
        status: 'ACTIVE',
        deleted: false,
        createdAt: new Date().toISOString()
      },
      {
        id: 2,
        email: 'admin@academic.com',
        fullName: 'Project Coordinator',
        role: 'ADMIN',
        status: 'ACTIVE',
        deleted: false,
        createdAt: new Date().toISOString()
      },
      {
        id: 3,
        email: 'developer@academic.com',
        fullName: 'Academic Project Developer',
        role: 'PROJECT_DEVELOPER',
        status: 'ACTIVE',
        deleted: false,
        createdAt: new Date().toISOString()
      },
      {
        id: 4,
        email: 'user@academic.com',
        fullName: 'Academic Researcher',
        role: 'USER',
        status: 'ACTIVE',
        deleted: false,
        createdAt: new Date().toISOString()
      }
    ];
    localStorage.setItem('users', JSON.stringify(initialUsers));
  }

  if (!localStorage.getItem('audit_logs')) {
    const initialLogs = [
      {
        id: 1,
        actorEmail: 'system',
        action: 'SYSTEM_INIT',
        details: 'Database bootstrapped with default roles and accounts.',
        timestamp: new Date().toISOString()
      }
    ];
    localStorage.setItem('audit_logs', JSON.stringify(initialLogs));
  }

  if (!localStorage.getItem('projects')) {
    const initialProjects = [
      {
        id: 1,
        projectName: 'Automated Academic Evaluation Portal',
        projectCode: 'PRJ-8F3A21',
        description: 'AI-driven portal for automated evaluation of academic submissions and instant feedback generation.',
        budget: 15000.00,
        technologyStack: 'Java, Spring Boot, React, MySQL',
        status: 'IN_PROGRESS',
        linkedRequirementId: 101,
        createdBy: 'admin@academic.com',
        createdAt: new Date(Date.now() - 7 * 86400000).toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 2,
        projectName: 'Campus Resource Scheduling Engine',
        projectCode: 'PRJ-4C91E0',
        description: 'Centralized resource booking platform for classrooms, laboratories, and high-performance clusters.',
        budget: 25000.00,
        technologyStack: 'React, Node.js, PostgreSQL, Docker',
        status: 'APPROVED',
        linkedRequirementId: 102,
        createdBy: 'admin@academic.com',
        createdAt: new Date(Date.now() - 3 * 86400000).toISOString(),
        updatedAt: new Date().toISOString()
      }
    ];
    localStorage.setItem('projects', JSON.stringify(initialProjects));
  }

  if (!localStorage.getItem('project_assignments')) {
    const initialAssignments = [
      {
        id: 1,
        project: {
          id: 1,
          projectName: 'Automated Academic Evaluation Portal',
          projectCode: 'PRJ-8F3A21',
          status: 'IN_PROGRESS'
        },
        user: {
          id: 3,
          email: 'user@academic.com',
          fullName: 'Academic Researcher',
          role: 'USER'
        },
        active: true,
        assignedAt: new Date(Date.now() - 5 * 86400000).toISOString(),
        expiredAt: new Date(Date.now() + 180 * 86400000).toISOString(),
        assignedBy: 'admin@academic.com',
        notes: 'Lead Academic Researcher'
      }
    ];
    localStorage.setItem('project_assignments', JSON.stringify(initialAssignments));
  }

  if (!localStorage.getItem('mock_requirements')) {
    const initialReqs = [
      {
        id: 101,
        title: 'Automated Grading & Feedback System',
        description: 'AI-driven portal for automated evaluation of academic submissions and instant feedback generation.',
        budget: 15000.00,
        technologyStack: 'Java, Spring Boot, React, Python',
        status: 'APPROVED'
      },
      {
        id: 102,
        title: 'Campus Resource Scheduling Engine',
        description: 'Centralized resource booking platform for classrooms, laboratories, and high-performance clusters.',
        budget: 25000.00,
        technologyStack: 'React, Node.js, PostgreSQL, Docker',
        status: 'APPROVED'
      },
      {
        id: 103,
        title: 'Academic Research Repository & Metadata Indexer',
        description: 'Secure multi-tenant repository for indexing thesis papers, citations, and research datasets.',
        budget: 18000.00,
        technologyStack: 'Spring Boot, ElasticSearch, React, MySQL',
        status: 'APPROVED'
      }
    ];
    localStorage.setItem('mock_requirements', JSON.stringify(initialReqs));
  }

  if (!localStorage.getItem('folders')) {
    localStorage.setItem('folders', JSON.stringify([]));
  }

  if (!localStorage.getItem('assets')) {
    const initialAssets = [
      {
        id: 1,
        folderId: 2,
        projectId: 1,
        fileName: 'System_Requirements_Specification.pdf',
        originalFileName: 'System_Requirements_Specification.pdf',
        mimeType: 'application/pdf',
        extension: 'pdf',
        fileSize: 245760,
        versionNo: 1,
        isCurrentVersion: true,
        parentAssetId: null,
        description: 'Official Software Requirements Specification (SRS) for the Academic Integration Tool.',
        uploadedBy: 'admin@academic.com',
        createdAt: new Date(Date.now() - 4 * 86400000).toISOString(),
        updatedAt: new Date(Date.now() - 4 * 86400000).toISOString(),
        active: true,
        contentUrl: 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
      },
      {
        id: 2,
        folderId: 3,
        projectId: 1,
        fileName: 'Architecture_Blueprint.png',
        originalFileName: 'Architecture_Blueprint.png',
        mimeType: 'image/png',
        extension: 'png',
        fileSize: 184320,
        versionNo: 1,
        isCurrentVersion: true,
        parentAssetId: null,
        description: 'System Architecture Blueprint & Layered Security Topology.',
        uploadedBy: 'admin@academic.com',
        createdAt: new Date(Date.now() - 3 * 86400000).toISOString(),
        updatedAt: new Date(Date.now() - 3 * 86400000).toISOString(),
        active: true,
        contentUrl: 'https://picsum.photos/1200/800'
      },
      {
        id: 3,
        folderId: 9,
        projectId: 1,
        fileName: 'Database_Schema_v1.sql',
        originalFileName: 'Database_Schema_v1.sql',
        mimeType: 'text/plain',
        extension: 'sql',
        fileSize: 4096,
        versionNo: 1,
        isCurrentVersion: true,
        parentAssetId: null,
        description: 'MySQL 8.x DDL Schema definitions for folder_master and asset_master.',
        uploadedBy: 'admin@academic.com',
        createdAt: new Date(Date.now() - 2 * 86400000).toISOString(),
        updatedAt: new Date(Date.now() - 2 * 86400000).toISOString(),
        active: true,
        textContent: `-- ====================================================================\n-- Academic Integration Tool - Developer 4: Folder & Asset Schema\n-- ====================================================================\n\nCREATE TABLE folder_master (\n    id BIGINT AUTO_INCREMENT PRIMARY KEY,\n    name VARCHAR(255) NOT NULL,\n    parent_folder_id BIGINT NULL,\n    project_id BIGINT NOT NULL,\n    created_by VARCHAR(255) NOT NULL,\n    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,\n    active BOOLEAN DEFAULT TRUE\n);\n\nCREATE TABLE asset_master (\n    id BIGINT AUTO_INCREMENT PRIMARY KEY,\n    folder_id BIGINT NOT NULL,\n    file_name VARCHAR(255) NOT NULL,\n    original_file_name VARCHAR(255) NOT NULL,\n    mime_type VARCHAR(150) NOT NULL,\n    file_size BIGINT NOT NULL,\n    version_no INT DEFAULT 1,\n    is_current_version BOOLEAN DEFAULT TRUE\n);`
      },
      {
        id: 4,
        folderId: 6,
        projectId: 1,
        fileName: 'Frontend_Component_Spec.md',
        originalFileName: 'Frontend_Component_Spec.md',
        mimeType: 'text/plain',
        extension: 'md',
        fileSize: 3200,
        versionNo: 1,
        isCurrentVersion: true,
        parentAssetId: null,
        description: 'Frontend architectural guidelines and secure viewer specifications.',
        uploadedBy: 'user@academic.com',
        createdAt: new Date(Date.now() - 1 * 86400000).toISOString(),
        updatedAt: new Date(Date.now() - 1 * 86400000).toISOString(),
        active: true,
        textContent: `# Secure Viewer Component Specification\n\n## 1. Dynamic Watermarking\n- Displays authenticated user identity, project code, and real-time timestamp.\n- Semi-transparent, unselectable overlay across the document canvas.\n\n## 2. Risk Mitigation Layer\n- Content automatically blurs when the browser window loses focus.\n- Selection and right-click context menu are prevented in the viewer frame.`
      },
      {
        id: 5,
        folderId: 12,
        projectId: 1,
        fileName: 'Academic_Demo_Walkthrough.mp4',
        originalFileName: 'Academic_Demo_Walkthrough.mp4',
        mimeType: 'video/mp4',
        extension: 'mp4',
        fileSize: 5242880,
        versionNo: 1,
        isCurrentVersion: true,
        parentAssetId: null,
        description: 'System demonstration and research walkthrough video.',
        uploadedBy: 'admin@academic.com',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        active: true,
        contentUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4'
      }
    ];
    localStorage.setItem('assets', JSON.stringify(initialAssets));
  }
};

initMockDB();

// Mock API setting helper (auto-enables on preview if backend is unreachable or not configured)
export const isMockMode = () => {
  const customSetting = localStorage.getItem('MOCK_API_MODE');
  if (customSetting !== null) {
    return customSetting === 'true';
  }
  // If explicitly configured in environment variables, respect that
  if (import.meta.env.VITE_MOCK_MODE !== undefined) {
    return import.meta.env.VITE_MOCK_MODE === 'true';
  }
  // If a custom API URL is provided (e.g. public tunnel or production backend), use live backend
  if (import.meta.env.VITE_API_URL && import.meta.env.VITE_API_URL.trim() !== '') {
    return false;
  }
  // If hosted on Vercel without custom backend env, fallback to mock demo mode
  if (typeof window !== 'undefined' && !window.location.hostname.includes('localhost') && !window.location.hostname.includes('127.0.0.1')) {
    return true;
  }
  return false;
};

export const setMockMode = (value) => {
  localStorage.setItem('MOCK_API_MODE', value ? 'true' : 'false');
  window.location.reload();
};

// High-performance instant execution
const delay = (ms = 0) => ms > 0 ? new Promise(resolve => setTimeout(resolve, ms)) : Promise.resolve();

// Mock Database Helper Actions
const getMockUsers = () => JSON.parse(localStorage.getItem('users')) || [];
const saveMockUsers = (users) => localStorage.setItem('users', JSON.stringify(users));

const getMockLogs = () => JSON.parse(localStorage.getItem('audit_logs')) || [];
const saveMockLogs = (logs) => localStorage.setItem('audit_logs', JSON.stringify(logs));

const IGNORED_MOCK_AUDIT_ACTIONS = new Set([
  'LOGIN',
  'LOGOUT',
  'OTP_RESENT',
  'OTP_VERIFIED',
  'SYSTEM_INIT',
  'VIEW_FILE',
  'VIEW_PROJECT',
  'VIEW_REQUIREMENT'
]);

const addMockAuditLog = (actorEmail, action, details) => {
  if (action && IGNORED_MOCK_AUDIT_ACTIONS.has(action.trim().toUpperCase())) {
    return; // Skip registering low-value routine events
  }
  const logs = getMockLogs();
  const newLog = {
    id: logs.length ? Math.max(...logs.map(l => l.id)) + 1 : 1,
    actorEmail,
    action,
    details,
    timestamp: new Date().toISOString()
  };
  saveMockLogs([newLog, ...logs]); // prepend so newest shows first
};

const getMockProjects = () => JSON.parse(localStorage.getItem('projects')) || [];
const saveMockProjects = (projects) => localStorage.setItem('projects', JSON.stringify(projects));

const getMockAssignments = () => JSON.parse(localStorage.getItem('project_assignments')) || [];
const saveMockAssignments = (assignments) => localStorage.setItem('project_assignments', JSON.stringify(assignments));

const getMockRequirements = () => JSON.parse(localStorage.getItem('mock_requirements')) || [];
const saveMockRequirements = (reqs) => localStorage.setItem('mock_requirements', JSON.stringify(reqs));

const getMockFolders = () => JSON.parse(localStorage.getItem('folders')) || [];
const saveMockFolders = (folders) => localStorage.setItem('folders', JSON.stringify(folders));

const getMockAssets = () => JSON.parse(localStorage.getItem('assets')) || [];
const saveMockAssets = (assets) => localStorage.setItem('assets', JSON.stringify(assets));

const isValidProjectStatusTransition = (current, target) => {
  if (current === target) return true;
  switch (current) {
    case 'DRAFT': return ['APPROVED', 'REJECTED', 'INACTIVE'].includes(target);
    case 'APPROVED': return ['IN_PROGRESS', 'REJECTED', 'INACTIVE'].includes(target);
    case 'IN_PROGRESS': return ['COMPLETED', 'INACTIVE'].includes(target);
    case 'COMPLETED':
    case 'REJECTED': return target === 'INACTIVE';
    case 'INACTIVE': return target === 'DRAFT';
    default: return false;
  }
};

// Authentication Headers Helper for Live Mode
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true',
    'bypass-tunnel-reminder': 'true',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

// Fetch wrapper for Live Spring Boot API connected to MySQL (with tunnel header support)
const fetchWithFallback = async (input, init = {}) => {
  const headers = new Headers(init.headers || {});
  if (!headers.has('ngrok-skip-browser-warning')) {
    headers.set('ngrok-skip-browser-warning', 'true');
  }
  if (!headers.has('bypass-tunnel-reminder')) {
    headers.set('bypass-tunnel-reminder', 'true');
  }
  const response = await fetch(input, { ...init, headers });
  return response;
};

// High-Performance In-Memory SWR Cache & Request Deduplication
const apiCache = new Map();
const inFlightRequests = new Map();

export const clearApiCache = (pattern = null) => {
  if (!pattern) {
    apiCache.clear();
    return;
  }
  for (const key of apiCache.keys()) {
    if (key.includes(pattern)) {
      apiCache.delete(key);
    }
  }
};

export const cachedApiCall = async (key, fetcher, ttlMs = 15000) => {
  const cached = apiCache.get(key);
  const now = Date.now();

  if (cached && (now - cached.timestamp < ttlMs)) {
    return cached.data;
  }

  if (inFlightRequests.has(key)) {
    return inFlightRequests.get(key);
  }

  const promise = (async () => {
    try {
      const result = await fetcher();
      apiCache.set(key, { data: result, timestamp: Date.now() });
      return result;
    } finally {
      inFlightRequests.delete(key);
    }
  })();

  inFlightRequests.set(key, promise);
  return promise;
};

export const api = {
  // ----------------------------------------------------
  // Authentication
  // ----------------------------------------------------
  login: async (email, password) => {
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      const user = users.find(u => u.email.toLowerCase() === email.toLowerCase() && !u.deleted);
      
      if (!user) {
        throw new Error('Invalid email or password');
      }
      
      if (user.status !== 'ACTIVE') {
        throw new Error('Your account is currently inactive. Contact your administrator.');
      }
      
      // Simple password validation helper for mock mode
      let isValidPassword = false;
      if (user.role === 'SUPER_ADMIN' && password === 'Superadmin123!') isValidPassword = true;
      else if (user.role === 'ADMIN' && password === 'Admin123!') isValidPassword = true;
      else if (user.role === 'PROJECT_DEVELOPER' && (password === 'Dev12345!' || password === 'Developer123!')) isValidPassword = true;
      else if (user.role === 'USER' && password === 'User123!') isValidPassword = true;
      // Allow custom created mock users to log in with any password for ease of testing
      else if (user.id > 4 && password) isValidPassword = true;
      
      if (!isValidPassword) {
        throw new Error('Invalid email or password');
      }

      // Generate a mock JWT
      const mockToken = `mock-jwt-token-for-${user.email}-${user.role}`;
      localStorage.setItem('token', mockToken);
      localStorage.setItem('currentUser', JSON.stringify(user));
      
      addMockAuditLog(user.email, 'LOGIN', `User successfully authenticated as ${user.role}.`);
      return { token: mockToken, user };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Login failed' }));
        throw new Error(errorData.message || 'Login failed');
      }
      const data = await response.json();
      localStorage.setItem('token', data.token);
      localStorage.setItem('currentUser', JSON.stringify(data.user));
      return data;
    }
  },

  register: async (registerData) => {
    if (isMockMode()) {
      await delay(300);
      const users = getMockUsers();
      const email = registerData.email.toLowerCase().trim();
      if (users.some(u => u.email.toLowerCase() === email && !u.deleted)) {
        throw new Error('An account with this email is already registered. Please login.');
      }
      const newUser = {
        id: users.length ? Math.max(...users.map(u => u.id)) + 1 : 1,
        email,
        fullName: registerData.fullName,
        mobileNumber: registerData.mobileNumber || '',
        organization: registerData.organization || '',
        role: 'USER',
        status: 'ACTIVE',
        emailVerified: true,
        deleted: false,
        createdAt: new Date().toISOString()
      };
      saveMockUsers([...users.filter(u => u.email.toLowerCase() !== email), newUser]);
      return {
        success: true,
        message: 'Account registered successfully! You can now sign in with your email and password.',
        email
      };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerData)
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Registration failed' }));
        throw new Error(errorData.message || 'Registration failed');
      }
      return response.json();
    }
  },

  verifyOtp: async (email, otp) => {
    if (isMockMode()) {
      await delay(300);
      const users = getMockUsers();
      const userIndex = users.findIndex(u => u.email.toLowerCase() === email.toLowerCase().trim());
      if (userIndex === -1) {
        throw new Error('No registration found for email.');
      }
      if (otp !== '123456') {
        throw new Error('Invalid verification OTP. Please check the code.');
      }
      users[userIndex].status = 'ACTIVE';
      users[userIndex].emailVerified = true;
      saveMockUsers(users);

      const user = users[userIndex];
      const mockToken = `mock-jwt-token-for-${user.email}-${user.role}`;
      localStorage.setItem('token', mockToken);
      localStorage.setItem('currentUser', JSON.stringify(user));
      return { success: true, token: mockToken, user, message: 'Account verified successfully!' };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp })
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'OTP verification failed' }));
        throw new Error(errorData.message || 'OTP verification failed');
      }
      const data = await response.json();
      if (data.token) {
        localStorage.setItem('token', data.token);
      }
      if (data.user) {
        localStorage.setItem('currentUser', JSON.stringify(data.user));
      }
      return data;
    }
  },

  resendOtp: async (email) => {
    if (isMockMode()) {
      await delay(200);
      return { success: true, message: 'New 6-digit OTP code sent.', otp: '123456' };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/auth/resend-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Failed to resend OTP' }));
        throw new Error(errorData.message || 'Failed to resend OTP');
      }
      return response.json();
    }
  },

  logout: async () => {
    const userJson = localStorage.getItem('currentUser');
    const user = userJson ? JSON.parse(userJson) : null;
    
    if (isMockMode()) {
      await delay(200);
      if (user) {
        addMockAuditLog(user.email, 'LOGOUT', 'User logged out.');
      }
      localStorage.removeItem('token');
      localStorage.removeItem('currentUser');
      return { message: 'Logged out successfully' };
    } else {
      try {
        await fetchWithFallback(`${BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: getAuthHeaders()
        });
      } catch (e) {
        console.warn('Backend logout failed or was unreachable. Clearing local cache.', e);
      }
      localStorage.removeItem('token');
      localStorage.removeItem('currentUser');
      return { message: 'Logged out successfully' };
    }
  },

  getCurrentUser: async () => {
    if (isMockMode()) {
      await delay(100);
      const userJson = localStorage.getItem('currentUser');
      if (!userJson) throw new Error('Unauthenticated');
      return JSON.parse(userJson);
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/auth/me`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        throw new Error('Session expired');
      }
      const user = await response.json();
      localStorage.setItem('currentUser', JSON.stringify(user));
      return user;
    }
  },

  // ----------------------------------------------------
  // User Management
  // ----------------------------------------------------
  getUsers: async (search = '', status = '') => {
    if (isMockMode()) {
      await delay();
      let users = getMockUsers().filter(u => !u.deleted && u.role !== 'SUPER_ADMIN'); // Super Admin is filtered in standard lists
      
      if (search) {
        const q = search.toLowerCase();
        users = users.filter(u => u.fullName.toLowerCase().includes(q) || u.email.toLowerCase().includes(q));
      }
      
      if (status) {
        users = users.filter(u => u.status === status);
      }
      
      return users;
    } else {
      const cacheKey = `users_${search}_${status}`;
      return cachedApiCall(cacheKey, async () => {
        const baseUrl = getApiBaseUrl();
        let urlStr = `${baseUrl}/users`;
        const params = [];
        if (search) params.push(`search=${encodeURIComponent(search)}`);
        if (status) params.push(`status=${encodeURIComponent(status)}`);
        if (params.length > 0) urlStr += `?${params.join('&')}`;
        
        try {
          const response = await fetchWithFallback(urlStr, { headers: getAuthHeaders() });
          if (!response.ok) {
            console.warn(`Live getUsers returned status ${response.status}. Using cached/local user directory.`);
            return getMockUsers().filter(u => !u.deleted && u.role !== 'SUPER_ADMIN');
          }
          return response.json();
        } catch (netErr) {
          console.warn('Network error fetching users. Using local user directory:', netErr);
          return getMockUsers().filter(u => !u.deleted && u.role !== 'SUPER_ADMIN');
        }
      }, 15000);
    }
  },

  createUser: async (userData) => {
    clearApiCache('users');
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      
      if (users.some(u => u.email.toLowerCase() === userData.email.toLowerCase() && !u.deleted)) {
        throw new Error('A user with this email address already exists.');
      }

      const newUser = {
        id: users.length ? Math.max(...users.map(u => u.id)) + 1 : 1,
        email: userData.email,
        fullName: userData.fullName,
        role: userData.role || 'USER',
        status: userData.status || 'ACTIVE',
        deleted: false,
        createdAt: new Date().toISOString()
      };

      saveMockUsers([...users, newUser]);
      addMockAuditLog(
        actor?.email || 'system',
        'CREATE_USER',
        `Created user ${newUser.fullName} (${newUser.email}) with role ${newUser.role}`
      );
      return newUser;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/users`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(userData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to create user' }));
        throw new Error(err.message || 'Failed to create user');
      }
      return response.json();
    }
  },

  updateUser: async (id, userData) => {
    clearApiCache('users');
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      const userIndex = users.findIndex(u => u.id === Number(id));
      
      if (userIndex === -1) throw new Error('User not found');
      
      // Check email uniqueness if email is changing
      if (userData.email && users.some(u => u.id !== Number(id) && u.email.toLowerCase() === userData.email.toLowerCase() && !u.deleted)) {
        throw new Error('A user with this email address already exists.');
      }

      const updatedUser = {
        ...users[userIndex],
        ...userData,
        updatedAt: new Date().toISOString()
      };

      users[userIndex] = updatedUser;
      saveMockUsers(users);
      
      // Update self cache if modifying own profile
      if (actor && actor.id === Number(id)) {
        localStorage.setItem('currentUser', JSON.stringify(updatedUser));
      }

      addMockAuditLog(
        actor?.email || 'system',
        'UPDATE_USER',
        `Updated user ${updatedUser.fullName} (${updatedUser.email})`
      );
      return updatedUser;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/users/${id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(userData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to update user' }));
        throw new Error(err.message || 'Failed to update user');
      }
      const data = await response.json();
      if (actor && actor.id === Number(id)) {
        localStorage.setItem('currentUser', JSON.stringify(data));
      }
      return data;
    }
  },

  deleteUser: async (id) => {
    clearApiCache('users');
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      const user = users.find(u => u.id === Number(id));
      
      if (!user) throw new Error('User not found');
      
      user.deleted = true;
      saveMockUsers(users);
      
      addMockAuditLog(
        actor?.email || 'system',
        'DELETE_USER',
        `Soft deleted user ${user.fullName} (${user.email})`
      );
      return { message: 'User soft deleted' };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/users/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      if (!response.ok) throw new Error('Failed to delete user');
      return response.json();
    }
  },

  bulkCreateUsers: async (usersList) => {
    clearApiCache('users');
    const actor = JSON.parse(localStorage.getItem('currentUser'));

    if (isMockMode()) {
      await delay();
      const existingUsers = getMockUsers();
      let maxId = existingUsers.length ? Math.max(...existingUsers.map(u => u.id || 0)) : 1;

      const createdUsers = [];
      const errors = [];
      let duplicateCount = 0;
      let failedCount = 0;
      const processedEmails = new Set();
      const emailRegex = /^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$/;

      for (let i = 0; i < usersList.length; i++) {
        const item = usersList[i];
        const rowNum = i + 1;

        if (!item || !item.fullName || !item.fullName.trim()) {
          errors.push({ rowIndex: rowNum, email: item?.email || 'N/A', reason: 'Full Name is required' });
          failedCount++;
          continue;
        }

        const email = (item.email || '').trim().toLowerCase();
        if (!email || !emailRegex.test(email)) {
          errors.push({ rowIndex: rowNum, email: item.email || 'N/A', reason: 'Invalid email address format' });
          failedCount++;
          continue;
        }

        if (processedEmails.has(email)) {
          errors.push({ rowIndex: rowNum, email, reason: 'Duplicate email in batch' });
          duplicateCount++;
          failedCount++;
          continue;
        }

        if (existingUsers.some(u => !u.deleted && u.email.toLowerCase() === email)) {
          errors.push({ rowIndex: rowNum, email, reason: 'Email already registered in system' });
          duplicateCount++;
          failedCount++;
          continue;
        }

        let role = (item.role || 'USER').toUpperCase();
        if (actor?.role === 'ADMIN' && (role === 'SUPER_ADMIN' || role === 'ADMIN')) {
          errors.push({ rowIndex: rowNum, email, reason: `Admin cannot provision ${role} accounts` });
          failedCount++;
          continue;
        }

        maxId++;
        const newUser = {
          id: maxId,
          fullName: item.fullName.trim(),
          email,
          phone: item.phone || item.mobileNumber || '',
          organization: item.organization || item.department || 'Academic Institution',
          department: item.department || '',
          role,
          status: 'ACTIVE',
          emailVerified: true,
          deleted: false,
          createdAt: new Date().toISOString()
        };

        createdUsers.push(newUser);
        processedEmails.add(email);
      }

      if (createdUsers.length > 0) {
        saveMockUsers([...existingUsers, ...createdUsers]);
        addMockAuditLog(
          actor?.email || 'system',
          'BULK_USER_CREATE',
          `Bulk created ${createdUsers.length} users successfully (${failedCount} skipped/failed) out of ${usersList.length} records.`
        );
      }

      return {
        totalRecords: usersList.length,
        successCount: createdUsers.length,
        failedCount,
        duplicateCount,
        createdUsers,
        errors
      };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/users/bulk`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ users: usersList })
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to process bulk user creation' }));
        throw new Error(err.message || 'Failed to process bulk user creation');
      }
      return response.json();
    }
  },

  // ----------------------------------------------------
  // Admin Management (Super Admin Exclusive)
  // ----------------------------------------------------
  getAdmins: async (search = '', status = '') => {
    if (isMockMode()) {
      await delay();
      return getMockUsers().filter(u => !u.deleted && (u.role === 'ADMIN' || u.role === 'SUPER_ADMIN'));
    } else {
      const cacheKey = `admins_${search}_${status}`;
      return cachedApiCall(cacheKey, async () => {
        const baseUrl = getApiBaseUrl();
        let urlStr = `${baseUrl}/admins`;
        const params = [];
        if (search) params.push(`search=${encodeURIComponent(search)}`);
        if (status) params.push(`status=${encodeURIComponent(status)}`);
        if (params.length > 0) urlStr += `?${params.join('&')}`;

        try {
          const response = await fetchWithFallback(urlStr, { headers: getAuthHeaders() });
          if (!response.ok) {
            console.warn(`Live getAdmins returned status ${response.status}. Using cached/local admin directory.`);
            return getMockUsers().filter(u => !u.deleted && (u.role === 'ADMIN' || u.role === 'SUPER_ADMIN'));
          }
          return response.json();
        } catch (netErr) {
          console.warn('Network error fetching admins. Using local admin directory:', netErr);
          return getMockUsers().filter(u => !u.deleted && (u.role === 'ADMIN' || u.role === 'SUPER_ADMIN'));
        }
      }, 15000);
    }
  },

  createAdmin: async (adminData) => {
    clearApiCache('admins');
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      
      if (users.some(u => u.email.toLowerCase() === adminData.email.toLowerCase() && !u.deleted)) {
        throw new Error('An administrator with this email address already exists.');
      }

      const newAdmin = {
        id: users.length ? Math.max(...users.map(u => u.id)) + 1 : 1,
        email: adminData.email,
        fullName: adminData.fullName,
        role: 'ADMIN',
        status: adminData.status || 'ACTIVE',
        deleted: false,
        createdAt: new Date().toISOString()
      };

      saveMockUsers([...users, newAdmin]);
      addMockAuditLog(
        actor?.email || 'system',
        'CREATE_ADMIN',
        `Created administrator account for ${newAdmin.fullName} (${newAdmin.email})`
      );
      return newAdmin;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/admins`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(adminData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to create admin' }));
        throw new Error(err.message || 'Failed to create admin');
      }
      return response.json();
    }
  },

  updateAdmin: async (id, adminData) => {
    clearApiCache('admins');
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      const adminIndex = users.findIndex(u => u.id === Number(id) && u.role === 'ADMIN');
      
      if (adminIndex === -1) throw new Error('Admin not found');

      if (adminData.email && users.some(u => u.id !== Number(id) && u.email.toLowerCase() === adminData.email.toLowerCase() && !u.deleted)) {
        throw new Error('A user with this email address already exists.');
      }

      const updatedAdmin = {
        ...users[adminIndex],
        ...adminData,
        updatedAt: new Date().toISOString()
      };

      users[adminIndex] = updatedAdmin;
      saveMockUsers(users);
      
      addMockAuditLog(
        actor?.email || 'system',
        'UPDATE_ADMIN',
        `Updated administrator account details for ${updatedAdmin.fullName} (${updatedAdmin.email})`
      );
      return updatedAdmin;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/admins/${id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(adminData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to update admin' }));
        throw new Error(err.message || 'Failed to update admin');
      }
      return response.json();
    }
  },

  deleteAdmin: async (id) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      const admin = users.find(u => u.id === Number(id) && (u.role === 'ADMIN' || u.role === 'SUPER_ADMIN'));
      
      if (!admin) throw new Error('Administrator not found');
      
      admin.deleted = true;
      saveMockUsers(users);
      
      addMockAuditLog(
        actor?.email || 'system',
        'DELETE_ADMIN',
        `Soft deleted administrator ${admin.fullName} (${admin.email})`
      );
      return { message: 'Administrator deleted' };
    } else {
      const response = await fetchWithFallback(`${getApiBaseUrl()}/admins/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to delete administrator' }));
        throw new Error(err.message || 'Failed to delete administrator');
      }
      return response.json();
    }
  },

  // ----------------------------------------------------
  // Developer Management (Super Admin Exclusive)
  // ----------------------------------------------------
  getDevelopers: async (search = '', status = '') => {
    if (isMockMode()) {
      await delay();
      return getMockUsers().filter(u => !u.deleted && u.role === 'PROJECT_DEVELOPER');
    } else {
      const cacheKey = `developers_${search}_${status}`;
      return cachedApiCall(cacheKey, async () => {
        const baseUrl = getApiBaseUrl();
        let urlStr = `${baseUrl}/developers`;
        const params = [];
        if (search) params.push(`search=${encodeURIComponent(search)}`);
        if (status) params.push(`status=${encodeURIComponent(status)}`);
        if (params.length > 0) urlStr += `?${params.join('&')}`;

        try {
          const response = await fetchWithFallback(urlStr, { headers: getAuthHeaders() });
          if (!response.ok) {
            console.warn(`Live getDevelopers returned ${response.status}. Using local mock developers.`);
            return getMockUsers().filter(u => !u.deleted && u.role === 'PROJECT_DEVELOPER');
          }
          return response.json();
        } catch (netErr) {
          console.warn('Network error fetching developers:', netErr);
          return getMockUsers().filter(u => !u.deleted && u.role === 'PROJECT_DEVELOPER');
        }
      }, 15000);
    }
  },

  createDeveloper: async (devData) => {
    clearApiCache('developers');
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      
      if (users.some(u => u.email.toLowerCase() === devData.email.toLowerCase() && !u.deleted)) {
        throw new Error('A developer with this email address already exists.');
      }

      const newDev = {
        id: users.length ? Math.max(...users.map(u => u.id)) + 1 : 1,
        email: devData.email,
        fullName: devData.fullName,
        role: 'PROJECT_DEVELOPER',
        phone: devData.phone || '',
        department: devData.department || '',
        organization: devData.organization || devData.department || 'Academic Development Team',
        status: devData.status || 'ACTIVE',
        deleted: false,
        createdAt: new Date().toISOString()
      };

      saveMockUsers([...users, newDev]);
      addMockAuditLog(
        actor?.email || 'system',
        'CREATE_DEVELOPER',
        `Created project developer account for ${newDev.fullName} (${newDev.email})`
      );
      return newDev;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/developers`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(devData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to create developer profile' }));
        throw new Error(err.message || 'Failed to create developer profile');
      }
      return response.json();
    }
  },

  updateDeveloper: async (id, devData) => {
    clearApiCache('developers');
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      const devIndex = users.findIndex(u => u.id === Number(id) && u.role === 'PROJECT_DEVELOPER');
      if (devIndex === -1) throw new Error('Developer not found');

      const updatedDev = {
        ...users[devIndex],
        ...devData,
        updatedAt: new Date().toISOString()
      };

      users[devIndex] = updatedDev;
      saveMockUsers(users);
      addMockAuditLog(
        actor?.email || 'system',
        'UPDATE_DEVELOPER',
        `Updated developer profile for ${updatedDev.fullName} (${updatedDev.email})`
      );
      return updatedDev;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/developers/${id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(devData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to update developer' }));
        throw new Error(err.message || 'Failed to update developer');
      }
      return response.json();
    }
  },

  deleteDeveloper: async (id) => {
    clearApiCache('developers');
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      const dev = users.find(u => u.id === Number(id) && u.role === 'PROJECT_DEVELOPER');
      if (!dev) throw new Error('Developer not found');

      dev.deleted = true;
      saveMockUsers(users);
      addMockAuditLog(
        actor?.email || 'system',
        'DELETE_DEVELOPER',
        `Soft deleted developer ${dev.fullName} (${dev.email})`
      );
      return { message: 'Developer profile deleted' };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/developers/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to delete developer' }));
        throw new Error(err.message || 'Failed to delete developer');
      }
      return response.json();
    }
  },

  getDeveloperProjects: async (developerId) => {
    if (isMockMode()) {
      await delay();
      const assignments = JSON.parse(localStorage.getItem('project_assignments')) || [];
      return assignments.filter(a => Number(a.userId) === Number(developerId) && a.active);
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/developers/${developerId}/projects`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        return [];
      }
      return response.json();
    }
  },

  assignDeveloperToProject: async (developerId, payload) => {
    clearApiCache('projects');
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const assignments = JSON.parse(localStorage.getItem('project_assignments')) || [];
      const newAssign = {
        id: assignments.length ? Math.max(...assignments.map(a => a.id)) + 1 : 1,
        projectId: Number(payload.projectId),
        userId: Number(developerId),
        notes: payload.notes || 'Assigned by Super Admin',
        active: true,
        assignedBy: actor?.email || 'superadmin@academic.com',
        assignedAt: new Date().toISOString(),
        expiredAt: payload.expiredAt || null
      };
      localStorage.setItem('project_assignments', JSON.stringify([...assignments, newAssign]));
      addMockAuditLog(
        actor?.email || 'system',
        'ASSIGN_DEVELOPER_PROJECT',
        `Assigned project #${payload.projectId} to developer #${developerId}`
      );
      return newAssign;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/developers/${developerId}/assign-project`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to assign project to developer' }));
        throw new Error(err.message || 'Failed to assign project to developer');
      }
      return response.json();
    }
  },

  // ----------------------------------------------------
  // Audit Logs
  getAuditLogs: async (date = '') => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const allLogs = getMockLogs();
      
      let filtered = allLogs;
      if (date) {
        filtered = filtered.filter(log => log.timestamp.startsWith(date));
      }

      if (actor?.role === 'SUPER_ADMIN') {
        return filtered;
      } else if (actor?.role === 'ADMIN') {
        return filtered.filter(log => {
          const detail = log.details.toLowerCase();
          return !detail.includes('role super_admin') && 
                 !detail.includes('administrator account') && 
                 !detail.includes('system_init');
        });
      }
      
      return []; // Users don't see any audit logs
    } else {
      const url = new URL(`${BASE_URL}/audit-logs`);
      if (date) url.searchParams.append('date', date);
      
      const response = await fetchWithFallback(url.toString(), { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Failed to retrieve audit logs');
      return response.json();
    }
  },

  // ----------------------------------------------------
  // ----------------------------------------------------
  // Project Management (Developer 3)
  // ----------------------------------------------------
  getProjects: async (search = '', status = '', techStack = '', assignedUserId = null) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      let projects = getMockProjects();
      const assignments = getMockAssignments();

      if (assignedUserId) {
        const assignedProjIds = assignments
          .filter(a => a.user?.id === Number(assignedUserId) && a.active)
          .map(a => a.project?.id);
        projects = projects.filter(p => assignedProjIds.includes(p.id) || p.assignedUserId === Number(assignedUserId));
      }

      if (search) {
        const q = search.toLowerCase();
        projects = projects.filter(p => p.projectName.toLowerCase().includes(q) || p.projectCode.toLowerCase().includes(q));
      }

      if (status) {
        projects = projects.filter(p => p.status === status);
      }

      if (techStack) {
        const t = techStack.toLowerCase();
        projects = projects.filter(p => p.technologyStack && p.technologyStack.toLowerCase().includes(t));
      }

      return projects;
    } else {
      const cacheKey = `projects_${search}_${status}_${techStack}_${assignedUserId}`;
      return cachedApiCall(cacheKey, async () => {
        const url = new URL(`${BASE_URL}/projects`);
        if (search) url.searchParams.append('search', search);
        if (status) url.searchParams.append('status', status);
        if (techStack) url.searchParams.append('techStack', techStack);
        if (assignedUserId) url.searchParams.append('assignedUserId', assignedUserId);

        const response = await fetchWithFallback(url.toString(), { headers: getAuthHeaders() });
        if (!response.ok) throw new Error('Failed to retrieve projects');
        return response.json();
      }, 15000);
    }
  },

  getProjectDashboard: async () => {
    if (isMockMode()) {
      await delay();
      const projects = getMockProjects();
      const statusCounts = {
        TOTAL: projects.length,
        DRAFT: projects.filter(p => p.status === 'DRAFT').length,
        APPROVED: projects.filter(p => p.status === 'APPROVED').length,
        IN_PROGRESS: projects.filter(p => p.status === 'IN_PROGRESS').length,
        COMPLETED: projects.filter(p => p.status === 'COMPLETED').length,
        REJECTED: projects.filter(p => p.status === 'REJECTED').length,
        INACTIVE: projects.filter(p => p.status === 'INACTIVE').length,
      };
      return {
        statusCounts,
        recentProjects: projects.slice(0, 5)
      };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects/dashboard`, { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Failed to retrieve project dashboard metrics');
      return response.json();
    }
  },

  getProjectById: async (id) => {
    if (isMockMode()) {
      await delay();
      const projects = getMockProjects();
      const project = projects.find(p => p.id === Number(id));
      if (!project) throw new Error('Project not found');
      return project;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects/${id}`, { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Failed to retrieve project details');
      return response.json();
    }
  },

  getProjectByRequirementId: async (reqId) => {
    const response = await fetchWithFallback(`${BASE_URL}/projects/by-requirement/${reqId}`, { headers: getAuthHeaders() });
    if (!response.ok) return null;
    return response.json();
  },

  createProject: async (projectData) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      if (actor?.role !== 'SUPER_ADMIN') {
        throw new Error('Access denied. Only Super Admin is authorized to create new projects.');
      }

      const projects = getMockProjects();
      const requirements = getMockRequirements();

      let projectName = projectData.projectName;
      let description = projectData.description;
      let budget = projectData.budget;
      let technologyStack = projectData.technologyStack;

      if (projectData.linkedRequirementId) {
        const req = requirements.find(r => r.id === Number(projectData.linkedRequirementId));
        if (req) {
          if (!projectName) projectName = req.title;
          if (!description) description = req.description;
          if (!budget) budget = req.budget;
          if (!technologyStack) technologyStack = req.technologyStack;
        }
      }

      if (!projectName) throw new Error('Project name is required');

      const randomCode = 'PRJ-' + Math.random().toString(36).substring(2, 8).toUpperCase();
      const newProject = {
        id: projects.length ? Math.max(...projects.map(p => p.id)) + 1 : 1,
        projectName,
        projectCode: randomCode,
        description: description || '',
        budget: Number(budget) || 0,
        technologyStack: technologyStack || '',
        status: projectData.status || 'DRAFT',
        linkedRequirementId: projectData.linkedRequirementId ? Number(projectData.linkedRequirementId) : null,
        createdBy: actor?.email || 'system',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      saveMockProjects([newProject, ...projects]);
      addMockAuditLog(
        actor?.email || 'system',
        'CREATE_PROJECT',
        `Created project ${newProject.projectCode} (${newProject.projectName}) with status ${newProject.status}`
      );
      return newProject;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(projectData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to create project' }));
        throw new Error(err.message || 'Failed to create project');
      }
      return response.json();
    }
  },

  updateProject: async (id, projectData) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      if (actor?.role !== 'SUPER_ADMIN') {
        throw new Error('Access denied. Only Super Admin is authorized to edit projects.');
      }

      const projects = getMockProjects();
      const index = projects.findIndex(p => p.id === Number(id));
      if (index === -1) throw new Error('Project not found');

      const updated = {
        ...projects[index],
        ...projectData,
        updatedAt: new Date().toISOString(),
        updatedBy: actor?.email || 'system'
      };

      projects[index] = updated;
      saveMockProjects(projects);
      addMockAuditLog(
        actor?.email || 'system',
        'UPDATE_PROJECT',
        `Updated details for project ${updated.projectCode} (${updated.projectName})`
      );
      return updated;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects/${id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(projectData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to update project' }));
        throw new Error(err.message || 'Failed to update project');
      }
      return response.json();
    }
  },

  updateProjectStatus: async (id, status) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      if (actor?.role !== 'SUPER_ADMIN') {
        throw new Error('Access denied. Only Super Admin is authorized to alter project status.');
      }

      const projects = getMockProjects();
      const index = projects.findIndex(p => p.id === Number(id));
      const project = projects[index];
      if (!project) throw new Error('Project not found');

      const validTransitions = {
        'DRAFT': ['APPROVED', 'REJECTED', 'INACTIVE'],
        'APPROVED': ['IN_PROGRESS', 'INACTIVE'],
        'IN_PROGRESS': ['COMPLETED', 'INACTIVE'],
        'COMPLETED': ['INACTIVE'],
        'REJECTED': ['DRAFT', 'INACTIVE'],
        'INACTIVE': ['DRAFT', 'APPROVED', 'IN_PROGRESS', 'COMPLETED']
      };

      if (!validTransitions[project.status]?.includes(status)) {
        throw new Error(`Invalid status transition: Cannot transition project ${project.projectCode} from ${project.status} to ${status}.`);
      }

      const updated = {
        ...project,
        status,
        updatedAt: new Date().toISOString(),
        updatedBy: actor?.email || 'system'
      };

      projects[index] = updated;
      saveMockProjects(projects);
      addMockAuditLog(
        actor?.email || 'system',
        'UPDATE_PROJECT_STATUS',
        `Transitioned project ${project.projectCode} status to ${status}`
      );
      return updated;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects/${id}/status`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify({ status })
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to change project status' }));
        throw new Error(err.message || 'Failed to change project status');
      }
      return response.json();
    }
  },

  // ----------------------------------------------------
  // Project Assignments API
  // ----------------------------------------------------
  getProjectAssignments: async (projectId) => {
    if (isMockMode()) {
      await delay();
      const assignments = getMockAssignments();
      return assignments.filter(a => a.project?.id === Number(projectId));
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/assignments`, { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Failed to retrieve project assignments');
      return response.json();
    }
  },

  assignUserToProject: async (projectId, userId, expiredAt = null, notes = '') => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      if (actor?.role !== 'SUPER_ADMIN') {
        throw new Error('Access denied. Only Super Admin is authorized to modify project assignments.');
      }

      const assignments = getMockAssignments();
      const projects = getMockProjects();
      const users = getMockUsers();

      const project = projects.find(p => p.id === Number(projectId));
      const user = users.find(u => u.id === Number(userId));

      if (!project) throw new Error('Project not found');
      if (!user) throw new Error('User not found');

      const updatedAssignments = assignments.map(a => {
        if (a.project?.id === Number(projectId)) {
          return { ...a, active: false, deactivatedAt: new Date().toISOString() };
        }
        return a;
      });

      const newAssignment = {
        id: updatedAssignments.length ? Math.max(...updatedAssignments.map(a => a.id)) + 1 : 1,
        project: {
          id: project.id,
          projectName: project.projectName,
          projectCode: project.projectCode,
          status: project.status
        },
        user: {
          id: user.id,
          email: user.email,
          fullName: user.fullName,
          role: user.role
        },
        active: true,
        assignedAt: new Date().toISOString(),
        expiredAt: expiredAt ? normalizeDeadline(expiredAt) : null,
        assignedBy: actor?.email || 'system',
        notes: notes || ''
      };

      saveMockAssignments([newAssignment, ...updatedAssignments]);
      addMockAuditLog(
        actor?.email || 'system',
        'ASSIGN_PROJECT_USER',
        `Assigned user ${user.fullName} (${user.email}) to project ${project.projectCode}`
      );
      return newAssignment;
    } else {
      const payload = {
        ...assignmentData,
        expiredAt: normalizeDeadline(assignmentData.expiredAt)
      };
      const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/assignments`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to assign user to project' }));
        throw new Error(err.message || 'Failed to assign user to project');
      }
      return response.json();
    }
  },

  updateAssignment: async (projectId, assignmentId, updateData) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      if (actor?.role === 'USER') throw new Error('Access denied.');

      const assignments = getMockAssignments();
      const index = assignments.findIndex(a => a.id === Number(assignmentId) && a.project?.id === Number(projectId));
      if (index === -1) throw new Error('Assignment not found');

      const updated = {
        ...assignments[index],
        ...updateData,
        expiredAt: updateData.expiredAt !== undefined ? normalizeDeadline(updateData.expiredAt) : assignments[index].expiredAt,
        ...(updateData.active === false ? { deactivatedAt: new Date().toISOString() } : {})
      };

      assignments[index] = updated;
      saveMockAssignments(assignments);
      addMockAuditLog(
        actor?.email || 'system',
        'UPDATE_PROJECT_ASSIGNMENT',
        `Updated assignment #${updated.id} for user ${updated.user?.email} on project ${updated.project?.projectCode}`
      );
      return updated;
    } else {
      const payload = {
        ...updateData,
        ...(updateData.expiredAt !== undefined ? { expiredAt: normalizeDeadline(updateData.expiredAt) } : {})
      };
      const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/assignments/${assignmentId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error('Failed to update project assignment');
      return response.json();
    }
  },

  deleteAssignment: async (projectId, assignmentId) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      if (actor?.role === 'USER') throw new Error('Access denied.');

      const assignments = getMockAssignments();
      const assignment = assignments.find(a => a.id === Number(assignmentId) && a.project?.id === Number(projectId));
      if (!assignment) throw new Error('Assignment not found');

      assignment.active = false;
      assignment.deactivatedAt = new Date().toISOString();

      saveMockAssignments(assignments);
      addMockAuditLog(
        actor?.email || 'system',
        'REVOKE_PROJECT_ASSIGNMENT',
        `Revoked assignment #${assignment.id} for user ${assignment.user?.email} on project ${assignment.project?.projectCode}`
      );
      return { success: true };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/assignments/${assignmentId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      if (!response.ok) throw new Error('Failed to revoke project assignment');
      return response.json();
    }
  },

  getAssignableUsers: async (role = null) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const targetRole = role || (actor?.role === 'ADMIN' ? 'USER' : null);
      return getMockUsers().filter(u => !u.deleted && (!targetRole || u.role === targetRole) && u.status === 'ACTIVE');
    } else {
      const url = role ? `${BASE_URL}/users/assignable?role=${role}` : `${BASE_URL}/users/assignable`;
      const response = await fetchWithFallback(url, {
        headers: getAuthHeaders()
      });
      if (!response.ok) throw new Error('Failed to retrieve assignable users');
      return response.json();
    }
  },

  assignProjectUser: async (projectId, userId, notes = '') => {
    clearApiCache('projects');
    const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/assign`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ userId: Number(userId), notes })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to assign project' }));
      throw new Error(err.message || 'Failed to assign project');
    }
    return response.json();
  },

  removeProjectUserAssignment: async (projectId, userId) => {
    clearApiCache('projects');
    const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/assign/${userId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to remove assignment' }));
      throw new Error(err.message || 'Failed to remove assignment');
    }
    return response.json();
  },

  getUserProjects: async () => {
    const response = await fetchWithFallback(`${BASE_URL}/projects/user/projects`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to retrieve assigned projects');
    return response.json();
  },

  assignProjectAdmin: async (projectId, adminUserId, expiredAt = null) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      if (actor?.role !== 'SUPER_ADMIN') {
        throw new Error('Access Denied: Only Super Admin can assign managing administrators to projects.');
      }

      const projects = getMockProjects();
      const users = getMockUsers();
      const assignments = getMockAssignments();

      const project = projects.find(p => p.id === Number(projectId));
      if (!project) throw new Error('Project not found');

      // Update project record assignedUserId field
      project.assignedUserId = adminUserId ? Number(adminUserId) : null;
      project.updatedAt = new Date().toISOString();
      saveMockProjects(projects);

      // Deactivate existing admin assignments for this project
      const updatedAssignments = assignments.map(a => {
        if (a.project?.id === Number(projectId) && (a.user?.role === 'ADMIN' || a.user?.role === 'SUPER_ADMIN')) {
          return { ...a, active: false, deactivatedAt: new Date().toISOString() };
        }
        return a;
      });

      if (adminUserId) {
        const targetAdmin = users.find(u => u.id === Number(adminUserId) && !u.deleted);
        if (!targetAdmin) throw new Error('Admin user not found');

        const newAssignment = {
          id: updatedAssignments.length ? Math.max(...updatedAssignments.map(a => a.id)) + 1 : 1,
          project: {
            id: project.id,
            projectName: project.projectName,
            projectCode: project.projectCode,
            status: project.status
          },
          user: {
            id: targetAdmin.id,
            email: targetAdmin.email,
            fullName: targetAdmin.fullName,
            role: targetAdmin.role
          },
          active: true,
          assignedAt: new Date().toISOString(),
          expiredAt: normalizeDeadline(expiredAt),
          assignedBy: actor?.email || 'superadmin@academic.com',
          notes: 'Assigned as Managing Administrator by Super Admin'
        };
        updatedAssignments.unshift(newAssignment);
        
        addMockAuditLog(
          actor?.email || 'superadmin@academic.com',
          'ASSIGN_PROJECT_ADMIN',
          `Assigned Admin ${targetAdmin.fullName} (${targetAdmin.email}) to manage project ${project.projectCode} with deadline ${expiredAt || 'None'}`
        );
      }

      saveMockAssignments(updatedAssignments);
      return { success: true, project };
    } else {
      if (!adminUserId) {
        return { success: true, message: 'Unassigned' };
      }
      const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/assignments`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ 
          userId: adminUserId, 
          notes: 'Managing Admin',
          expiredAt: normalizeDeadline(expiredAt)
        })
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to assign admin to project' }));
        throw new Error(err.message || 'Failed to assign admin to project');
      }
      return response.json();
    }
  },

  // ----------------------------------------------------
  // Approved Requirements (Developer 2 Mock Stub)
  // ----------------------------------------------------
  getApprovedRequirements: async () => {
    if (isMockMode()) {
      await delay();
      return getMockRequirements();
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/requirements/approved`, { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Failed to retrieve approved requirements');
      return response.json();
    }
  },

  // ----------------------------------------------------
  // Requirement Management (Developer 2)
  // ----------------------------------------------------
  getRequirements: async (search = '', status = '') => {
    const url = new URL(`${BASE_URL}/requirements`);
    if (search) url.searchParams.append('search', search);
    if (status) url.searchParams.append('status', status);
    
    const response = await fetchWithFallback(url.toString(), { headers: getAuthHeaders() });
    if (!response.ok) throw new Error('Failed to retrieve requirements');
    return response.json();
  },

  getRequirementById: async (id) => {
    const response = await fetchWithFallback(`${BASE_URL}/requirements/${id}`, { headers: getAuthHeaders() });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to retrieve requirement' }));
      throw new Error(err.message || 'Failed to retrieve requirement');
    }
    return response.json();
  },

  getRequirementStats: async () => {
    const response = await fetchWithFallback(`${BASE_URL}/requirements/stats`, { headers: getAuthHeaders() });
    if (!response.ok) throw new Error('Failed to retrieve requirement statistics');
    return response.json();
  },

  createRequirement: async (reqData) => {
    const response = await fetchWithFallback(`${BASE_URL}/requirements`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(reqData)
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to create requirement' }));
      throw new Error(err.message || 'Failed to create requirement');
    }
    return response.json();
  },

  updateRequirement: async (id, reqData) => {
    const response = await fetchWithFallback(`${BASE_URL}/requirements/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(reqData)
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to update requirement' }));
      throw new Error(err.message || 'Failed to update requirement');
    }
    return response.json();
  },

  submitRequirement: async (id) => {
    const response = await fetchWithFallback(`${BASE_URL}/requirements/${id}/submit`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to submit requirement' }));
      throw new Error(err.message || 'Failed to submit requirement');
    }
    return response.json();
  },

  approveRequirement: async (id) => {
    const response = await fetchWithFallback(`${BASE_URL}/requirements/${id}/approve`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to approve requirement' }));
      throw new Error(err.message || 'Failed to approve requirement');
    }
    return response.json();
  },

  rejectRequirement: async (id) => {
    const response = await fetchWithFallback(`${BASE_URL}/requirements/${id}/reject`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to reject requirement' }));
      throw new Error(err.message || 'Failed to reject requirement');
    }
    return response.json();
  },

  // ----------------------------------------------------
  // Folder Management (Developer 4)
  // ----------------------------------------------------
  getProjectFolders: async (projectId) => {
    if (isMockMode()) {
      await delay();
      const allFolders = getMockFolders().filter(f => f.projectId === Number(projectId) && f.active);
      const allAssets = getMockAssets().filter(a => a.projectId === Number(projectId) && a.active && a.isCurrentVersion);

      const buildHierarchy = (parentId = null) => {
        return allFolders
          .filter(f => f.parentFolderId === parentId)
          .map(f => {
            const crumbs = [];
            let curr = f;
            while (curr) {
              crumbs.unshift({ id: curr.id, name: curr.name });
              curr = allFolders.find(p => p.id === curr.parentFolderId);
            }

            return {
              ...f,
              breadcrumbs: crumbs,
              subFolders: buildHierarchy(f.id),
              assets: allAssets.filter(a => a.folderId === f.id)
            };
          });
      };

      return buildHierarchy(null);
    } else {
      const response = await fetchWithFallback(`${getApiBaseUrl()}/projects/${projectId}/folders`, { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Failed to retrieve project folders');
      const data = await response.json();
      return data || [];
    }
  },

  createFolder: async (projectId, folderData) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const folders = getMockFolders();
      const folderName = folderData.name?.trim();

      if (!folderName) throw new Error('Folder name cannot be empty');

      // Duplicate check in same parent
      const parentId = folderData.parentFolderId ? Number(folderData.parentFolderId) : null;
      const dup = folders.find(f => 
        f.projectId === Number(projectId) && 
        f.parentFolderId === parentId && 
        f.name.toLowerCase() === folderName.toLowerCase() && 
        f.active
      );
      if (dup) {
        throw new Error(`A folder named '${folderName}' already exists in this location.`);
      }

      const newFolder = {
        id: folders.length ? Math.max(...folders.map(f => f.id)) + 1 : 1,
        name: folderName,
        parentFolderId: parentId,
        projectId: Number(projectId),
        createdBy: actor?.email || 'admin@academic.com',
        createdAt: new Date().toISOString(),
        active: true
      };

      saveMockFolders([...folders, newFolder]);
      addMockAuditLog(
        actor?.email || 'system',
        'CREATE_FOLDER',
        `Created folder '${newFolder.name}' in project ID #${projectId}`
      );
      return newFolder;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/folders`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(folderData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to create folder' }));
        throw new Error(err.message || 'Failed to create folder');
      }
      return response.json();
    }
  },

  updateFolder: async (projectId, folderId, folderData) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const folders = getMockFolders();
      const index = folders.findIndex(f => f.id === Number(folderId) && f.projectId === Number(projectId));
      if (index === -1) throw new Error('Folder not found');

      const updated = {
        ...folders[index],
        name: folderData.name || folders[index].name,
        parentFolderId: folderData.parentFolderId !== undefined ? folderData.parentFolderId : folders[index].parentFolderId,
        updatedAt: new Date().toISOString()
      };

      folders[index] = updated;
      saveMockFolders(folders);
      addMockAuditLog(actor?.email || 'system', 'UPDATE_FOLDER', `Renamed/moved folder ID #${folderId}`);
      return updated;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/folders/${folderId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(folderData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to update folder' }));
        throw new Error(err.message || 'Failed to update folder');
      }
      return response.json();
    }
  },

  deleteFolder: async (projectId, folderId) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const folders = getMockFolders();
      const assets = getMockAssets();

      // Check if folder contains active subfolders or active files
      const hasChildren = folders.some(f => f.parentFolderId === Number(folderId) && f.active);
      const hasFiles = assets.some(a => a.folderId === Number(folderId) && a.active);

      if (hasChildren || hasFiles) {
        throw new Error('Cannot delete folder: It contains subfolders or files. Please empty it first.');
      }

      const folder = folders.find(f => f.id === Number(folderId));
      if (folder) {
        folder.active = false;
        saveMockFolders(folders);
        addMockAuditLog(actor?.email || 'system', 'DELETE_FOLDER', `Deactivated folder '${folder.name}'`);
      }
      return { message: 'Folder deactivated successfully' };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/folders/${folderId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to delete folder' }));
        throw new Error(err.message || 'Failed to delete folder');
      }
      return response.json();
    }
  },

  // ----------------------------------------------------
  // File & Secure Asset Management (Developer 4)
  // ----------------------------------------------------
  uploadAsset: async (projectId, folderId, file, description) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay(800);
      const assets = getMockAssets();
      const folders = getMockFolders();
      const folder = folders.find(f => f.id === Number(folderId) && f.active);
      if (!folder) throw new Error('Selected folder was not found.');

      const filename = file.name;
      // Duplicate check
      const dup = assets.find(a => a.folderId === Number(folderId) && a.originalFileName.toLowerCase() === filename.toLowerCase() && a.active && a.isCurrentVersion);
      if (dup) {
        throw new Error(`A file named '${filename}' already exists in folder '${folder.name}'. To update it, upload a replacement version.`);
      }

      const extension = filename.split('.').pop().toLowerCase();
      let mimeType = file.type || 'application/octet-stream';
      if (!mimeType || mimeType === 'application/octet-stream') {
        if (extension === 'pdf') mimeType = 'application/pdf';
        else if (['png', 'jpg', 'jpeg', 'gif', 'svg'].includes(extension)) mimeType = `image/${extension === 'jpg' ? 'jpeg' : extension}`;
        else if (['java', 'js', 'jsx', 'ts', 'tsx', 'py', 'sql', 'md', 'txt'].includes(extension)) mimeType = 'text/plain';
        else if (['mp4', 'webm'].includes(extension)) mimeType = `video/${extension}`;
        else if (['mp3', 'wav'].includes(extension)) mimeType = `audio/${extension}`;
      }

      // Read text content or create object URL
      let textContent = null;
      let contentUrl = null;
      if (mimeType.startsWith('text/') || ['sql', 'md', 'java', 'js', 'jsx', 'ts', 'tsx', 'py', 'json'].includes(extension)) {
        try {
          textContent = await file.text();
        } catch (e) {
          textContent = 'File preview unavailable';
        }
      } else {
        contentUrl = URL.createObjectURL(file);
      }

      const newAsset = {
        id: assets.length ? Math.max(...assets.map(a => a.id)) + 1 : 1,
        folderId: Number(folderId),
        projectId: Number(projectId),
        fileName: filename,
        originalFileName: filename,
        mimeType,
        extension,
        fileSize: file.size,
        versionNo: 1,
        isCurrentVersion: true,
        parentAssetId: null,
        description: description || '',
        uploadedBy: actor?.email || 'admin@academic.com',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        active: true,
        textContent,
        contentUrl
      };

      saveMockAssets([newAsset, ...assets]);
      addMockAuditLog(
        actor?.email || 'system',
        'UPLOAD_FILE',
        `Uploaded file '${newAsset.originalFileName}' to folder '${folder.name}'`
      );
      return newAsset;
    } else {
      const formData = new FormData();
      formData.append('projectId', projectId);
      formData.append('folderId', folderId);
      formData.append('file', file);
      if (description) formData.append('description', description);

      const token = localStorage.getItem('token');
      const response = await fetchWithFallback(`${BASE_URL}/assets/upload`, {
        method: 'POST',
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: formData
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Upload failed' }));
        throw new Error(err.message || 'Upload failed');
      }
      return response.json();
    }
  },

  replaceAsset: async (assetId, file, changeNotes) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay(800);
      const assets = getMockAssets();
      const currentAsset = assets.find(a => a.id === Number(assetId) && a.active);
      if (!currentAsset) throw new Error('Asset record not found');

      currentAsset.isCurrentVersion = false;

      const extension = file.name.split('.').pop().toLowerCase();
      let mimeType = file.type || 'application/octet-stream';
      if (!mimeType || mimeType === 'application/octet-stream') {
        if (extension === 'pdf') mimeType = 'application/pdf';
        else if (['png', 'jpg', 'jpeg', 'gif', 'svg'].includes(extension)) mimeType = `image/${extension === 'jpg' ? 'jpeg' : extension}`;
        else if (['java', 'js', 'jsx', 'ts', 'tsx', 'py', 'sql', 'md', 'txt'].includes(extension)) mimeType = 'text/plain';
        else if (['mp4', 'webm'].includes(extension)) mimeType = `video/${extension}`;
        else if (['mp3', 'wav'].includes(extension)) mimeType = `audio/${extension}`;
      }

      let textContent = null;
      let contentUrl = null;
      if (mimeType.startsWith('text/') || ['sql', 'md', 'java', 'js', 'jsx', 'ts', 'tsx', 'py', 'json'].includes(extension)) {
        try {
          textContent = await file.text();
        } catch (e) {
          textContent = 'File preview unavailable';
        }
      } else {
        contentUrl = URL.createObjectURL(file);
      }

      const rootId = currentAsset.parentAssetId || currentAsset.id;
      const newVersion = {
        id: assets.length ? Math.max(...assets.map(a => a.id)) + 1 : 1,
        folderId: currentAsset.folderId,
        projectId: currentAsset.projectId,
        fileName: file.name,
        originalFileName: file.name,
        mimeType,
        extension,
        fileSize: file.size,
        versionNo: currentAsset.versionNo + 1,
        isCurrentVersion: true,
        parentAssetId: rootId,
        description: changeNotes || `Updated to version ${currentAsset.versionNo + 1}`,
        uploadedBy: actor?.email || 'admin@academic.com',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        active: true,
        textContent,
        contentUrl
      };

      saveMockAssets([newVersion, ...assets]);
      addMockAuditLog(
        actor?.email || 'system',
        'REPLACE_FILE_VERSION',
        `Created version v${newVersion.versionNo} for '${newVersion.originalFileName}'`
      );
      return newVersion;
    } else {
      const formData = new FormData();
      formData.append('file', file);
      if (changeNotes) formData.append('changeNotes', changeNotes);

      const token = localStorage.getItem('token');
      const response = await fetchWithFallback(`${BASE_URL}/assets/${assetId}/replace`, {
        method: 'PUT',
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: formData
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Version replacement failed' }));
        throw new Error(err.message || 'Version replacement failed');
      }
      return response.json();
    }
  },

  getAssetVersions: async (assetId) => {
    if (isMockMode()) {
      await delay();
      const assets = getMockAssets();
      const target = assets.find(a => a.id === Number(assetId));
      if (!target) throw new Error('Asset not found');

      const rootId = target.parentAssetId || target.id;
      const versions = assets
        .filter(a => (a.id === rootId || a.parentAssetId === rootId) && a.active)
        .sort((a, b) => b.versionNo - a.versionNo);

      return versions;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/assets/${assetId}/versions`, { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Failed to retrieve asset version history');
      return response.json();
    }
  },

  restoreAssetVersion: async (assetId, versionNo) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const assets = getMockAssets();
      const current = assets.find(a => a.id === Number(assetId) && a.active);
      if (!current) throw new Error('Asset not found');

      const rootId = current.parentAssetId || current.id;
      const versions = assets.filter(a => (a.id === rootId || a.parentAssetId === rootId) && a.active);
      const target = versions.find(v => v.versionNo === Number(versionNo));
      if (!target) throw new Error(`Version v${versionNo} not found`);

      versions.forEach(v => {
        v.isCurrentVersion = (v.id === target.id);
      });

      saveMockAssets(assets);
      addMockAuditLog(
        actor?.email || 'system',
        'RESTORE_FILE_VERSION',
        `Restored asset '${target.originalFileName}' to version v${versionNo}`
      );
      return target;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/assets/${assetId}/restore/${versionNo}`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to restore version' }));
        throw new Error(err.message || 'Failed to restore version');
      }
      return response.json();
    }
  },

  viewAsset: async (assetId, versionNo = null) => {
    if (isMockMode()) {
      await delay(300);
      const assets = getMockAssets();
      let asset = assets.find(a => a.id === Number(assetId) && a.active);
      if (!asset) throw new Error('Asset not found');

      if (versionNo && asset.versionNo !== Number(versionNo)) {
        const rootId = asset.parentAssetId || asset.id;
        const target = assets.find(a => (a.id === rootId || a.parentAssetId === rootId) && a.versionNo === Number(versionNo) && a.active);
        if (target) asset = target;
      }

      return {
        asset,
        url: asset.contentUrl || null,
        textContent: asset.textContent || null,
        mimeType: asset.mimeType,
        fileName: asset.originalFileName
      };
    } else {
      const url = new URL(`${BASE_URL}/assets/${assetId}/view`);
      if (versionNo) url.searchParams.append('version', versionNo);

      const response = await fetchWithFallback(url.toString(), {
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('Access Denied: You do not have project assignment clearance to view this document.');
        }
        throw new Error('Failed to stream asset content');
      }

      const mimeType = response.headers.get('Content-Type') || 'application/octet-stream';
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);

      let textContent = null;
      if (mimeType.startsWith('text/') || mimeType.includes('json') || mimeType.includes('xml')) {
        textContent = await blob.text();
      }

      return {
        url: objectUrl,
        textContent,
        mimeType,
        fileName: 'Document'
      };
    }
  },

  // ----------------------------------------------------
  // Granular Folder & File Permission Management
  // ----------------------------------------------------
  getFolderPermissions: async (folderId) => {
    if (isMockMode()) {
      await delay();
      return JSON.parse(localStorage.getItem(`folder_perms_${folderId}`) || '[]');
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/permissions/folders/${folderId}`, { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Failed to fetch folder permissions');
      return response.json();
    }
  },

  setFolderPermission: async (folderId, userId, role, status) => {
    if (isMockMode()) {
      await delay();
      const perms = JSON.parse(localStorage.getItem(`folder_perms_${folderId}`) || '[]');
      const newPerm = { id: Date.now(), folderId, userId, role, permissionStatus: status };
      localStorage.setItem(`folder_perms_${folderId}`, JSON.stringify([newPerm, ...perms.filter(p => p.userId !== userId || p.role !== role)]));
      return newPerm;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/permissions/folders`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ folderId, userId, role, status })
      });
      if (!response.ok) throw new Error('Failed to update folder permission');
      return response.json();
    }
  },

  deleteFolderPermission: async (permissionId, folderId) => {
    if (isMockMode()) {
      await delay();
      const perms = JSON.parse(localStorage.getItem(`folder_perms_${folderId}`) || '[]');
      localStorage.setItem(`folder_perms_${folderId}`, JSON.stringify(perms.filter(p => p.id !== permissionId)));
      return { success: true };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/permissions/folders/${permissionId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      if (!response.ok) throw new Error('Failed to delete folder permission');
      return response.json();
    }
  },

  getFilePermissions: async (assetId) => {
    if (isMockMode()) {
      await delay();
      return JSON.parse(localStorage.getItem(`file_perms_${assetId}`) || '[]');
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/permissions/files/${assetId}`, { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Failed to fetch file permissions');
      return response.json();
    }
  },

  setFilePermission: async (assetId, userId, role, status) => {
    if (isMockMode()) {
      await delay();
      const perms = JSON.parse(localStorage.getItem(`file_perms_${assetId}`) || '[]');
      const newPerm = { id: Date.now(), assetId, userId, role, permissionStatus: status };
      localStorage.setItem(`file_perms_${assetId}`, JSON.stringify([newPerm, ...perms.filter(p => p.userId !== userId || p.role !== role)]));
      return newPerm;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/permissions/files`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ assetId, userId, role, status })
      });
      if (!response.ok) throw new Error('Failed to update file permission');
      return response.json();
    }
  },

  deleteFilePermission: async (permissionId, assetId) => {
    if (isMockMode()) {
      await delay();
      const perms = JSON.parse(localStorage.getItem(`file_perms_${assetId}`) || '[]');
      localStorage.setItem(`file_perms_${assetId}`, JSON.stringify(perms.filter(p => p.id !== permissionId)));
      return { success: true };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/permissions/files/${permissionId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      if (!response.ok) throw new Error('Failed to delete file permission');
      return response.json();
    }
  },

  // ----------------------------------------------------
  // Requirement Management & Review (Developer 2)
  // ----------------------------------------------------
  getRequirements: async (search = '', status = '') => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      let reqs = getMockRequirements();
      if (actor?.role === 'USER') {
        reqs = reqs.filter(r => (r.user?.id === actor.id || r.userId === actor.id || r.createdBy === actor.email));
      }
      if (search) {
        const q = search.toLowerCase();
        reqs = reqs.filter(r => 
          (r.title && r.title.toLowerCase().includes(q)) || 
          (r.problemStatement && r.problemStatement.toLowerCase().includes(q)) || 
          (r.description && r.description.toLowerCase().includes(q))
        );
      }
      if (status) {
        reqs = reqs.filter(r => r.status === status);
      }
      return reqs;
    } else {
      const cacheKey = `requirements_${actor?.email}_${search}_${status}`;
      return cachedApiCall(cacheKey, async () => {
        const url = new URL(`${BASE_URL}/requirements`);
        if (search) url.searchParams.append('search', search);
        if (status) url.searchParams.append('status', status);
        
        const response = await fetchWithFallback(url.toString(), { headers: getAuthHeaders() });
        if (!response.ok) throw new Error('Failed to retrieve requirements');
        return response.json();
      }, 15000);
    }
  },

  getRequirementById: async (id) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const reqs = getMockRequirements();
      const req = reqs.find(r => r.id === Number(id));
      if (!req) throw new Error('Requirement not found');
      if (actor?.role === 'USER' && req.user?.id && req.user.id !== actor.id && req.userId !== actor.id && req.createdBy !== actor.email) {
        throw new Error('Access denied: You do not own this requirement.');
      }
      return req;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/requirements/${id}`, { headers: getAuthHeaders() });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to retrieve requirement' }));
        throw new Error(err.message || 'Failed to retrieve requirement');
      }
      return response.json();
    }
  },

  getRequirementStats: async () => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const reqs = getMockRequirements();
      const userReqs = actor?.role === 'USER' 
        ? reqs.filter(r => r.user?.id === actor.id || r.userId === actor.id || r.createdBy === actor.email)
        : reqs;
      return {
        myRequirements: userReqs.length,
        pendingSubmissions: userReqs.filter(r => r.status === 'SUBMITTED').length,
        approvedRequirements: userReqs.filter(r => r.status === 'APPROVED').length
      };
    } else {
      const cacheKey = `requirement_stats_${actor?.email}`;
      return cachedApiCall(cacheKey, async () => {
        const response = await fetchWithFallback(`${BASE_URL}/requirements/stats`, { headers: getAuthHeaders() });
        if (!response.ok) throw new Error('Failed to retrieve requirement statistics');
        return response.json();
      }, 15000);
    }
  },

  getApprovedRequirements: async () => {
    if (isMockMode()) {
      await delay();
      return getMockRequirements().filter(r => r.status === 'APPROVED');
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/requirements/approved`, { headers: getAuthHeaders() });
      if (!response.ok) throw new Error('Failed to retrieve approved requirements');
      return response.json();
    }
  },

  getProjectByRequirementId: async (reqId) => {
    if (isMockMode()) {
      await delay();
      const projects = getMockProjects();
      return projects.find(p => p.linkedRequirementId === Number(reqId)) || null;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/projects/by-requirement/${reqId}`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) return null;
      return response.json();
    }
  },

  createRequirement: async (reqData) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const reqs = getMockRequirements();
      const newReq = {
        id: reqs.length ? Math.max(...reqs.map(r => r.id)) + 1 : 1,
        title: reqData.title,
        problemStatement: reqData.problemStatement,
        description: reqData.description || '',
        budget: reqData.budget !== undefined && reqData.budget !== '' ? Number(reqData.budget) : null,
        technologyStack: reqData.technologyStack || '',
        imageUrl: reqData.imageUrl || '',
        audioUrl: reqData.audioUrl || '',
        status: 'DRAFT',
        createdAt: new Date().toISOString(),
        user: actor ? {
          id: actor.id,
          email: actor.email,
          fullName: actor.fullName,
          role: actor.role
        } : null
      };
      saveMockRequirements([...reqs, newReq]);
      addMockAuditLog(
        actor?.email || 'system',
        'CREATE_REQUIREMENT',
        `Created requirement #${newReq.id}: ${newReq.title}`
      );
      return newReq;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/requirements`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(reqData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to create requirement' }));
        throw new Error(err.message || 'Failed to create requirement');
      }
      return response.json();
    }
  },

  updateRequirement: async (id, reqData) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const reqs = getMockRequirements();
      const index = reqs.findIndex(r => r.id === Number(id));
      if (index === -1) throw new Error('Requirement not found');
      if (actor?.role === 'USER' && reqs[index].status !== 'DRAFT') {
        throw new Error('Cannot edit requirement after submission.');
      }
      const updated = {
        ...reqs[index],
        ...reqData,
        budget: reqData.budget !== undefined && reqData.budget !== '' ? Number(reqData.budget) : reqs[index].budget,
        updatedAt: new Date().toISOString()
      };
      reqs[index] = updated;
      saveMockRequirements(reqs);
      addMockAuditLog(
        actor?.email || 'system',
        'UPDATE_REQUIREMENT',
        `Updated requirement #${updated.id}`
      );
      return updated;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/requirements/${id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(reqData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to update requirement' }));
        throw new Error(err.message || 'Failed to update requirement');
      }
      return response.json();
    }
  },

  submitRequirement: async (id) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      const reqs = getMockRequirements();
      const index = reqs.findIndex(r => r.id === Number(id));
      if (index === -1) throw new Error('Requirement not found');
      if (reqs[index].status !== 'DRAFT') {
        throw new Error('Only requirements in DRAFT status can be submitted.');
      }
      reqs[index].status = 'SUBMITTED';
      reqs[index].updatedAt = new Date().toISOString();
      saveMockRequirements(reqs);
      addMockAuditLog(
        actor?.email || 'system',
        'SUBMIT_REQUIREMENT',
        `Submitted requirement #${id} for admin review.`
      );
      return reqs[index];
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/requirements/${id}/submit`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to submit requirement' }));
        throw new Error(err.message || 'Failed to submit requirement');
      }
      return response.json();
    }
  },

  approveRequirement: async (id) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      if (actor?.role === 'USER') {
        throw new Error('Access denied: Regular users cannot approve requirements.');
      }
      const reqs = getMockRequirements();
      const index = reqs.findIndex(r => r.id === Number(id));
      if (index === -1) throw new Error('Requirement not found');
      if (reqs[index].status !== 'SUBMITTED') {
        throw new Error('Only SUBMITTED requirements can be approved.');
      }
      reqs[index].status = 'APPROVED';
      reqs[index].updatedAt = new Date().toISOString();
      saveMockRequirements(reqs);

      // Auto-create project in mock mode if not exists
      const projects = getMockProjects();
      const exists = projects.some(p => p.linkedRequirementId === Number(id));
      if (!exists) {
        const req = reqs[index];
        const newProj = {
          id: projects.length ? Math.max(...projects.map(p => p.id)) + 1 : 1,
          projectName: req.title,
          projectCode: `PRJ-${Math.random().toString(36).substring(2, 8).toUpperCase()}`,
          description: req.problemStatement || req.description || '',
          budget: req.budget || 0,
          technologyStack: req.technologyStack || '',
          status: 'APPROVED',
          linkedRequirementId: Number(id),
          createdBy: actor?.email || 'system',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
        saveMockProjects([...projects, newProj]);
      }

      addMockAuditLog(
        actor?.email || 'system',
        'APPROVE_REQUIREMENT',
        `Approved requirement #${id}`
      );
      return reqs[index];
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/requirements/${id}/approve`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to approve requirement' }));
        throw new Error(err.message || 'Failed to approve requirement');
      }
      return response.json();
    }
  },

  rejectRequirement: async (id) => {
    const actor = JSON.parse(localStorage.getItem('currentUser'));
    if (isMockMode()) {
      await delay();
      if (actor?.role === 'USER') {
        throw new Error('Access denied: Regular users cannot reject requirements.');
      }
      const reqs = getMockRequirements();
      const index = reqs.findIndex(r => r.id === Number(id));
      if (index === -1) throw new Error('Requirement not found');
      if (reqs[index].status !== 'SUBMITTED') {
        throw new Error('Only SUBMITTED requirements can be rejected.');
      }
      reqs[index].status = 'REJECTED';
      reqs[index].updatedAt = new Date().toISOString();
      saveMockRequirements(reqs);
      addMockAuditLog(
        actor?.email || 'system',
        'REJECT_REQUIREMENT',
        `Rejected requirement #${id}`
      );
      return reqs[index];
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/requirements/${id}/reject`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to reject requirement' }));
        throw new Error(err.message || 'Failed to reject requirement');
      }
      return response.json();
    }
  },

  // ----------------------------------------------------
  // Marketplace & Orders
  // ----------------------------------------------------
  getCatalog: async () => {
    if (isMockMode()) {
      await delay(150);
      return [
        {
          id: 'CAT-REQ-101',
          title: 'Automated Academic Evaluation Portal Package',
          category: 'Academic Requirements',
          itemType: 'REQUIREMENT',
          description: 'Complete IEEE standard requirement specification, architecture diagrams, and test matrix for student grading platforms.',
          price: 149.00,
          technologyStack: 'Java, Spring Boot 3, React 18, MySQL',
          deliverable: 'Instant PDF Specs + Markdown + Data Schemas',
          badge: 'Best Seller',
          rating: 4.9,
          reviewCount: 38
        },
        {
          id: 'CAT-DS-202',
          title: 'Multi-Tenant Research Dataset & Citation Index',
          category: 'Datasets',
          itemType: 'DATASET',
          description: 'Curated 50,000+ academic citation graph with schema definitions, vector embeddings, and indexing scripts.',
          price: 89.00,
          technologyStack: 'Python, PostgreSQL, ElasticSearch',
          deliverable: 'JSONL Data Dump + SQL Schema + Python Loader',
          badge: 'Verified',
          rating: 4.8,
          reviewCount: 24
        },
        {
          id: 'CAT-MOD-303',
          title: 'Zero-Delay DRM Watermark Security Module',
          category: 'Premium Modules',
          itemType: 'MODULE',
          description: 'High-performance frontend DRM snapshot shutter with forensic diagonal canvas watermark curtain.',
          price: 199.00,
          technologyStack: 'React, HTML5 Canvas, Web Audio API',
          deliverable: 'NPM Drop-in Module + Integration Guide',
          badge: 'Security Standard',
          rating: 5.0,
          reviewCount: 52
        },
        {
          id: 'CAT-SRV-404',
          title: 'Comprehensive Code Security Audit & Compliance Review',
          category: 'Research Services',
          itemType: 'SERVICE',
          description: 'End-to-end automated penetration test, static code analysis (SAST), and OWASP Top 10 vulnerability remediation report.',
          price: 299.00,
          technologyStack: 'SonarQube, OWASP ZAP, JUnit 5',
          deliverable: 'Signed Audit Certificate + PDF Executive Summary',
          badge: 'Enterprise',
          rating: 4.9,
          reviewCount: 19
        },
        {
          id: 'CAT-REQ-505',
          title: 'Campus Resource Scheduling Engine Blueprint',
          category: 'Academic Requirements',
          itemType: 'REQUIREMENT',
          description: 'Microservice architectural design and scheduling algorithm blueprints for university lab & classroom allocation.',
          price: 129.00,
          technologyStack: 'Node.js, Redis, Docker, RabbitMQ',
          deliverable: 'Architecture Diagrams + API Specs',
          badge: 'Popular',
          rating: 4.7,
          reviewCount: 29
        },
        {
          id: 'CAT-DS-606',
          title: 'IoT Weather Telemetry & Sensor Analytics Dataset',
          category: 'Datasets',
          itemType: 'DATASET',
          description: 'Real-time sensor telemetry stream dataset covering 12 meteorological variables with time-series benchmarks.',
          price: 79.00,
          technologyStack: 'InfluxDB, MQTT, Python',
          deliverable: 'Parquet Timeseries + InfluxDB DDL',
          badge: 'New',
          rating: 4.8,
          reviewCount: 14
        }
      ];
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/orders/catalog`);
      if (!response.ok) {
        throw new Error('Failed to retrieve catalog items');
      }
      return response.json();
    }
  },

  checkoutOrder: async (checkoutData) => {
    if (isMockMode()) {
      await delay(400);
      const actor = JSON.parse(localStorage.getItem('currentUser')) || { email: 'user@academic.com', fullName: 'Academic User' };
      const orders = JSON.parse(localStorage.getItem('mock_orders') || '[]');
      const orderNum = 'ORD-' + Math.random().toString(36).substring(2, 8).toUpperCase();
      const invoiceNum = 'INV-' + Math.floor(100000 + Math.random() * 900000);
      
      const newOrder = {
        id: orders.length + 1,
        orderNumber: orderNum,
        invoiceNumber: invoiceNum,
        user: actor,
        itemName: checkoutData.itemName,
        itemType: checkoutData.itemType || 'REQUIREMENT',
        itemDescription: checkoutData.itemDescription || 'Purchased item from catalog',
        amount: Number(checkoutData.amount),
        paymentMethod: checkoutData.paymentMethod || 'CARD',
        paymentStatus: 'COMPLETED',
        status: 'COMPLETED',
        fulfillmentDetails: JSON.stringify({ licenseKey: 'LIC-' + Math.random().toString(36).substring(2, 10).toUpperCase(), accessGrantedAt: new Date().toISOString() }),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      orders.unshift(newOrder);
      localStorage.setItem('mock_orders', JSON.stringify(orders));
      addMockAuditLog(actor.email, 'PURCHASE_CHECKOUT', `Purchased ${newOrder.itemName} for Rs. ${newOrder.amount}`);
      return newOrder;
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/orders/checkout`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(checkoutData)
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Checkout failed' }));
        throw new Error(err.message || 'Checkout failed');
      }
      return response.json();
    }
  },

  getMyOrders: async () => {
    if (isMockMode()) {
      await delay(200);
      return JSON.parse(localStorage.getItem('mock_orders') || '[]');
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/orders/my-orders`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        throw new Error('Failed to retrieve order history');
      }
      return response.json();
    }
  },

  getInvoice: async (orderId) => {
    if (isMockMode()) {
      await delay(200);
      const orders = JSON.parse(localStorage.getItem('mock_orders') || '[]');
      const order = orders.find(o => o.id === Number(orderId));
      if (!order) throw new Error('Order not found');
      return {
        invoiceNumber: order.invoiceNumber,
        orderNumber: order.orderNumber,
        createdAt: order.createdAt,
        customerName: order.user?.fullName || 'Valued Customer',
        customerEmail: order.user?.email || 'user@academic.com',
        organization: order.user?.organization || 'Academic Organization',
        mobileNumber: order.user?.mobileNumber || 'N/A',
        itemName: order.itemName,
        itemType: order.itemType,
        itemDescription: order.itemDescription,
        paymentMethod: order.paymentMethod,
        paymentStatus: order.paymentStatus,
        orderStatus: order.status,
        subtotal: order.amount,
        tax: 0.00,
        total: order.amount,
        currency: 'USD',
        fulfillmentDetails: order.fulfillmentDetails,
        qrVerificationPayload: `VERIFY:INV=${order.invoiceNumber}:ORD=${order.orderNumber}:AMT=${order.amount}`
      };
    } else {
      const response = await fetchWithFallback(`${BASE_URL}/orders/${orderId}/invoice`, {
        headers: getAuthHeaders()
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: 'Failed to retrieve invoice' }));
        throw new Error(err.message || 'Failed to retrieve invoice');
      }
      return response.json();
    }
  },

  // --- ACCESS CONTROL & PERMISSION SCOPING ---
  getAdminPermissions: async (adminId) => {
    const response = await fetchWithFallback(`${BASE_URL}/access-control/admins/${adminId}/permissions`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to retrieve admin permissions' }));
      throw new Error(err.message || 'Failed to retrieve admin permissions');
    }
    return response.json();
  },

  updateAdminPermissions: async (adminId, permissions) => {
    const response = await fetchWithFallback(`${BASE_URL}/access-control/admins/${adminId}/permissions`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(permissions)
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to update admin permissions' }));
      throw new Error(err.message || 'Failed to update admin permissions');
    }
    return response.json();
  },

  applyAdminPreset: async (adminId, preset) => {
    const response = await fetchWithFallback(`${BASE_URL}/access-control/admins/${adminId}/preset`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ preset })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to apply admin preset' }));
      throw new Error(err.message || 'Failed to apply admin preset');
    }
    return response.json();
  },

  getAssignedUsers: async (adminId) => {
    const response = await fetchWithFallback(`${BASE_URL}/access-control/admins/${adminId}/users`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to retrieve assigned users' }));
      throw new Error(err.message || 'Failed to retrieve assigned users');
    }
    return response.json();
  },

  assignUsersToAdmin: async (adminId, userIds) => {
    const response = await fetchWithFallback(`${BASE_URL}/access-control/admins/${adminId}/users`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ userIds })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to assign users to admin' }));
      throw new Error(err.message || 'Failed to assign users to admin');
    }
    return response.json();
  },

  getDevelopers: async () => {
    const response = await fetchWithFallback(`${BASE_URL}/access-control/developers`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to retrieve developer list' }));
      throw new Error(err.message || 'Failed to retrieve developer list');
    }
    return response.json();
  },

  getAccessControlOverview: async () => {
    const response = await fetchWithFallback(`${BASE_URL}/access-control/overview`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to retrieve access control overview' }));
      throw new Error(err.message || 'Failed to retrieve access control overview');
    }
    return response.json();
  },

  // --- REQUIREMENT ADVANCE & REVIEW ---
  payRequirementAdvance: async (requirementId, amount, idempotencyKey) => {
    const response = await fetchWithFallback(`${BASE_URL}/requirements/${requirementId}/pay-advance`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ amount, idempotencyKey })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to process advance payment' }));
      throw new Error(err.message || 'Failed to process advance payment');
    }
    return response.json();
  },

  reviewRequirement: async (requirementId, action, notes) => {
    const response = await fetchWithFallback(`${BASE_URL}/requirements/${requirementId}/review`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ action, notes })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to submit requirement review' }));
      throw new Error(err.message || 'Failed to submit requirement review');
    }
    return response.json();
  },

  // --- PROJECT LIFECYCLE & DEVELOPER / REVIEWER WORKFLOW ---
  payProjectRemaining: async (projectId, amount, idempotencyKey) => {
    const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/pay-remaining`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ amount, idempotencyKey })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to process remaining payment' }));
      throw new Error(err.message || 'Failed to process remaining payment');
    }
    return response.json();
  },

  purchaseMarketplaceProject: async (projectId, idempotencyKey) => {
    const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/purchase-marketplace`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ idempotencyKey })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to purchase marketplace project' }));
      throw new Error(err.message || 'Failed to purchase marketplace project');
    }
    return response.json();
  },

  assignDeveloperToProject: async (projectId, developerId) => {
    const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/assign-developer`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ developerId })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to assign developer' }));
      throw new Error(err.message || 'Failed to assign developer');
    }
    return response.json();
  },

  assignReviewerToProject: async (projectId, reviewerId) => {
    const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/assign-reviewer`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ reviewerId })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to assign reviewer' }));
      throw new Error(err.message || 'Failed to assign reviewer');
    }
    return response.json();
  },

  developerSubmitReview: async (projectId, notes) => {
    const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/developer-submit-review`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ notes })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to submit deliverables for review' }));
      throw new Error(err.message || 'Failed to submit deliverables for review');
    }
    return response.json();
  },

  adminReviewProject: async (projectId, action, notes) => {
    const response = await fetchWithFallback(`${BASE_URL}/projects/${projectId}/admin-review`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ action, notes })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to submit project review decision' }));
      throw new Error(err.message || 'Failed to submit project review decision');
    }
    return response.json();
  },

  getDeveloperProjects: async () => {
    const response = await fetchWithFallback(`${BASE_URL}/projects/my-developer-projects`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to load developer projects' }));
      throw new Error(err.message || 'Failed to load developer projects');
    }
    return response.json();
  },

  getReviewProjects: async () => {
    const response = await fetchWithFallback(`${BASE_URL}/projects/my-review-projects`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to load review projects' }));
      throw new Error(err.message || 'Failed to load review projects');
    }
    return response.json();
  },

  // --- NOTIFICATIONS ---
  getNotifications: async () => {
    const response = await fetchWithFallback(`${BASE_URL}/notifications`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      return { notifications: [], unreadCount: 0 };
    }
    return response.json();
  },

  markNotificationRead: async (notificationId) => {
    const response = await fetchWithFallback(`${BASE_URL}/notifications/${notificationId}/read`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error('Failed to mark notification read');
    }
    return response.json();
  },

  markAllNotificationsRead: async () => {
    const response = await fetchWithFallback(`${BASE_URL}/notifications/read-all`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new Error('Failed to mark all notifications read');
    }
    return response.json();
  },

  // --- ACCESS CONTROL & PERMISSIONS ---
  getAdminPermissions: async (adminId) => {
    if (isMockMode()) {
      await delay();
      const perms = JSON.parse(localStorage.getItem(`admin_permissions_${adminId}`)) || {};
      const scopes = JSON.parse(localStorage.getItem(`admin_scopes_${adminId}`)) || {};
      return { permissions: perms, scopes };
    }
    const response = await fetchWithFallback(`${BASE_URL}/access-control/admin/${adminId}/permissions`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to load admin permissions' }));
      throw new Error(err.message || 'Failed to load admin permissions');
    }
    return response.json();
  },

  updateAdminPermissions: async (adminId, permissions) => {
    if (isMockMode()) {
      await delay();
      localStorage.setItem(`admin_permissions_${adminId}`, JSON.stringify(permissions.permissions || permissions));
      if (permissions.scopes) {
        localStorage.setItem(`admin_scopes_${adminId}`, JSON.stringify(permissions.scopes));
      }
      addMockAuditLog('superadmin@academic.com', 'ADMIN_PERMISSIONS_UPDATED', `Updated permissions for admin #${adminId}`);
      return { success: true, message: 'Permissions updated successfully' };
    }
    const response = await fetchWithFallback(`${BASE_URL}/access-control/admin/${adminId}/permissions`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(permissions)
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to update admin permissions' }));
      throw new Error(err.message || 'Failed to update admin permissions');
    }
    return response.json();
  },

  applyAdminPreset: async (adminId, presetName) => {
    if (isMockMode()) {
      await delay();
      const standardPerms = {
        USER_VIEW: true,
        USER_VIEW_PERSONAL_DATA: true,
        PROJECT_VIEW: true,
        PROJECT_VIEW_DETAILS: true,
        PROJECT_CREATE: true,
        PROJECT_EDIT: true
      };
      localStorage.setItem(`admin_permissions_${adminId}`, JSON.stringify(standardPerms));
      addMockAuditLog('superadmin@academic.com', 'ADMIN_PRESET_APPLIED', `Applied preset ${presetName} to admin #${adminId}`);
      return { success: true, message: `Preset ${presetName} applied` };
    }
    const response = await fetchWithFallback(`${BASE_URL}/access-control/admins/${adminId}/apply-preset`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ preset: presetName })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to apply admin preset' }));
      throw new Error(err.message || 'Failed to apply admin preset');
    }
    return response.json();
  },

  getAssignedUsers: async (adminId) => {
    if (isMockMode()) {
      await delay();
      const assignments = JSON.parse(localStorage.getItem(`admin_assigned_users_${adminId}`)) || [];
      return assignments;
    }
    const response = await fetchWithFallback(`${BASE_URL}/access-control/admin/${adminId}/users`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to load assigned users' }));
      throw new Error(err.message || 'Failed to load assigned users');
    }
    return response.json();
  },

  assignUsersToAdmin: async (adminId, userIds) => {
    if (isMockMode()) {
      await delay();
      localStorage.setItem(`admin_assigned_users_${adminId}`, JSON.stringify(userIds));
      addMockAuditLog('superadmin@academic.com', 'ADMIN_USERS_ASSIGNED', `Assigned ${userIds.length} users to admin #${adminId}`);
      return { success: true, message: 'Users assigned successfully' };
    }
    const response = await fetchWithFallback(`${BASE_URL}/access-control/admin/${adminId}/users`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ userIds })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to assign users to admin' }));
      throw new Error(err.message || 'Failed to assign users to admin');
    }
    return response.json();
  },

  getDevelopersList: async () => {
    if (isMockMode()) {
      await delay();
      return getMockUsers().filter(u => u.role === 'PROJECT_DEVELOPER' && !u.deleted);
    }
    const response = await fetchWithFallback(`${BASE_URL}/access-control/developers`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to load developers list' }));
      throw new Error(err.message || 'Failed to load developers list');
    }
    return response.json();
  },

  getAccessControlOverview: async () => {
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      return {
        totalAdmins: users.filter(u => (u.role === 'ADMIN' || u.role === 'SUPER_ADMIN') && !u.deleted).length,
        totalUsers: users.filter(u => u.role === 'USER' && !u.deleted).length
      };
    }
    const response = await fetchWithFallback(`${BASE_URL}/access-control/overview`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to load access control overview' }));
      throw new Error(err.message || 'Failed to load access control overview');
    }
    return response.json();
  },

  updateUserRole: async (userId, role) => {
    if (isMockMode()) {
      await delay();
      const users = getMockUsers();
      const u = users.find(x => x.id === Number(userId));
      if (u) {
        u.role = role;
        saveMockUsers(users);
      }
      addMockAuditLog('superadmin@academic.com', 'ROLE_UPDATE', `Updated user #${userId} role to ${role}`);
      return { success: true, user: u };
    }
    const response = await fetchWithFallback(`${BASE_URL}/access-control/users/${userId}/role`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ role })
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ message: 'Failed to update user role' }));
      throw new Error(err.message || 'Failed to update user role');
    }
    return response.json();
  }
};

export default api;



