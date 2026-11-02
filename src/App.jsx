import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ShieldAlert } from 'lucide-react';
import { useAuth } from './context/AuthContext';
import ProtectedLayout from './components/ProtectedLayout';
import { EmptyState, LoadingBlock } from './components/ui';
import Login from './pages/Login';

const Register = lazy(() => import('./pages/Register'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Library = lazy(() => import('./pages/Library'));
const Colleges = lazy(() => import('./pages/Colleges'));
const Allocations = lazy(() => import('./pages/Allocations'));
const Marketplace = lazy(() => import('./pages/Marketplace'));
const MarketplaceProject = lazy(() => import('./pages/MarketplaceProject'));
const Orders = lazy(() => import('./pages/Orders'));
const Projects = lazy(() => import('./pages/Projects'));
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'));
const Requirements = lazy(() => import('./pages/Requirements'));
const RequirementForm = lazy(() => import('./pages/RequirementForm'));
const RequirementDetail = lazy(() => import('./pages/RequirementDetail'));
const UserManagement = lazy(() => import('./pages/UserManagement'));
const AdminManagement = lazy(() => import('./pages/AdminManagement'));
const DeveloperManagement = lazy(() => import('./pages/DeveloperManagement'));
const AuditLogs = lazy(() => import('./pages/AuditLogs'));
const Profile = lazy(() => import('./pages/Profile'));

const ALL = ['SUPER_ADMIN', 'ADMIN', 'PROJECT_DEVELOPER', 'USER'];

/**
 * Route guard for signed-in screens. Role lists only decide what is shown; every action is
 * authorized again by the backend.
 */
const ProtectedRoute = ({ children, roles = ALL }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}><LoadingBlock label="Checking your session…" /></div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return (
    <ProtectedLayout>
      {roles.includes(user.role) ? (
        <Suspense fallback={<LoadingBlock />}>{children}</Suspense>
      ) : (
        <div className="card" style={{ maxWidth: 520, margin: '48px auto' }}>
          <EmptyState
            icon={ShieldAlert}
            title="This area isn't available for your role"
            text="If you think you should have access, contact your platform administrator."
            action={<button className="btn btn-secondary" onClick={() => window.history.back()}>Go back</button>}
          />
        </div>
      )}
    </ProtectedLayout>
  );
};

const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <LoadingBlock />;
  if (user) return <Navigate to="/dashboard" replace />;
  return <Suspense fallback={<LoadingBlock />}>{children}</Suspense>;
};

const RootRedirect = () => {
  const { user, loading } = useAuth();
  if (loading) return <LoadingBlock />;
  return <Navigate to={user ? '/dashboard' : '/login'} replace />;
};

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />

        {/* Catalogue (Super Admin) */}
        <Route path="/library" element={<ProtectedRoute roles={['SUPER_ADMIN']}><Library /></ProtectedRoute>} />
        <Route path="/colleges" element={<ProtectedRoute roles={['SUPER_ADMIN']}><Colleges /></ProtectedRoute>} />
        <Route path="/allocations" element={<ProtectedRoute roles={['SUPER_ADMIN']}><Allocations /></ProtectedRoute>} />

        {/* Marketplace */}
        <Route path="/marketplace" element={<ProtectedRoute roles={['SUPER_ADMIN', 'ADMIN', 'USER']}><Marketplace /></ProtectedRoute>} />
        <Route path="/marketplace/:id" element={<ProtectedRoute roles={['SUPER_ADMIN', 'ADMIN', 'USER']}><MarketplaceProject /></ProtectedRoute>} />
        <Route path="/orders" element={<ProtectedRoute roles={['SUPER_ADMIN', 'ADMIN', 'USER']}><Orders /></ProtectedRoute>} />

        {/* Projects and development */}
        <Route path="/projects" element={<ProtectedRoute><Projects /></ProtectedRoute>} />
        <Route path="/projects/:id" element={<ProtectedRoute><ProjectDetail /></ProtectedRoute>} />
        <Route path="/requirements" element={<ProtectedRoute><Requirements /></ProtectedRoute>} />
        <Route path="/requirements/new" element={<ProtectedRoute roles={['USER']}><RequirementForm /></ProtectedRoute>} />
        <Route path="/requirements/:id" element={<ProtectedRoute><RequirementDetail /></ProtectedRoute>} />
        <Route path="/requirements/:id/edit" element={<ProtectedRoute roles={['USER', 'SUPER_ADMIN']}><RequirementForm /></ProtectedRoute>} />

        {/* People and system */}
        <Route path="/users" element={<ProtectedRoute roles={['SUPER_ADMIN', 'ADMIN']}><UserManagement /></ProtectedRoute>} />
        <Route path="/admins" element={<ProtectedRoute roles={['SUPER_ADMIN']}><AdminManagement /></ProtectedRoute>} />
        <Route path="/developers" element={<ProtectedRoute roles={['SUPER_ADMIN']}><DeveloperManagement /></ProtectedRoute>} />
        <Route path="/audit-logs" element={<ProtectedRoute roles={['SUPER_ADMIN', 'ADMIN']}><AuditLogs /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />

        {/* Legacy paths */}
        <Route path="/project-files" element={<Navigate to="/projects" replace />} />
        <Route path="/projects/:id/folders/:folderId" element={<Navigate to="/projects" replace />} />
        <Route path="/developer/workspace" element={<Navigate to="/dashboard" replace />} />
        <Route path="/admin/project-review" element={<Navigate to="/dashboard" replace />} />

        <Route path="/" element={<RootRedirect />} />
        <Route path="*" element={<RootRedirect />} />
      </Routes>
    </Router>
  );
}
