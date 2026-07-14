import React, { useState, useEffect } from 'react';
import axios from 'axios';
import NavbarLayout from '../../components/NavbarLayout';
import { theme } from '../../theme';

const AsignacionCargos = () => {
  const [asignaciones, setAsignaciones] = useState([]);
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  // Payload exacto para la tabla 'asignaciones_aulas'
  const [asignacion, setAsignacion] = useState({
    usuario_id: '', aula_id: '', curso_id: '', tipo_cargo: 'docente_curso'
  });

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    listarAsignaciones();
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const listarAsignaciones = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get('http://127.0.0.1:8000/asignaciones/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAsignaciones(res.data);
    } catch (err) {
      console.error("Error al traer cuadro de cargos");
    }
  };

  const guardarAsignacion = async (e) => {
    e.preventDefault();
    setMensaje({ tipo: '', texto: '' });

    // Preparar datos respetando reglas relacionales
    const payload = {
      usuario_id: parseInt(asignacion.usuario_id, 10),
      aula_id: parseInt(asignacion.aula_id, 10),
      tipo_cargo: asignacion.tipo_cargo,
      // Si es auxiliar_grado, forzamos null en curso_id tal como dicta la DB
      curso_id: asignacion.tipo_cargo === 'auxiliar_grado' || !asignacion.curso_id 
        ? null 
        : parseInt(asignacion.curso_id, 10)
    };

    try {
      const token = localStorage.getItem('token');
      await axios.post('http://127.0.0.1:8000/asignaciones/', payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMensaje({ tipo: 'exito', texto: '¡Asignación de responsabilidad vinculada con éxito!' });
      setAsignacion({ usuario_id: '', aula_id: '', curso_id: '', tipo_cargo: 'docente_curso' });
      listarAsignaciones();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.response?.data?.detail || 'Incoherencia de IDs o conflicto con la regla única de asignación.' });
    }
  };

  return (
    <NavbarLayout>
      <div className="cargos-container">
        {/* CSS Encapsulado - Inmune a fallas de Tailwind */}
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

          /* Sistema de Alertas */
          .alert-box {
            padding: 14px 20px !important;
            border-radius: 12px !important;
            margin-bottom: 24px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            display: flex !important;
            align-items: center !important;
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

          /* Grid de Secciones */
          .cargos-grid {
            display: grid !important;
            grid-template-columns: ${isMobile ? '1fr' : '1fr 2fr'} !important;
            gap: 28px !important;
          }

          /* Tarjetas */
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

          /* Formularios y Inputs */
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
          }

          .input-custom:focus {
            border-color: ${theme?.colors?.secondary || '#3b82f6'} !important;
            background-color: #ffffff !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
          }

          .btn-vincular {
            width: 100% !important;
            background-color: ${theme?.colors?.secondary || '#3b82f6'} !important;
            color: white !important;
            border: none !important;
            padding: 12px !important;
            border-radius: 10px !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            cursor: pointer !important;
            margin-top: 8px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2) !important;
          }

          .btn-vincular:hover {
            opacity: 0.95 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 12px -1px rgba(59, 130, 246, 0.3) !important;
          }

          /* Tablas Modernas */
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
            padding: 16px !important;
            font-size: 14px !important;
            color: #334155 !important;
            border-bottom: 1px solid ${theme?.colors?.border || '#f1f5f9'} !important;
            vertical-align: middle !important;
          }

          .custom-table tr:last-child td {
            border-bottom: none !important;
          }

          /* Badges de Roles */
          .badge-cargo {
            display: inline-block !important;
            padding: 6px 10px !important;
            border-radius: 8px !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.25px !important;
          }

          .badge-docente { background-color: #e0f2fe !important; color: #0369a1 !important; }
          .badge-tutor { background-color: #d1fae5 !important; color: #065f46 !important; }
          .badge-auxiliar { background-color: #fef3c7 !important; color: #b45309 !important; }

          /* Tarjetas Internas de Entidad */
          .entity-pill {
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            background-color: #f1f5f9 !important;
            padding: 4px 8px !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            color: #475569 !important;
          }
          
          .entity-pill-primary {
            background-color: #eef2ff !important;
            color: ${theme?.colors?.primary || '#4f46e5'} !important;
          }

          .global-badge {
            color: #94a3b8 !important;
            font-style: italic !important;
            font-size: 13px !important;
          }
        `}</style>

        {/* CABECERA */}
        <div className="cargos-header">
          <h2>🔑 Asignación de Responsabilidades y Salones</h2>
          <p>Cruza personal de la intranet con sus respectivas aulas y cursos.</p>
        </div>

        {/* FEEDBACK MENSAJE */}
        {mensaje.texto && (
          <div className={`alert-box ${mensaje.tipo === 'exito' ? 'alert-exito' : 'alert-error'}`}>
            {mensaje.tipo === 'exito' ? '✅ ' : '❌ '} {mensaje.texto}
          </div>
        )}

        {/* CONTENIDO EN GRID */}
        <div className="cargos-grid">
          
          {/* COLUMNA 1: FORMULARIO */}
          <div className="cargo-card">
            <h3 className="cargo-card-title">Nueva Responsabilidad</h3>
            <form onSubmit={guardarAsignacion}>
              
              <div className="form-group">
                <label>ID del Usuario (Personal)</label>
                <input 
                  type="number" 
                  required 
                  placeholder="Ej. 12" 
                  value={asignacion.usuario_id} 
                  onChange={(e) => setAsignacion({...asignacion, usuario_id: e.target.value})} 
                  className="input-custom" 
                />
              </div>

              <div className="form-group">
                <label>ID del Aula</label>
                <input 
                  type="number" 
                  required 
                  placeholder="Ej. 4" 
                  value={asignacion.aula_id} 
                  onChange={(e) => setAsignacion({...asignacion, aula_id: e.target.value})} 
                  className="input-custom" 
                />
              </div>

              <div className="form-group">
                <label>Función / Tipo de Cargo</label>
                <select 
                  value={asignacion.tipo_cargo} 
                  onChange={(e) => setAsignacion({...asignacion, tipo_cargo: e.target.value})} 
                  className="input-custom"
                >
                  <option value="docente_curso">Docente dictando Curso</option>
                  <option value="tutor_seccion">Profesor Tutor de Sección</option>
                  <option value="auxiliar_grado">Auxiliar de Grado Completo</option>
                </select>
              </div>
              
              {asignacion.tipo_cargo !== 'auxiliar_grado' && (
                <div className="form-group">
                  <label>ID del Curso</label>
                  <input 
                    type="number" 
                    placeholder="Vacío si es Tutor General" 
                    value={asignacion.curso_id} 
                    onChange={(e) => setAsignacion({...asignacion, curso_id: e.target.value})} 
                    className="input-custom" 
                  />
                </div>
              )}

              <button type="submit" className="btn-vincular">
                Vincular Cargo
              </button>
            </form>
          </div>

          {/* COLUMNA 2: TABLA/ORGANIGRAMA */}
          <div className="cargo-card table-wrapper">
            <h3 className="cargo-card-title">Cuadro de Responsabilidades Vigente</h3>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Aula</th>
                  <th>Tipo Responsabilidad</th>
                  <th>Curso Asignado</th>
                </tr>
              </thead>
              <tbody>
                {asignaciones.length === 0 ? (
                  <tr>
                    <td colSpan="4" style={{ textAlign: 'center', color: '#94a3b8', padding: '24px' }}>
                      Ninguna responsabilidad asignada hasta el momento.
                    </td>
                  </tr>
                ) : (
                  asignaciones.map(asig => {
                    // Seleccionar clase del badge dinámicamente
                    const badgeClass = asig.tipo_cargo === 'auxiliar_grado' 
                      ? 'badge-auxiliar' 
                      : asig.tipo_cargo === 'tutor_seccion' 
                        ? 'badge-tutor' 
                        : 'badge-docente';

                    return (
                      <tr key={asig.id}>
                        <td>
                          <span className="entity-pill entity-pill-primary">
                            👤 ID: {asig.usuario_id}
                          </span>
                        </td>
                        <td>
                          <span className="entity-pill">
                            🏫 ID: {asig.aula_id}
                          </span>
                        </td>
                        <td>
                          <span className={`badge-cargo ${badgeClass}`}>
                            {asig.tipo_cargo.replace('_', ' ')}
                          </span>
                        </td>
                        <td>
                          {asig.curso_id ? (
                            <span className="entity-pill" style={{ backgroundColor: '#f0fdf4', color: '#166534' }}>
                              📚 ID: {asig.curso_id}
                            </span>
                          ) : (
                            <span className="global-badge">🚫 [Aplica Global]</span>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

        </div>
      </div>
    </NavbarLayout>
  );
};

export default AsignacionCargos;