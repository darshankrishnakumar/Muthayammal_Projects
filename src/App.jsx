import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import ProtectedLayout from './components/ProtectedLayout';

// Eager Login for immediate first-paint
import Login from './pages/Login';

// Lazy-loaded pages for 70%+ faster initial load & code splitting
const Register = lazy(() => import('./pages/Register'));
const Marketplace = lazy(() => import('./pages/Marketplace'));
const Orders = lazy(() => import('./pages/Orders'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Projects = lazy(() => import('./pages/Projects'));
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'));
const UserManagement = lazy(() => import('./pages/UserManagement'));
const AdminManagement = lazy(() => import('./pages/AdminManagement'));
const DeveloperManagement = lazy(() => import('./pages/DeveloperManagement'));
const AuditLogs = lazy(() => import('./pages/AuditLogs'));
const Profile = lazy(() => import('./pages/Profile'));
const ProjectFiles = lazy(() => import('./pages/ProjectFiles'));
const Requirements = lazy(() => import('./pages/Requirements'));
const RequirementForm = lazy(() => import('./pages/RequirementForm'));
const RequirementDetail = lazy(() => import('./pages/RequirementDetail'));

const RouteLoader = () => (
  <div style={{ display: 'flex', height: '60vh', width: '100%', alignItems: 'center', justifyContent: 'center' }}>
    <div style={{ textAlign: 'center' }}>
      <div style={{ border: '3px solid var(--border-color)', borderTop: '3px solid var(--primary)', borderRadius: '50%', width: '32px', height: '32px', animation: 'spin 0.6s linear infinite', margin: '0 auto 12px' }}></div>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading workspace...</p>
    </div>
  </div>
);

// Protected Route Wrapper
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', height: '100vh', width: '100vw', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--bg-main)' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ border: '4px solid var(--border-color)', borderTop: '4px solid var(--primary)', borderRadius: '50%', width: '40px', height: '40px', animation: 'spin 1s linear infinite', margin: '0 auto 16px' }}></div>
          <p style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-sans)', fontWeight: 500 }}>Verifying session clearance...</p>
        </div>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Check if role is authorized
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <ProtectedLayout>
        <div className="card text-center" style={{ padding: '60px 20px', maxWidth: '500px', margin: '40px auto' }}>
          <div style={{ margin: '0 auto 20px', width: '56px', height: '56px', borderRadius: '50%', backgroundColor: 'var(--error-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--error)' }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>!</span>
          </div>
          <h2 className="font-display" style={{ fontSize: '1.4rem', fontWeight: 600, marginBottom: '8px' }}>Access Denied</h2>
          <p className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '24px' }}>
            Your account role <strong>({user.role.replace('_', ' ')})</strong> does not possess clearance for this management section.
          </p>
          <button className="btn btn-primary" onClick={() => window.history.back()}>
            Go Back
          </button>
        </div>
      </ProtectedLayout>
    );
  }

  return (
    <ProtectedLayout>
      <Suspense fallback={<RouteLoader />}>
        {children}
      </Suspense>
    </ProtectedLayout>
  );
};

// Public Route Wrapper (Redirects to dashboard if already logged in)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <RouteLoader />;
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Smart Root Redirect (Sends logged-in users to /dashboard and guests to /login)
const RootRedirect = () => {
  const { user, loading } = useAuth();
  if (loading) {
    return <RouteLoader />;
  }
  return <Navigate to={user ? "/dashboard" : "/login"} replace />;
};

function App() {
  return (
    <Router>
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            } 
          />
          <Route 
            path="/register" 
            element={
              <PublicRoute>
                <Suspense fallback={<RouteLoader />}>
                  <Register />
                </Suspense>
              </PublicRoute>
            } 
          />

          {/* Secure Portal Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'PROJECT_DEVELOPER', 'USER']}>
                <Dashboard />
              </ProtectedRoute>
            } 
          />

          <Route path="/developer/workspace" element={<Navigate to="/dashboard" replace />} />
          <Route path="/admin/project-review" element={<Navigate to="/dashboard" replace />} />

          <Route 
            path="/marketplace" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'USER']}>
                <Marketplace />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/orders" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'USER']}>
                <Orders />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/projects" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'PROJECT_DEVELOPER', 'USER']}>
                <Projects />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/projects/:id" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'PROJECT_DEVELOPER', 'USER']}>
                <ProjectDetail />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/projects/:id/folders/:folderId" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'USER']}>
                <ProjectDetail />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/project-files" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'USER']}>
                <ProjectFiles />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/requirements" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'USER']}>
                <Requirements />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/requirements/new" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'USER']}>
                <RequirementForm />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/requirements/:id" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'USER']}>
                <RequirementDetail />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/requirements/:id/edit" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'USER']}>
                <RequirementForm />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/users" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN']}>
                <UserManagement />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/admins" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN']}>
                <AdminManagement />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/developers" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN']}>
                <DeveloperManagement />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/audit-logs" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN']}>
                <AuditLogs />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/profile" 
            element={
              <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'USER']}>
                <Profile />
              </ProtectedRoute>
            } 
          />

          {/* Root/Wildcard fallback redirects */}
          <Route path="/" element={<RootRedirect />} />
          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </Router>
  );
}

export default App;
