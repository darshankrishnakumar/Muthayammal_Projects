import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

const CHUNK_ERROR_HINTS = ['dynamically imported module', 'Failed to fetch', 'Loading chunk', 'Unexpected token'];

/**
 * Catches render errors anywhere below it. Renders outside the toast provider and layout shell,
 * so it only relies on design-system CSS classes.
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Unhandled render error caught by ErrorBoundary:', error, errorInfo);

    // A stale lazy chunk after a deployment: reload once (at most every 10 seconds).
    const message = error?.message || '';
    if (CHUNK_ERROR_HINTS.some((hint) => message.includes(hint))) {
      try {
        const lastReload = sessionStorage.getItem('chunk_error_reload');
        const now = Date.now();
        if (!lastReload || now - Number(lastReload) > 10000) {
          sessionStorage.setItem('chunk_error_reload', String(now));
          window.location.reload();
        }
      } catch {
        /* storage unavailable */
      }
    }
  }

  handleReload = () => {
    if ('caches' in window) {
      caches.keys().then((names) => names.forEach((name) => caches.delete(name))).catch(() => {});
    }
    window.location.reload();
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="flex items-center justify-center" style={{ minHeight: '100vh', padding: 24, background: 'var(--bg)' }}>
        <div className="card" style={{ maxWidth: 440, width: '100%' }}>
          <div className="empty-state">
            <div className="empty-icon"><AlertTriangle aria-hidden="true" /></div>
            <div className="empty-title">Something went wrong</div>
            <p className="empty-text">
              The page could not be displayed. Reloading usually fixes this, especially right after an update.
            </p>
            {import.meta.env.DEV && this.state.error?.message && (
              <pre className="surface-muted text-xs text-left mt-4 w-full overflow-auto" style={{ padding: 12, whiteSpace: 'pre-wrap' }}>
                {this.state.error.message}
              </pre>
            )}
            <button type="button" className="btn btn-primary" onClick={this.handleReload}>
              <RefreshCw aria-hidden="true" />
              Reload
            </button>
          </div>
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;
