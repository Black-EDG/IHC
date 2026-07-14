import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { theme } from '../theme';

const NavbarLayout = ({ children }) => {
  const nombreUsuario = localStorage.getItem('nombre_usuario') || 'Usuario';
  const rol = localStorage.getItem('rol') || 'docente';
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [menuAbierto, setMenuAbierto] = useState(false);
  const location = useLocation();

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

  // Verificar si una ruta está activa
  const isActive = (path) => location.pathname === path;

  return (
    <div className="intranet-layout-root">
      <style>{`
        .intranet-layout-root {
          min-height: 100vh;
          background-color: ${theme?.colors?.bg || '#f8fafc'} !important;
          font-family: 'Inter', -apple-system, sans-serif !important;
          display: flex;
          flex-direction: column;
        }

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
        }

        .btn-logout-action:hover {
          background-color: #dc2626 !important;
        }

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

        .layout-body-wrapper {
          display: flex !important;
          flex: 1 !important;
        }

        .desktop-sidebar {
          width: 260px !important;
          background-color: #0f172a !important;
          min-height: calc(100vh - 62px) !important;
          padding: 24px 16px !important;
          box-sizing: border-box !important;
          display: flex !important;
          flex-direction: column !important;
          gap: 4px !important;
          border-right: 1px solid #1e293b !important;
        }

        .sidebar-section-title {
          color: #475569 !important;
          font-size: 11px !important;
          font-weight: 800 !important;
          padding: 0 12px !important;
          margin-top: 16px !important;
          margin-bottom: 8px !important;
          text-transform: uppercase !important;
          letter-spacing: 0.75px !important;
        }

        .sidebar-link {
          color: #94a3b8 !important;
          text-decoration: none !important;
          padding: 11px 14px !important;
          border-radius: 10px !important;
          display: flex !important;
          align-items: center !important;
          gap: 10px !important;
          font-size: 13px !important;
          font-weight: 600 !important;
          transition: all 0.2s ease !important;
        }

        .sidebar-link:hover {
          background-color: #1e293b !important;
          color: #f1f5f9 !important;
        }

        .sidebar-link.active {
          background-color: #1e3a8a !important;
          color: #ffffff !important;
          box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15) !important;
        }

        .main-content-viewport {
          flex: 1 !important;
          box-sizing: border-box !important;
          overflow-x: hidden !important;
        }

        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* HEADER */}
      <header className="intranet-header">
        <div className="header-brand-group">
          {isMobile && (
            <button onClick={() => setMenuAbierto(!menuAbierto)} className="btn-hamburger" aria-label="Abrir menú">
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
          <button onClick={cerrarSesion} className="btn-logout-action">Salir</button>
        </div>
      </header>

      {/* MENÚ MÓVIL */}
      {isMobile && menuAbierto && (
        <nav className="mobile-nav-menu">
          {rol === 'admin' && (
            <>
              <Link to="/admin/usuarios" onClick={() => setMenuAbierto(false)} className={`mobile-nav-link ${isActive('/admin/usuarios') ? 'active' : ''}`}>👥 Gestión Usuarios</Link>
              <Link to="/admin/alumnos" onClick={() => setMenuAbierto(false)} className={`mobile-nav-link ${isActive('/admin/alumnos') ? 'active' : ''}`}>📝 Matrícula Alumnos</Link>
              <Link to="/admin/apoderados" onClick={() => setMenuAbierto(false)} className={`mobile-nav-link ${isActive('/admin/apoderados') ? 'active' : ''}`}>👨‍👩‍👦 Apoderados</Link>
              <Link to="/admin/asignaciones" onClick={() => setMenuAbierto(false)} className={`mobile-nav-link ${isActive('/admin/asignaciones') ? 'active' : ''}`}>🔗 Asignaciones</Link>
              <Link to="/admin/aulas" onClick={() => setMenuAbierto(false)} className={`mobile-nav-link ${isActive('/admin/aulas') ? 'active' : ''}`}>🏫 Aulas</Link>
              <Link to="/admin/cursos" onClick={() => setMenuAbierto(false)} className={`mobile-nav-link ${isActive('/admin/cursos') ? 'active' : ''}`}>📚 Cursos</Link>
            </>
          )}
          <Link to="/asistencia" onClick={() => setMenuAbierto(false)} className={`mobile-nav-link ${isActive('/asistencia') ? 'active' : ''}`}>✅ Asistencia</Link>
        </nav>
      )}

      {/* CUERPO */}
      <div className="layout-body-wrapper">
        {/* SIDEBAR ESCRITORIO */}
        {!isMobile && (
          <aside className="desktop-sidebar">
            {rol === 'admin' && (
              <>
                <div className="sidebar-section-title">👑 Administración</div>
                <Link to="/admin/usuarios" className={`sidebar-link ${isActive('/admin/usuarios') ? 'active' : ''}`}>
                  <span>👥</span> Gestión de Usuarios
                </Link>
                <Link to="/admin/alumnos" className={`sidebar-link ${isActive('/admin/alumnos') ? 'active' : ''}`}>
                  <span>📝</span> Matrícula de Alumnos
                </Link>
                <Link to="/admin/apoderados" className={`sidebar-link ${isActive('/admin/apoderados') ? 'active' : ''}`}>
                  <span>👨‍👩‍👦</span> Registro Apoderados
                </Link>
                <Link to="/admin/asignaciones" className={`sidebar-link ${isActive('/admin/asignaciones') ? 'active' : ''}`}>
                  <span>🔗</span> Asignar Cargos
                </Link>
              </>
            )}

            <div className="sidebar-section-title">🏫 Académico</div>
            <Link to="/admin/aulas" className={`sidebar-link ${isActive('/admin/aulas') ? 'active' : ''}`}>
              <span>🏫</span> Aulas y Secciones
            </Link>
            <Link to="/admin/cursos" className={`sidebar-link ${isActive('/admin/cursos') ? 'active' : ''}`}>
              <span>📚</span> Cursos
            </Link>

            <div className="sidebar-section-title">✅ Operaciones</div>
            <Link to="/asistencia" className={`sidebar-link ${isActive('/asistencia') ? 'active' : ''}`}>
              <span>✅</span> Tomar Asistencia
            </Link>
            <Link to="/justificaciones" className={`sidebar-link ${isActive('/justificaciones') ? 'active' : ''}`}>
              <span>📝</span> Justificaciones
            </Link>
            <Link to="/alertas" className={`sidebar-link ${isActive('/alertas') ? 'active' : ''}`}>
              <span>🔔</span> Alertas
            </Link>
          </aside>
        )}

        {/* CONTENIDO PRINCIPAL */}
        <main className="main-content-viewport" style={{ padding: isMobile ? '20px 16px' : '32px' }}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default NavbarLayout;