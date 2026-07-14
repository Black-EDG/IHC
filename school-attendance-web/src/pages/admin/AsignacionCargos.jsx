import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { theme } from '../../theme';

const AsignacionCargos = () => {
  const [asignaciones, setAsignaciones] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [aulas, setAulas] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  const [asignacion, setAsignacion] = useState({
    usuario_id: '',
    aula_id: '',
    curso_id: '',
    tipo_cargo: 'docente_curso'
  });

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    cargarDatos();
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const cargarDatos = async () => {
    try {
      const [resAsig, resUsu, resAulas, resCursos] = await Promise.all([
        axios.get(`${API_URL}/asignaciones/`, { headers }),
        axios.get(`${API_URL}/usuarios/`, { headers }),
        axios.get(`${API_URL}/aulas/`, { headers }),
        axios.get(`${API_URL}/cursos/`, { headers })
      ]);
      setAsignaciones(resAsig.data);
      setUsuarios(resUsu.data);
      setAulas(resAulas.data);
      setCursos(resCursos.data);
    } catch (err) {
      console.error("Error al cargar datos:", err);
      setMensaje({ tipo: 'error', texto: 'Error al cargar datos del servidor.' });
    }
  };

  const guardarAsignacion = async (e) => {
    e.preventDefault();
    setMensaje({ tipo: '', texto: '' });

    if (!asignacion.usuario_id || !asignacion.aula_id) {
      setMensaje({ tipo: 'error', texto: 'Debe seleccionar un usuario y un aula.' });
      return;
    }

    if (asignacion.tipo_cargo === 'docente_curso' && !asignacion.curso_id) {
      setMensaje({ tipo: 'error', texto: 'Para docente_curso debe seleccionar un curso.' });
      return;
    }

    const payload = {
      usuario_id: parseInt(asignacion.usuario_id, 10),
      aula_id: parseInt(asignacion.aula_id, 10),
      tipo_cargo: asignacion.tipo_cargo,
      curso_id: asignacion.tipo_cargo === 'docente_curso' 
        ? parseInt(asignacion.curso_id, 10) 
        : null
    };

    try {
      await axios.post(`${API_URL}/asignaciones/`, payload, { headers });
      setMensaje({ tipo: 'exito', texto: '¡Asignación vinculada con éxito!' });
      setAsignacion({ usuario_id: '', aula_id: '', curso_id: '', tipo_cargo: 'docente_curso' });
      cargarDatos();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error al crear la asignación.';
      setMensaje({ tipo: 'error', texto: errorMsg });
    }
  };

  const eliminarAsignacion = async (id) => {
    if (!window.confirm('¿Eliminar esta asignación?')) return;
    try {
      await axios.delete(`${API_URL}/asignaciones/${id}`, { headers });
      setMensaje({ tipo: 'exito', texto: 'Asignación eliminada.' });
      cargarDatos();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: 'Error al eliminar.' });
    }
  };

  const tipoCargoLegible = (tipo) => {
    const nombres = {
      'docente_curso': 'Docente de Curso',
      'tutor_seccion': 'Tutor de Sección',
      'auxiliar_grado': 'Auxiliar de Grado'
    };
    return nombres[tipo] || tipo;
  };

  return (
    <div className="cargos-container">
      <style>{`
        .cargos-container {
          font-family: 'Inter', -apple-system, sans-serif !important;
        }
        .cargos-header {
          margin-bottom: 28px !important;
        }
        .cargos-header h2 {
          color: ${theme?.colors?.primary || '#1e3a8a'} !important;
          font-size: 24px !important;
          font-weight: 800 !important;
          margin: 0 0 6px 0 !important;
          letter-spacing: -0.5px !important;
        }
        .cargos-header p {
          color: ${theme?.colors?.textLight || '#64748b'} !important;
          font-size: 14px !important;
          margin: 0 !important;
        }
        .alert-box {
          padding: 14px 20px !important;
          border-radius: 12px !important;
          margin-bottom: 24px !important;
          font-size: 14px !important;
          font-weight: 600 !important;
          display: flex !important;
          align-items: center !important;
          gap: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
        }
        .alert-exito {
          background-color: #ecfdf5 !important;
          color: #065f46 !important;
          border: 1px solid #a7f3d0 !important;
        }
        .alert-error {
          background-color: #fef2f2 !important;
          color: #991b1b !important;
          border: 1px solid #fca5a5 !important;
        }
        .cargos-grid {
          display: grid !important;
          grid-template-columns: ${isMobile ? '1fr' : '1fr 2fr'} !important;
          gap: 28px !important;
        }
        .cargo-card {
          background-color: #ffffff !important;
          padding: 24px !important;
          border-radius: 16px !important;
          border: 1px solid ${theme?.colors?.border || '#e2e8f0'} !important;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
          height: fit-content !important;
        }
        .cargo-card-title {
          margin: 0 0 20px 0 !important;
          color: ${theme?.colors?.text || '#0f172a'} !important;
          font-size: 16px !important;
          font-weight: 700 !important;
        }
        .form-group {
          margin-bottom: 16px !important;
        }
        .form-group label {
          display: block !important;
          font-size: 13px !important;
          font-weight: 600 !important;
          color: #475569 !important;
          margin-bottom: 6px !important;
        }
        .input-custom {
          width: 100% !important;
          padding: 10px 14px !important;
          border-radius: 10px !important;
          border: 1px solid ${theme?.colors?.border || '#cbd5e1'} !important;
          box-sizing: border-box !important;
          font-size: 14px !important;
          outline: none !important;
          color: #334155 !important;
          transition: all 0.2s ease !important;
          background-color: #f8fafc !important;
          cursor: pointer;
        }
        .input-custom:focus {
          border-color: ${theme?.colors?.secondary || '#3b82f6'} !important;
          background-color: #ffffff !important;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
        }
        .btn-vincular {
          width: 100% !important;
          background-color: ${theme?.colors?.secondary || '#2563eb'} !important;
          color: white !important;
          border: none !important;
          padding: 12px !important;
          border-radius: 10px !important;
          font-size: 14px !important;
          font-weight: 700 !important;
          cursor: pointer !important;
          margin-top: 8px !important;
          transition: all 0.2s ease !important;
        }
        .btn-vincular:hover {
          opacity: 0.95 !important;
          transform: translateY(-1px) !important;
        }
        .btn-eliminar {
          background: #ef4444 !important;
          color: white !important;
          border: none !important;
          padding: 6px 12px !important;
          border-radius: 8px !important;
          cursor: pointer !important;
          font-size: 12px !important;
          font-weight: 600 !important;
        }
        .btn-eliminar:hover {
          background: #dc2626 !important;
        }
        .table-wrapper {
          overflow-x: auto !important;
        }
        .custom-table {
          width: 100% !important;
          border-collapse: separate !important;
          border-spacing: 0 !important;
          text-align: left !important;
        }
        .custom-table th {
          background-color: #f8fafc !important;
          color: #64748b !important;
          font-size: 12px !important;
          font-weight: 700 !important;
          text-transform: uppercase !important;
          letter-spacing: 0.5px !important;
          padding: 14px 16px !important;
          border-bottom: 2px solid ${theme?.colors?.border || '#e2e8f0'} !important;
        }
        .custom-table td {
          padding: 14px 16px !important;
          font-size: 14px !important;
          color: #334155 !important;
          border-bottom: 1px solid ${theme?.colors?.border || '#f1f5f9'} !important;
          vertical-align: middle !important;
        }
        .custom-table tr:last-child td {
          border-bottom: none !important;
        }
        .custom-table tr:hover td {
          background-color: #fafbfc !important;
        }
        .badge-cargo {
          display: inline-block !important;
          padding: 6px 10px !important;
          border-radius: 8px !important;
          font-size: 11px !important;
          font-weight: 700 !important;
          text-transform: uppercase !important;
        }
        .badge-docente { background-color: #e0f2fe !important; color: #0369a1 !important; }
        .badge-tutor { background-color: #d1fae5 !important; color: #065f46 !important; }
        .badge-auxiliar { background-color: #fef3c7 !important; color: #b45309 !important; }
      `}</style>

      <div className="cargos-header">
        <h2>🔑 Asignación de Responsabilidades y Salones</h2>
        <p>Vincula personal de la intranet con sus respectivas aulas y cursos.</p>
      </div>

      {mensaje.texto && (
        <div className={`alert-box ${mensaje.tipo === 'exito' ? 'alert-exito' : 'alert-error'}`}>
          {mensaje.tipo === 'exito' ? '✅' : '❌'} {mensaje.texto}
        </div>
      )}

      <div className="cargos-grid">
        <div className="cargo-card">
          <h3 className="cargo-card-title">Nueva Responsabilidad</h3>
          <form onSubmit={guardarAsignacion}>
            <div className="form-group">
              <label>Personal *</label>
              <select required value={asignacion.usuario_id} onChange={(e) => setAsignacion({...asignacion, usuario_id: e.target.value})} className="input-custom">
                <option value="">Seleccionar personal...</option>
                {usuarios.map(u => (
                  <option key={u.id} value={u.id}>{u.nombres} {u.apellidos} ({u.rol})</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Aula *</label>
              <select required value={asignacion.aula_id} onChange={(e) => setAsignacion({...asignacion, aula_id: e.target.value})} className="input-custom">
                <option value="">Seleccionar aula...</option>
                {aulas.map(a => (
                  <option key={a.id} value={a.id}>{a.nombre_completo || `${a.grado}° ${a.seccion}`}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Función *</label>
              <select value={asignacion.tipo_cargo} onChange={(e) => setAsignacion({...asignacion, tipo_cargo: e.target.value, curso_id: ''})} className="input-custom">
                <option value="docente_curso">Docente de Curso</option>
                <option value="tutor_seccion">Tutor de Sección</option>
                <option value="auxiliar_grado">Auxiliar de Grado</option>
              </select>
            </div>

            {asignacion.tipo_cargo === 'docente_curso' && (
              <div className="form-group">
                <label>Curso *</label>
                <select required value={asignacion.curso_id} onChange={(e) => setAsignacion({...asignacion, curso_id: e.target.value})} className="input-custom">
                  <option value="">Seleccionar curso...</option>
                  {cursos.map(c => (
                    <option key={c.id} value={c.id}>{c.nombre}</option>
                  ))}
                </select>
              </div>
            )}

            <button type="submit" className="btn-vincular">Vincular Cargo</button>
          </form>
        </div>

        <div className="cargo-card table-wrapper">
          <h3 className="cargo-card-title">Cuadro de Responsabilidades</h3>
          <table className="custom-table">
            <thead>
              <tr>
                <th>Personal</th>
                <th>Aula</th>
                <th>Tipo</th>
                <th>Curso</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {asignaciones.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', color: '#94a3b8', padding: '24px' }}>
                    Sin asignaciones.
                  </td>
                </tr>
              ) : (
                asignaciones.map(asig => {
                  const badgeClass = asig.tipo_cargo === 'auxiliar_grado' ? 'badge-auxiliar' : asig.tipo_cargo === 'tutor_seccion' ? 'badge-tutor' : 'badge-docente';
                  return (
                    <tr key={asig.id}>
                      <td style={{ fontWeight: '600' }}>{asig.usuario_nombre || `ID: ${asig.usuario_id}`}</td>
                      <td>{asig.aula_nombre || `ID: ${asig.aula_id}`}</td>
                      <td><span className={`badge-cargo ${badgeClass}`}>{tipoCargoLegible(asig.tipo_cargo)}</span></td>
                      <td>{asig.curso_nombre || '—'}</td>
                      <td><button className="btn-eliminar" onClick={() => eliminarAsignacion(asig.id)}>🗑️</button></td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AsignacionCargos;