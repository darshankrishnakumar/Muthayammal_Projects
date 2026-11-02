import { useEffect, useRef, useState } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Library, Share2, Building2, FileText, FolderKanban, Receipt, Users, ShieldCheck,
  Code2, ScrollText, Store, BookMarked, Search, Menu, PanelLeftClose, PanelLeftOpen, LogOut, User as UserIcon,
  Sun, Moon, Monitor, ChevronDown,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import NotificationDrawer from './NotificationDrawer';
import { Avatar } from './ui';
import { ROLE_LABELS } from '../utils/format';
import { getTheme, setTheme } from '../utils/theme';

const NAV = {
  SUPER_ADMIN: [
    { title: 'Overview', items: [{ to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard }] },
    {
      title: 'Catalogue',
      items: [
        { to: '/library', label: 'Project library', icon: Library },
        { to: '/allocations', label: 'Allocations', icon: Share2 },
        { to: '/colleges', label: 'Colleges', icon: Building2 },
      ],
    },
    {
      title: 'Development',
      items: [
        { to: '/requirements', label: 'Requirements', icon: FileText },
        { to: '/projects', label: 'Development projects', icon: FolderKanban },
      ],
    },
    { title: 'Commerce', items: [{ to: '/orders', label: 'Orders & payments', icon: Receipt }] },
    {
      title: 'People',
      items: [
        { to: '/users', label: 'Students', icon: Users },
        { to: '/admins', label: 'College admins', icon: ShieldCheck },
        { to: '/developers', label: 'Developers', icon: Code2 },
      ],
    },
    { title: 'System', items: [{ to: '/audit-logs', label: 'Audit log', icon: ScrollText }] },
  ],
  ADMIN: [
    { title: 'Overview', items: [{ to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard }] },
    {
      title: 'College',
      items: [
        { to: '/marketplace', label: 'Allocated projects', icon: Store },
        { to: '/users', label: 'Students', icon: Users },
      ],
    },
    {
      title: 'Development',
      items: [
        { to: '/requirements', label: 'Requirements', icon: FileText },
        { to: '/projects', label: 'Projects', icon: FolderKanban },
      ],
    },
    { title: 'Reports', items: [{ to: '/orders', label: 'Orders', icon: Receipt }, { to: '/audit-logs', label: 'Audit log', icon: ScrollText }] },
  ],
  PROJECT_DEVELOPER: [
    { title: 'Overview', items: [{ to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard }] },
    {
      title: 'Work',
      items: [
        { to: '/projects', label: 'My assignments', icon: FolderKanban },
        { to: '/requirements', label: 'Requirements', icon: FileText },
      ],
    },
  ],
  USER: [
    { title: 'Overview', items: [{ to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard }] },
    {
      title: 'Projects',
      items: [
        { to: '/marketplace', label: 'Browse projects', icon: Store },
        { to: '/projects', label: 'My projects', icon: BookMarked },
      ],
    },
    {
      title: 'Custom development',
      items: [{ to: '/requirements', label: 'My requirements', icon: FileText }],
    },
    { title: 'Account', items: [{ to: '/orders', label: 'Orders', icon: Receipt }] },
  ],
};

const SEARCH_TARGET = {
  SUPER_ADMIN: { path: '/library', placeholder: 'Search the project library…' },
  ADMIN: { path: '/marketplace', placeholder: 'Search allocated projects…' },
  PROJECT_DEVELOPER: { path: '/projects', placeholder: 'Search your projects…' },
  USER: { path: '/marketplace', placeholder: 'Search projects…' },
};

const COLLAPSE_KEY = 'ui.sidebarCollapsed';

