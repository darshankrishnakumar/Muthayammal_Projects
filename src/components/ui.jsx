import { Children, cloneElement, createContext, isValidElement, useCallback, useContext, useEffect, useId, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, CheckCircle2, ChevronRight, Info, Inbox, X } from 'lucide-react';
import { statusLabel, statusTone, initials, dateTime } from '../utils/format';

/* ------------------------------------------------------------------ */
/* Layout                                                              */
/* ------------------------------------------------------------------ */

export function PageHeader({ title, description, actions, breadcrumbs }) {
  return (
    <div className="blur-in">
      {breadcrumbs && <Breadcrumbs items={breadcrumbs} />}
      <div className="page-header">
        <div className="min-w-0">
          <h1 className="page-title">{title}</h1>
          {description && <p className="page-description">{description}</p>}
        </div>
        {actions && <div className="page-actions">{actions}</div>}
      </div>
    </div>
  );
}

export function Breadcrumbs({ items }) {
  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      {items.map((item, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 && <ChevronRight aria-hidden="true" />}
          {item.to ? <Link to={item.to}>{item.label}</Link> : <span>{item.label}</span>}
        </span>
      ))}
    </nav>
  );
}

export function Card({ title, subtitle, actions, children, footer, flush, className = '', ...rest }) {
  return (
    <section className={`card ${flush || title ? 'card-flush' : ''} ${className}`} {...rest}>
      {title && (
        <header className="card-header">
          <div className="min-w-0">
            <h2 className="card-title">{title}</h2>
            {subtitle && <p className="card-subtitle">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </header>
      )}
      {title && !flush ? <div className="card-body">{children}</div> : children}
      {footer && <footer className="card-footer">{footer}</footer>}
    </section>
  );
}

/** Card with a cursor-following highlight (ReactBits "spotlight" pattern). */
export function SpotlightCard({ className = '', children, ...rest }) {
  const ref = useRef(null);
  const onMove = (e) => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    el.style.setProperty('--mx', `${e.clientX - r.left}px`);
    el.style.setProperty('--my', `${e.clientY - r.top}px`);
  };
  return (
    <div ref={ref} onMouseMove={onMove} className={`card spotlight ${className}`} {...rest}>
      {children}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Data display                                                        */
/* ------------------------------------------------------------------ */

const prefersReducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

/** Animated number that counts up once when first shown. */
export function CountUp({ value, format = (n) => Math.round(n).toLocaleString('en-IN'), duration = 700 }) {
  const target = Number(value) || 0;
  const [display, setDisplay] = useState(prefersReducedMotion() ? target : 0);
  const from = useRef(0);

  useEffect(() => {
    if (prefersReducedMotion()) {
      setDisplay(target);
      return undefined;
    }
    const start = performance.now();
    const initial = from.current;
    let frame;
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(initial + (target - initial) * eased);
      if (t < 1) frame = requestAnimationFrame(tick);
      else from.current = target;
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration]);

  return <span className="tabular">{format(display)}</span>;
}

export function StatCard({ label, value, icon: Icon, hint, tone, format, onClick, index = 0, loading }) {
  return (
    <div
      className={`stat-card reveal ${tone ? `is-${tone}` : ''}`}
      style={{ '--i': index }}
      role={onClick ? 'link' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={onClick}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
    >
      <div className="stat-card-top">
        <span className="stat-label">{label}</span>
        {Icon && <span className="stat-icon"><Icon aria-hidden="true" /></span>}
      </div>
      <div className="stat-value">
        {loading ? <span className="skeleton" style={{ display: 'inline-block', width: 64, height: 26 }} /> : <CountUp value={value} format={format} />}
      </div>
      {hint && <div className="stat-hint">{hint}</div>}
    </div>
  );
}

export function Badge({ tone = 'neutral', dot, children, className = '' }) {
  return <span className={`badge badge-${tone} ${dot ? 'badge-dot' : ''} ${className}`}>{children}</span>;
}

export function StatusBadge({ status, label }) {
  if (!status) return null;
  return <Badge tone={statusTone(status)} dot>{label || statusLabel(status)}</Badge>;
}

export function Avatar({ name, size }) {
  return <span className={`avatar ${size ? `avatar-${size}` : ''}`} aria-hidden="true">{initials(name)}</span>;
}

export function Progress({ value = 0, tone }) {
  const v = Math.max(0, Math.min(100, Number(value) || 0));
  return (
    <div className={`progress ${tone ? `is-${tone}` : ''}`} role="progressbar" aria-valuenow={v} aria-valuemin={0} aria-valuemax={100}>
      <div className="progress-bar" style={{ width: `${v}%` }} />
    </div>
  );
}

export function Timeline({ items = [], empty = 'No activity yet.' }) {
  if (!items.length) return <p className="text-sm text-subtle">{empty}</p>;
  return (
    <ol className="timeline">
      {items.map((item, i) => (
        <li key={item.id ?? i} className={`timeline-item ${i === items.length - 1 ? 'is-latest' : ''}`}>
          <span className="timeline-dot" aria-hidden="true" />
          <div className="timeline-title">
            {item.toStatus && item.fromStatus !== item.toStatus ? statusLabel(item.toStatus) : (item.note?.split(':')[0] || statusLabel(item.toStatus))}
          </div>
          <div className="timeline-meta">{dateTime(item.createdAt)} · {item.actorEmail}</div>
          {item.note && <div className="timeline-note">{item.note}</div>}
        </li>
      ))}
    </ol>
  );
}

export function Steps({ steps, current }) {
  const idx = steps.findIndex((s) => s.key === current);
  return (
    <div className="steps" aria-label="Progress">
      {steps.map((s, i) => (
        <div key={s.key} className="flex items-center">
          <div className={`step ${i < idx ? 'is-done' : ''} ${i === idx ? 'is-current' : ''}`}>
            <span className="step-dot">{i + 1}</span>
            <span>{s.label}</span>
          </div>
          {i < steps.length - 1 && <span className="step-line" aria-hidden="true" />}
        </div>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Feedback                                                            */
/* ------------------------------------------------------------------ */

export function EmptyState({ icon: Icon = Inbox, title, text, action }) {
  return (
    <div className="empty-state">
      <div className="empty-icon"><Icon aria-hidden="true" /></div>
      <div className="empty-title">{title}</div>
      {text && <p className="empty-text">{text}</p>}
      {action}
    </div>
  );
}

export function Alert({ tone = 'info', title, children }) {
  const Icon = tone === 'success' ? CheckCircle2 : tone === 'info' ? Info : AlertCircle;
  return (
    <div className={`alert alert-${tone}`} role={tone === 'danger' ? 'alert' : 'status'}>
      <Icon aria-hidden="true" />
      <div>
        {title && <div className="font-medium">{title}</div>}
        {children && <div className="text-sm">{children}</div>}
      </div>
    </div>
  );
}

export function ErrorState({ error, onRetry }) {
  return (
    <div className="card">
      <EmptyState
        icon={AlertCircle}
        title={error?.status === 403 ? 'You do not have access to this' : 'Could not load this page'}
        text={error?.message}
        action={onRetry && <button className="btn btn-secondary" onClick={onRetry}>Try again</button>}
      />
    </div>
  );
}

export function Spinner({ large }) {
  return <span className={`spinner ${large ? 'spinner-lg' : ''}`} role="status" aria-label="Loading" />;
}

export function LoadingBlock({ label = 'Loading…' }) {
  return (
    <div className="flex items-center justify-center gap-3" style={{ padding: '56px 0', color: 'var(--text-3)' }}>
      <Spinner large /> <span className="text-sm">{label}</span>
    </div>
  );
}

export function SkeletonRows({ rows = 5, height = 44 }) {
  return (
    <div className="space-y-2" aria-hidden="true">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height }} />
      ))}
    </div>
  );
}

/* Toasts */
const ToastContext = createContext({ notify: () => {} });

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const notify = useCallback((message, { tone = 'success', title } = {}) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, message, tone, title }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), tone === 'error' ? 6500 : 4000);
  }, []);
  return (
    <ToastContext.Provider value={{ notify }}>
      {children}
      <div className="toast-stack" aria-live="polite">
        {toasts.map((t) => {
          const Icon = t.tone === 'error' ? AlertCircle : t.tone === 'info' ? Info : CheckCircle2;
          return (
            <div key={t.id} className={`toast is-${t.tone}`}>
              <Icon aria-hidden="true" />
              <div className="min-w-0">
                {t.title && <div className="toast-title">{t.title}</div>}
                <div className={t.title ? 'toast-text' : 'toast-title'}>{t.message}</div>
              </div>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);

/* ------------------------------------------------------------------ */
/* Overlays                                                            */
/* ------------------------------------------------------------------ */

function useEscape(open, onClose) {
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => e.key === 'Escape' && onClose?.();
    document.addEventListener('keydown', onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prev;
    };
  }, [open, onClose]);
}

export function Modal({ open, onClose, title, description, children, footer, size }) {
  useEscape(open, onClose);
  if (!open) return null;
  return (
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose?.()}>
      <div className={`modal ${size ? `modal-${size}` : ''}`} role="dialog" aria-modal="true" aria-label={title}>
        <div className="modal-header">
          <div className="min-w-0">
            <h2 className="modal-title">{title}</h2>
            {description && <p className="modal-description">{description}</p>}
          </div>
          <button className="btn btn-ghost btn-icon btn-sm" onClick={onClose} aria-label="Close"><X /></button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  );
}

export function Drawer({ open, onClose, title, description, children, footer }) {
  useEscape(open, onClose);
  if (!open) return null;
  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <aside className="drawer" role="dialog" aria-modal="true" aria-label={title}>
        <div className="modal-header">
          <div className="min-w-0">
            <h2 className="modal-title">{title}</h2>
            {description && <p className="modal-description">{description}</p>}
          </div>
          <button className="btn btn-ghost btn-icon btn-sm" onClick={onClose} aria-label="Close"><X /></button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </aside>
    </>
  );
}

