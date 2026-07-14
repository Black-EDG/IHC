import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { theme } from '../../theme';

const GestionCursos = () => {
  const [cursos, setCursos] = useState([]);
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [nuevoCurso, setNuevoCurso] = useState({ nombre: '', descripcion: '' });

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    listarCursos();
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const listarCursos = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get('http://127.0.0.1:8000/cursos/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCursos(res.data);
    } catch (err) {
      console.error("Error al obtener materias");
    }
  };

  const guardarCurso = async (e) => {
    e.preventDefault();
    setMensaje({ tipo: '', texto: '' });
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://127.0.0.1:8000/cursos/', nuevoCurso, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMensaje({ tipo: 'exito', texto: `¡Curso "${nuevoCurso.nombre}" añadido al catálogo escolar!` });
      setNuevoCurso({ nombre: '', descripcion: '' });
      listarCursos();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.response?.data?.detail || 'El curso ya existe.' });
    }
  };

  return (
    <div className="cursos-modulo-limpio">
      {/* CSS Encapsulado Avanzado */}
      <style>{`
        .cursos-modulo-limpio {
          font-family: 'Inter', -apple-system, sans-serif !important;
          width: 100% !important;
          box-sizing: border-box !important;
        }

        .cursos-header-clean {
          margin-bottom: 24px !important;
        }

        .cursos-header-clean h2 {
          color: #1e293b !important;
          font-size: 24px !important;
          font-weight: 800 !important;
          margin: 0 0 4px 0 !important;
          letter-spacing: -0.5px !important;
        }

        .cursos-header-clean p {
          color: #64748b !important;
          font-size: 14px !important;
          margin: 0 !important;
        }

        /* Feedback Banners */
        .feedback-banner-clean {
          padding: 12px 16px !important;
          border-radius: 10px !important;
          margin-bottom: 24px !important;
          font-size: 14px !important;
          font-weight: 600 !important;
          border: 1px solid transparent !important;
        }
        .feedback-exito-clean { background-color: #ecfdf5 !important; color: #065f46 !important; border-color: #a7f3d0 !important; }
        .feedback-error-clean { background-color: #fef2f2 !important; color: #991b1b !important; border-color: #fca5a5 !important; }

        /* Grid de Distribución */
        .cursos-layout-grid {
          display: grid !important;
          grid-template-columns: ${isMobile ? '1fr' : '1fr 2fr'} !important;
          gap: 28px !important;
        }

        /* Tarjetas Base */
        .cursos-card-panel {
          background-color: #ffffff !important;
          padding: 24px !important;
          border-radius: 14px !important;
          border: 1px solid #e2e8f0 !important;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
          height: fit-content !important;
        }

        .panel-title-clean {
          margin: 0 0 20px 0 !important;
          color: #0f172a !important;
          font-size: 16px !important;
          font-weight: 700 !important;
        }

        /* Campos de Formulario */
        .form-field-group {
          margin-bottom: 16px !important;
        }

        .form-field-group label {
          display: block !important;
          font-size: 13px !important;
          font-weight: 600 !important;
          color: #475569 !important;
          margin-bottom: 6px !important;
        }

        .input-text-clean, .textarea-clean {
          width: 100% !important;
          padding: 10px 14px !important;
          border-radius: 10px !important;
          border: 1px solid #cbd5e1 !important;
          box-sizing: border-box !important;
          font-size: 14px !important;
          outline: none !important;
          color: #334155 !important;
          background-color: #f8fafc !important;
          transition: all 0.2s ease !important;
        }

        .input-text-clean:focus, .textarea-clean:focus {
          border-color: #4f46e5 !important;
          background-color: #ffffff !important;
          box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
        }

        .btn-submit-course {
          width: 100% !important;
          background-color: #4f46e5 !important;
          color: #ffffff !important;
          border: none !important;
          padding: 12px !important;
          border-radius: 10px !important;
          font-size: 14px !important;
          font-weight: 700 !important;
          cursor: pointer !important;
          transition: all 0.2s ease !important;
          box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2) !important;
        }

        .btn-submit-course:hover {
          background-color: #4338ca !important;
          transform: translateY(-1px) !important;
        }

        /* Lista de Materias Estilizada */
        .courses-list-stack {
          display: flex !important;
          flex-direction: column !important;
          gap: 12px !important;
        }

        .course-item-row {
          display: flex !important;
          justify-content: space-between !important;
          align-items: center !important;
          padding: 16px !important;
          border: 1px solid #f1f5f9 !important;
          border-radius: 12px !important;
          background-color: #f8fafc !important;
          transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }

        .course-item-row:hover {
          transform: translateY(-1px) !important;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02) !important;
          background-color: #ffffff !important;
          border-color: #e2e8f0 !important;
        }

        .course-info-block strong {
          color: #0f172a !important;
          font-size: 15px !important;
          font-weight: 700 !important;
        }

        .course-info-block p {
          margin: 4px 0 0 0 !important;
          font-size: 13px !important;
          color: #64748b !important;
          line-height: 1.4 !important;
        }

        .id-badge-pill {
          background-color: #e0f2fe !important;
          color: #0369a1 !important;
          padding: 6px 10px !important;
          border-radius: 8px !important;
          font-size: 12px !important;
          font-weight: 700 !important;
          white-space: nowrap !important;
        }
      `}</style>

      {/* CABECERA */}
      <div className="cursos-header-clean">
        <h2>📚 Plan de Estudios / Catálogo de Cursos</h2>
        <p>Define las materias del plantel. Recuerda registrar 'Tutoría' para el seguimiento global de salones.</p>
      </div>

      {/* BANNER DE RETROALIMENTACIÓN */}
      {mensaje.texto && (
        <div className={`feedback-banner-clean ${mensaje.tipo === 'exito' ? 'feedback-exito-clean' : 'feedback-error-clean'}`}>
          {mensaje.tipo === 'exito' ? '✅ ' : '⚠️ '} {mensaje.texto}
        </div>
      )}

      {/* CONTENEDOR GRID */}
      <div className="cursos-layout-grid">
        
        {/* COLUMNA FORMULARIO */}
        <div className="cursos-card-panel">
          <h3 className="panel-title-clean">Nuevo Curso</h3>
          <form onSubmit={guardarCurso}>
            
            <div className="form-field-group">
              <label>Nombre de la Materia</label>
              <input 
                type="text" 
                required 
                placeholder="Ej: Matemática, Ciencias, Tutoría..." 
                value={nuevoCurso.nombre} 
                onChange={(e) => setNuevoCurso({ ...nuevoCurso, nombre: e.target.value })} 
                className="input-text-clean"
              />
            </div>

            <div className="form-field-group">
              <label>Descripción / Sílabo breve</label>
              <textarea 
                rows="4"
                placeholder="Ingresa un resumen o lineamiento del curso (opcional)..." 
                value={nuevoCurso.descripcion} 
                onChange={(e) => setNuevoCurso({ ...nuevoCurso, descripcion: e.target.value })} 
                className="textarea-clean"
                style={{ resize: 'vertical' }}
              />
            </div>

            <button type="submit" className="btn-submit-course">
              Registrar Materia
            </button>
          </form>
        </div>

        {/* COLUMNA CATÁLOGO */}
        <div className="cursos-card-panel">
          <h3 className="panel-title-clean">Cursos Activos en el Sistema</h3>
          <div className="courses-list-stack">
            {cursos.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#94a3b8', padding: '24px' }}>
                No hay asignaturas configuradas en el catálogo aún.
              </div>
            ) : (
              cursos.map(c => (
                <div key={c.id} className="course-item-row">
                  <div className="course-info-block">
                    <strong>📖 {c.nombre}</strong>
                    <p>{c.descripcion || 'Sin descripción adicional en el sistema.'}</p>
                  </div>
                  <span className="id-badge-pill">
                    ID: {c.id}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default GestionCursos;