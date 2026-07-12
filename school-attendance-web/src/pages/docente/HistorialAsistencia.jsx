import React, { useState, useEffect } from 'react';
import axios from 'axios';
import NavbarLayout from '../../components/NavbarLayout';
import { theme } from '../../theme';

const HistorialAsistencia = () => {
  const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0]);
  const [aulaId, setAulaId] = useState('1');
  const [registros, setRegistros] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const buscarHistorial = async () => {
    setCargando(true);
    setMensaje({ tipo: '', texto: '' });
    try {
      const token = localStorage.getItem('token');
      // Filtramos en el frontend u ocupamos tu endpoint de consulta por aula y fecha
      const res = await axios.get(`http://127.0.0.1:8000/asistencias/aula/${aulaId}?fecha=${fecha}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRegistros(res.data);
      if (res.data.length === 0) {
        setMensaje({ tipo: 'info', texto: 'No se encontraron registros de asistencia para esta fecha.' });
      }
    } catch (err) {
      setMensaje({ tipo: 'error', texto: 'Error al cargar el historial del servidor.' });
    } finally {
      setCargando(false);
    }
  };

  const actualizarEstadoFila = async (asistenciaId, nuevoEstado, alumnoId, observacionActual) => {
    try {
      const token = localStorage.getItem('token');
      const usuarioId = 1; // ID del usuario autenticado

      // Petición PUT exacta al backend para actualizar la asistencia
      await axios.put(`http://127.0.0.1:8000/asistencias/${asistenciaId}`, {
        estado: nuevoEstado,
        observacion: observacionActual || null,
        alumno_id: alumnoId,
        usuario_id: usuarioId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Actualizar el estado local para reflejar el cambio visualmente en tiempo real
      setRegistros(prev => prev.map(reg => reg.id === asistenciaId ? { ...reg, estado: nuevoEstado } : reg));
      setMensaje({ tipo: 'exito', texto: 'Registro actualizado correctamente en la base de datos.' });
    } catch (err) {
      setMensaje({ tipo: 'error', texto: 'No se pudo actualizar el estado de la asistencia.' });
    }
  };

  const estadosEnum = [
    { valor: 'presente', label: 'P', color: '#10b981' },
    { valor: 'tarde', label: 'T', color: '#f59e0b' },
    { valor: 'falta_justificada', label: 'FJ', color: '#3b82f6' },
    { valor: 'falta_injustificada', label: 'FI', color: '#ef4444' }
  ];

  return (
    <NavbarLayout>
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ color: theme.colors.primary, margin: 0 }}>Historial y Correcciones</h2>
        <p style={{ color: theme.colors.textLight, margin: '4px 0 0 0', fontSize: '14px' }}>Modifica asistencias pasadas o del día en caso de errores.</p>
      </div>

      {/* Panel de Filtros Responsivo */}
      <div style={{
        backgroundColor: 'white', padding: '15px', borderRadius: '10px', marginBottom: '20px',
        boxShadow: theme.shadows.card, display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: '15px', alignItems: 'center'
      }}>
        <div style={{ width: '100%' }}>
          <label style={{ fontSize: '12px', fontWeight: 'bold', color: theme.colors.text }}>Fecha de Consulta</label>
          <input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: `1px solid ${theme.colors.border}`, marginTop: '4px', boxSizing: 'border-box' }} />
        </div>
        <div style={{ width: '100%' }}>
          <label style={{ fontSize: '12px', fontWeight: 'bold', color: theme.colors.text }}>Aula</label>
          <select value={aulaId} onChange={(e) => setAulaId(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: `1px solid ${theme.colors.border}`, marginTop: '4px', boxSizing: 'border-box' }}>
            <option value="1">1° de Secundaria</option>
            <option value="2">2° de Secundaria</option>
            <option value="3">3° de Secundaria</option>
          </select>
        </div>
        <button onClick={buscarHistorial} style={{ width: isMobile ? '100%' : '200px', backgroundColor: theme.colors.primary, color: 'white', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', alignSelf: isMobile ? 'stretch' : 'flex-end' }}>
          🔍 Consultar Fecha
        </button>
      </div>

      {mensaje.texto && (
        <div style={{
          backgroundColor: mensaje.tipo === 'exito' ? '#d1fae5' : mensaje.tipo === 'info' ? '#eff6ff' : '#fee2e2',
          color: mensaje.tipo === 'exito' ? '#065f46' : mensaje.tipo === 'info' ? '#1e40af' : '#991b1b',
          padding: '12px', borderRadius: '8px', marginBottom: '20px', fontSize: '14px', fontWeight: '600'
        }}>
          {mensaje.texto}
        </div>
      )}

      {/* Contenedor de Registros */}
      {registros.length > 0 && (
        <div style={{ backgroundColor: 'white', borderRadius: '12px', boxShadow: theme.shadows.card, overflowX: 'auto', border: `1px solid ${theme.colors.border}` }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb', borderBottom: `2px solid ${theme.colors.border}`, textAlign: 'left' }}>
                <th style={{ padding: '14px' }}>Estudiante</th>
                <th style={{ padding: '14px', textAlign: 'center' }}>Estado Actual</th>
                <th style={{ padding: '14px', textAlign: 'center' }}>Cambiar Estado</th>
              </tr>
            </thead>
            <tbody>
              {registros.map(reg => (
                <tr key={reg.id} style={{ borderBottom: `1px solid ${theme.colors.border}` }}>
                  <td style={{ padding: '14px', fontWeight: '500' }}>
                    {reg.alumno?.apellidos || 'Alumno'}, {reg.alumno?.nombres || `ID: ${reg.alumno_id}`}
                  </td>
                  <td style={{ padding: '14px', textAlign: 'center' }}>
                    <span style={{
                      padding: '5px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold', color: 'white',
                      backgroundColor: estadosEnum.find(e => e.valor === reg.estado)?.color || '#6b7280'
                    }}>
                      {reg.estado.toUpperCase().replace('_', ' ')}
                    </span>
                  </td>
                  <td style={{ padding: '14px', textAlign: 'center' }}>
                    <div style={{ display: 'inline-flex', gap: '4px' }}>
                      {estadosEnum.map(est => (
                        <button
                          key={est.valor}
                          title={est.label}
                          onClick={() => actualizarEstadoFila(reg.id, est.valor, reg.alumno_id, reg.observacion)}
                          style={{
                            width: '32px', height: '32px', borderRadius: '6px', border: 'none', fontWeight: 'bold', fontSize: '11px', cursor: 'pointer',
                            backgroundColor: reg.estado === est.valor ? est.color : '#e5e7eb',
                            color: reg.estado === est.valor ? 'white' : '#4b5563'
                          }}
                        >
                          {est.valor === 'falta_justificada' ? 'FJ' : est.valor === 'falta_injustificada' ? 'FI' : est.valor[0].toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </NavbarLayout>
  );
};

export default HistorialAsistencia;