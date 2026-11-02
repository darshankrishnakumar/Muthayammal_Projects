import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import { AuthProvider } from './context/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';

// Sanitize stale insecure URLs from previous visits on HTTPS origins
if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
  try {
    const custom = localStorage.getItem('CUSTOM_API_URL');
    if (custom && (custom.startsWith('http://localhost') || custom.startsWith('http://127.0.0.1') || (custom.startsWith('http://') && !custom.startsWith('https://')))) {
      console.log('Sanitizing obsolete insecure CUSTOM_API_URL on HTTPS origin.');
      localStorage.removeItem('CUSTOM_API_URL');
    }
  } catch (e) {}
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <AuthProvider>
        <App />
      </AuthProvider>
    </ErrorBoundary>
  </StrictMode>
);

// Non-blocking Service Worker update and cleanup on load
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').then((reg) => {
      reg.onupdatefound = () => {
        const installingWorker = reg.installing;
        if (installingWorker) {
          installingWorker.onstatechange = () => {
            if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
              console.log('New update available, refreshing to latest bundle.');
              window.location.reload();
            }
          };
        }
      };
    }).catch((err) => {
      console.warn('SW registration skipped:', err);
    });
  });
}
