import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { isMockMode, setMockMode, api } from '../utils/api';
import { isDeadlineExpired } from '../utils/dateUtils';
import NotificationDrawer from './NotificationDrawer';
import { 
  LayoutDashboard, 
  FolderKanban,
  Users, 
  ShieldAlert, 
  FileText, 
  User, 
  LogOut, 
  Database,
  ArrowLeftRight,
  AlertCircle,
  Clock,
  Folder,
  Sparkles,
  ShoppingBag,
  Code2,
  ShieldCheck
} from 'lucide-react';

const ProtectedLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const mockActive = isMockMode();
  const [expiredCount, setExpiredCount] = useState(0);

  useEffect(() => {
    if (user && (user.role === 'SUPER_ADMIN' || user.role === 'ADMIN')) {
      checkExpiredAssignments();
    }
  }, [user]);

  const checkExpiredAssignments = async () => {
    try {
      const projects = await api.getProjects();
      if (!projects || projects.length === 0) {
        setExpiredCount(0);
        return;
      }

      const assignPromises = projects.slice(0, 20).map(p => 
        api.getProjectAssignments(p.id).catch(() => [])
      );
      const results = await Promise.all(assignPromises);
      let totalExpired = 0;

      results.forEach(assignList => {
        if (assignList && assignList.some(a => a.active && isDeadlineExpired(a.expiredAt))) {
          totalExpired++;
        }
      });

      setExpiredCount(totalExpired);
    } catch (e) {
      console.warn('Could not check expired assignments:', e);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) {
    return null;
  }

  const navItems = [
    {
      name: 'Dashboard',
      path: '/dashboard',
      icon: LayoutDashboard,
      roles: ['SUPER_ADMIN', 'ADMIN', 'PROJECT_DEVELOPER', 'USER']
    },
    {
      name: 'Marketplace',
      path: '/marketplace',
      icon: Sparkles,
      roles: ['SUPER_ADMIN', 'ADMIN', 'USER']
    },
    {
      name: 'My Orders',
      path: '/orders',
      icon: ShoppingBag,
      roles: ['SUPER_ADMIN', 'ADMIN', 'USER']
    },
    {
      name: 'Projects & Assignments',
      path: '/projects',
      icon: FolderKanban,
      roles: ['SUPER_ADMIN', 'ADMIN', 'PROJECT_DEVELOPER', 'USER']
    },
    {
      name: 'Requirements',
      path: '/requirements',
      icon: FileText,
      roles: ['SUPER_ADMIN', 'ADMIN', 'USER']
    },
    {
      name: 'User Management',
      path: '/users',
      icon: Users,
      roles: ['SUPER_ADMIN', 'ADMIN']
    },
    {
      name: 'Admin Management',
      path: '/admins',
      icon: ShieldAlert,
      roles: ['SUPER_ADMIN']
    },
    {
      name: 'Developer Management',
      path: '/developers',
      icon: Code2,
      roles: ['SUPER_ADMIN']
    },
    {
      name: 'Audit Logs',
      path: '/audit-logs',
      icon: FileText,
      roles: ['SUPER_ADMIN', 'ADMIN']
    },
    {
      name: 'My Profile',
      path: '/profile',
      icon: User,
      roles: ['SUPER_ADMIN', 'ADMIN', 'PROJECT_DEVELOPER', 'USER']
    }
  ];

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-logo">
            <span className="brand-logo-icon">A</span>
            <div className="brand-text">
              <h3>Academic Tool</h3>
              <p>Security & RBAC Layer</p>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <ul>
            {navItems.map((item) => {
              if (item.roles && !item.roles.includes(user.role)) return null;
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <li key={item.path}>
                  <Link 
                    to={item.path} 
                    className={`nav-link ${isActive ? 'active' : ''}`}
                  >
                    <Icon size={18} />
                    <span>{item.name}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Sidebar Footer */}
        <div className="sidebar-footer">
          <button onClick={handleLogout} className="btn-logout">
            <LogOut size={16} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Page Area */}
      <main className="main-content">
        {/* Top Header with Notification Bell */}
        <header className="content-header" style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 32px',
          borderBottom: '1px solid var(--border-color)',
          background: 'var(--bg-card)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Role Clearance:</span>
            <span className={`badge ${user.role === 'SUPER_ADMIN' ? 'badge-primary' : user.role === 'ADMIN' ? 'badge-info' : user.role === 'PROJECT_DEVELOPER' ? 'badge-warning' : 'badge-secondary'}`}>
              {user.role}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <NotificationDrawer />
            
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '6px 12px',
              borderRadius: 'var(--radius-full)',
              background: 'var(--bg-main)',
              border: '1px solid var(--border-color)'
            }}>
              <div style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--primary), #4f46e5)',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                fontSize: '0.82rem'
              }}>
                {(user.fullName || user.email || 'U').charAt(0).toUpperCase()}
              </div>
              <span style={{ fontSize: '0.86rem', fontWeight: 600, color: 'var(--text-main)' }}>
                {user.fullName || user.email}
              </span>
            </div>
          </div>
        </header>

        <div className="page-body">
          {children}
        </div>
      </main>

      {/* Add specific layout CSS directly to avoid importing issues */}
      <style>{`
        .layout-container {
          display: flex;
          min-height: 100vh;
          width: 100%;
        }

        .sidebar {
          width: 240px;
          background-color: var(--bg-sidebar);
          border-right: 1px solid var(--border-color);
          display: flex;
          flex-direction: column;
          position: fixed;
          top: 0;
          bottom: 0;
          left: 0;
          z-index: 100;
          transition: width 0.2s ease;
        }

        .main-content {
          margin-left: 240px;
          flex: 1;
          display: flex;
          flex-direction: column;
          min-width: 0;
          max-width: 1440px;
        }

        .content-header {
          height: 56px;
          padding: 0 24px;
          background: var(--bg-card);
          border-bottom: 1px solid var(--border-color);
          display: flex;
          align-items: center;
          justify-content: space-between;
          position: sticky;
          top: 0;
          z-index: 90;
        }

        .sidebar {
          width: 260px;
          height: 100vh;
          position: fixed;
          top: 0;
          left: 0;
          background-color: var(--bg-card);
          border-right: 1px solid var(--border-color);
          padding: 24px 18px;
          display: flex;
          flex-direction: column;
          z-index: 100;
          box-shadow: 0 0 20px rgba(0, 0, 0, 0.03);
        }

        .sidebar-brand {
          margin-bottom: 24px;
          padding: 0 4px;
        }

        .brand-logo {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .brand-logo-icon {
          background: linear-gradient(135deg, var(--primary) 0%, hsl(220, 90%, 45%) 100%);
          color: white;
          width: 36px;
          height: 36px;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: var(--font-display);
          font-weight: 700;
          font-size: 1.2rem;
          box-shadow: 0 4px 12px hsla(220, 90%, 56%, 0.25);
        }

        .brand-text h3 {
          font-family: var(--font-display);
          font-size: 1rem;
          font-weight: 700;
          color: var(--text-main);
          line-height: 1.2;
        }

        .brand-text p {
          font-size: 0.72rem;
          color: var(--text-muted);
          margin-top: 2px;
        }

        .sidebar-nav {
          flex: 1;
          overflow-y: auto;
        }

        .sidebar-nav ul {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .nav-link {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 11px 14px;
          border-radius: var(--radius-md);
          color: var(--text-muted);
          text-decoration: none;
          font-weight: 500;
          font-size: 0.9rem;
          transition: all 0.2s ease;
        }

        .nav-link:hover {
          background-color: var(--primary-light);
          color: var(--primary);
        }

        .nav-link.active {
          background-color: var(--primary);
          color: #ffffff;
          font-weight: 600;
          box-shadow: 0 4px 12px hsla(220, 90%, 56%, 0.25);
        }

        .sidebar-footer {
          display: flex;
          flex-direction: column;
          margin-top: auto;
          border-top: 1px solid var(--border-color);
          padding-top: 16px;
          padding-bottom: 8px;
        }

        .btn-logout {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          width: 100%;
          padding: 11px 16px;
          background: none;
          border: 1px solid var(--border-color);
          border-radius: var(--radius-md);
          color: var(--error);
          font-family: var(--font-sans);
          font-weight: 600;
          font-size: 0.9rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .btn-logout:hover {
          background-color: var(--error-light);
          border-color: transparent;
        }

        .main-content {
          margin-left: 260px;
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }

        .content-header {
          padding: 24px 32px;
          background-color: var(--bg-card);
          border-bottom: 1px solid var(--border-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .header-title {
          font-family: var(--font-display);
          font-size: 1.75rem;
          font-weight: 700;
          color: var(--text-main);
          letter-spacing: -0.5px;
          margin: 0 !important;
        }

        .header-subtitle {
          font-size: 0.85rem;
          color: var(--text-muted);
          margin-top: 2px;
        }

        .connection-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.8rem;
          font-weight: 500;
          color: var(--text-muted);
          background-color: var(--bg-main);
          padding: 6px 12px;
          border-radius: var(--radius-full);
          border: 1px solid var(--border-color);
        }

        .dot {
          width: 8px;
          height: 8px;
          border-radius: var(--radius-full);
        }

        .dot-mock {
          background-color: var(--warning);
          box-shadow: 0 0 8px var(--warning);
        }

        .dot-live {
          background-color: var(--success);
          box-shadow: 0 0 8px var(--success);
        }

        .page-body {
          padding: 32px;
          flex: 1;
          max-width: 1400px;
          width: 100%;
          margin: 0 auto;
        }

        @media (max-width: 1024px) {
          .sidebar {
            width: 80px;
            padding: 20px 8px;
          }
          
          .brand-text, .user-info, .sidebar-footer .mode-selector, .nav-link span, .btn-logout span {
            display: none;
          }

          .sidebar-brand {
            display: flex;
            justify-content: center;
          }

          .user-profile-badge {
            justify-content: center;
            padding: 8px 4px;
          }

          .nav-link {
            justify-content: center;
            padding: 12px;
          }

          .main-content {
            margin-left: 80px;
          }

          .content-header {
            padding: 16px 20px;
          }

          .page-body {
            padding: 20px;
          }
        }
      `}</style>
    </div>
  );
};

export default ProtectedLayout;
