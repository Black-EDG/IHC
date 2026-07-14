import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// ═══════════════════════════════════════════════════════════════
// ICONOS SVG
// ═══════════════════════════════════════════════════════════════
const HomeIcon = () => (
  <svg style={{ width: '20px', height: '20px', minWidth: '20px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
  </svg>
);

const AcademicIcon = () => (
  <svg style={{ width: '20px', height: '20px', minWidth: '20px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
  </svg>
);

const UserGroupIcon = () => (
  <svg style={{ width: '20px', height: '20px', minWidth: '20px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v1h8v-1zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-1a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v1h-3zM4.75 12.094A5.973 5.973 0 004 15v1H1v-1a3 3 0 013.75-2.906z" />
  </svg>
);

const UsersIcon = () => (
  <svg style={{ width: '20px', height: '20px', minWidth: '20px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
  </svg>
);

const LinkIcon = () => (
  <svg style={{ width: '20px', height: '20px', minWidth: '20px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clipRule="evenodd" />
  </svg>
);

const BuildingIcon = () => (
  <svg style={{ width: '20px', height: '20px', minWidth: '20px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 01-1 1h-2a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd" />
  </svg>
);

const BellIcon = () => (
  <svg style={{ width: '20px', height: '20px', minWidth: '20px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
  </svg>
);

const DocumentIcon = () => (
  <svg style={{ width: '20px', height: '20px', minWidth: '20px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
  </svg>
);

const LogoutIcon = () => (
  <svg style={{ width: '20px', height: '20px', minWidth: '20px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h5a1 1 0 001-1V3a1 1 0 00-1-1H3zm10.293 3.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L14.586 11H7a1 1 0 110-2h7.586l-1.293-1.293a1 1 0 010-1.414z" clipRule="evenodd" />
  </svg>
);

const BarsIcon = () => (
  <svg style={{ width: '24px', height: '24px', minWidth: '24px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
  </svg>
);

const CloseIcon = () => (
  <svg style={{ width: '24px', height: '24px', minWidth: '24px' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
  </svg>
);

// ═══════════════════════════════════════════════════════════════
// COMPONENTE PRINCIPAL
// ═══════════════════════════════════════════════════════════════
const AdminLayout = () => {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', to: '/admin', icon: HomeIcon },
    { name: 'Alumnos', to: '/admin/alumnos', icon: AcademicIcon },
    { name: 'Apoderados', to: '/admin/apoderados', icon: UserGroupIcon },
    { name: 'Usuarios', to: '/admin/usuarios', icon: UsersIcon },
    { name: 'Asignar Cargos', to: '/admin/asignaciones', icon: LinkIcon },
    { name: 'Aulas', to: '/admin/aulas', icon: BuildingIcon },
    { name: 'Alertas', to: '/admin/alertas', icon: BellIcon },
    { name: 'Justificaciones', to: '/admin/justificaciones', icon: DocumentIcon },
  ];

  return (
    <div className="admin-layout-root">
      <style>{`
        .admin-layout-root {
          display: flex;
          min-height: 100vh;
          background-color: #f8fafc !important;
          font-family: 'Inter', -apple-system, sans-serif;
        }
        .admin-layout-root svg {
          display: inline-block !important;
          vertical-align: middle !important;
          flex-shrink: 0 !important;
        }
        .layout-sidebar {
          width: 260px !important;
          background-color: #ffffff !important;
          border-right: 1px solid #e2e8f0 !important;
          position: fixed !important;
          height: 100vh !important;
          left: 0 !important;
          top: 0 !important;
          z-index: 50 !important;
          display: flex !important;
          flex-direction: column !important;
          box-shadow: 4px 0 24px rgba(15, 23, 42, 0.015) !important;
        }
        .sidebar-brand-box {
          padding: 24px !important;
          border-bottom: 1px solid #f1f5f9 !important;
        }
        .brand-title {
          font-size: 20px !important;
          font-weight: 800 !important;
          color: #4f46e5 !important;
          margin: 0 !important;
          letter-spacing: -0.5px;
        }
        .brand-subtitle {
          font-size: 12px !important;
          color: #64748b !important;
          margin: 4px 0 0 0 !important;
        }
        .sidebar-nav {
          flex: 1 !important;
          padding: 20px 16px !important;
          display: flex !important;
          flex-direction: column !important;
          gap: 6px !important;
          overflow-y: auto !important;
        }
        .nav-item-link {
          display: flex !important;
          align-items: center !important;
          gap: 12px !important;
          padding: 12px 16px !important;
          color: #64748b !important;
          text-decoration: none !important;
          font-size: 14px !important;
          font-weight: 600 !important;
          border-radius: 12px !important;
          transition: all 0.2s ease !important;
        }
        .nav-item-link:hover {
          background-color: #f1f5f9 !important;
          color: #0f172a !important;
        }
        .nav-item-link.active {
          background-color: #eef2ff !important;
          color: #4f46e5 !important;
        }
        .sidebar-footer {
          padding: 16px !important;
          border-top: 1px solid #f1f5f9 !important;
        }
        .btn-logout {
          display: flex !important;
          align-items: center !important;
          gap: 12px !important;
          width: 100% !important;
          padding: 12px 16px !important;
          background: none !important;
          border: none !important;
          color: #ef4444 !important;
          font-size: 14px !important;
          font-weight: 600 !important;
          text-align: left !important;
          cursor: pointer !important;
          border-radius: 12px !important;
          transition: all 0.2s ease !important;
        }
        .btn-logout:hover {
          background-color: #fef2f2 !important;
        }
        .layout-main-area {
          flex: 1 1 0% !important;
          margin-left: 260px !important;
          display: flex !important;
          flex-direction: column !important;
          min-width: 0 !important;
        }
        .mobile-header {
          display: none !important;
          background-color: #ffffff !important;
          border-bottom: 1px solid #e2e8f0 !important;
          padding: 16px 20px !important;
          align-items: center !important;
          justify-content: space-between !important;
          position: sticky !important;
          top: 0 !important;
          z-index: 40 !important;
        }
        .btn-menu-toggle {
          background: none !important;
          border: none !important;
          color: #334155 !important;
          cursor: pointer !important;
          padding: 4px !important;
          display: flex !important;
          align-items: center !important;
        }
        .mobile-brand-title {
          font-size: 18px !important;
          font-weight: 800 !important;
          color: #4f46e5 !important;
          margin: 0 !important;
        }
        .mobile-overlay {
          position: fixed !important;
          inset: 0 !important;
          background-color: rgba(15, 23, 42, 0.4) !important;
          backdrop-filter: blur(4px) !important;
          z-index: 100 !important;
          display: flex !important;
        }
        .mobile-sidebar {
          width: 280px !important;
          background-color: #ffffff !important;
          height: 100% !important;
          padding: 24px !important;
          display: flex !important;
          flex-direction: column !important;
          box-shadow: 4px 0 24px rgba(0,0,0,0.1) !important;
        }
        .btn-close-menu {
          background: none !important;
          border: none !important;
          color: #64748b !important;
          cursor: pointer !important;
          padding: 4px !important;
          align-self: flex-end !important;
          margin-bottom: 24px !important;
          display: flex !important;
        }
        @media (max-width: 768px) {
          .layout-sidebar { display: none !important; }
          .layout-main-area { margin-left: 0 !important; }
          .mobile-header { display: flex !important; }
        }
      `}</style>

      {/* SIDEBAR ESCRITORIO */}
      <aside className="layout-sidebar">
        <div className="sidebar-brand-box">
          <h2 className="brand-title">Admin Panel</h2>
          <p className="brand-subtitle">{user?.correo || 'admin@colegio.edu'}</p>
        </div>
        <nav className="sidebar-nav">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/admin'}
              className={({ isActive }) => `nav-item-link ${isActive ? 'active' : ''}`}
            >
              <item.icon />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button onClick={logout} className="btn-logout">
            <LogoutIcon />
            <span>Cerrar sesión</span>
          </button>
        </div>
      </aside>

      {/* SIDEBAR MÓVIL */}
      {sidebarOpen && (
        <div className="mobile-overlay" onClick={() => setSidebarOpen(false)}>
          <aside className="mobile-sidebar" onClick={(e) => e.stopPropagation()}>
            <button className="btn-close-menu" onClick={() => setSidebarOpen(false)}>
              <CloseIcon />
            </button>
            <nav className="sidebar-nav" style={{ padding: 0 }}>
              {navigation.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/admin'}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) => `nav-item-link ${isActive ? 'active' : ''}`}
                >
                  <item.icon />
                  <span>{item.name}</span>
                </NavLink>
              ))}
              <div style={{ borderTop: '1px solid #f1f5f9', marginTop: '16px', paddingTop: '16px' }}>
                <button onClick={logout} className="btn-logout">
                  <LogoutIcon />
                  <span>Cerrar sesión</span>
                </button>
              </div>
            </nav>
          </aside>
        </div>
      )}

      {/* CONTENIDO PRINCIPAL */}
      <div className="layout-main-area">
        <header className="mobile-header">
          <button className="btn-menu-toggle" onClick={() => setSidebarOpen(true)}>
            <BarsIcon />
          </button>
          <h1 className="mobile-brand-title">Admin</h1>
          <div style={{ width: '24px' }} />
        </header>

        <main style={{ padding: '24px', boxSizing: 'border-box' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;