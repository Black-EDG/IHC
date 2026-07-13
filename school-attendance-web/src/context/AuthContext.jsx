import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')));
  const navigate = useNavigate();

  useEffect(() => {
    if (token && user) {
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }, [token, user]);

  const login = (access_token, userData) => {
    setToken(access_token);
    setUser(userData);
    // Redirigir según el rol
    switch (userData.rol) {
      case 'admin':
        navigate('/admin/dashboard');
        break;
      case 'docente':
        navigate('/docente/dashboard');
        break;
      case 'auxiliar':
        navigate('/auxiliar/dashboard');
        break;
      default:
        navigate('/');
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    navigate('/login');
  };

  const value = {
    token,
    user,
    login,
    logout,
    isAuthenticated: !!token,
    isAdmin: user?.rol === 'admin',
    isDocente: user?.rol === 'docente',
    isAuxiliar: user?.rol === 'auxiliar',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};