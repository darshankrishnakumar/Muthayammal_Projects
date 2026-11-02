import React, { useState, useEffect } from 'react';
import { Shield, Check, X, Users, FolderKanban, IndianRupee, FileText, Code2, AlertTriangle, Sparkles, CheckCircle2, Search, UserCheck } from 'lucide-react';
import api from '../utils/api';

const PERMISSION_GROUPS = [
  {
    category: 'User Management',
    icon: Users,
    color: '#6366f1',
    permissions: [
      { key: 'USER_VIEW', label: 'View Users Directory' },
      { key: 'USER_VIEW_PERSONAL_DATA', label: 'View Personal Details' },
      { key: 'USER_VIEW_REQUIREMENTS', label: 'View User Requirements' },
      { key: 'USER_VIEW_PROJECTS', label: 'View User Projects' },
      { key: 'USER_VIEW_ORDERS', label: 'View User Orders' },
      { key: 'USER_ONBOARD', label: 'Onboard / Bulk Create Users' },
      { key: 'USER_EDIT', label: 'Edit User Information' }
    ]
  },
  {
    category: 'Project & Workspace Oversight',
    icon: FolderKanban,
    color: '#059669',
    permissions: [
      { key: 'PROJECT_VIEW', label: 'View Projects Directory' },
      { key: 'PROJECT_VIEW_DETAILS', label: 'View Project Specifications' },
      { key: 'PROJECT_VIEW_FILES', label: 'View & Download Project Files' },
      { key: 'PROJECT_REVIEW', label: 'Review Deliverables' },
      { key: 'PROJECT_APPROVE', label: 'Approve Deliverables for Customer' }
    ]
  },
  {
    category: 'Payment & Orders Oversight',
    icon: IndianRupee,
    color: '#d97706',
    permissions: [
      { key: 'PAYMENT_VIEW', label: 'View Payments & Invoices' },
      { key: 'PAYMENT_VERIFY', label: 'Verify Payment Invoices' },
      { key: 'ORDER_VIEW', label: 'View Customer Orders' }
    ]
  }
];

const DATA_SCOPES = [
  { value: 'GLOBAL', label: 'Global (All Records)' },
  { value: 'USER_ASSIGNED', label: 'Assigned Users Only' },
  { value: 'PROJECT_ASSIGNED', label: 'Assigned Projects Only' },
  { value: 'ASSIGNED_ONLY', label: 'Assigned Scope Only' }
];

