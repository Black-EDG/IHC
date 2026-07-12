import React, { useState, useEffect } from 'react';
import axios from 'axios';
import NavbarLayout from '../../components/NavbarLayout';
import { theme } from '../../theme';

const ControlAsistencia = () => {
  const [aulaId, setAulaId] = useState('1'); 
  const [alumnos, setAlumnos] = useState([]);
  const [asistencias, setAsistencias] = useState({}); // { alumno_id: 'presente' }
  const [observaciones, setObservaciones] = useState({});
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [cargando, setCargando] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const cargarListaAula = async () => {
    if (!aulaId) return;
    setCargando(true);
    setMensaje({ tipo: '', texto: '' });
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`http://127.0.0.1:8000/alumnos/aula/${aulaId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAlumnos(res.data);
      
      // Estado inicial por defecto mapeado a tu EstadoAsistencia enum
      const baseEstados = {};
      res.data.forEach(al => {
        baseEstados[al.id] = 'presente';
      });
      setAsistencias(baseEstados);
    } catch (err) {
      setMensaje({ tipo: 'error', texto: 'No se pudo obtener la lista de alumnos para esta aula.' });
    } finally {
      setCargando(false);
    }
  };

  const handleEstadoChange = (id, estado) => {
    setAsistencias(prev => ({ ...prev, [id]: estado }));
  };

  const handleObservacionChange = (id, texto) => {
    setObservaciones(prev => ({ ...prev, [id]: texto }));
  };

  const guardarAsistenciaMasiva = async () => {
    setMensaje({ tipo: '', texto: '' });
    try {
      const token = localStorage.getItem('token');
      // ID simulado o decodificado del JWT para cumplir con usuario_id en tu base de datos
      const usuarioId = 1; 
      
      const peticiones = alumnos.map(al => {
        return axios.post('http://127.0.0.1:8000/asistencias/', {
          fecha: null, // El backend asignará date.today() automáticamente
          estado: asistencias[al.id], // presente, tarde, falta_justificada, falta_injustificada
          observacion: observaciones[al.id] || null,
          alumno_id: al.id,
          usuario_id: usuarioId
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
      });

      await Promise.all(peticiones);
      setMensaje({ tipo: 'exito', texto: '¡Padrón de asistencia enviado y guardado en PostgreSQL con éxito!' });
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.response?.data?.detail || 'Error al guardar el registro diario.' });
    }
  };

  // Botones de selección de estados basados estrictamente en tu backend
  const estadosEnum = [
    { valor: 'presente', label: 'Presente', color: '#10b981' },
    { valor: 'tarde', label: 'Tarde', color: '#f59e0b' },
    { valor: 'falta_justificada', label: 'F. Justificada', color: '#3b82f6' },
    { valor: 'falta_injustificada', label: 'F. Injustificada', color: '#ef4444' }
  ];

  return (
    <NavbarLayout>
      <div style={{ marginBottom: '20px', display: 'flex', flexWrap: 'wrap', gap: '15px', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ color: theme.colors.primary, margin: 0 }}>Control de Asistencia Diaria</h2>
          <p style={{ color: theme.colors.textLight, margin: '2px 0 0 0', fontSize: '14px' }}>Selecciona el aula para cargar el padrón de alumnos.</p>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <select 
            value={aulaId} 
            onChange={(e) => setAulaId(e.target.value)}
            style={{ padding: '10px', borderRadius: '6px', border: `1px solid ${theme.colors.border}`, fontSize: '14px', outline: 'none' }}
          >
            <option value="1">Aula 1 (1° de Secundaria)</option>
            <option value="2">Aula 2 (2° de Secundaria)</option>
            <option value="3">Aula 3 (3° de Secundaria)</option>
          </select>
          <button onClick={cargarListaAula} style={{ backgroundColor: theme.colors.primary, color: 'white', border: 'none', padding: '10px 16px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
            Cargar Lista
          </button>
        </div>
      </div>

      {mensaje.texto && (
        <div style={{
          backgroundColor: mensaje.tipo === 'exito' ? '#d1fae5' : '#fee2e2',
          color: mensaje.tipo === 'exito' ? '#065f46' : '#991b1b',
          padding: '12px', borderRadius: '8px', marginBottom: '20px', fontWeight: 'bold', fontSize: '14px', textAlign: 'center'
        }}>
          {mensaje.texto}
        </div>
      )}

      {cargando ? (
        <p style={{ color: theme.colors.textLight, textAlign: 'center', marginTop: '4px' }}>Cargando datos relacionales desde el servidor...</p>
      ) : alumnos.length === 0 ? (
        <div style={{ textAlign: 'center', color: theme.colors.textLight, backgroundColor: 'white', padding: '30px', borderRadius: '12px', border: `1px solid ${theme.colors.border}` }}>
          Ningún alumno cargado en pantalla. Selecciona un aula válida.
        </div>
      ) : (
        <div>
          {/* MODO MOBILE: RENDER EN TARJETAS INDIVIDUALES */}
          {isMobile ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '20px' }}>
              {alumnos.map(al => (
                <div key={al.id} style={{ backgroundColor: 'white', padding: '15px', borderRadius: '10px', boxShadow: theme.shadows.card, border: `1px solid ${theme.colors.border}` }}>
                  <div style={{ fontWeight: 'bold', fontSize: '16px', color: theme.colors.text, marginBottom: '10px' }}>
                    {al.apellidos}, {al.nombres}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                    {estadosEnum.map(est => (
                      <button
                        key={est.valor}
                        type="button"
                        onClick={() => handleEstadoChange(al.id, est.valor)}
                        style={{
                          padding: '8px', borderRadius: '6px', fontSize: '12px', fontWeight: 'bold', border: 'none', cursor: 'pointer',
                          backgroundColor: asistencias[al.id] === est.valor ? est.color : '#f3f4f6',
                          color: asistencias[al.id] === est.valor ? 'white' : '#4b5563'
                        }}
                      >
                        {est.label}
                      </button>
                    ))}
                  </div>
                  <input
                    type="text"
                    placeholder="Agregar observación..."
                    value={observaciones[al.id] || ''}
                    onChange={(e) => handleObservacionChange(al.id, e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '6px', border: `1px solid ${theme.colors.border}`, boxSizing: 'border-box', fontSize: '13px' }}
                  />
                </div>
              ))}
            </div>
          ) : (
            /* MODO DESKTOP: TABLA ESTRUCTURADA */
            <div style={{ backgroundColor: 'white', borderRadius: '12px', boxShadow: theme.shadows.card, overflow: 'hidden', marginBottom: '20px', border: `1px solid ${theme.colors.border}` }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f9fafb', borderBottom: `2px solid ${theme.colors.border}` }}>
                    <th style={{ padding: '14px', color: theme.colors.text }}>Estudiante</th>
                    <th style={{ padding: '14px', color: theme.colors.text, textAlign: 'center' }}>Estado de Asistencia (PostgreSQL ENUM)</th>
                    <th style={{ padding: '14px', color: theme.colors.text }}>Observación</th>
                  </tr>
                </thead>
                <tbody>
                  {alumnos.map(al => (
                    <tr key={al.id} style={{ borderBottom: `1px solid ${theme.colors.border}` }}>
                      <td style={{ padding: '14px', fontWeight: '600', color: theme.colors.text }}>
                        {al.apellidos}, {al.nombres}
                      </td>
                      <td style={{ padding: '14px', textAlign: 'center' }}>
                        <div style={{ display: 'inline-flex', gap: '8px', backgroundColor: '#f3f4f6', padding: '4px', borderRadius: '8px' }}>
                          {estadosEnum.map(est => (
                            <button
                              key={est.valor}
                              type="button"
                              onClick={() => handleEstadoChange(al.id, est.valor)}
                              style={{
                                padding: '8px 12px', borderRadius: '6px', fontSize: '13px', fontWeight: 'bold', border: 'none', cursor: 'pointer',
                                backgroundColor: asistencias[al.id] === est.valor ? est.color : 'transparent',
                                color: asistencias[al.id] === est.valor ? 'white' : '#4b5563'
                              }}
                            >
                              {est.label}
                            </button>
                          ))}
                        </div>
                      </td>
                      <td style={{ padding: '14px' }}>
                        <input
                          type="text"
                          placeholder="Justificación, retraso..."
                          value={observaciones[al.id] || ''}
                          onChange={(e) => handleObservacionChange(al.id, e.target.value)}
                          style={{ width: '100%', padding: '8px', borderRadius: '6px', border: `1px solid ${theme.colors.border}`, boxSizing: 'border-box' }}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* ACCIÓN DE GUARDADO MASIVO */}
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              onClick={guardarAsistenciaMasiva}
              style={{
                backgroundColor: theme.colors.secondary, color: 'white', border: 'none',
                padding: '14px 28px', borderRadius: '8px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer',
                boxShadow: '0 4px 6px rgba(16, 185, 129, 0.2)', width: isMobile ? '100%' : 'auto'
              }}
            >
              Guardar Asistencia del Día
            </button>
          </div>
        </div>
      )}
    </NavbarLayout>
  );
};

export default ControlAsistencia;