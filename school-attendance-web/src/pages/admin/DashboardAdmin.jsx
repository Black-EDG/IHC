import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// LIMITAMOS EL TAMAÑO DIRECTAMENTE EN EL SVG (width y height inline obligatorios)
const Icons = {
  Aulas: () => (
    <svg style={{ width: '22px', height: '22px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    </svg>
  ),
  Alumnos: () => (
    <svg style={{ width: '22px', height: '22px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
    </svg>
  ),
  Personal: () => (
    <svg style={{ width: '22px', height: '22px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  ),
  Apoderados: () => (
    <svg style={{ width: '22px', height: '22px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>
  ),
  ArrowRight: () => (
    <svg style={{ width: '16px', height: '16px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
    </svg>
  )
};

const DashboardAdmin = () => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    aulas: 0,
    alumnos: 0,
    personal: 0,
    apoderados: 0,
  });
  const [loading, setLoading] = useState(true);

  const getInitials = () => {
    if (user?.nombres) {
      const parts = user.nombres.trim().split(/\s+/);
      return parts.length > 1 ? `${parts[0][0]}${parts[1][0]}`.toUpperCase() : parts[0][0].toUpperCase();
    }
    return 'AD';
  };

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const aulasRes = await axios.get(`${API_URL}/aulas`, { headers });
        setStats({
          aulas: Array.isArray(aulasRes.data) ? aulasRes.data.length : 0,
          alumnos: 0,
          personal: 0,
          apoderados: 0,
        });
      } catch (error) {
        console.error('Error al cargar estadísticas', error);
      } finally {
        setLoading(false);
      }
    };
    if (token) {
      fetchStats();
    } else {
      // Si no hay token cargado todavía (o estás probando local), quitamos el loading para ver el diseño
      setLoading(false);
    }
  }, [token]);

  return (
    <div className="dashboard-container">
      {/* CSS Inyectado */}
      <style>{`
        .dashboard-container {
          min-height: 100vh;
          background-color: #f8fafc;
          font-family: 'Inter', -apple-system, sans-serif;
          padding: 40px 24px;
          box-sizing: border-box;
          color: #0f172a;
        }

        .dashboard-header {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 20px;
          padding: 32px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 32px;
          box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
          flex-wrap: wrap;
          gap: 20px;
        }

        .header-profile {
          display: flex;
          align-items: center;
          gap: 20px;
        }

        .profile-avatar {
          width: 64px;
          height: 64px;
          background: linear-gradient(135deg, #4f46e5, #6366f1);
          color: #ffffff;
          font-size: 22px;
          font-weight: 700;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .profile-welcome {
          font-size: 24px;
          font-weight: 800;
          color: #0f172a;
          margin: 0;
        }

        .profile-sub {
          font-size: 14px;
          color: #64748b;
          margin: 4px 0 0 0;
        }

        .header-badge {
          display: flex;
          align-items: center;
          gap: 8px;
          background: #f1f5f9;
          border: 1px solid #e2e8f0;
          padding: 10px 18px;
          border-radius: 9999px;
          font-size: 12px;
          font-weight: 600;
          color: #334155;
        }

        .badge-dot {
          width: 8px;
          height: 8px;
          background-color: #10b981;
          border-radius: 50%;
        }

        .loader-wrapper {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 100px 0;
        }

        .spinner {
          width: 48px;
          height: 48px;
          border: 4px solid #e2e8f0;
          border-top-color: #4f46e5;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 24px;
          margin-bottom: 32px;
        }

        .card-stat {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 20px;
          padding: 24px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.01);
          transition: all 0.2s ease;
          display: flex;
          flex-direction: column;
        }

        .card-stat:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 20px rgba(0,0,0,0.05);
        }

        .stat-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .stat-title {
          font-size: 12px;
          font-weight: 700;
          text-transform: uppercase;
          color: #64748b;
        }

        .icon-container {
          width: 44px;
          height: 44px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .blue .icon-container { background: #eff6ff; color: #3b82f6; }
        .emerald .icon-container { background: #ecfdf5; color: #10b981; }
        .purple .icon-container { background: #f5f3ff; color: #8b5cf6; }
        .amber .icon-container { background: #fffbeb; color: #f59e0b; }

        .stat-number {
          font-size: 36px;
          font-weight: 800;
          color: #0f172a;
          margin: 8px 0;
        }

        .stat-pill {
          display: inline-block;
          font-size: 11px;
          font-weight: 600;
          padding: 4px 10px;
          border-radius: 9999px;
          align-self: flex-start;
        }

        .blue .stat-pill { background: #eff6ff; color: #3b82f6; }
        .emerald .stat-pill { background: #ecfdf5; color: #10b981; }
        .purple .stat-pill { background: #f5f3ff; color: #8b5cf6; }
        .amber .stat-pill { background: #fffbeb; color: #f59e0b; }

        .actions-panel {
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 24px;
          padding: 36px;
        }

        .panel-header {
          margin-bottom: 28px;
        }

        .panel-title {
          font-size: 20px;
          font-weight: 800;
          margin: 0;
        }

        .panel-desc {
          font-size: 14px;
          color: #64748b;
          margin: 6px 0 0 0;
        }

        .actions-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 20px;
        }

        .btn-action {
          background: #fafafa;
          border: 1px solid #e2e8f0;
          border-radius: 18px;
          padding: 24px;
          text-align: left;
          cursor: pointer;
          display: flex;
          flex-direction: column;
          height: 170px;
          justify-content: space-between;
          box-sizing: border-box;
          transition: all 0.2s ease;
        }

        .btn-action:hover {
          background: #ffffff;
          transform: translateY(-4px);
          box-shadow: 0 10px 15px rgba(0, 0, 0, 0.05);
        }

        .btn-blue:hover { border-color: #3b82f6; }
        .btn-emerald:hover { border-color: #10b981; }
        .btn-purple:hover { border-color: #8b5cf6; }
        .btn-amber:hover { border-color: #f59e0b; }

        .action-icon {
          width: 44px;
          height: 44px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .btn-blue .action-icon { background: #eff6ff; color: #3b82f6; }
        .btn-emerald .action-icon { background: #ecfdf5; color: #10b981; }
        .btn-purple .action-icon { background: #f5f3ff; color: #8b5cf6; }
        .btn-amber .action-icon { background: #fffbeb; color: #f59e0b; }

        .btn-blue:hover .action-icon { background: #3b82f6; color: #ffffff; }
        .btn-emerald:hover .action-icon { background: #10b981; color: #ffffff; }
        .btn-purple:hover .action-icon { background: #8b5cf6; color: #ffffff; }
        .btn-amber:hover .action-icon { background: #f59e0b; color: #ffffff; }

        .action-title {
          font-size: 15px;
          font-weight: 700;
          margin: 12px 0 4px 0;
        }

        .action-desc {
          font-size: 12px;
          color: #64748b;
          margin: 0;
          line-height: 1.4;
        }

        .action-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-top: 1px solid #f1f5f9;
          padding-top: 12px;
          margin-top: 12px;
          width: 100%;
        }

        .footer-lbl {
          font-size: 12px;
          font-weight: 600;
        }

        .btn-blue .footer-lbl { color: #3b82f6; }
        .btn-emerald .footer-lbl { color: #10b981; }
        .btn-purple .footer-lbl { color: #8b5cf6; }
        .btn-amber .footer-lbl { color: #f59e0b; }

        .btn-action:hover .arrow-svg {
          transform: translateX(4px);
        }

        @media (max-width: 768px) {
          .dashboard-container { padding: 20px 16px; }
          .dashboard-header { padding: 24px; flex-direction: column; align-items: flex-start; }
          .stats-grid { grid-template-columns: 1fr; }
          .actions-grid { grid-template-columns: 1fr; }
        }
      `}</style>

      {/* 1. CABECERA */}
      <div className="dashboard-header">
        <div className="header-profile">
          <div className="profile-avatar">{getInitials()}</div>
          <div>
            <h1 className="profile-welcome">Bienvenido, {user?.nombres || 'Admin Panel'}</h1>
            <p className="profile-sub">
              {user?.correo || 'admin.central@colegio.edu.pe'}
            </p>
          </div>
        </div>
        <div className="header-badge">
          <div className="badge-dot"></div>
          <span>Servidor en línea</span>
        </div>
      </div>

      {loading ? (
        <div className="loader-wrapper">
          <div className="spinner"></div>
        </div>
      ) : (
        <>
          {/* 2. GRID DE ESTADÍSTICAS */}
          <div className="stats-grid">
            {/* Aulas */}
            <div className="card-stat blue">
              <div className="stat-meta">
                <span className="stat-title">Aulas</span>
                <div className="icon-container">
                  <Icons.Aulas />
                </div>
              </div>
              <p className="stat-number">{stats.aulas}</p>
              <span className="stat-pill">Secciones</span>
            </div>

            {/* Alumnos */}
            <div className="card-stat emerald">
              <div className="stat-meta">
                <span className="stat-title">Alumnos</span>
                <div className="icon-container">
                  <Icons.Alumnos />
                </div>
              </div>
              <p className="stat-number">{stats.alumnos > 0 ? stats.alumnos : '--'}</p>
              <span className="stat-pill">Matriculados</span>
            </div>

            {/* Personal */}
            <div className="card-stat purple">
              <div className="stat-meta">
                <span className="stat-title">Personal</span>
                <div className="icon-container">
                  <Icons.Personal />
                </div>
              </div>
              <p className="stat-number">{stats.personal > 0 ? stats.personal : '--'}</p>
              <span className="stat-pill">Docentes</span>
            </div>

            {/* Apoderados */}
            <div className="card-stat amber">
              <div className="stat-meta">
                <span className="stat-title">Apoderados</span>
                <div className="icon-container">
                  <Icons.Apoderados />
                </div>
              </div>
              <p className="stat-number">{stats.apoderados > 0 ? stats.apoderados : '--'}</p>
              <span className="stat-pill">Responsables</span>
            </div>
          </div>

          {/* 3. MÓDULOS */}
          <div className="actions-panel">
            <div className="panel-header">
              <h2 className="panel-title">Módulos Administrativos</h2>
              <p className="panel-desc">Selecciona un acceso para comenzar con la gestión del plantel.</p>
            </div>

            <div className="actions-grid">
              <div className="btn-action btn-blue" onClick={() => navigate('/admin/alumnos')}>
                <div className="action-icon">
                  <Icons.Alumnos />
                </div>
                <div>
                  <h3 className="action-title">Matricular Alumno</h3>
                  <p className="action-desc">Ficha de matrícula y asignación.</p>
                </div>
                <div className="action-footer">
                  <span className="footer-lbl">Ingresar</span>
                  <Icons.ArrowRight />
                </div>
              </div>

              <div className="btn-action btn-emerald" onClick={() => navigate('/admin/apoderados')}>
                <div className="action-icon">
                  <Icons.Apoderados />
                </div>
                <div>
                  <h3 className="action-title">Registrar Apoderado</h3>
                  <p className="action-desc">Asociar datos familiares y tutores.</p>
                </div>
                <div className="action-footer">
                  <span className="footer-lbl">Ingresar</span>
                  <Icons.ArrowRight />
                </div>
              </div>

              <div className="btn-action btn-purple" onClick={() => navigate('/admin/usuarios')}>
                <div className="action-icon">
                  <Icons.Personal />
                </div>
                <div>
                  <h3 className="action-title">Gestionar Personal</h3>
                  <p className="action-desc">Administrar accesos de docentes.</p>
                </div>
                <div className="action-footer">
                  <span className="footer-lbl">Ingresar</span>
                  <Icons.ArrowRight />
                </div>
              </div>

              <div className="btn-action btn-amber" onClick={() => navigate('/admin/aulas')}>
                <div className="action-icon">
                  <Icons.Aulas />
                </div>
                <div>
                  <h3 className="action-title">Gestionar Aulas</h3>
                  <p className="action-desc">Definir secciones y turnos.</p>
                </div>
                <div className="action-footer">
                  <span className="footer-lbl">Ingresar</span>
                  <Icons.ArrowRight />
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DashboardAdmin;