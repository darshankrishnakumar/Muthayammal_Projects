import { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { isMockMode, getApiBaseUrl, setCustomApiUrl, ACTIVE_LIVE_TUNNEL_URL, FALLBACK_LOCALTUNNEL_URL } from '../utils/api';
import { Mail, Lock, ShieldAlert, KeyRound, Server, Settings2, Check, RefreshCw, CheckCircle2, Zap } from 'lucide-react';

const Login = () => {
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [currentServer, setCurrentServer] = useState(getApiBaseUrl());
  const [showServerConfig, setShowServerConfig] = useState(false);
  const [serverInput, setServerInput] = useState(getApiBaseUrl());
  const [serverSavedMsg, setServerSavedMsg] = useState('');

  const { login, user } = useAuth();
  const navigate = useNavigate();
  const mockActive = isMockMode();

  // Sanitize cached URL on initial load
  useEffect(() => {
    const active = getApiBaseUrl();
    setCurrentServer(active);
    setServerInput(active);
  }, []);

  // Handle redirected registration params
  useEffect(() => {
    const registered = searchParams.get('registered');
    const paramEmail = searchParams.get('email');
    if (registered === 'true') {
      if (paramEmail) setEmail(paramEmail);
      setSuccessMsg('Account created successfully! Please enter your password to sign in.');
    }
  }, [searchParams]);

  // If already authenticated, redirect to dashboard immediately
  useEffect(() => {
    if (user) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, navigate]);

  const handleSaveServer = (e) => {
    e.preventDefault();
    if (!serverInput || !serverInput.trim()) {
      setCustomApiUrl('');
    } else {
      setCustomApiUrl(serverInput.trim());
    }
    const updated = getApiBaseUrl();
    setCurrentServer(updated);
    setServerSavedMsg('Server URL updated!');
    setTimeout(() => setServerSavedMsg(''), 3000);
    setShowServerConfig(false);
  };

  const handleResetServer = () => {
    setCustomApiUrl('');
    localStorage.removeItem('CUSTOM_API_URL');
    const defaultUrl = ACTIVE_LIVE_TUNNEL_URL;
    setServerInput(defaultUrl);
    setCurrentServer(getApiBaseUrl());
    setServerSavedMsg('Restored active live Cloudflare gateway!');
    setTimeout(() => setServerSavedMsg(''), 3000);
  };

  const handleUseCloudflare = () => {
    setCustomApiUrl(ACTIVE_LIVE_TUNNEL_URL);
    setServerInput(ACTIVE_LIVE_TUNNEL_URL);
    setCurrentServer(getApiBaseUrl());
    setServerSavedMsg('Connected to Cloudflare Live Gateway!');
    setShowServerConfig(false);
    setErrorMsg('');
    setTimeout(() => setServerSavedMsg(''), 3000);
  };

  const handleUseLocaltunnel = () => {
    setCustomApiUrl(FALLBACK_LOCALTUNNEL_URL);
    setServerInput(FALLBACK_LOCALTUNNEL_URL);
    setCurrentServer(getApiBaseUrl());
    setServerSavedMsg('Connected to Localtunnel Gateway!');
    setShowServerConfig(false);
    setErrorMsg('');
    setTimeout(() => setServerSavedMsg(''), 3000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMsg('Please enter both email and password.');
      return;
    }

    setLoading(true);
    setErrorMsg('');
    try {
      const loggedUser = await login(email, password);
      if (loggedUser) {
        navigate('/dashboard', { replace: true });
      }
    } catch (err) {
      const msg = err.message || 'Authentication failed. Please verify credentials.';
      setErrorMsg(msg);
      // Auto-open server config on connection failures
      if (msg.includes('Failed to fetch') || msg.includes('Network') || msg.includes('connect') || msg.includes('ERR_')) {
        setShowServerConfig(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (role) => {
    if (role === 'super') {
      setEmail('superadmin@academic.com');
      setPassword('Superadmin123!');
    } else if (role === 'admin') {
      setEmail('admin@academic.com');
      setPassword('Admin123!');
    } else if (role === 'dev' || role === 'developer') {
      setEmail('developer@academic.com');
      setPassword('Dev12345!');
    } else if (role === 'user') {
      setEmail('user@academic.com');
      setPassword('User123!');
    }
  };

  return (
    <div className="login-wrapper">
      <div className="login-card card">
        <div className="login-header">
          <div className="login-logo">A</div>
          <h2>Academic Portal</h2>
          <p className="text-muted">Enter credentials to access the secure workspace</p>
        </div>

        {errorMsg && (
          <div className="login-error-alert" style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-start', textAlign: 'left' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShieldAlert size={16} style={{ flexShrink: 0 }} />
              <span>{errorMsg}</span>
            </div>
            {(errorMsg.includes('Failed to fetch') || errorMsg.includes('Network') || errorMsg.includes('ERR_') || errorMsg.includes('unreachable') || errorMsg.includes('connect')) && (
              <div style={{ display: 'flex', gap: '6px', width: '100%', marginTop: '4px' }}>
                <button
                  type="button"
                  onClick={handleUseCloudflare}
                  className="btn btn-primary"
                  style={{ fontSize: '0.75rem', padding: '5px 10px', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px' }}
                >
                  <Zap size={12} />
                  <span>Connect Live Gateway</span>
                </button>
                <button
                  type="button"
                  onClick={handleUseLocaltunnel}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.75rem', padding: '5px 10px', flex: 1 }}
                >
                  Localtunnel
                </button>
              </div>
            )}
          </div>
        )}

        {successMsg && (
          <div className="login-success-alert" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 14px', backgroundColor: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#34d399', borderRadius: 'var(--radius-md)', marginBottom: '16px', fontSize: '0.86rem' }}>
            <CheckCircle2 size={16} style={{ flexShrink: 0 }} />
            <span>{successMsg}</span>
          </div>
        )}

        {serverSavedMsg && (
          <div className="login-success-alert" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', backgroundColor: 'var(--success-light)', color: 'var(--success)', borderRadius: 'var(--radius-md)', marginBottom: '16px', fontSize: '0.85rem' }}>
            <Check size={16} />
            <span>{serverSavedMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label">
              <Mail size={14} />
              <span>Email Address</span>
            </label>
            <input
              type="email"
              className="form-control"
              placeholder="e.g. name@academic.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <Lock size={14} />
              <span>Password</span>
            </label>
            <input
              type="password"
              className="form-control"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary w-full mt-4" disabled={loading}>
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>

          {/* New User Register CTA */}
          <div style={{ marginTop: '18px', textAlign: 'center', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
            <span>New User? </span>
            <Link 
              to="/register" 
              style={{ 
                color: 'var(--primary)', 
                fontWeight: 600, 
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <strong>Register Now</strong> →
            </Link>
          </div>
        </form>

        {/* Quick Credentials Helper Buttons */}
        <div className="quick-login-section">
          <div className="quick-login-title">
            <KeyRound size={12} className="text-primary" />
            <span>One-Click Role Login</span>
          </div>
          <div className="quick-login-buttons" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px' }}>
            <button 
              type="button"
              onClick={() => handleQuickLogin('super')} 
              className="btn btn-secondary quick-btn"
              disabled={loading}
              style={{ padding: '6px 4px', fontSize: '0.78rem' }}
            >
              Super Admin
            </button>
            <button 
              type="button"
              onClick={() => handleQuickLogin('admin')} 
              className="btn btn-secondary quick-btn"
              disabled={loading}
              style={{ padding: '6px 4px', fontSize: '0.78rem' }}
            >
              Admin
            </button>
            <button 
              type="button"
              onClick={() => handleQuickLogin('dev')} 
              className="btn btn-secondary quick-btn"
              disabled={loading}
              style={{ padding: '6px 4px', fontSize: '0.78rem' }}
            >
              Developer
            </button>
            <button 
              type="button"
              onClick={() => handleQuickLogin('user')} 
              className="btn btn-secondary quick-btn"
              disabled={loading}
              style={{ padding: '6px 4px', fontSize: '0.78rem' }}
            >
              User
            </button>
          </div>
        </div>

        {/* Live Backend Connection Indicator & Switcher */}
        <div className="server-config-section" style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-color)', fontSize: '0.8rem', textAlign: 'left' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              <Server size={14} className="text-primary" />
              <span>Server:</span>
              <code style={{ fontSize: '0.75rem', backgroundColor: 'var(--bg-main)', padding: '2px 6px', borderRadius: '4px', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'inline-block' }}>
                {currentServer}
              </code>
            </div>
            <button 
              type="button" 
              onClick={() => setShowServerConfig(!showServerConfig)}
              style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontSize: '0.78rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '3px' }}
            >
              <Settings2 size={12} />
              <span>{showServerConfig ? 'Close' : 'Configure'}</span>
            </button>
          </div>

          {showServerConfig && (
            <div style={{ marginTop: '12px', padding: '12px', backgroundColor: 'var(--bg-main)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, marginBottom: '6px', color: 'var(--text-main)' }}>
                Target Backend URL (e.g. Tunnel or Localhost):
              </label>
              <input 
                type="text" 
                className="form-control" 
                style={{ fontSize: '0.8rem', padding: '6px 10px', marginBottom: '8px' }}
                value={serverInput}
                onChange={(e) => setServerInput(e.target.value)}
                placeholder="https://people-comparative-desirable-inform.trycloudflare.com"
              />

              {/* 1-Click Gateway Presets */}
              <div style={{ display: 'flex', gap: '4px', marginBottom: '10px', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={handleUseCloudflare}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.72rem', padding: '3px 8px', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                >
                  <Zap size={10} className="text-primary" />
                  <span>Cloudflare Tunnel</span>
                </button>
                <button
                  type="button"
                  onClick={handleUseLocaltunnel}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                >
                  Localtunnel
                </button>
              </div>

              <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                <button 
                  type="button" 
                  onClick={handleResetServer} 
                  className="btn btn-secondary" 
                  style={{ fontSize: '0.75rem', padding: '4px 10px' }}
                >
                  <RefreshCw size={11} />
                  <span>Reset</span>
                </button>
                <button 
                  type="button" 
                  onClick={handleSaveServer} 
                  className="btn btn-primary" 
                  style={{ fontSize: '0.75rem', padding: '4px 12px' }}
                >
                  Save URL
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .login-wrapper {
          min-height: 100vh;
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, hsl(210, 80%, 94%) 0%, hsl(215, 60%, 98%) 100%);
          padding: 20px;
        }

        .login-card {
          width: 100%;
          max-width: 440px;
          padding: 40px;
          text-align: center;
          border-radius: var(--radius-lg);
          background-color: rgba(255, 255, 255, 0.85);
          backdrop-filter: blur(10px);
          box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.5);
        }

        .login-logo {
          width: 50px;
          height: 50px;
          background-color: var(--primary);
          color: white;
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: var(--font-display);
          font-weight: 700;
          font-size: 1.6rem;
          margin: 0 auto 16px;
          box-shadow: 0 6px 16px hsla(215, 95%, 55%, 0.3);
        }

        .login-header h2 {
          font-family: var(--font-display);
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--text-main);
          margin-bottom: 6px;
        }

        .login-header p {
          font-size: 0.85rem;
          margin-bottom: 24px;
        }

        .login-error-alert {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px 16px;
          background-color: var(--error-light);
          color: var(--error);
          border-radius: var(--radius-md);
          margin-bottom: 24px;
          font-size: 0.85rem;
          text-align: left;
          border: 1px solid hsla(350, 80%, 55%, 0.1);
        }

        .login-form {
          display: flex;
          flex-direction: column;
        }

        .quick-login-section {
          margin-top: 32px;
          padding-top: 24px;
          border-top: 1px solid var(--border-color);
        }

        .quick-login-title {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 12px;
        }

        .quick-login-buttons {
          display: flex;
          gap: 8px;
          justify-content: center;
        }

        .quick-btn {
          font-size: 0.8rem;
          padding: 8px 12px;
          border-radius: var(--radius-sm);
        }
      `}</style>
    </div>
  );
};

export default Login;
