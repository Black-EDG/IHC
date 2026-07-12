import React, { useState, useEffect } from 'react';
import { theme } from '../theme';

const NavbarLayout = ({ children }) => {
  const nombreUsuario = localStorage.getItem('nombre_usuario') || 'Usuario';
  const rol = localStorage.getItem('rol') || 'docente';
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [menuAbierto, setMenuAbierto] = useState(false);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const cerrarSesion = () => {
    localStorage.clear();
    window.location.href = '/';
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: theme.colors.bg, fontFamily: 'sans-serif' }}>
      {/* Barra de Navegación Superior */}
      <header style={{
        backgroundColor: theme.colors.primary, color: 'white', padding: '15px 20px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        position: 'sticky', top: 0, zIndex: 100, boxShadow: theme.shadows.card
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          {isMobile && (
            <button 
              onClick={() => setMenuAbierto(!menuAbierto)}
              style={{ backgroundColor: 'transparent', border: 'none', color: 'white', fontSize: '24px', cursor: 'pointer' }}
            >
              ☰
            </button>
          )}
          <span style={{ fontSize: '20px', fontWeight: 'bold', letterSpacing: '0.5px' }}>Intranet Escolar</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          {!isMobile && (
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontWeight: '600', fontSize: '15px' }}>{nombreUsuario}</div>
              <div style={{ fontSize: '12px', color: '#93c5fd', textTransform: 'uppercase' }}>{rol}</div>
            </div>
          )}
          <button 
            onClick={cerrarSesion}
            style={{
              backgroundColor: '#ef4444', color: 'white', border: 'none',
              padding: '8px 14px', borderRadius: '6px', fontSize: '13px', fontWeight: 'bold', cursor: 'pointer'
            }}
          >
            Salir
          </button>
        </div>
      </header>

      {/* Menú de navegación móvil */}
      {isMobile && menuAbierto && (
        <div style={{ backgroundColor: '#1e293b', padding: '15px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {rol === 'admin' && (
            <>
              <a href="/admin/alumnos" style={{ color: 'white', textDecoration: 'none', padding: '10px', borderRadius: '4px' }}>Matrícula Alumnos</a>
              <a href="/admin/apoderados" style={{ color: 'white', textDecoration: 'none', padding: '10px', borderRadius: '4px' }}>Registrar Apoderados</a>
            </>
          )}
          <a href="/asistencia" style={{ color: 'white', textDecoration: 'none', padding: '10px', borderRadius: '4px' }}>Tomar Asistencia</a>
        </div>
      )}

      {/* Barra lateral para modo Escritorio */}
      <div style={{ display: 'flex' }}>
        {!isMobile && (
          <aside style={{
            width: '240px', backgroundColor: '#1f2937', minHeight: 'calc(100vh - 62px)',
            padding: '20px 10px', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: '8px'
          }}>
            {rol === 'admin' && (
              <>
                <div style={{ color: '#4b5563', fontSize: '12px', fontWeight: 'bold', padding: '0 10px', marginBottom: '5px', textTransform: 'uppercase' }}>Administración</div>
                <a href="/admin/alumnos" style={{ color: '#d1d5db', textDecoration: 'none', padding: '12px 10px', borderRadius: '6px', display: 'block', fontWeight: '500', backgroundColor: window.location.pathname === '/admin/alumnos' ? '#374151' : 'transparent' }}>📝 Matrícula de Alumnos</a>
                <a href="/admin/apoderados" style={{ color: '#d1d5db', textDecoration: 'none', padding: '12px 10px', borderRadius: '6px', display: 'block', fontWeight: '500', backgroundColor: window.location.pathname === '/admin/apoderados' ? '#374151' : 'transparent' }}>👨‍👩‍👦 Registro Apoderados</a>
                <div style={{ height: '15px' }}></div>
              </>
            )}
            <div style={{ color: '#4b5563', fontSize: '12px', fontWeight: 'bold', padding: '0 10px', marginBottom: '5px', textTransform: 'uppercase' }}>Operaciones</div>
            <a href="/asistencia" style={{ color: '#d1d5db', textDecoration: 'none', padding: '12px 10px', borderRadius: '6px', display: 'block', fontWeight: '500', backgroundColor: window.location.pathname === '/asistencia' ? '#374151' : 'transparent' }}>✅ Tomar Asistencia</a>
          </aside>
        )}

        {/* Área de Contenido Principal */}
        <main style={{ flex: 1, padding: isMobile ? '15px' : '30px', boxSizing: 'border-box', overflowX: 'hidden' }}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default NavbarLayout;