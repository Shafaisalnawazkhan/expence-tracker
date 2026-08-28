import { createContext, useContext, useMemo, useState } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);
const readUser = () => JSON.parse(localStorage.getItem('finance_user') || 'null');
export function AuthProvider({ children }) {
  const [user, setUser] = useState(readUser); const [appLocked, setAppLocked] = useState(() => Boolean(readUser()?.app_lock_enabled));
  const saveUser = (nextUser) => { localStorage.setItem('finance_user', JSON.stringify(nextUser)); setUser(nextUser); };
  const authenticate = async (mode, payload) => { const { data } = await api.post(`/auth/${mode}`, payload); if (mode === 'register') return data; localStorage.setItem('finance_access_token', data.access_token); localStorage.setItem('finance_refresh_token', data.refresh_token); saveUser(data.user); setAppLocked(false); return data; };
  const setupLock = async (pin) => { await api.post('/auth/app-lock/setup', { pin }); saveUser({ ...user, app_lock_enabled: true }); };
  const disableLock = async () => { await api.delete('/auth/app-lock'); saveUser({ ...user, app_lock_enabled: false }); setAppLocked(false); };
  const unlock = async (pin) => { await api.post('/auth/app-lock/verify', { pin }); setAppLocked(false); };
  const lockNow = () => { if (user?.app_lock_enabled) setAppLocked(true); };
  const logout = () => { localStorage.removeItem('finance_access_token'); localStorage.removeItem('finance_refresh_token'); localStorage.removeItem('finance_user'); setUser(null); setAppLocked(false); };
  const updateUser = (nextUser) => saveUser(nextUser);
  const value = useMemo(() => ({ user, appLocked, authenticate, logout, setupLock, disableLock, unlock, lockNow, updateUser }), [user, appLocked]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);
