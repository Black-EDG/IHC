import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const PrivateRoute = ({ allowedRoles }) => {
  const { token, user } = useAuth();

  // 1. ¿Hay sesión?
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // 2. ¿El rol está permitido?
  if (allowedRoles && !allowedRoles.includes(user?.rol)) {
    // Si no tiene permiso, redirigir a su propio dashboard o a un 403
    switch (user?.rol) {
      case 'admin':
        return <Navigate to="/admin/dashboard" replace />;
      case 'docente':
        return <Navigate to="/docente/dashboard" replace />;
      case 'auxiliar':
        return <Navigate to="/auxiliar/dashboard" replace />;
      default:
        return <Navigate to="/login" replace />;
    }
  }

  // 3. Todo bien, mostrar la ruta
  return <Outlet />;
};

export default PrivateRoute;