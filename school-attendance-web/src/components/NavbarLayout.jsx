import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { theme } from '../theme';

const NavbarLayout = ({ children }) => {
  const nombreUsuario = localStorage.getItem('nombre_usuario') || 'Usuario';
  const rol = localStorage.getItem('rol') || 'docente';
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [menuAbierto, setMenuAbierto] = useState(false);
  const location = useLocation(); // Permite detectar la ruta activa de forma reactiva

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) setMenuAbierto(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const cerrarSesion = () => {
    localStorage.clear();
    window.location.href = '/';
  };

  return (
    <div className="intranet-layout-root">
      {/* CSS Inyectado para control absoluto y consistencia visual */}
      <style>{`
        .intranet-layout-root {
          min-height: 100vh;
          background-color: ${theme?.colors?.bg || '#f8fafc'} !important;
          font-family: 'Inter', -apple-system, sans-serif !important;
          display: flex;
          flex-direction: column;
        }

        /* HEADER SUPERIOR */
        .intranet-header {
          background-color: ${theme?.colors?.primary || '#1e3a8a'} !important;
          color: #ffffff !important;
          padding: 14px 24px !important;
          display: flex !important;
          justify-content: space-between !important;
          align-items: center !important;
          position: sticky !important;
          top: 0 !important;
          z-index: 100 !important;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        }

        .header-brand-group {
          display: flex !important;
          align-items: center !important;
          gap: 16px !important;
        }

        .btn-hamburger {
          background: none !important;
          border: none !important;
          color: #ffffff !important;
          font-size: 22px !important;
          cursor: pointer !important;
          padding: 4px !important;
          display: flex !important;
          align-items: center;
          transition: transform 0.2s ease !important;
        }

        .btn-hamburger:active {
          transform: scale(0.9) !important;
        }

        .brand-logo-text {
          font-size: 19px !important;
          font-weight: 800 !important;
          letter-spacing: -0.5px !important;
        }

        .user-controls {
          display: flex !important;
          align-items: center !important;
          gap: 20px !important;
        }

        .user-badge-info {
          text-align: right !important;
        }

        .user-badge-name {
          font-weight: 600 !important;
          font-size: 14px !important;
        }

        .user-badge-role {
          font-size: 11px !important;
          color: #93c5fd !important;
          text-transform: uppercase !important;
          font-weight: 700 !important;
          letter-spacing: 0.5px !important;
        }

        .btn-logout-action {
          background-color: #ef4444 !important;
          color: #ffffff !important;
          border: none !important;
          padding: 8px 16px !important;
          border-radius: 8px !important;
          font-size: 13px !important;
          font-weight: 700 !important;
          cursor: pointer !important;
          transition: all 0.2s ease !important;
          box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2) !important;
        }

        .btn-logout-action:hover {
          background-color: #dc2626 !important;
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
        }

        /* MENÚ DE NAVEGACIÓN MÓVIL */
        .mobile-nav-menu {
          background-color: #0f172a !important;
          padding: 12px !important;
          display: flex !important;
          flex-direction: column !important;
          gap: 6px !important;
          border-bottom: 1px solid #1e293b !important;
          animation: slideDown 0.25s ease-out !important;
        }

        .mobile-nav-link {
          color: #cbd5e1 !important;
          text-decoration: none !important;
          padding: 12px 16px !important;
          border-radius: 8px !important;
          font-size: 14px !important;
          font-weight: 600 !important;
          transition: all 0.2s ease !important;
        }

        .mobile-nav-link:hover {
          background-color: #1e293b !important;
          color: #ffffff !important;
        }

        .mobile-nav-link.active {
          background-color: #3b82f6 !important;
          color: #ffffff !important;
        }

        /* CONTENEDOR DE DISTRIBUCIÓN (BARRA LATERAL + MAIN) */
        .layout-body-wrapper {
          display: flex !important;
          flex: 1 !important;
        }

        /* BARRA LATERAL (ESCRITORIO) */
        .desktop-sidebar {
          width: 250px !important;
          background-color: #0f172a !important; /* Azul pizarra oscuro elegante */
          min-height: calc(100vh - 62px) !important;
          padding: 24px 16px !important;
          box-sizing: border-box !important;
          display: flex !important;
          flex-direction: column !important;
          gap: 6px !important;
          border-right: 1px solid #1e293b !important;
        }

        .sidebar-section-title {
          color: #475569 !important;
          font-size: 11px !important;
          font-weight: 800 !important;
          padding: 0 12px !important;
          margin-top: 14px !important;
          margin-bottom: 6px !important;
          text-transform: uppercase !important;
          letter-spacing: 0.75px !important;
        }

        .sidebar-link {
          color: #94a3b8 !important;
          text-decoration: none !important;
          padding: 12px 14px !important;
          border-radius: 10px !important;
          display: flex !important;
          align-items: center !important;
          gap: 10px !important;
          font-size: 14px !important;
          font-weight: 600 !important;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .sidebar-link:hover {
          background-color: #1e293b !important;
          color: #f1f5f9 !important;
        }

        .sidebar-link.active {
          background-color: #1e3a8a !important; /* Color primario suave */
          color: #ffffff !important;
          box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15) !important;
        }

        /* ÁREA PRINCIPAL */
        .main-content-viewport {
          flex: 1 !important;
          box-sizing: border-box !important;
          overflow-x: hidden !important;
          transition: padding 0.25s ease !important;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>

      {/* 1. HEADER SUPERIOR */}
      <header className="intranet-header">
        <div className="header-brand-group">
          {isMobile && (
            <button 
              onClick={() => setMenuAbierto(!menuAbierto)}
              className="btn-hamburger"
              aria-label="Abrir menú"
            >
              ☰
            </button>
          )}
          <span className="brand-logo-text">Intranet Escolar</span>
        </div>

        <div className="user-controls">
          {!isMobile && (
            <div className="user-badge-info">
              <div className="user-badge-name">{nombreUsuario}</div>
              <div className="user-badge-role">{rol}</div>
            </div>
          )}
          <button onClick={cerrarSesion} className="btn-logout-action">
            Salir
          </button>
        </div>
      </header>

      {/* 2. MENÚ MÓVIL DESPLEGABLE */}
      {isMobile && menuAbierto && (
        <nav className="mobile-nav-menu">
          {rol === 'admin' && (
            <>
              <Link 
                to="/admin/alumnos" 
                onClick={() => setMenuAbierto(false)}
                className={`mobile-nav-link ${location.pathname === '/admin/alumnos' ? 'active' : ''}`}
              >
                📝 Matrícula Alumnos
              </Link>
              <Link 
                to="/admin/apoderados" 
                onClick={() => setMenuAbierto(false)}
                className={`mobile-nav-link ${location.pathname === '/admin/apoderados' ? 'active' : ''}`}
              >
                👨‍👩‍👦 Registrar Apoderados
              </Link>
            </>
          )}
          <Link 
            to="/asistencia" 
            onClick={() => setMenuAbierto(false)}
            className={`mobile-nav-link ${location.pathname === '/asistencia' ? 'active' : ''}`}
          >
            ✅ Tomar Asistencia
          </Link>
        </nav>
      )}

      {/* 3. DISTRIBUCIÓN DEL CUERPO */}
      <div className="layout-body-wrapper">
        {/* Barra lateral escritorio */}
        {!isMobile && (
          <aside className="desktop-sidebar">
            {rol === 'admin' && (
              <>
                <div className="sidebar-section-title">Administración</div>
                <Link 
                  to="/admin/alumnos" 
                  className={`sidebar-link ${location.pathname === '/admin/alumnos' ? 'active' : ''}`}
                >
                  <span>📝</span> Matrícula de Alumnos
                </Link>
                <Link 
                  to="/admin/apoderados" 
                  className={`sidebar-link ${location.pathname === '/admin/apoderados' ? 'active' : ''}`}
                >
                  <span>👨‍👩‍👦</span> Registro Apoderados
                </Link>
                <div style={{ height: '8px' }}></div>
              </>
            )}
            <div className="sidebar-section-title">Operaciones</div>
            <Link 
              to="/asistencia" 
              className={`sidebar-link ${location.pathname === '/asistencia' ? 'active' : ''}`}
            >
              <span>✅</span> Tomar Asistencia
            </Link>
          </aside>
        )}

        {/* Viewport para inyectar las páginas hijas */}
        <main 
          className="main-content-viewport"
          style={{ padding: isMobile ? '20px 16px' : '32px' }}
        >
          {children}
        </main>
      </div>
    </div>
  );
};

export default NavbarLayout;