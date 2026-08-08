import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import api from '../lib/api';

const AuthContext = createContext(null);

function safeGetStorage(key) {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(key);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => safeGetStorage('access_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    api.get('/auth/me').then((res) => setUser(res.data)).catch(() => {
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem('access_token');
        window.localStorage.removeItem('refresh_token');
      }
      setToken(null);
      setUser(null);
    }).finally(() => setLoading(false));
  }, [token]);

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, refresh_token } = response.data;
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('access_token', access_token);
      window.localStorage.setItem('refresh_token', refresh_token);
    }
    setToken(access_token);
    return response.data;
  };

  const register = async (fullName, email, password) => {
    await api.post('/auth/register', { full_name: fullName, email, password });
    return login(email, password);
  };

  const logout = async () => {
    const refreshToken = safeGetStorage('refresh_token');
    if (refreshToken) {
      try {
        await api.post('/auth/logout', { refresh_token: refreshToken });
      } catch (error) {
        console.error('Logout failed', error);
      }
    }
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('access_token');
      window.localStorage.removeItem('refresh_token');
    }
    setToken(null);
    setUser(null);
  };

  const value = useMemo(() => ({ user, token, loading, login, register, logout }), [user, token, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