export default function AdminAccessControlModal({ admin, isOpen, onClose, onUpdated }) {
  const [permissions, setPermissions] = useState({});
  const [scopes, setScopes] = useState({});
  const [allUsers, setAllUsers] = useState([]);
  const [assignedUserIds, setAssignedUserIds] = useState([]);
  const [userSearch, setUserSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });
  const [activeTab, setActiveTab] = useState('permissions');

  useEffect(() => {
    if (isOpen && admin) {
      loadAdminData();
    }
  }, [isOpen, admin]);

  const loadAdminData = async () => {
    setLoading(true);
    setStatusMsg({ type: '', text: '' });
    try {
      // 1. Fetch current permissions
      const res = await api.getAdminPermissions(admin.id);
      const permMap = {};
      const scopeMap = {};
      (res || []).forEach(p => {
        permMap[p.permissionKey] = true;
        scopeMap[p.permissionKey] = p.dataScope || 'GLOBAL';
      });
      setPermissions(permMap);
      setScopes(scopeMap);

      // 2. Fetch regular users for scoping
      try {
        const usersRes = await api.getUsers();
        setAllUsers((usersRes || []).filter(u => u.role === 'USER'));
      } catch {
        setAllUsers([]);
      }

      // 3. Fetch assigned users
      try {
        const assignedRes = await api.getAssignedUsers(admin.id);
        setAssignedUserIds((assignedRes || []).map(a => a.assignedUser?.id || a.assignedUserId || a.id).filter(Boolean));
      } catch {
        setAssignedUserIds([]);
      }
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to load admin access data.' });
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePerm = (key) => {
    setPermissions(prev => ({ ...prev, [key]: !prev[key] }));
    if (!scopes[key]) {
      setScopes(prev => ({ ...prev, [key]: 'GLOBAL' }));
    }
  };

  const handleScopeChange = (key, scope) => {
    setScopes(prev => ({ ...prev, [key]: scope }));
  };

  const handleApplyPreset = async (presetName) => {
    setSaving(true);
    setStatusMsg({ type: '', text: '' });
    try {
      await api.applyAdminPreset(admin.id, presetName);
      setStatusMsg({ type: 'success', text: `Preset '${presetName}' successfully applied!` });
      await loadAdminData();
      if (onUpdated) onUpdated();
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to apply preset.' });
    } finally {
      setSaving(false);
    }
  };

  const handleSavePermissions = async () => {
    setSaving(true);
    setStatusMsg({ type: '', text: '' });
    try {
      const payload = Object.keys(permissions)
        .filter(k => permissions[k])
        .map(k => ({
          permissionKey: k,
          dataScope: scopes[k] || 'GLOBAL'
        }));

      await api.updateAdminPermissions(admin.id, payload);

      // Save user assignments if modified
      if (assignedUserIds) {
        await api.assignUsersToAdmin(admin.id, assignedUserIds);
      }

      setStatusMsg({ type: 'success', text: 'Admin permissions & scopes saved successfully!' });
      if (onUpdated) onUpdated();
      setTimeout(() => {
        onClose();
      }, 1200);
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to save permissions.' });
    } finally {
      setSaving(false);
    }
  };

  const toggleUserAssignment = (userId) => {
    setAssignedUserIds(prev => 
      prev.includes(userId) ? prev.filter(id => id !== userId) : [...prev, userId]
    );
  };

  const filteredUsers = allUsers.filter(u => 
    (u.fullName || '').toLowerCase().includes(userSearch.toLowerCase()) ||
    (u.email || '').toLowerCase().includes(userSearch.toLowerCase())
  );

  if (!isOpen || !admin) return null;

  const activePermsCount = Object.values(permissions).filter(Boolean).length;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px'
    }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '940px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 24px 48px rgba(0, 0, 0, 0.35)',
        overflow: 'hidden'
      }}>
        
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'var(--bg-card)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #4f46e5, #3b82f6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              boxShadow: '0 4px 12px rgba(79, 70, 229, 0.3)'
            }}>
              <Shield size={24} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
                Access Control & Permissions
              </h2>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '3px' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Configuring:</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
                  {admin.fullName || 'Admin User'}
                </span>
                <span style={{
                  fontSize: '0.75rem',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  background: 'var(--bg-secondary)',
                  color: 'var(--text-muted)',
                  border: '1px solid var(--border-color)',
                  fontFamily: 'monospace'
                }}>
                  {admin.email}
                </span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Quick Presets Bar */}
        <div style={{
          padding: '12px 24px',
          background: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          flexWrap: 'wrap'
        }}>
          <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sparkles size={15} color="#4f46e5" /> Quick Presets:
          </span>
          <button
            onClick={() => handleApplyPreset('COMPANY_ADMIN')}
            disabled={saving}
            className="btn btn-secondary btn-sm"
            style={{ fontSize: '0.78rem', padding: '5px 12px', borderRadius: '8px', fontWeight: 500 }}
          >
            Company Admin
          </button>
          <button
            onClick={() => handleApplyPreset('ONBOARDING_ADMIN')}
            disabled={saving}
            className="btn btn-secondary btn-sm"
            style={{ fontSize: '0.78rem', padding: '5px 12px', borderRadius: '8px', fontWeight: 500 }}
          >
            Onboarding Admin (User-Scoped)
          </button>
          <button
            onClick={() => handleApplyPreset('PROJECT_REVIEWER')}
            disabled={saving}
            className="btn btn-secondary btn-sm"
            style={{ fontSize: '0.78rem', padding: '5px 12px', borderRadius: '8px', fontWeight: 500 }}
          >
            Project Reviewer (Project-Scoped)
          </button>
          <button
            onClick={() => handleApplyPreset('FULL_ADMIN')}
            disabled={saving}
            className="btn btn-primary btn-sm"
            style={{ fontSize: '0.78rem', padding: '5px 12px', borderRadius: '8px', fontWeight: 600 }}
          >
            Full Admin (Global)
          </button>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          gap: '24px',
          padding: '0 24px',
          borderBottom: '1px solid var(--border-color)',
          background: 'var(--bg-card)'
        }}>
          <button
            onClick={() => setActiveTab('permissions')}
            style={{
              padding: '14px 0',
              border: 'none',
              background: 'transparent',
              color: activeTab === 'permissions' ? '#4f46e5' : 'var(--text-muted)',
              borderBottom: activeTab === 'permissions' ? '3px solid #4f46e5' : '3px solid transparent',
              fontWeight: activeTab === 'permissions' ? 700 : 500,
              fontSize: '0.92rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Shield size={16} />
            Permission Matrix & Scopes
          </button>
          <button
            onClick={() => setActiveTab('users')}
            style={{
              padding: '14px 0',
              border: 'none',
              background: 'transparent',
              color: activeTab === 'users' ? '#4f46e5' : 'var(--text-muted)',
              borderBottom: activeTab === 'users' ? '3px solid #4f46e5' : '3px solid transparent',
              fontWeight: activeTab === 'users' ? 700 : 500,
              fontSize: '0.92rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <UserCheck size={16} />
            Assigned Users
            <span style={{
              fontSize: '0.75rem',
              padding: '2px 8px',
              borderRadius: '10px',
              background: assignedUserIds.length > 0 ? '#4f46e5' : 'var(--bg-secondary)',
              color: assignedUserIds.length > 0 ? '#ffffff' : 'var(--text-muted)',
              fontWeight: 600
            }}>
              {assignedUserIds.length}
            </span>
          </button>
        </div>

        {/* Status Alerts */}
        {statusMsg.text && (
          <div style={{
            margin: '14px 24px 0 24px',
            padding: '12px 16px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '0.88rem',
            fontWeight: 500,
            background: statusMsg.type === 'error' ? 'rgba(239, 68, 68, 0.12)' : 'rgba(16, 185, 129, 0.12)',
            color: statusMsg.type === 'error' ? '#dc2626' : '#059669',
            border: `1px solid ${statusMsg.type === 'error' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`
          }}>
            {statusMsg.type === 'error' ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
            <span>{statusMsg.text}</span>
          </div>
        )}

        {/* Modal Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-muted)' }}>
              Loading permissions and scoping rules...
            </div>
          ) : activeTab === 'permissions' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {PERMISSION_GROUPS.map((group) => {
                const Icon = group.icon;
                return (
                  <div key={group.category} style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '12px',
                    padding: '16px 20px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
                      <div style={{
                        padding: '6px',
                        borderRadius: '8px',
                        background: `${group.color}15`,
                        color: group.color,
                        display: 'flex'
                      }}>
                        <Icon size={18} />
                      </div>
                      <h3 style={{ margin: 0, fontSize: '0.98rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        {group.category}
                      </h3>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '10px' }}>
                      {group.permissions.map((p) => {
                        const isChecked = !!permissions[p.key];
                        return (
                          <div key={p.key} style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '10px 14px',
                            background: isChecked ? 'rgba(79, 70, 229, 0.08)' : 'var(--bg-secondary)',
                            border: `1px solid ${isChecked ? 'rgba(79, 70, 229, 0.35)' : 'var(--border-color)'}`,
                            borderRadius: '10px',
                            transition: 'all 0.15s ease'
                          }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', flex: 1, marginRight: '10px' }}>
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => handleTogglePerm(p.key)}
                                style={{
                                  accentColor: '#4f46e5',
                                  width: '17px',
                                  height: '17px',
                                  cursor: 'pointer'
                                }}
                              />
                              <div>
                                <div style={{
                                  fontSize: '0.88rem',
                                  fontWeight: isChecked ? 600 : 500,
                                  color: isChecked ? 'var(--text-main)' : 'var(--text-muted)'
                                }}>
                                  {p.label}
                                </div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'monospace', marginTop: '1px' }}>
                                  {p.key}
                                </div>
                              </div>
                            </label>

                            {isChecked && (
                              <select
                                value={scopes[p.key] || 'GLOBAL'}
                                onChange={(e) => handleScopeChange(p.key, e.target.value)}
                                style={{
                                  padding: '5px 10px',
                                  fontSize: '0.78rem',
                                  background: 'var(--bg-card)',
                                  border: '1px solid #4f46e5',
                                  borderRadius: '6px',
                                  color: 'var(--text-main)',
                                  fontWeight: 600,
                                  cursor: 'pointer',
                                  outline: 'none'
                                }}
                              >
                                {DATA_SCOPES.map(s => (
                                  <option key={s.value} value={s.value} style={{ background: 'var(--bg-card)', color: 'var(--text-main)' }}>
                                    {s.label}
                                  </option>
                                ))}
                              </select>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '16px',
                flexWrap: 'wrap',
                gap: '12px'
              }}>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: '0 0 4px 0', color: 'var(--text-main)' }}>
                    Customer Account Scoping
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                    Select customer accounts that <strong style={{ color: 'var(--text-main)' }}>{admin.fullName || admin.email}</strong> is authorized to manage under <code>USER_ASSIGNED</code> scope.
                  </p>
                </div>

                <div style={{ position: 'relative', minWidth: '240px' }}>
                  <Search size={16} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }} />
                  <input
                    type="text"
                    value={userSearch}
                    onChange={(e) => setUserSearch(e.target.value)}
                    placeholder="Search users..."
                    style={{
                      width: '100%',
                      padding: '8px 12px 8px 34px',
                      fontSize: '0.85rem',
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '8px',
                      color: 'var(--text-main)',
                      outline: 'none'
                    }}
                  />
                </div>
              </div>

              {filteredUsers.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)', background: 'var(--bg-secondary)', borderRadius: '12px' }}>
                  {allUsers.length === 0 ? 'No customer user accounts found in database.' : 'No users match your search.'}
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
                  {filteredUsers.map((u) => {
                    const isAssigned = assignedUserIds.includes(u.id);
                    return (
                      <div
                        key={u.id}
                        onClick={() => toggleUserAssignment(u.id)}
                        style={{
                          padding: '12px 14px',
                          borderRadius: '10px',
                          background: isAssigned ? 'rgba(79, 70, 229, 0.1)' : 'var(--bg-secondary)',
                          border: `1px solid ${isAssigned ? '#4f46e5' : 'var(--border-color)'}`,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          transition: 'all 0.15s ease'
                        }}
                      >
                        <div>
                          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>
                            {u.fullName || 'User #' + u.id}
                          </div>
                          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                            {u.email}
                          </div>
                        </div>
                        <div style={{
                          width: '24px',
                          height: '24px',
                          borderRadius: '50%',
                          background: isAssigned ? '#4f46e5' : 'var(--bg-card)',
                          border: `1px solid ${isAssigned ? '#4f46e5' : 'var(--border-color)'}`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#ffffff'
                        }}>
                          {isAssigned && <Check size={14} />}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'var(--bg-card)'
        }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Active Permissions: <strong style={{ color: '#4f46e5', fontWeight: 700 }}>{activePermsCount}</strong>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={onClose}
              disabled={saving}
              className="btn btn-secondary"
              style={{ padding: '8px 18px', borderRadius: '8px' }}
            >
              Cancel
            </button>
            <button
              onClick={handleSavePermissions}
              disabled={saving}
              className="btn btn-primary"
              style={{ padding: '8px 20px', borderRadius: '8px', fontWeight: 600 }}
            >
              {saving ? 'Saving...' : 'Save Permissions & Scopes'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

