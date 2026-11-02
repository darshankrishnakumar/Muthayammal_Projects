import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { Link } from 'react-router-dom';
import { 
  FolderKanban, 
  FileText, 
  Users, 
  ShieldAlert, 
  User, 
  PlusCircle, 
  ArrowRight,
  Clock,
  CheckCircle2,
  Lock,
  Layers,
  Sparkles,
  TrendingUp,
  Activity,
  FolderOpen,
  History,
  ShieldCheck
} from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalAdmins: 0,
    totalLogs: 0,
    totalProjects: 0,
    myRequirements: 0,
    pendingSubmissions: 0,
    approvedRequirements: 0,
    myOrdersCount: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchStats = async () => {
      try {
        const promises = [
          (user?.role === 'SUPER_ADMIN' || user?.role === 'ADMIN') ? api.getUsers().catch(() => []) : Promise.resolve([]),
          user?.role === 'SUPER_ADMIN' ? api.getAdmins().catch(() => []) : Promise.resolve([]),
          (user?.role === 'SUPER_ADMIN' || user?.role === 'ADMIN') ? api.getAuditLogs().catch(() => []) : Promise.resolve([]),
          api.getRequirementStats().catch(() => ({ myRequirements: 0, pendingSubmissions: 0, approvedRequirements: 0 })),
          api.getProjects().catch(() => []),
          api.getMyOrders().catch(() => [])
        ];

        const [usersList, adminsList, logsList, reqStats, projectsList, ordersList] = await Promise.all(promises);

        if (!isMounted) return;

        setStats({
          totalUsers: (usersList || []).length,
          activeUsers: (usersList || []).filter(u => u.status === 'ACTIVE').length,
          totalAdmins: user?.role === 'SUPER_ADMIN' ? (adminsList || []).length : 1,
          totalLogs: (logsList || []).length,
          totalProjects: (projectsList || []).length,
          myRequirements: reqStats?.myRequirements || 0,
          pendingSubmissions: reqStats?.pendingSubmissions || 0,
          approvedRequirements: reqStats?.approvedRequirements || 0,
          myOrdersCount: (ordersList || []).length
        });
      } catch (err) {
        console.error('Error fetching dashboard statistics:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchStats();
    return () => { isMounted = false; };
  }, [user]);

  // Define Navigation Modules tailored by Role
  const getNavModules = () => {
    const isUser = user.role === 'USER';
    const isAdmin = user.role === 'ADMIN';
    const isSuperAdmin = user.role === 'SUPER_ADMIN';

    return [
      {
        id: 'marketplace',
        title: 'Academic Marketplace',
        subtitle: 'Browse & purchase pre-approved requirement specifications, datasets, and research modules.',
        icon: Sparkles,
        badge: 'Store Catalog',
        badgeType: 'badge-primary',
        link: '/marketplace',
        btnText: 'Browse Catalog',
        show: true
      },
      {
        id: 'orders',
        title: 'Orders & Invoices',
        subtitle: 'Review purchased digital assets, license keys, and download cryptographically verified receipts.',
        icon: History,
        badge: `${stats.myOrdersCount} Orders`,
        badgeType: 'badge-secondary',
        link: '/orders',
        btnText: 'View Invoices',
        show: true
      },
      {
        id: 'projects',
        title: 'Projects & Assignments',
        subtitle: 'Explore active project repositories, root folder structures, and source assets.',
        icon: FolderKanban,
        badge: 'Core Workspace',
        badgeType: 'badge-primary',
        link: '/projects',
        btnText: 'Open Project Directory',
        show: true
      },
      {
        id: 'requirements',
        title: 'Requirements Management',
        subtitle: 'Submit, review, and track research requirement specifications and project requests.',
        icon: FileText,
        badge: isUser ? `${stats.myRequirements} Submitted` : `${stats.pendingSubmissions} Pending`,
        badgeType: 'badge-primary',
        link: '/requirements',
        btnText: isUser ? 'View My Requirements' : 'Review Requirements',
        show: isSuperAdmin || isAdmin || isUser
      },
      {
        id: 'users',
        title: 'User Management',
        subtitle: 'Manage system users, update role clearance levels, and toggle account activation state.',
        icon: Users,
        badge: `${stats.totalUsers} Registered`,
        badgeType: 'badge-primary',
        link: '/users',
        btnText: 'Manage System Users',
        show: isSuperAdmin || isAdmin
      },
      {
        id: 'admins',
        title: 'Admin Management Panel',
        subtitle: 'Super Admin portal for configuring administrator credentials and top-level privileges.',
        icon: ShieldAlert,
        badge: 'Super Admin Only',
        badgeType: 'badge-danger',
        link: '/admins',
        btnText: 'Manage Admin Accounts',
        show: isSuperAdmin
      },
      {
        id: 'audit',
        title: 'Security Audit Logs',
        subtitle: 'Monitor operational system logs, access events, and file streaming activity.',
        icon: Clock,
        badge: `${stats.totalLogs} Logs`,
        badgeType: 'badge-warning',
        link: '/audit-logs',
        btnText: 'Inspect Audit Logs',
        show: isSuperAdmin || isAdmin
      },
      {
        id: 'profile',
        title: 'My Profile & Account',
        subtitle: 'View your identity badge, update email credentials, or change your account password.',
        icon: User,
        badge: 'Account Settings',
        badgeType: 'badge-secondary',
        link: '/profile',
        btnText: 'Manage Profile',
        show: true
      }
    ].filter(m => m.show);
  };

  const navModules = getNavModules();

  return (
    <div className="dashboard-container text-left flex flex-col" style={{ gap: '32px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* 1. Welcome Profile Header Card */}
      <div className="card" style={{ padding: '24px 32px' }}>
        <div className="flex justify-between items-center gap-6 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="badge badge-primary">
                Portal Workspace ({user?.role ? user.role.replace('_', ' ') : 'USER'})
              </span>
            </div>
            <h2 className="font-display" style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Welcome back, {user?.fullName}!
            </h2>
            <p className="text-muted" style={{ fontSize: '0.9rem', marginTop: '4px', maxWidth: '600px' }}>
              Track project deliverables, folder assets, and system security clearances in real-time.
            </p>
          </div>

          <div className="flex items-center gap-3" style={{ backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', padding: '10px 16px', borderRadius: 'var(--radius-md)' }}>
            <div className="profile-hero-avatar" style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: 'var(--primary-light)', color: 'var(--primary)', fontWeight: 700, fontSize: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {user?.fullName ? user.fullName.substring(0, 2).toUpperCase() : 'US'}
            </div>
            <div>
              <span style={{ fontSize: '0.88rem', fontWeight: 600, display: 'block', color: 'var(--text-main)' }}>{user?.fullName}</span>
              <span className="text-muted" style={{ fontSize: '0.78rem' }}>{user?.email}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. KPI Metrics Section */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="font-display" style={{ fontSize: '1.25rem', fontWeight: 700 }}>Project & Operational KPI Metrics</h3>
            <p className="text-muted" style={{ fontSize: '0.85rem' }}>Real-time performance indicators and system status overview.</p>
          </div>
          <Activity size={18} className="text-primary" />
        </div>

        {/* KPI Cards Grid */}
        {user?.role === 'USER' ? (
          <div className="grid grid-cols-3 gap-6">
            <div className="card dashboard-kpi-card">
              <div className="kpi-icon-box bg-primary-light text-primary">
                <FolderKanban size={24} />
              </div>
              <div className="kpi-content">
                <span className="kpi-label text-muted">Assigned Projects</span>
                <h3 className="kpi-value font-display">{loading ? '...' : stats.totalProjects}</h3>
                <span className="kpi-trend text-primary flex items-center gap-1">
                  <TrendingUp size={12} />
                  <span>Active Workspaces</span>
                </span>
              </div>
            </div>

            <div className="card dashboard-kpi-card" style={{ borderLeft: '4px solid var(--warning)' }}>
              <div className="kpi-icon-box bg-warning-light text-warning">
                <History size={24} />
              </div>
              <div className="kpi-content">
                <span className="kpi-label text-muted">Marketplace Orders</span>
                <h3 className="kpi-value font-display text-warning">{loading ? '...' : stats.myOrdersCount}</h3>
                <span className="kpi-trend text-warning flex items-center gap-1">
                  <Clock size={12} />
                  <span>Purchased Solutions</span>
                </span>
              </div>
            </div>

            <div className="card dashboard-kpi-card" style={{ borderLeft: '4px solid var(--success)' }}>
              <div className="kpi-icon-box bg-success-light text-success">
                <CheckCircle2 size={24} />
              </div>
              <div className="kpi-content">
                <span className="kpi-label text-muted">Account Clearance</span>
                <h3 className="kpi-value font-display text-success">ACTIVE</h3>
                <span className="kpi-trend text-success flex items-center gap-1">
                  <CheckCircle2 size={12} />
                  <span>Verified Researcher</span>
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-6">
            <div className="card dashboard-kpi-card">
              <div className="kpi-icon-box bg-primary-light text-primary">
                <Users size={24} />
              </div>
              <div className="kpi-content">
                <span className="kpi-label text-muted">Registered Users</span>
                <h3 className="kpi-value font-display">{loading ? '...' : stats.totalUsers}</h3>
                <span className="kpi-trend text-success flex items-center gap-1">
                  <CheckCircle2 size={12} />
                  <span>{stats.activeUsers} Active Accounts</span>
                </span>
              </div>
            </div>

            {user?.role === 'SUPER_ADMIN' ? (
              <div className="card dashboard-kpi-card" style={{ borderLeft: '4px solid var(--success)' }}>
                <div className="kpi-icon-box bg-success-light text-success">
                  <ShieldCheck size={24} />
                </div>
                <div className="kpi-content">
                  <span className="kpi-label text-muted">System Administrators</span>
                  <h3 className="kpi-value font-display text-success">{loading ? '...' : stats.totalAdmins}</h3>
                  <span className="kpi-trend text-primary flex items-center gap-1">
                    <ShieldCheck size={12} />
                    <span>Super Admin Governance</span>
                  </span>
                </div>
              </div>
            ) : (
              <div className="card dashboard-kpi-card" style={{ borderLeft: '4px solid var(--primary)' }}>
                <div className="kpi-icon-box bg-primary-light text-primary">
                  <FolderOpen size={24} />
                </div>
                <div className="kpi-content">
                  <span className="kpi-label text-muted">Active Projects</span>
                  <h3 className="kpi-value font-display text-primary">{loading ? '...' : stats.totalProjects}</h3>
                  <span className="kpi-trend text-primary flex items-center gap-1">
                    <TrendingUp size={12} />
                    <span>Project Repositories</span>
                  </span>
                </div>
              </div>
            )}

            <div className="card dashboard-kpi-card" style={{ borderLeft: '4px solid var(--warning)' }}>
              <div className="kpi-icon-box bg-warning-light text-warning">
                <History size={24} />
              </div>
              <div className="kpi-content">
                <span className="kpi-label text-muted">Audit Log Records</span>
                <h3 className="kpi-value font-display text-warning">{loading ? '...' : stats.totalLogs}</h3>
                <span className="kpi-trend text-warning flex items-center gap-1">
                  <Clock size={12} />
                  <span>Security Events Logged</span>
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 3. System Navigation Modules Hub */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="font-display" style={{ fontSize: '1.25rem', fontWeight: 700 }}>System Navigation Modules</h3>
            <p className="text-muted" style={{ fontSize: '0.85rem' }}>Direct entry points for your operational session clearance level.</p>
          </div>
          <Sparkles size={18} className="text-primary" />
        </div>

        {/* Navigation Cards Grid */}
        <div className="grid grid-cols-3 gap-6">
          {navModules.map((module) => {
            const Icon = module.icon;
            return (
              <div key={module.id} className="card card-hover flex flex-col justify-between" style={{ padding: '24px' }}>
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <div className="nav-icon-box bg-primary-light text-primary">
                      <Icon size={22} />
                    </div>
                    <span className={`badge ${module.badgeType}`}>{module.badge}</span>
                  </div>

                  <h4 className="font-display mb-1" style={{ fontSize: '1.1rem', fontWeight: 700 }}>
                    {module.title}
                  </h4>
                  <p className="text-muted" style={{ fontSize: '0.85rem', lineHeight: '1.5', marginBottom: '20px' }}>
                    {module.subtitle}
                  </p>
                </div>

                <Link to={module.link} className="btn btn-secondary flex items-center justify-between" style={{ padding: '10px 14px', width: '100%' }}>
                  <span style={{ fontSize: '0.85rem' }}>{module.btnText}</span>
                  <ArrowRight size={14} />
                </Link>
              </div>
            );
          })}
        </div>
      </div>

      <style>{`
        .dashboard-hero-card {
          background: linear-gradient(135deg, hsl(220, 90%, 56%) 0%, hsl(220, 90%, 42%) 100%);
          border: none;
          box-shadow: 0 8px 24px hsla(220, 90%, 56%, 0.25);
        }

        .dashboard-avatar-pill {
          background: rgba(255, 255, 255, 0.15);
          padding: 6px 14px 6px 6px;
          border-radius: var(--radius-full);
          border: 1px solid rgba(255, 255, 255, 0.25);
        }

        .avatar-circle {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: #ffffff;
          color: var(--primary);
          font-family: var(--font-display);
          font-weight: 700;
          font-size: 0.95rem;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .dashboard-kpi-card {
          display: flex;
          align-items: center;
          gap: 18px;
          padding: 22px 24px;
        }

        .kpi-icon-box {
          width: 52px;
          height: 52px;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .kpi-content {
          display: flex;
          flex-direction: column;
        }

        .kpi-label {
          font-size: 0.8rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .kpi-value {
          font-size: 1.85rem;
          font-weight: 700;
          line-height: 1.15;
          margin: 2px 0 4px 0;
        }

        .kpi-trend {
          font-size: 0.75rem;
          font-weight: 500;
        }

        .nav-icon-box {
          width: 44px;
          height: 44px;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
