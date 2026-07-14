import React from 'react';
import { Navigate, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const PrivateRoute = ({ allowedRoles }) => {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  // 1. ¿No hay sesión activa? Redirigir directo al login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // 2. ¿El rol actual del usuario está autorizado para esta ruta?
  if (allowedRoles && !allowedRoles.includes(user?.rol)) {
    // Función auxiliar para saber a dónde mandarlo de vuelta si decide regresar
    const getHomePath = () => {
      switch (user?.rol) {
        case 'admin': return '/admin';
        case 'docente': return '/asistencia'; // O la ruta principal de tus docentes
        case 'auxiliar': return '/asistencia'; 
        default: return '/login';
      }
    };

    // RENDERIZAMOS UNA VISTA 403 ELEGANTE E INMUNE A TAILWIND
    return (
      <div className="forbidden-page-root">
        <style>{`
          .forbidden-page-root {
            min-height: 100vh !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background-color: #f8fafc !important;
            font-family: 'Inter', -apple-system, sans-serif !important;
            padding: 24px !important;
            box-sizing: border-box !important;
          }
          .forbidden-card {
            background: #ffffff !important;
            padding: 40px 32px !important;
            border-radius: 20px !important;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05), 0 8px 10px -6px rgba(15, 23, 42, 0.05) !important;
            max-width: 440px !important;
            width: 100% !important;
            text-align: center !important;
            border: 1px solid #e2e8f0 !important;
          }
          .forbidden-icon-box {
            width: 64px !important;
            height: 64px !important;
            background-color: #fef2f2 !important;
            color: #ef4444 !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 auto 20px auto !important;
          }
          .forbidden-title {
            font-size: 22px !important;
            font-weight: 800 !important;
            color: #0f172a !important;
            margin: 0 0 10px 0 !important;
            letter-spacing: -0.5px !important;
          }
          .forbidden-text {
            font-size: 14px !important;
            color: #64748b !important;
            line-height: 1.6 !important;
            margin: 0 0 28px 0 !important;
          }
          .btn-forbidden-action {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            background-color: #4f46e5 !important;
            color: #ffffff !important;
            border: none !important;
            padding: 12px 24px !important;
            border-radius: 12px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2) !important;
          }
          .btn-forbidden-action:hover {
            background-color: #4338ca !important;
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.3) !important;
          }
        `}</style>

        <div className="forbidden-card">
          <div className="forbidden-icon-box">
            {/* Icono de escudo de protección/bloqueo de 24px exactos */}
            <svg style={{ width: '24px', height: '24px' }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m0-6V9m12.828-1.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-12.828 5.04M2.05 11.12a12.054 12.054 0 0019.9 0M21.5 12a9.5 9.5 0 11-19 0 9.5 9.5 0 0119 0z" />
            </svg>
          </div>
          <h2 className="forbidden-title">Acceso Restringido</h2>
          <p className="forbidden-text">
            Tu cuenta actual con rol de <strong>{user?.rol || 'usuario'}</strong> no tiene los privilegios necesarios para ver este apartado de la intranet.
          </p>
          <button 
            onClick={() => navigate(getHomePath(), { replace: true })} 
            className="btn-forbidden-action"
          >
            Volver a mi Panel Principal
          </button>
        </div>
      </div>
    );
  }

  // 3. Todo en orden, renderizar la subruta solicitada
  return <Outlet />;
};

export default PrivateRoute;