import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  // ═══════════════════════════════════════════════════════════
  // ESTADOS
  // ═══════════════════════════════════════════════════════════
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken'));
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  });
  const [dashboard, setDashboard] = useState(() => {
    const stored = localStorage.getItem('dashboard');
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  // ═══════════════════════════════════════════════════════════
  // PERSISTENCIA EN LOCALSTORAGE
  // ═══════════════════════════════════════════════════════════
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
    }
  }, [token]);

  useEffect(() => {
    if (refreshToken) {
      localStorage.setItem('refreshToken', refreshToken);
    } else {
      localStorage.removeItem('refreshToken');
    }
  }, [refreshToken]);

  useEffect(() => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
    }
  }, [user]);

  useEffect(() => {
    if (dashboard) {
      localStorage.setItem('dashboard', JSON.stringify(dashboard));
    } else {
      localStorage.removeItem('dashboard');
    }
  }, [dashboard]);

  // Al cargar la app, si hay token, configurarlo
  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, []);

  // ═══════════════════════════════════════════════════════════
  // LOGIN PERSONAL (ADMIN, AUXILIAR, DOCENTE) - CON CORREO
  // ═══════════════════════════════════════════════════════════
  const loginPersonal = useCallback(async (correo, contrasena) => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/auth/login/personal', {
        correo: correo.trim(),
        contrasena
      });

      const { access_token, refresh_token, usuario, dashboard: dashboardData } = response.data;

      // Guardar tokens
      setToken(access_token);
      setRefreshToken(refresh_token);

      // Guardar datos del usuario
      const userData = {
        ...usuario,
        tipo_usuario: 'personal'
      };
      setUser(userData);

      // Guardar dashboard si existe (docentes/auxiliares)
      if (dashboardData) {
        setDashboard(dashboardData);
      }

      // Redirigir según el rol
      switch (usuario.rol) {
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

      return { success: true, usuario };

    } catch (err) {
      const mensaje = err.response?.data?.detail || 'Error al iniciar sesión. Verifique su correo y contraseña.';
      setError(mensaje);
      return { success: false, error: mensaje };
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // ═══════════════════════════════════════════════════════════
  // LOGIN APODERADO (PADRE DE FAMILIA - SOLO DNI)
  // ═══════════════════════════════════════════════════════════
  const loginApoderado = useCallback(async (dni) => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/auth/login/apoderado', {
        dni
      });

      const { access_token, refresh_token, apoderado, hijos } = response.data;

      // Guardar tokens
      setToken(access_token);
      setRefreshToken(refresh_token);

      // Guardar datos del apoderado como "user"
      const userData = {
        ...apoderado,
        rol: 'apoderado',
        tipo_usuario: 'apoderado'
      };
      setUser(userData);

      // Guardar hijos en el dashboard
      setDashboard({ hijos });

      // Redirigir a la bandeja de selección de hijos
      navigate('/apoderado/seleccionar-hijo');

      return { success: true, apoderado, hijos };

    } catch (err) {
      const mensaje = err.response?.data?.detail || 'Error al iniciar sesión. Verifique su DNI.';
      setError(mensaje);
      return { success: false, error: mensaje };
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // ═══════════════════════════════════════════════════════════
  // LOGIN APODERADO CON SMS (MÁS SEGURO)
  // ═══════════════════════════════════════════════════════════
  const loginApoderadoSMS = useCallback(async (dni, codigoSMS) => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/auth/login/apoderado/sms', {
        dni,
        codigo_sms: codigoSMS
      });

      const { access_token, refresh_token, apoderado, hijos } = response.data;

      setToken(access_token);
      setRefreshToken(refresh_token);

      const userData = {
        ...apoderado,
        rol: 'apoderado',
        tipo_usuario: 'apoderado'
      };
      setUser(userData);
      setDashboard({ hijos });

      navigate('/apoderado/seleccionar-hijo');

      return { success: true, apoderado, hijos };

    } catch (err) {
      const mensaje = err.response?.data?.detail || 'Código SMS inválido.';
      setError(mensaje);
      return { success: false, error: mensaje };
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // ═══════════════════════════════════════════════════════════
  // ENVIAR CÓDIGO SMS PARA LOGIN DE APODERADO
  // ═══════════════════════════════════════════════════════════
  const enviarSMSLogin = useCallback(async (dni) => {
    try {
      const response = await api.post('/auth/login/apoderado/enviar-sms', {
        dni
      });

      return {
        success: true,
        mensaje: response.data.mensaje,
        celular_enmascarado: response.data.celular_enmascarado
      };
    } catch (err) {
      const mensaje = err.response?.data?.detail || 'Error al enviar SMS.';
      return { success: false, error: mensaje };
    }
  }, []);

  // ═══════════════════════════════════════════════════════════
  // REFRESCAR TOKEN (MANTENER SESIÓN)
  // ═══════════════════════════════════════════════════════════
  const refreshAccessToken = useCallback(async () => {
    if (!refreshToken) {
      return false;
    }

    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken
      });

      const { access_token } = response.data;
      setToken(access_token);

      return true;
    } catch (err) {
      // Si falla el refresh, hacer logout
      logout();
      return false;
    }
  }, [refreshToken]);

  // ═══════════════════════════════════════════════════════════
  // LOGOUT
  // ═══════════════════════════════════════════════════════════
  const logout = useCallback(async () => {
    try {
      // Intentar revocar el token en el backend
      if (token) {
        await api.post('/auth/logout', {
          token,
          tipo_usuario: user?.tipo_usuario || 'personal'
        });
      }
    } catch (err) {
      // Si falla, igual cerramos sesión localmente
      console.log('Error al revocar token:', err);
    } finally {
      // Limpiar todo
      setToken(null);
      setRefreshToken(null);
      setUser(null);
      setDashboard(null);
      setError(null);

      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      localStorage.removeItem('dashboard');

      delete api.defaults.headers.common['Authorization'];

      navigate('/login');
    }
  }, [token, user, navigate]);

  // ═══════════════════════════════════════════════════════════
  // VERIFICAR SI EL TOKEN ES VÁLIDO
  // ═══════════════════════════════════════════════════════════
  const verificarToken = useCallback(async () => {
    if (!token) return false;

    try {
      await api.get('/auth/verificar');
      return true;
    } catch (err) {
      return false;
    }
  }, [token]);

  // ═══════════════════════════════════════════════════════════
  // SELECCIONAR HIJO (PARA APODERADOS)
  // ═══════════════════════════════════════════════════════════
  const seleccionarHijo = useCallback((hijo) => {
    setDashboard(prev => ({
      ...prev,
      hijoSeleccionado: hijo
    }));
    navigate(`/apoderado/alumno/${hijo.id}`);
  }, [navigate]);

  // ═══════════════════════════════════════════════════════════
  // OBTENER PERFIL DEL USUARIO ACTUAL
  // ═══════════════════════════════════════════════════════════
  const obtenerPerfil = useCallback(async () => {
    if (!token || !user) return null;

    try {
      const endpoint = user.tipo_usuario === 'apoderado'
        ? '/auth/me/apoderado'
        : '/auth/me/personal';

      const response = await api.get(endpoint);
      setUser(prev => ({ ...prev, ...response.data }));

      return response.data;
    } catch (err) {
      console.error('Error al obtener perfil:', err);
      return null;
    }
  }, [token, user]);

  // ═══════════════════════════════════════════════════════════
  // INTERCEPTOR PARA REFRESCAR TOKEN AUTOMÁTICAMENTE
  // ═══════════════════════════════════════════════════════════
  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Si el error es 401 y no es un intento de refresh
        if (error.response?.status === 401 &&
            !originalRequest._retry &&
            originalRequest.url !== '/auth/refresh' &&
            originalRequest.url !== '/auth/login/personal' &&
            originalRequest.url !== '/auth/login/apoderado') {

          originalRequest._retry = true;

          // Intentar refrescar el token
          const refreshed = await refreshAccessToken();

          if (refreshed) {
            // Reintentar la petición original con el nuevo token
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
            return api(originalRequest);
          }
        }

        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.response.eject(interceptor);
    };
  }, [refreshAccessToken, token]);

  // ═══════════════════════════════════════════════════════════
  // VALOR DEL CONTEXTO
  // ═══════════════════════════════════════════════════════════
  const value = {
    // Estado
    token,
    refreshToken,
    user,
    dashboard,
    loading,
    error,

    // Acciones de autenticación
    loginPersonal,        // (correo, contrasena) → Personal
    loginApoderado,       // (dni) → Padre de familia
    loginApoderadoSMS,    // (dni, codigoSMS) → Padre con SMS
    enviarSMSLogin,       // (dni) → Enviar código SMS
    logout,
    refreshAccessToken,
    verificarToken,

    // Acciones de apoderado
    seleccionarHijo,
    obtenerPerfil,

    // Utilidades
    isAuthenticated: !!token,
    isPersonal: user?.tipo_usuario === 'personal',
    isApoderado: user?.tipo_usuario === 'apoderado',
    isAdmin: user?.rol === 'admin',
    isDocente: user?.rol === 'docente',
    isAuxiliar: user?.rol === 'auxiliar',

    // Limpiar errores
    clearError: () => setError(null),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;