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

  const inputStyle = {
    width: '100%', padding: '10px', borderRadius: '6px', border: `1px solid ${theme.colors.border}`,
    boxSizing: 'border-box', fontSize: '14px', marginTop: '4px', outline: 'none'
  };

  return (
    <NavbarLayout>
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ color: theme.colors.primary, margin: 0 }}>🔑 Asignación de Responsabilidades y Salones</h2>
        <p style={{ color: theme.colors.textLight, fontSize: '14px' }}>Cruza personal de la intranet con sus respectivas aulas y cursos.</p>
      </div>

      {mensaje.texto && (
        <div style={{
          padding: '12px', borderRadius: '8px', marginBottom: '20px', fontWeight: 'bold',
          backgroundColor: mensaje.tipo === 'exito' ? '#d1fae5' : '#fee2e2', color: mensaje.tipo === 'exito' ? '#065f46' : '#991b1b'
        }}>
          {mensaje.texto}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : '1fr 2fr', gap: '25px' }}>
        {/* ENLAZAR CARGO */}
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: theme.shadows.card, height: 'fit-content' }}>
          <h3 style={{ margin: '0 0 15px 0', color: theme.colors.text }}>Nueva Responsabilidad</h3>
          <form onSubmit={guardarAsignacion}>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ fontSize: '13px', fontWeight: 'bold' }}>ID del Usuario (Personal)</label>
              <input type="number" required placeholder="ID numérico del Docente/Auxiliar" value={asignacion.usuario_id} onChange={(e)=>setAsignacion({...asignacion, usuario_id: e.target.value})} style={inputStyle} />
            </div>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ fontSize: '13px', fontWeight: 'bold' }}>ID del Aula</label>
              <input type="number" required placeholder="ID numérico del salón" value={asignacion.aula_id} onChange={(e)=>setAsignacion({...asignacion, aula_id: e.target.value})} style={inputStyle} />
            </div>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ fontSize: '13px', fontWeight: 'bold' }}>Función / Tipo de Cargo (ENUM)</label>
              <select value={asignacion.tipo_cargo} onChange={(e)=>setAsignacion({...asignacion, tipo_cargo: e.target.value})} style={inputStyle}>
                <option value="docente_curso">Docente dictando Curso</option>
                <option value="tutor_seccion">Profesor Tutor de Sección</option>
                <option value="auxiliar_grado">Auxiliar de Grado Completo</option>
              </select>
            </div>
            
            {asignacion.tipo_cargo !== 'auxiliar_grado' && (
              <div style={{ marginBottom: '15px' }}>
                <label style={{ fontSize: '13px', fontWeight: 'bold' }}>ID del Curso</label>
                <input type="number" placeholder="Deja vacío si es Tutor General" value={asignacion.curso_id} onChange={(e)=>setAsignacion({...asignacion, curso_id: e.target.value})} style={inputStyle} />
              </div>
            )}

            <button type="submit" style={{ width: '100%', backgroundColor: theme.colors.secondary, color: 'white', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', marginTop: '5px' }}>
              Vincular Cargo
            </button>
          </form>
        </div>

        {/* ORGANIGRAMA / CUADRO COMPLETO */}
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: theme.shadows.card, overflowX: 'auto' }}>
          <h3 style={{ margin: '0 0 15px 0', color: theme.colors.text }}>Cuadro de Responsabilidades Vigente</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb', borderBottom: `2px solid ${theme.colors.border}` }}>
                <th style={{ padding: '10px' }}>Usuario ID</th>
                <th style={{ padding: '10px' }}>Aula ID</th>
                <th style={{ padding: '10px' }}>Tipo Responsabilidad</th>
                <th style={{ padding: '10px' }}>Curso ID</th>
              </tr>
            </thead>
            <tbody>
              {asignaciones.map(asig => (
                <tr key={asig.id} style={{ borderBottom: `1px solid ${theme.colors.border}`, fontSize: '14px' }}>
                  <td style={{ padding: '12px', fontWeight: 'bold', color: theme.colors.primary }}>👤 ID: {asig.usuario_id}</td>
                  <td style={{ padding: '12px' }}>🏫 ID: {asig.aula_id}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ 
                      backgroundColor: asig.tipo_cargo === 'auxiliar_grado' ? '#fef3c7' : asig.tipo_cargo === 'tutor_seccion' ? '#d1fae5' : '#e0f2fe',
                      color: asig.tipo_cargo === 'auxiliar_grado' ? '#b45309' : asig.tipo_cargo === 'tutor_seccion' ? '#065f46' : '#0369a1',
                      padding: '4px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold', textTransform: 'uppercase'
                    }}>{asig.tipo_cargo.replace('_', ' ')}</span>
                  </td>
                  <td style={{ padding: '12px', color: asig.curso_id ? theme.colors.text : theme.colors.textLight }}>
                    {asig.curso_id ? `📚 ID: ${asig.curso_id}` : '🚫 [Aplica Global]'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </NavbarLayout>
  );
};

export default AsignacionCargos;