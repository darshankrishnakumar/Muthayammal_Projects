import { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../utils/api';

const AuthContext = createContext(null);

// Helper to safely read cached user on initial render to prevent route guard race conditions
const getStoredUser = () => {
  try {
    const token = localStorage.getItem('token');
    const userJson = localStorage.getItem('currentUser');
    if (token && userJson) {
      return JSON.parse(userJson);
    }
  } catch (e) {
    console.warn('Failed to parse cached user:', e);
  }
  return null;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(getStoredUser);
  const [loading, setLoading] = useState(() => !getStoredUser() && !!localStorage.getItem('token'));
  const [error, setError] = useState(null);

  // Validate or refresh session in the background
  useEffect(() => {
    let isCancelled = false;
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        if (!isCancelled) {
          setUser(null);
          setLoading(false);
        }
        return;
      }
      try {
        // Fast timeout promise so UI is never stalled
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Auth check timeout')), 3000)
        );
        const currentUser = await Promise.race([api.getCurrentUser(), timeoutPromise]);
        if (currentUser && !isCancelled) {
          setUser(currentUser);
          localStorage.setItem('currentUser', JSON.stringify(currentUser));
        }
      } catch (err) {
        console.warn('Session verification notice:', err.message);
        // Only clear the session when the server rejected the token
        if (err.status === 401 || err.status === 403) {
          localStorage.removeItem('token');
          localStorage.removeItem('currentUser');
          if (!isCancelled) setUser(null);
        }
      } finally {
        if (!isCancelled) setLoading(false);
      }
    };
    initAuth();
    const onExpired = () => {
      if (!isCancelled) setUser(null);
    };
    window.addEventListener('auth:expired', onExpired);
    return () => {
      isCancelled = true;
      window.removeEventListener('auth:expired', onExpired);
    };
  }, []);

  const refreshUser = async () => {
    const current = await api.getCurrentUser();
    setUser(current);
    return current;
  };

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.login(email, password);
      if (data && data.user) {
        setUser(data.user);
        return data.user;
      }
      throw new Error('Invalid user payload received from server');
    } catch (err) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await api.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('currentUser');
      setUser(null);
      setLoading(false);
    }
  };

  const updateProfile = async (userData) => {
    if (!user) throw new Error('Unauthenticated');
    const updated = await api.updateUser(user.id, userData);
    setUser(updated);
    return updated;
  };

  const hasRole = (roles) => {
    if (!user) return false;
    if (Array.isArray(roles)) {
      return roles.includes(user.role);
    }
    return user.role === roles;
  };

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    updateProfile,
    refreshUser,
    hasRole,
    isAuthenticated: !!user
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
