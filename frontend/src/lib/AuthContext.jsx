import { createContext, useContext, useState, useEffect } from 'react';
import { getMe, logout as apiLogout } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      getMe()
        .then(setUser)
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const refreshUser = async () => {
    try {
      const u = await getMe();
      setUser(u);
    } catch {
      setUser(null);
    }
  };

  const logout = () => {
    apiLogout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
