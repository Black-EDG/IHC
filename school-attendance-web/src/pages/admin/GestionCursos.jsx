import React, { useState, useEffect } from 'react';
import axios from 'axios';
import NavbarLayout from '../../components/NavbarLayout';
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
    <NavbarLayout>
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ color: theme.colors.primary, margin: 0 }}>📚 Plan de Estudios / Catálogo de Cursos</h2>
        <p style={{ color: theme.colors.textLight, fontSize: '14px' }}>Define las materias. Recuerda registrar 'Tutoría' para el seguimiento global.</p>
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
        {/* CREACIÓN DE MATERIAS */}
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: theme.shadows.card, height: 'fit-content' }}>
          <h3 style={{ margin: '0 0 15px 0', color: theme.colors.text }}>Nuevo Curso</h3>
          <form onSubmit={guardarCurso}>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ fontSize: '13px', fontWeight: 'bold' }}>Nombre de la Materia</label>
              <input 
                type="text" 
                required 
                placeholder="Ej: Matemática, Tutoría..." 
                value={nuevoCurso.nombre} 
                onChange={(e) => setNuevoCurso({ ...nuevoCurso, nombre: e.target.value })} 
                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: `1px solid ${theme.colors.border}`, marginTop: '4px', boxSizing: 'border-box' }} 
              />
            </div>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ fontSize: '13px', fontWeight: 'bold' }}>Descripción / Silabo breve</label>
              <textarea 
                rows="3"
                placeholder="Opcional..." 
                value={nuevoCurso.descripcion} 
                onChange={(e) => setNuevoCurso({ ...nuevoCurso, descripcion: e.target.value })} 
                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: `1px solid ${theme.colors.border}`, marginTop: '4px', boxSizing: 'border-box', resize: 'vertical' }} 
              />
            </div>
            <button type="submit" style={{ width: '100%', backgroundColor: theme.colors.primary, color: 'white', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
              Registrar Materia
            </button>
          </form>
        </div>

        {/* LISTADO GLOBAL */}
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: theme.shadows.card }}>
          <h3 style={{ margin: '0 0 15px 0', color: theme.colors.text }}>Cursos Activos en el Sistema</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {cursos.map(c => (
              <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', border: `1px solid ${theme.colors.border}`, borderRadius: '8px', backgroundColor: '#f9fafb' }}>
                <div>
                  <strong style={{ color: theme.colors.text, fontSize: '15px' }}>{c.nombre}</strong>
                  <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: theme.colors.textLight }}>{c.descripcion || 'Sin descripción adicional.'}</p>
                </div>
                <span style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '4px 8px', borderRadius: '6px', fontSize: '12px', fontWeight: 'bold' }}>
                  ID: {c.id}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </NavbarLayout>
  );
};

export default GestionCursos;