export function ConfirmDialog({ open, title, text, confirmLabel = 'Confirm', tone = 'primary', busy, onConfirm, onClose, children }) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose} disabled={busy}>Cancel</button>
          <button className={`btn btn-${tone}`} onClick={onConfirm} disabled={busy}>
            {busy && <Spinner />} {confirmLabel}
          </button>
        </>
      }
    >
      {text && <p className="text-base">{text}</p>}
      {children}
    </Modal>
  );
}

/* ------------------------------------------------------------------ */
/* Inputs                                                              */
/* ------------------------------------------------------------------ */

/**
 * Form field wrapper. Links the label to a single input child automatically (generating an id
 * when the child has none) and wires hint/error text through aria-describedby.
 */
export function Field({ label, hint, error, children, className = '', htmlFor }) {
  const autoId = useId();
  const only = Children.count(children) === 1 && isValidElement(children) && ['input', 'select', 'textarea'].includes(children.type) ? children : null;
  const id = htmlFor || only?.props.id || autoId;
  const describedBy = error || hint ? `${id}-desc` : undefined;
  const control = only
    ? cloneElement(only, { id, 'aria-invalid': error ? true : undefined, 'aria-describedby': describedBy })
    : children;
  return (
    <div className={`field ${className}`}>
      {label && <label className="field-label" htmlFor={only || htmlFor ? id : undefined}>{label}</label>}
      {control}
      {error ? <span className="field-error" id={describedBy}>{error}</span> : hint && <span className="field-hint" id={describedBy}>{hint}</span>}
    </div>
  );
}

