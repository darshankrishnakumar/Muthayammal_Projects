import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { api } from '../utils/api';
import { Alert, Field, Spinner } from '../components/ui';
import { AuthAside } from './Login';

const MOBILE = /^(\+91[\s-]?)?[6-9]\d{9}$/;

export default function Register() {
  const navigate = useNavigate();
  const [colleges, setColleges] = useState([]);
  const [form, setForm] = useState({ fullName: '', email: '', mobileNumber: '', collegeId: '', password: '', confirmPassword: '' });
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.registrationColleges().then(setColleges).catch(() => setColleges([]));
  }, []);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const validate = () => {
    const e = {};
    if (!form.fullName.trim()) e.fullName = 'Enter your full name.';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) e.email = 'Enter a valid email address.';
    if (form.mobileNumber && !MOBILE.test(form.mobileNumber.trim())) e.mobileNumber = 'Use a 10-digit Indian mobile number.';
    if (!form.collegeId) e.collegeId = 'Select your college.';
    if (form.password.length < 8) e.password = 'Use at least 8 characters.';
    if (form.password !== form.confirmPassword) e.confirmPassword = 'Passwords do not match.';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const submit = async (e) => {
    e.preventDefault();
    setServerError('');
    if (!validate()) return;
    setBusy(true);
    try {
      await api.register({ ...form, email: form.email.trim().toLowerCase(), collegeId: Number(form.collegeId) });
      setDone(true);
    } catch (err) {
      setServerError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-panel">
        <div className="auth-card">
          {done ? (
            <div className="blur-in">
              <h1 style={{ fontSize: 'var(--text-2xl)' }}>Account created</h1>
              <p className="mt-2">You can now sign in and browse the projects available to your college.</p>
              <button className="btn btn-primary btn-lg btn-block mt-6" onClick={() => navigate('/login')}>Go to sign in <ArrowRight /></button>
            </div>
          ) : (
            <>
              <div className="mb-6 blur-in">
                <h1 style={{ fontSize: 'var(--text-2xl)' }}>Create a student account</h1>
                <p className="mt-1">Choose your college so you see the projects it offers.</p>
              </div>
              {serverError && <Alert tone="danger">{serverError}</Alert>}
              {colleges.length === 0 && (
                <Alert tone="warning">No colleges are open for registration yet. Ask your college administrator for an account.</Alert>
              )}
              <form onSubmit={submit} noValidate>
                <Field label="Full name" error={errors.fullName} htmlFor="fullName">
                  <input id="fullName" className="input" value={form.fullName} onChange={set('fullName')} autoComplete="name" />
                </Field>
                <Field label="Email" error={errors.email} htmlFor="email">
                  <input id="email" className="input" type="email" value={form.email} onChange={set('email')} autoComplete="email" />
                </Field>
                <Field label="College" error={errors.collegeId} htmlFor="college">
                  <select id="college" className="select" value={form.collegeId} onChange={set('collegeId')}>
                    <option value="">Select your college</option>
                    {colleges.map((c) => <option key={c.id} value={c.id}>{c.name}{c.city ? ` — ${c.city}` : ''}</option>)}
                  </select>
                </Field>
                <Field label="Mobile number" hint="Optional" error={errors.mobileNumber} htmlFor="mobile">
                  <input id="mobile" className="input" value={form.mobileNumber} onChange={set('mobileNumber')} autoComplete="tel" placeholder="98765 43210" />
                </Field>
                <div className="form-grid">
                  <Field label="Password" error={errors.password} htmlFor="password">
                    <input id="password" className="input" type="password" value={form.password} onChange={set('password')} autoComplete="new-password" />
                  </Field>
                  <Field label="Confirm password" error={errors.confirmPassword} htmlFor="confirm">
                    <input id="confirm" className="input" type="password" value={form.confirmPassword} onChange={set('confirmPassword')} autoComplete="new-password" />
                  </Field>
                </div>
                <button type="submit" className="btn btn-primary btn-lg btn-block mt-2" disabled={busy || colleges.length === 0}>
                  {busy && <Spinner />} Create account
                </button>
              </form>
              <p className="text-sm mt-6 text-center">Already have an account? <Link to="/login">Sign in</Link></p>
            </>
          )}
        </div>
      </div>
      <AuthAside />
    </div>
  );
}
