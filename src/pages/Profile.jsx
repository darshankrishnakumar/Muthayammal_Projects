import { useState } from 'react';
import { KeyRound, Save } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { PageHeader, Card, Avatar, Badge, StatusBadge, Field, useToast } from '../components/ui';
import { ROLE_LABELS, date } from '../utils/format';

const MIN_PASSWORD = 8;

const Profile = () => {
  const { user, refreshUser } = useAuth();
  const { notify } = useToast();

  const [fullName, setFullName] = useState(user?.fullName || '');
  const [mobileNumber, setMobileNumber] = useState(user?.mobileNumber || '');
  const [savingDetails, setSavingDetails] = useState(false);
  const [detailsError, setDetailsError] = useState('');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [savingPassword, setSavingPassword] = useState(false);
  const [passwordError, setPasswordError] = useState('');

  if (!user) return null;

  const detailsChanged = fullName.trim() !== (user.fullName || '') || mobileNumber.trim() !== (user.mobileNumber || '');

  const handleSaveDetails = async (e) => {
    e.preventDefault();
    setDetailsError('');
    if (!fullName.trim()) {
      setDetailsError('Enter your full name.');
      return;
    }
    setSavingDetails(true);
    try {
      await api.updateUser(user.id, { fullName: fullName.trim(), mobileNumber: mobileNumber.trim() });
      const fresh = await refreshUser();
      setFullName(fresh?.fullName || fullName.trim());
      setMobileNumber(fresh?.mobileNumber || '');
      notify('Profile updated');
    } catch (err) {
      setDetailsError(err.message);
    } finally {
      setSavingDetails(false);
    }
  };

  const handleSavePassword = async (e) => {
    e.preventDefault();
    setPasswordError('');
    if (password.length < MIN_PASSWORD) {
      setPasswordError(`Use at least ${MIN_PASSWORD} characters.`);
      return;
    }
    if (password !== confirmPassword) {
      setPasswordError('The passwords do not match.');
      return;
    }
    setSavingPassword(true);
    try {
      await api.updateUser(user.id, { password });
      await refreshUser();
      setPassword('');
      setConfirmPassword('');
      notify('Password changed');
    } catch (err) {
      setPasswordError(err.message);
    } finally {
      setSavingPassword(false);
    }
  };

  return (
    <>
      <PageHeader title="Profile" description="Manage your personal details and password." />

      <div className="layout-split">
        <div className="space-y-6">
          <Card title="Personal details" subtitle="Your name and contact number are visible to administrators.">
            <form onSubmit={handleSaveDetails} noValidate>
              {detailsError && <div className="alert alert-danger">{detailsError}</div>}
              <div className="form-grid">
                <Field label="Full name" htmlFor="profile-name">
                  <input
                    id="profile-name"
                    className="input"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    disabled={savingDetails}
                    autoComplete="name"
                    required
                  />
                </Field>
                <Field label="Mobile number" htmlFor="profile-mobile">
                  <input
                    id="profile-mobile"
                    className="input"
                    type="tel"
                    value={mobileNumber}
                    onChange={(e) => setMobileNumber(e.target.value)}
                    disabled={savingDetails}
                    autoComplete="tel"
                    placeholder="Optional"
                  />
                </Field>
                <Field label="Email" hint="Contact your administrator to change your email." className="span-2" htmlFor="profile-email">
                  <input id="profile-email" className="input" value={user.email || ''} disabled readOnly />
                </Field>
              </div>
              <div className="flex justify-end">
                <button type="submit" className="btn btn-primary" disabled={savingDetails || !detailsChanged}>
                  {savingDetails ? <span className="spinner" /> : <Save aria-hidden="true" />}
                  Save changes
                </button>
              </div>
            </form>
          </Card>

          <Card title="Password" subtitle={`Choose a new password with at least ${MIN_PASSWORD} characters.`}>
            <form onSubmit={handleSavePassword} noValidate>
              {passwordError && <div className="alert alert-danger">{passwordError}</div>}
              <div className="form-grid">
                <Field label="New password" htmlFor="profile-password">
                  <input
                    id="profile-password"
                    className="input"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={savingPassword}
                    autoComplete="new-password"
                    minLength={MIN_PASSWORD}
                  />
                </Field>
                <Field label="Confirm new password" htmlFor="profile-password-confirm">
                  <input
                    id="profile-password-confirm"
                    className="input"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={savingPassword}
                    autoComplete="new-password"
                  />
                </Field>
              </div>
              <div className="flex justify-end">
                <button type="submit" className="btn btn-secondary" disabled={savingPassword || !password}>
                  {savingPassword ? <span className="spinner" /> : <KeyRound aria-hidden="true" />}
                  Update password
                </button>
              </div>
            </form>
          </Card>
        </div>

        <Card>
          <div className="flex items-center gap-3 mb-4">
            <Avatar name={user.fullName} size="lg" />
            <div className="min-w-0">
              <div className="font-semibold truncate">{user.fullName}</div>
              <div className="text-sm text-muted truncate">{user.email}</div>
            </div>
          </div>
          <dl className="kv" style={{ gridTemplateColumns: '96px 1fr' }}>
            <dt>Role</dt>
            <dd><Badge tone="accent">{ROLE_LABELS[user.role] || user.role}</Badge></dd>
            <dt>College</dt>
            <dd>
              {user.college ? (
                <>
                  {user.college.name}
                  {user.college.code && <span className="text-subtle"> · {user.college.code}</span>}
                </>
              ) : (
                <span className="text-subtle">Not applicable</span>
              )}
            </dd>
            <dt>Status</dt>
            <dd><StatusBadge status={user.status || 'ACTIVE'} /></dd>
            <dt>Member since</dt>
            <dd>{date(user.createdAt)}</dd>
            <dt>Account ID</dt>
            <dd className="font-mono">#{user.id}</dd>
          </dl>
          <p className="text-xs text-subtle mt-4">Your role and college are managed by your administrator.</p>
        </Card>
      </div>
    </>
  );
};

export default Profile;