export function Tabs({ tabs, value, onChange }) {
  return (
    <div className="tabs" role="tablist">
      {tabs.map((t) => (
        <button
          key={t.value}
          role="tab"
          aria-selected={value === t.value}
          className={`tab ${value === t.value ? 'active' : ''}`}
          onClick={() => onChange(t.value)}
        >
          {t.icon && <t.icon size={15} aria-hidden="true" />}
          {t.label}
          {t.count !== undefined && <span className="count">{t.count}</span>}
        </button>
      ))}
    </div>
  );
}

export function Segmented({ options, value, onChange }) {
  return (
    <div className="segmented" role="radiogroup">
      {options.map((o) => (
        <button key={o.value} role="radio" aria-checked={value === o.value} className={value === o.value ? 'active' : ''} onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

/** Button that shows a spinner while its async onClick runs. */
export function AsyncButton({ onClick, children, className = 'btn btn-primary', disabled, ...rest }) {
  const [busy, setBusy] = useState(false);
  const mounted = useRef(true);
  useEffect(() => () => { mounted.current = false; }, []);
  const handle = async (e) => {
    if (busy) return;
    setBusy(true);
    try {
      await onClick?.(e);
    } finally {
      if (mounted.current) setBusy(false);
    }
  };
  return (
    <button className={className} onClick={handle} disabled={disabled || busy} {...rest}>
      {busy && <Spinner />} {children}
    </button>
  );
}
