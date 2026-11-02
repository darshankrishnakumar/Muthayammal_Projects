import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  User, 
  Mail, 
  KeyRound, 
  CheckCircle2, 
  AlertTriangle,
  ShieldCheck,
  Building,
  Calendar,
  Lock,
  BadgeCheck,
  Save,
  Shield
} from 'lucide-react';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [fullName, setFullName] = useState(user?.fullName || '');
  const [email, setEmail] = useState(user?.email || '');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('general');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!fullName || !email) {
      setError('Name and Email fields are required.');
      return;
    }

    if (password && password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const payload = { fullName, email };
      if (password) {
        payload.password = password;
      }
      
      await updateProfile(payload);
      setSuccess('Profile updated successfully.');
      setPassword('');
      setConfirmPassword('');
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      setError(err.message || 'Failed to update profile settings.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-container text-left" style={{ maxWidth: '1000px', margin: '0 auto' }}>
      {/* Alert Notifications */}
      {success && (
        <div className="alert alert-success card flex items-center gap-3" style={{ marginBottom: '20px' }}>
          <CheckCircle2 size={18} />
          <span style={{ fontWeight: 500 }}>{success}</span>
        </div>
      )}
      {error && (
        <div className="alert alert-danger card flex items-center gap-3" style={{ marginBottom: '20px' }}>
          <AlertTriangle size={18} />
          <span style={{ fontWeight: 500 }}>{error}</span>
        </div>
      )}

      {/* Top Profile Header Hero Bar */}
      <div className="card profile-hero-card" style={{ padding: '20px 28px', marginBottom: '24px' }}>
        <div className="flex items-center justify-between gap-4" style={{ flexWrap: 'nowrap' }}>
          <div className="flex items-center gap-4" style={{ minWidth: 0, flex: 1 }}>
            <div className="profile-hero-avatar" style={{ flexShrink: 0 }}>
              {user?.fullName ? user.fullName.substring(0, 2).toUpperCase() : 'US'}
            </div>
            <div style={{ minWidth: 0 }}>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="font-display" style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, whiteSpace: 'nowrap' }}>{user?.fullName}</h2>
                <span className={`badge ${
                  user?.role === 'SUPER_ADMIN' ? 'badge-danger' : 
                  user?.role === 'ADMIN' ? 'badge-primary' : 'badge-success'
                }`} style={{ fontSize: '0.7rem', padding: '3px 10px' }}>
                  {user?.role ? user.role.replace('_', ' ') : 'USER'}
                </span>
              </div>
              <p className="text-muted" style={{ fontSize: '0.85rem', marginTop: '3px', margin: 0 }}>{user?.email}</p>
            </div>
          </div>

          <div className="flex items-center gap-6" style={{ flexShrink: 0, paddingRight: '4px' }}>
            <div className="flex flex-col items-end" style={{ minWidth: '90px' }}>
              <span className="text-muted" style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px', fontWeight: 600, whiteSpace: 'nowrap' }}>
                Account ID
              </span>
              <strong className="font-mono text-primary" style={{ fontSize: '1rem', lineHeight: '1.2' }}>
                #{user?.id}
              </strong>
            </div>

            <div className="flex flex-col items-end" style={{ borderLeft: '1px solid var(--border-color)', paddingLeft: '24px', minWidth: '90px' }}>
              <span className="text-muted" style={{ fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px', fontWeight: 600, whiteSpace: 'nowrap' }}>
                Status
              </span>
              <span className="badge badge-success" style={{ fontSize: '0.7rem', padding: '3px 10px', marginTop: '2px' }}>
                ACTIVE
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Settings Card */}
      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        {/* Sub-navigation Tabs Bar */}
        <div className="profile-tabs-bar flex" style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', padding: '0 24px' }}>
          <button 
            className={`tab-btn flex items-center gap-2 ${activeTab === 'general' ? 'active' : ''}`}
            onClick={() => setActiveTab('general')}
          >
            <User size={15} />
            <span>General Information</span>
          </button>
          <button 
            className={`tab-btn flex items-center gap-2 ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            <Lock size={15} />
            <span>Security & Password</span>
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} style={{ padding: '32px' }}>
          {activeTab === 'general' && (
            <div className="tab-content flex flex-col gap-6">
              <div>
                <h4 className="font-display" style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '4px' }}>Personal Details</h4>
                <p className="text-muted" style={{ fontSize: '0.85rem' }}>Update your account display name and email address.</p>
              </div>

              <div className="grid grid-cols-2 gap-5">
                <div className="form-group mb-0">
                  <label className="form-label">
                    <User size={14} className="text-muted" />
                    <span>Full Name</span>
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    disabled={loading}
                    required
                    placeholder="Enter full name"
                  />
                </div>

                <div className="form-group mb-0">
                  <label className="form-label">
                    <Mail size={14} className="text-muted" />
                    <span>Email Address</span>
                  </label>
                  <input
                    type="email"
                    className="form-control"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={loading}
                    required
                    placeholder="Enter email address"
                  />
                </div>
              </div>

              <div className="info-box flex items-center gap-3" style={{ background: 'var(--primary-light)', padding: '16px 20px', borderRadius: 'var(--radius-md)', border: '1px solid hsla(220, 90%, 56%, 0.2)' }}>
                <ShieldCheck size={20} className="text-primary" />
                <div>
                  <h5 style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--primary)' }}>Role Authorization</h5>
                  <p className="text-muted" style={{ fontSize: '0.8rem', margin: 0 }}>
                    Your role <strong style={{ color: 'var(--text-main)' }}>{user?.role}</strong> grants automatic access to authorized project folders.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="tab-content flex flex-col gap-6">
              <div>
                <h4 className="font-display" style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '4px' }}>Change Password</h4>
                <p className="text-muted" style={{ fontSize: '0.85rem' }}>Set a new password to keep your account safe.</p>
              </div>

              <div className="grid grid-cols-2 gap-5">
                <div className="form-group mb-0">
                  <label className="form-label">
                    <KeyRound size={14} className="text-muted" />
                    <span>New Password</span>
                  </label>
                  <input
                    type="password"
                    className="form-control"
                    placeholder="Enter new password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                  />
                </div>

                <div className="form-group mb-0">
                  <label className="form-label">
                    <KeyRound size={14} className="text-muted" />
                    <span>Confirm New Password</span>
                  </label>
                  <input
                    type="password"
                    className="form-control"
                    placeholder="Re-enter new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Action Footer */}
          <div className="flex justify-end items-center" style={{ marginTop: '32px', paddingTop: '20px', borderTop: '1px solid var(--border-color)' }}>
            <button type="submit" className="btn btn-primary flex items-center gap-2" disabled={loading}>
              <Save size={16} />
              <span>{loading ? 'Saving Changes...' : 'Save Profile Changes'}</span>
            </button>
          </div>
        </form>
      </div>

      <style>{`
        .profile-hero-avatar {
          width: 64px;
          height: 64px;
          border-radius: var(--radius-lg);
          background: linear-gradient(135deg, var(--primary) 0%, hsl(220, 90%, 45%) 100%);
          color: #ffffff;
          font-family: var(--font-display);
          font-weight: 700;
          font-size: 1.5rem;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 14px hsla(220, 90%, 56%, 0.25);
        }

        .tab-btn {
          padding: 16px 20px;
          font-size: 0.9rem;
          font-weight: 600;
          color: var(--text-muted);
          border: none;
          background: transparent;
          border-bottom: 2px solid transparent;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .tab-btn:hover {
          color: var(--text-main);
        }

        .tab-btn.active {
          color: var(--primary);
          border-bottom-color: var(--primary);
          background-color: var(--bg-card);
        }

        .alert-success {
          background-color: var(--success-light);
          color: var(--success);
          border: 1px solid hsla(158, 70%, 40%, 0.2);
          padding: 12px 18px;
        }

        .alert-danger {
          background-color: var(--error-light);
          color: var(--error);
          border: 1px solid hsla(350, 84%, 55%, 0.2);
          padding: 12px 18px;
        }
      `}</style>
    </div>
  );
};

export default Profile;
