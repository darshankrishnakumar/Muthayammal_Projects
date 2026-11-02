import { useEffect, useRef, useState } from 'react';
import { Bell, CheckCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { relativeTime } from '../utils/format';

const POLL_MS = 30000;

export default function NotificationDrawer() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const navigate = useNavigate();

  const load = async () => {
    try {
      const res = await api.getNotifications();
      setNotifications(res?.notifications || []);
      setUnreadCount(res?.unreadCount || 0);
    } catch {
      /* notifications are non-critical */
    }
  };

  useEffect(() => {
    load();
    const interval = setInterval(() => document.visibilityState === 'visible' && load(), POLL_MS);
    return () => clearInterval(interval);
  }, []);

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

  const isRead = (n) => n.read || n.isRead;

  const openItem = async (n) => {
    if (!isRead(n)) {
      try {
        await api.markNotificationRead(n.id);
        setNotifications((prev) => prev.map((x) => (x.id === n.id ? { ...x, read: true, isRead: true } : x)));
        setUnreadCount((c) => Math.max(0, c - 1));
      } catch { /* ignore */ }
    }
    setOpen(false);
    if (n.linkUrl && n.linkUrl.startsWith('/')) navigate(n.linkUrl);
  };

  const markAll = async () => {
    try {
      await api.markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true, isRead: true })));
      setUnreadCount(0);
    } catch { /* ignore */ }
  };

  return (
    <div className="dropdown" ref={ref}>
      <button className="btn btn-ghost btn-icon relative" onClick={() => setOpen((o) => !o)} aria-label={`Notifications${unreadCount ? `, ${unreadCount} unread` : ''}`} aria-expanded={open}>
        <Bell />
        {unreadCount > 0 && (
          <span style={{ position: 'absolute', top: 6, right: 6, width: 8, height: 8, borderRadius: '50%', background: 'var(--accent)', boxShadow: '0 0 0 2px var(--bg)' }} />
        )}
      </button>
      {open && (
        <div className="dropdown-menu" style={{ width: 'min(380px, calc(100vw - 24px))', padding: 0 }} role="dialog" aria-label="Notifications">
          <div className="flex items-center justify-between" style={{ padding: '12px 14px', borderBottom: '1px solid var(--border)' }}>
            <span className="font-semibold text-md">Notifications</span>
            {unreadCount > 0 && (
              <button className="btn btn-ghost btn-sm" onClick={markAll}><CheckCheck /> Mark all read</button>
            )}
          </div>
          <div style={{ maxHeight: 420, overflowY: 'auto' }}>
            {notifications.length === 0 ? (
              <div className="text-center text-sm text-subtle" style={{ padding: '36px 16px' }}>You're all caught up.</div>
            ) : (
              notifications.slice(0, 30).map((n) => (
                <button key={n.id} className="list-item w-full text-left" onClick={() => openItem(n)} style={{ alignItems: 'flex-start' }}>
                  <span style={{ width: 7, height: 7, marginTop: 7, borderRadius: '50%', flexShrink: 0, background: isRead(n) ? 'transparent' : 'var(--accent)' }} />
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-medium" style={{ color: 'var(--text)' }}>{n.title}</span>
                    <span className="block text-sm text-muted">{n.message}</span>
                    <span className="block text-xs text-subtle mt-1">{relativeTime(n.createdAt)}</span>
                  </span>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
