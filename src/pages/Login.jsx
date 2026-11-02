import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Eye, EyeOff, Library, ShieldCheck, Workflow } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Alert, Field, Spinner } from '../components/ui';
import { getApiBaseUrl } from '../utils/api';

export function AuthAside() {
  const points = [
    { icon: Library, title: 'One central library', text: 'Every completed project is stored once and shared with colleges through allocations.' },
    { icon: Workflow, title: 'Custom development, tracked', text: 'Requirements move from college review to delivery with a full timeline.' },
    { icon: ShieldCheck, title: 'Access you can trust', text: 'Deliverables unlock only after verified payment, per student and per college.' },
  ];
  return (
    <aside className="auth-aside">
      <div className="auth-grid-bg" aria-hidden="true" />
      <div className="auth-glow" aria-hidden="true" />
      <div className="relative flex items-center gap-2">
        <span className="brand-mark" style={{ background: 'var(--ink-text)', color: 'var(--ink)' }}>AI</span>
        <span className="font-semibold">Academic Integration</span>
      </div>
      <div className="relative" style={{ maxWidth: 440 }}>
        <h2 className="blur-in" style={{ color: 'var(--ink-text)', fontSize: '2rem', letterSpacing: '-0.035em', lineHeight: 1.15 }}>
          Academic projects, distributed to every partner college.
        </h2>
        <div className="mt-8 space-y-6">
          {points.map((p, i) => (
            <div key={p.title} className="flex gap-3 reveal" style={{ '--i': i + 2 }}>
              <span style={{ width: 32, height: 32, borderRadius: 8, display: 'grid', placeItems: 'center', flexShrink: 0, background: 'color-mix(in srgb, var(--ink-text) 10%, transparent)' }}>
                <p.icon size={16} aria-hidden="true" />
              </span>
              <div>
                <div className="font-medium" style={{ color: 'var(--ink-text)' }}>{p.title}</div>
                <p className="text-sm mt-1">{p.text}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
      <p className="relative text-xs">© {new Date().getFullYear()} Academic Integration Tool</p>
    </aside>
  );
}

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      await login(email.trim(), password);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message || 'Sign in failed.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-panel">
        <div className="auth-card">
          <div className="mb-8 blur-in">
            <h1 style={{ fontSize: 'var(--text-2xl)' }}>Sign in</h1>
            <p className="mt-1">Welcome back. Use the account your college or administrator gave you.</p>
          </div>

          {error && <Alert tone="danger">{error}</Alert>}

          <form onSubmit={submit} noValidate>
            <Field label="Email" htmlFor="email">
              <input id="email" className="input" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
            </Field>
            <Field label="Password" htmlFor="password">
              <div className="relative">
                <input id="password" className="input" type={show ? 'text' : 'password'} autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ paddingRight: 40 }} />
                <button type="button" className="btn btn-ghost btn-icon btn-sm" onClick={() => setShow((s) => !s)} aria-label={show ? 'Hide password' : 'Show password'} style={{ position: 'absolute', right: 4, top: 4 }}>
                  {show ? <EyeOff /> : <Eye />}
                </button>
              </div>
            </Field>
            <button type="submit" className="btn btn-primary btn-lg btn-block mt-2" disabled={busy || !email || !password}>
              {busy ? <Spinner /> : null} Sign in {!busy && <ArrowRight />}
            </button>
          </form>

          <p className="text-sm mt-6 text-center">
            New student? <Link to="/register">Create an account</Link>
          </p>

          {import.meta.env.DEV && (
            <div className="surface-muted mt-8 p-3 text-xs text-muted">
              <div className="font-medium mb-1" style={{ color: 'var(--text)' }}>Development</div>
              <div>API: <span className="font-mono">{getApiBaseUrl()}</span></div>
              <div className="mt-1">Demo accounts (when seeding is enabled): superadmin@academic.com, admin@academic.com, developer@academic.com, user@academic.com — see backend DataInitializer.</div>
            </div>
          )}
        </div>
      </div>
      <AuthAside />
    </div>
  );
}
