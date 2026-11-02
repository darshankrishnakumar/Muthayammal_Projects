import React, { useState, useEffect, useRef } from 'react';
import { Bell, Check, ExternalLink, Clock, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../utils/api';

export default function NotificationDrawer() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const drawerRef = useRef(null);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 20000); // Poll every 20s
    return () => clearInterval(interval);
  }, []);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (drawerRef.current && !drawerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const fetchNotifications = async () => {
    try {
      const res = await api.getNotifications();
      if (res) {
        setNotifications(res.notifications || []);
        setUnreadCount(res.unreadCount || 0);
      }
    } catch (e) {
      // Non-blocking
    }
  };

  const handleMarkAsRead = async (id, e) => {
    if (e) e.stopPropagation();
    try {
      await api.markNotificationRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true, isRead: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {}
  };

  const handleMarkAllAsRead = async () => {
    try {
      await api.markAllNotificationsRead();
      setNotifications(prev => prev.map(n => ({ ...n, read: true, isRead: true })));
      setUnreadCount(0);
    } catch (err) {}
  };

  return (
    <div ref={drawerRef} style={{ position: 'relative' }}>
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          background: isOpen ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
          border: '1px solid var(--border-color)',
          borderRadius: '10px',
          padding: '8px 10px',
          color: 'var(--text-main)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          transition: 'all 0.2s ease'
        }}
        title="Notifications"
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span style={{
            position: 'absolute',
            top: '-4px',
            right: '-4px',
            background: '#ef4444',
            color: '#fff',
            fontSize: '0.7rem',
            fontWeight: 700,
            borderRadius: '10px',
            padding: '2px 6px',
            minWidth: '18px',
            textAlign: 'center',
            lineHeight: 1,
            boxShadow: '0 2px 6px rgba(239, 68, 68, 0.5)'
          }}>
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 10px)',
          right: 0,
          width: '360px',
          maxHeight: '480px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-xl)',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          {/* Top Bar */}
          <div style={{
            padding: '14px 18px',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: 'rgba(255, 255, 255, 0.02)'
          }}>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)' }}>
              Notifications
            </div>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllAsRead}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--primary-light)',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Mark all read
              </button>
            )}
          </div>

          {/* List Content */}
          <div style={{ flex: 1, overflowY: 'auto', maxHeight: '400px' }}>
            {notifications.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                No notifications yet.
              </div>
            ) : (
              notifications.map((n) => {
                const isUnread = !(n.read || n.isRead);
                return (
                  <div
                    key={n.id}
                    onClick={() => {
                      if (isUnread) handleMarkAsRead(n.id);
                      setIsOpen(false);
                    }}
                    style={{
                      padding: '12px 16px',
                      borderBottom: '1px solid var(--border-color)',
                      background: isUnread ? 'rgba(99, 102, 241, 0.06)' : 'transparent',
                      cursor: 'pointer',
                      transition: 'background 0.15s ease'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
                      <div style={{ fontSize: '0.88rem', fontWeight: isUnread ? 700 : 500, color: 'var(--text-main)' }}>
                        {n.title}
                      </div>
                      {isUnread && (
                        <span style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: 'var(--primary)',
                          flexShrink: 0
                        }} />
                      )}
                    </div>

                    <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.4, marginBottom: '6px' }}>
                      {n.message}
                    </div>

                    {n.linkUrl && (
                      <Link
                        to={n.linkUrl}
                        style={{
                          fontSize: '0.78rem',
                          color: 'var(--primary-light)',
                          textDecoration: 'none',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontWeight: 500
                        }}
                      >
                        Open View <ExternalLink size={12} />
                      </Link>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