export default function ProtectedLayout({ children }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(() => {
    try { return localStorage.getItem(COLLAPSE_KEY) === '1'; } catch { return false; }
  });
  const [mobileOpen, setMobileOpen] = useState(false);
  const [query, setQuery] = useState('');
  const searchRef = useRef(null);

  const role = user?.role || 'USER';
  const sections = NAV[role] || NAV.USER;
  const search = SEARCH_TARGET[role] || SEARCH_TARGET.USER;

  useEffect(() => setMobileOpen(false), [location.pathname]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
        e.preventDefault();
        searchRef.current?.focus();
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  const toggleCollapsed = () => {
    setCollapsed((c) => {
      try { localStorage.setItem(COLLAPSE_KEY, c ? '0' : '1'); } catch { /* ignore */ }
      return !c;
    });
  };

  const submitSearch = (e) => {
    e.preventDefault();
    navigate(`${search.path}${query.trim() ? `?search=${encodeURIComponent(query.trim())}` : ''}`);
  };

  return (
    <div className="app-shell">
      <aside className={`sidebar ${collapsed ? 'is-collapsed' : ''} ${mobileOpen ? 'is-open' : ''}`} aria-label="Main navigation">
        <div className="sidebar-brand">
          <span className="brand-mark" aria-hidden="true">AI</span>
          <div className="brand-text">
            <div className="brand-name">Academic Integration</div>
            <div className="brand-sub">{user?.college?.name || ROLE_LABELS[role]}</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {sections.map((section) => (
            <div className="nav-section" key={section.title}>
              <div className="nav-section-title">{section.title}</div>
              {section.items.map((item) => (
                <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title={collapsed ? item.label : undefined}>
                  <item.icon aria-hidden="true" />
                  <span className="nav-label">{item.label}</span>
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer desktop-only">
          <button className="nav-item" onClick={toggleCollapsed} aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
            {collapsed ? <PanelLeftOpen aria-hidden="true" /> : <PanelLeftClose aria-hidden="true" />}
            <span className="nav-label">Collapse</span>
          </button>
        </div>
      </aside>
      <div className={`sidebar-scrim ${mobileOpen ? 'is-open' : ''}`} onClick={() => setMobileOpen(false)} />

      <div className="main-area">
        <header className="topbar">
          <button className="btn btn-ghost btn-icon mobile-only" onClick={() => setMobileOpen(true)} aria-label="Open navigation">
            <Menu />
          </button>
          <form className="topbar-search" onSubmit={submitSearch} role="search">
            <Search size={15} aria-hidden="true" />
            <input
              ref={searchRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={search.placeholder}
              aria-label="Search"
            />
            <kbd className="desktop-only">/</kbd>
          </form>
          <div className="topbar-actions">
            <NotificationDrawer />
            <ProfileMenu user={user} onLogout={async () => { await logout(); navigate('/login'); }} />
          </div>
        </header>

        <main className="page" id="main">
          {children}
        </main>
      </div>
    </div>
  );
}

function ProfileMenu({ user, onLogout }) {
  const [open, setOpen] = useState(false);
  const [theme, setThemeState] = useState(getTheme());
  const ref = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const onDown = (e) => ref.current && !ref.current.contains(e.target) && setOpen(false);
    const onKey = (e) => e.key === 'Escape' && setOpen(false);
    document.addEventListener('mousedown', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  const chooseTheme = (t) => {
    setTheme(t);
    setThemeState(t);
  };

  return (
    <div className="dropdown" ref={ref}>
      <button className="btn btn-ghost" style={{ paddingLeft: 6, paddingRight: 8 }} onClick={() => setOpen((o) => !o)} aria-haspopup="menu" aria-expanded={open}>
        <Avatar name={user?.fullName} size="sm" />
        <span className="desktop-only text-sm font-medium truncate" style={{ maxWidth: 140 }}>{user?.fullName}</span>
        <ChevronDown size={14} className="desktop-only" aria-hidden="true" />
      </button>
      {open && (
        <div className="dropdown-menu" role="menu">
          <div className="dropdown-label">
            <div className="font-medium text-sm" style={{ color: 'var(--text)' }}>{user?.fullName}</div>
            <div className="truncate">{user?.email}</div>
            <div className="mt-1">{ROLE_LABELS[user?.role]}{user?.college ? ` · ${user.college.name}` : ''}</div>
          </div>
          <div className="dropdown-sep" />
          <Link to="/profile" className="dropdown-item" role="menuitem" onClick={() => setOpen(false)}>
            <UserIcon aria-hidden="true" /> Profile & security
          </Link>
          <div className="dropdown-sep" />
          <div className="dropdown-label">Theme</div>
          <div className="flex gap-1" style={{ padding: '2px 6px 6px' }}>
            {[
              { v: 'light', icon: Sun, label: 'Light' },
              { v: 'dark', icon: Moon, label: 'Dark' },
              { v: 'system', icon: Monitor, label: 'System' },
            ].map((t) => (
              <button key={t.v} className={`btn btn-sm flex-1 ${theme === t.v ? 'btn-secondary' : 'btn-ghost'}`} onClick={() => chooseTheme(t.v)} aria-pressed={theme === t.v}>
                <t.icon aria-hidden="true" /> {t.label}
              </button>
            ))}
          </div>
          <div className="dropdown-sep" />
          <button className="dropdown-item is-danger" role="menuitem" onClick={onLogout}>
            <LogOut aria-hidden="true" /> Sign out
          </button>
        </div>
      )}
    </div>
  );
}
