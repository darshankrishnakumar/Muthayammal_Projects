import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api, getApiBaseUrl, setCustomApiUrl } from '../utils/api';
import { 
  UserPlus, 
  Mail, 
  Lock, 
  User, 
  Phone, 
  Building, 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  Sparkles,
  Eye,
  EyeOff,
  Server,
  Settings2,
  Check
} from 'lucide-react';

const Register = () => {
  const navigate = useNavigate();

  // Form fields
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [mobileNumber, setMobileNumber] = useState('');
  const [organization, setOrganization] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // UI state
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Server configuration
  const [currentServer, setCurrentServer] = useState(getApiBaseUrl());
  const [showServerConfig, setShowServerConfig] = useState(false);
  const [serverInput, setServerInput] = useState(getApiBaseUrl());
  const [serverSavedMsg, setServerSavedMsg] = useState('');

  const handleSaveServer = (e) => {
    e.preventDefault();
    if (serverInput.trim()) {
      setCustomApiUrl(serverInput.trim());
      setCurrentServer(serverInput.trim());
      setServerSavedMsg('Backend server URL saved successfully!');
      setTimeout(() => {
        setServerSavedMsg('');
        setShowServerConfig(false);
      }, 1500);
    }
  };

  const handleResetServer = () => {
    setCustomApiUrl(null);
    setCurrentServer(getApiBaseUrl());
    setServerInput(getApiBaseUrl());
    setServerSavedMsg('Reset back to default tunnel URL.');
    setTimeout(() => {
      setServerSavedMsg('');
      setShowServerConfig(false);
    }, 1500);
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    // Full name validation
    if (!fullName.trim()) {
      setErrorMsg('Full Name is required.');
      return;
    }

    // Email validation
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setErrorMsg('Please enter a valid email address.');
      return;
    }

    // Indian Mobile Number Validation: 10-digits starting with 6, 7, 8, or 9 (with optional +91 or 0 prefix)
    const cleanedMobile = mobileNumber.trim().replace(/[\s\-()]/g, '');
    const indianMobileRegex = /^(?:\+91|0)?[6-9]\d{9}$/;
    if (!cleanedMobile || !indianMobileRegex.test(cleanedMobile)) {
      setErrorMsg('Please enter a valid 10-digit Indian mobile number (e.g. 9342666379 or +91 9342666379).');
      return;
    }

    // Password validations
    if (!password || password.length < 8) {
      setErrorMsg('Password must be at least 8 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg('Passwords do not match. Please verify.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.register({
        fullName: fullName.trim(),
        email: email.trim().toLowerCase(),
        mobileNumber: mobileNumber.trim(),
        organization: organization.trim(),
        password,
        confirmPassword
      });

      setSuccessMsg(res.message || 'Account registered successfully! Redirecting to login...');
      
      // Direct navigation to Login page with pre-filled email
      setTimeout(() => {
        navigate(`/login?registered=true&email=${encodeURIComponent(email.trim().toLowerCase())}`, { replace: true });
      }, 1200);
    } catch (err) {
      const msg = err.message || 'Registration failed. Please check details and try again.';
      setErrorMsg(msg);
      // Auto-open server config on connection issues
      if (msg.includes('Failed to fetch') || msg.includes('Network') || msg.includes('connect')) {
        setShowServerConfig(true);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(ellipse at top, rgba(99, 102, 241, 0.15), transparent 70%), var(--bg-main)',
      padding: '40px 20px',
      fontFamily: 'var(--font-sans)'
    }}>
      <div style={{ width: '100%', maxWidth: '520px' }}>
        
        {/* Header Branding */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '56px',
            height: '56px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, var(--primary), #4f46e5)',
            color: '#fff',
            boxShadow: '0 8px 24px rgba(99, 102, 241, 0.35)',
            marginBottom: '16px'
          }}>
            <UserPlus size={28} />
          </div>
          <h1 style={{ fontSize: '1.85rem', fontWeight: 700, margin: '0 0 8px 0', letterSpacing: '-0.02em', color: 'var(--text-main)' }}>
            Create Academic Account
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', margin: 0 }}>
            Join the academic research and requirement management platform
          </p>
        </div>

        {/* Card Container */}
        <div className="card" style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-xl)',
          padding: '36px 32px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.25)'
        }}>

          {/* Feedback Alerts */}
          {errorMsg && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              fontSize: '0.88rem',
              marginBottom: '20px'
            }}>
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              color: '#34d399',
              fontSize: '0.88rem',
              marginBottom: '20px'
            }}>
              <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
              <span>{successMsg}</span>
            </div>
          )}

          {serverSavedMsg && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 14px',
              backgroundColor: 'rgba(16, 185, 129, 0.12)',
              color: '#34d399',
              borderRadius: 'var(--radius-md)',
              marginBottom: '16px',
              fontSize: '0.85rem'
            }}>
              <Check size={16} />
              <span>{serverSavedMsg}</span>
            </div>
          )}

          {/* Registration Form */}
          <form onSubmit={handleRegisterSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            
            {/* Full Name */}
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                Full Name *
              </label>
              <div style={{ position: 'relative' }}>
                <User size={18} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  required
                  placeholder="e.g. Aarav Sharma"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px 14px 12px 42px',
                    background: 'var(--bg-main)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--text-main)',
                    fontSize: '0.9rem'
                  }}
                />
              </div>
            </div>

            {/* Email Address */}
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                Email Address *
              </label>
              <div style={{ position: 'relative' }}>
                <Mail size={18} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="email"
                  required
                  placeholder="researcher@university.ac.in"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px 14px 12px 42px',
                    background: 'var(--bg-main)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--text-main)',
                    fontSize: '0.9rem'
                  }}
                />
              </div>
            </div>

            {/* Indian Mobile Number & Organization in 2 columns */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Indian Mobile Number *
                </label>
                <div style={{ position: 'relative' }}>
                  <Phone size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input
                    type="tel"
                    required
                    placeholder="9876543210"
                    value={mobileNumber}
                    onChange={(e) => setMobileNumber(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px 12px 12px 38px',
                      background: 'var(--bg-main)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--text-main)',
                      fontSize: '0.88rem'
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Organization
                </label>
                <div style={{ position: 'relative' }}>
                  <Building size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input
                    type="text"
                    placeholder="e.g. Institute of Technology"
                    value={organization}
                    onChange={(e) => setOrganization(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px 12px 12px 38px',
                      background: 'var(--bg-main)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-md)',
                      color: 'var(--text-main)',
                      fontSize: '0.88rem'
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Password */}
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                Password (min 8 chars) *
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={18} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px 42px 12px 42px',
                    background: 'var(--bg-main)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--text-main)',
                    fontSize: '0.9rem'
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer'
                  }}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                Confirm Password *
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={18} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  placeholder="••••••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px 14px 12px 42px',
                    background: 'var(--bg-main)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--text-main)',
                    fontSize: '0.9rem'
                  }}
                />
              </div>
            </div>

            {/* Role Notice */}
            <div style={{
              background: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid rgba(99, 102, 241, 0.2)',
              borderRadius: 'var(--radius-md)',
              padding: '10px 14px',
              fontSize: '0.8rem',
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Sparkles size={16} color="var(--primary)" />
              <span>Account will be assigned standard <strong>USER</strong> researcher privileges.</span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{
                width: '100%',
                padding: '13px',
                fontWeight: 600,
                fontSize: '0.95rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                marginTop: '8px'
              }}
            >
              {loading ? (
                <>
                  <RefreshCw size={18} className="animate-spin" />
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span>Create Account & Sign In</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          {/* Live Backend Connection Indicator & Switcher */}
          <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-color)', fontSize: '0.8rem', textAlign: 'left' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                <Server size={14} className="text-primary" />
                <span>Backend:</span>
                <code style={{ fontSize: '0.75rem', backgroundColor: 'var(--bg-main)', padding: '2px 6px', borderRadius: '4px', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'inline-block' }}>
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
                  Target Backend URL (e.g. Cloudflare Tunnel or Localhost):
                </label>
                <input 
                  type="text" 
                  className="form-control" 
                  style={{ fontSize: '0.8rem', padding: '6px 10px', marginBottom: '8px' }}
                  value={serverInput}
                  onChange={(e) => setServerInput(e.target.value)}
                  placeholder="https://your-tunnel.trycloudflare.com"
                />
                <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                  <button 
                    type="button" 
                    onClick={handleResetServer} 
                    className="btn btn-secondary" 
                    style={{ fontSize: '0.75rem', padding: '4px 10px' }}
                  >
                    <RefreshCw size={11} />
                    <span>Reset Tunnel</span>
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

          {/* Footer Switcher */}
          <div style={{
            marginTop: '16px',
            paddingTop: '16px',
            borderTop: '1px solid var(--border-color)',
            textAlign: 'center',
            fontSize: '0.88rem',
            color: 'var(--text-muted)'
          }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--primary)', fontWeight: 600, textDecoration: 'none' }}>
              Login here
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Register;
