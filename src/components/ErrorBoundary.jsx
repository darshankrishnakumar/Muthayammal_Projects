import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Unhandled UI render error caught by ErrorBoundary:', error, errorInfo);
    
    // Auto-reload if error was caused by a stale Vite chunk after a new deployment
    const errMsg = error?.message || '';
    if (
      errMsg.includes('dynamically imported module') ||
      errMsg.includes('Failed to fetch') ||
      errMsg.includes('Loading chunk') ||
      errMsg.includes('Unexpected token')
    ) {
      const lastReload = sessionStorage.getItem('chunk_error_reload');
      const now = Date.now();
      if (!lastReload || now - Number(lastReload) > 10000) {
        sessionStorage.setItem('chunk_error_reload', String(now));
        window.location.reload();
      }
    }
  }

  handleReload = () => {
    // Clear caches and reload
    if ('caches' in window) {
      caches.keys().then(names => {
        names.forEach(name => caches.delete(name));
      });
    }
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'var(--bg-main, #0f172a)',
          color: 'var(--text-main, #f8fafc)',
          padding: '24px',
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}>
          <div style={{
            maxWidth: '480px',
            width: '100%',
            background: 'var(--bg-card, #1e293b)',
            border: '1px solid var(--border-color, rgba(255,255,255,0.1))',
            borderRadius: '16px',
            padding: '32px',
            textAlign: 'center',
            boxShadow: '0 20px 40px rgba(0,0,0,0.4)'
          }}>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: 'rgba(239, 68, 68, 0.15)',
              color: '#ef4444',
              marginBottom: '16px'
            }}>
              <AlertTriangle size={28} />
            </div>

            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: '0 0 8px 0' }}>
              Interface Render Notice
            </h2>

            <p style={{ color: 'var(--text-muted, #94a3b8)', fontSize: '0.88rem', margin: '0 0 24px 0', lineHeight: 1.5 }}>
              The application encountered an update transition. Click below to refresh your workspace assets.
            </p>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button
                onClick={this.handleReload}
                style={{
                  background: 'var(--primary, #4f46e5)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '10px 20px',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <RefreshCw size={16} />
                <span>Refresh Workspace</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
