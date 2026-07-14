import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const styles = `
  .aulas-container { padding: 24px; max-width: 1340px; margin: 0 auto; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; color: #1f2937; }
  .aulas-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 28px; flex-wrap: wrap; gap: 16px; }
  .aulas-header h1 { font-size: 28px; font-weight: 800; color: #111827; margin: 0; letter-spacing: -0.5px; }
  .aulas-header p { font-size: 14px; color: #6b7280; margin: 4px 0 0 0; }
  
  .btn { padding: 10px 20px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }
  .btn-primary { background: #f97316; color: #fff; }
  .btn-primary:hover { background: #ea580c; box-shadow: 0 4px 15px rgba(249,115,22,0.3); }
  .btn-secondary { background: #fff; color: #374151; border: 1px solid #d1d5db; }
  .btn-secondary:hover { background: #f9fafb; }
  .btn-ghost { background: transparent; color: #6b7280; padding: 8px; border-radius: 8px; border: none; cursor: pointer; }
  .btn-ghost:hover { background: #f3f4f6; color: #374151; }
  
  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
  @media (max-width: 900px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
  
  .stat-card { background: #fff; border-radius: 14px; padding: 20px 24px; border: 1px solid #e5e7eb; transition: all 0.2s; cursor: default; }
  .stat-card:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.06); transform: translateY(-2px); }
  .stat-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; }
  .stat-value { font-size: 32px; font-weight: 800; color: #111827; line-height: 1; }
  .stat-label { font-size: 13px; color: #6b7280; margin-top: 6px; font-weight: 500; }
  
  .filters-bar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }
  .select { padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 10px; font-size: 14px; outline: none; background: #fff; cursor: pointer; color: #1f2937; }
  .select:focus { border-color: #f97316; box-shadow: 0 0 0 3px rgba(249,115,22,0.1); }
  
  .grados-container { display: flex; flex-direction: column; gap: 32px; }
  
  .grado-section { }
  .grado-title { font-size: 22px; font-weight: 800; color: #111827; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
  .grado-title .line { flex: 1; height: 2px; background: #e5e7eb; border-radius: 1px; }
  
  .aulas-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 18px; }
  
  .aula-card { background: #fff; border-radius: 18px; border: 1px solid #e5e7eb; overflow: hidden; transition: all 0.25s; cursor: default; }
  .aula-card:hover { box-shadow: 0 12px 35px rgba(0,0,0,0.08); transform: translateY(-3px); }
  
  .aula-card-header { background: linear-gradient(135deg, #f97316, #ea580c); padding: 20px 22px; color: #fff; }
  .aula-card-header .top-row { display: flex; justify-content: space-between; align-items: flex-start; }
  .aula-card-header .seccion { font-size: 42px; font-weight: 800; line-height: 1; }
  .aula-card-header .anio { font-size: 12px; opacity: 0.85; font-weight: 500; }
  .aula-card-header .turno-badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; background: rgba(255,255,255,0.2); margin-top: 8px; }
  
  .aula-card-body { padding: 18px 22px; }
  .aula-card-body .tutor-section { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
  .aula-card-body .tutor-info { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
  .aula-card-body .tutor-avatar { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; color: #fff; flex-shrink: 0; }
  .aula-card-body .tutor-name { font-weight: 600; font-size: 14px; color: #111827; }
  .aula-card-body .tutor-dni { font-size: 12px; color: #6b7280; }
  .aula-card-body .no-tutor { font-size: 13px; color: #9ca3af; font-style: italic; }
  .aula-card-body .change-btn { font-size: 11px; font-weight: 600; color: #f97316; background: #fff7ed; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; white-space: nowrap; }
  .aula-card-body .change-btn:hover { background: #ffedd5; }
  
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 20px; }
  .modal { background: #fff; border-radius: 20px; width: 100%; max-width: 550px; max-height: 90vh; overflow-y: auto; box-shadow: 0 25px 60px rgba(0,0,0,0.2); }
  .modal-header { display: flex; align-items: center; justify-content: space-between; padding: 24px 28px; border-bottom: 1px solid #e5e7eb; position: sticky; top: 0; background: #fff; z-index: 1; border-radius: 20px 20px 0 0; }
  .modal-header h2 { font-size: 20px; font-weight: 700; color: #111827; margin: 0; }
  .modal-body { padding: 28px; }
  
  .form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 18px; }
  .form-group label { font-size: 13px; font-weight: 600; color: #374151; }
  .input { width: 100%; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 10px; font-size: 14px; outline: none; transition: all 0.2s; background: #fff; box-sizing: border-box; color: #1f2937; }
  .input:focus { border-color: #f97316; box-shadow: 0 0 0 3px rgba(249,115,22,0.1); }
  .form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 20px; border-top: 1px solid #f3f4f6; }
  
  .alert { padding: 12px 16px; border-radius: 12px; font-size: 14px; display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
  .alert-error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
  .alert-success { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
  
  .tutor-list { display: flex; flex-direction: column; gap: 8px; max-height: 250px; overflow-y: auto; }
  .tutor-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border: 1px solid #e5e7eb; border-radius: 10px; cursor: pointer; transition: all 0.15s; }
  .tutor-item:hover { background: #f9fafb; border-color: #f97316; }
  .tutor-item.selected { background: #fff7ed; border-color: #f97316; }
  .tutor-item .tutor-left { display: flex; align-items: center; gap: 10px; }
  
  .spinner { width: 40px; height: 40px; border: 3px solid #ffedd5; border-top-color: #f97316; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 40px auto; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .empty-state { text-align: center; padding: 60px 24px; color: #9ca3af; }
`;

const GestionAulas = () => {
  const { token } = useAuth();
  const [aulas, setAulas] = useState([]);
  const [docentes, setDocentes] = useState([]);
  const [asignaciones, setAsignaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalAulaOpen, setModalAulaOpen] = useState(false);
  const [modalTutorOpen, setModalTutorOpen] = useState(false);
  const [aulaSeleccionada, setAulaSeleccionada] = useState(null);
  const [tutorSeleccionado, setTutorSeleccionado] = useState(null);
  const [saving, setSaving] = useState(false);
  const [filterGrado, setFilterGrado] = useState('todos');
  const [filterTurno, setFilterTurno] = useState('todos');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formAula, setFormAula] = useState({
    grado: 1, seccion: '', anio_escolar: new Date().getFullYear(), turno: 'mañana',
  });

  const headers = { Authorization: `Bearer ${token}` };

  const cargarDatos = useCallback(async () => {
    try {
      setLoading(true);
      const [aulasRes, docentesRes, asignacionesRes] = await Promise.all([
        axios.get(`${API_URL}/aulas`, { headers }),
        axios.get(`${API_URL}/usuarios?rol=docente`, { headers }).catch(() => ({ data: [] })),
        axios.get(`${API_URL}/asignaciones`, { headers }).catch(() => ({ data: [] })),
      ]);
      setAulas(Array.isArray(aulasRes.data) ? aulasRes.data : []);
      setDocentes(Array.isArray(docentesRes.data) ? docentesRes.data.filter(u => u.rol === 'docente') : []);
      setAsignaciones(Array.isArray(asignacionesRes.data) ? asignacionesRes.data : []);
    } catch (err) {
      console.error('Error al cargar datos:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { if (token) cargarDatos(); }, [token, cargarDatos]);

  const getTutorAula = (aulaId) => {
    const asignacion = asignaciones.find(a => a.aula_id === aulaId && a.tipo_cargo === 'tutor_seccion');
    if (!asignacion) return null;
    return docentes.find(d => d.id === asignacion.usuario_id) || null;
  };

  const abrirAsignarTutor = (aula) => {
    setAulaSeleccionada(aula);
    const tutorActual = getTutorAula(aula.id);
    setTutorSeleccionado(tutorActual);
    setModalTutorOpen(true);
  };

  const guardarTutor = async () => {
    if (!tutorSeleccionado) {
      setError('Selecciona un docente');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await axios.post(`${API_URL}/asignaciones`, {
        usuario_id: tutorSeleccionado.id,
        aula_id: aulaSeleccionada.id,
        curso_id: null,
        tipo_cargo: 'tutor_seccion',
      }, { headers });
      setSuccess('Tutor asignado correctamente');
      cargarDatos();
      setTimeout(() => { setModalTutorOpen(false); setSuccess(''); }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al asignar tutor');
    } finally {
      setSaving(false);
    }
  };

  const handleCrearAula = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);
    try {
      await axios.post(`${API_URL}/aulas`, {
        ...formAula, seccion: formAula.seccion.toUpperCase().trim(),
      }, { headers });
      setSuccess('Aula creada correctamente');
      setFormAula({ grado: 1, seccion: '', anio_escolar: new Date().getFullYear(), turno: 'mañana' });
      cargarDatos();
      setTimeout(() => { setModalAulaOpen(false); setSuccess(''); }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al crear aula');
    } finally {
      setSaving(false);
    }
  };

  const filteredAulas = aulas.filter(aula => {
    const matchGrado = filterGrado === 'todos' || aula.grado.toString() === filterGrado;
    const matchTurno = filterTurno === 'todos' || aula.turno === filterTurno;
    return matchGrado && matchTurno;
  });

  const aulasPorGrado = {};
  filteredAulas.forEach(aula => {
    if (!aulasPorGrado[aula.grado]) aulasPorGrado[aula.grado] = [];
    aulasPorGrado[aula.grado].push(aula);
  });

  const stats = {
    total: aulas.length,
    conTutor: asignaciones.filter(a => a.tipo_cargo === 'tutor_seccion').length,
    manana: aulas.filter(a => a.turno === 'mañana').length,
    tarde: aulas.filter(a => a.turno === 'tarde').length,
  };

  return (
    <div className="aulas-container">
      <style>{styles}</style>

      <div className="aulas-header">
        <div>
          <h1>Gestión de Aulas</h1>
          <p>Administra secciones, grados, turnos y asigna tutores a cada salón</p>
        </div>
        <button onClick={() => { setError(''); setSuccess(''); setModalAulaOpen(true); }} className="btn btn-primary">
          <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Nueva Aula
        </button>
      </div>

      {success && (
        <div className="alert alert-success" style={{ marginBottom: 24 }}>
          <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {success}
        </div>
      )}

      <div className="stats-grid">
        {[
          { icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4', color: '#f97316', bg: '#fff7ed', value: stats.total, label: 'Total Aulas' },
          { icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z', color: '#059669', bg: '#d1fae5', value: stats.conTutor, label: 'Con Tutor' },
          { icon: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z', color: '#d97706', bg: '#fef3c7', value: stats.manana, label: 'Mañana' },
          { icon: 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z', color: '#2563eb', bg: '#dbeafe', value: stats.tarde, label: 'Tarde' },
        ].map((s, i) => (
          <div className="stat-card" key={i}>
            <div className="stat-icon" style={{ background: s.bg }}>
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke={s.color} strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d={s.icon} />
              </svg>
            </div>
            <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="filters-bar">
        <select value={filterGrado} onChange={(e) => setFilterGrado(e.target.value)} className="select">
          <option value="todos">Todos los grados</option>
          {[1,2,3,4,5].map(g => <option key={g} value={g}>{g}° Grado</option>)}
        </select>
        <select value={filterTurno} onChange={(e) => setFilterTurno(e.target.value)} className="select">
          <option value="todos">Todos los turnos</option>
          <option value="mañana">Mañana</option>
          <option value="tarde">Tarde</option>
        </select>
      </div>

      {loading ? (
        <div className="spinner" />
      ) : Object.keys(aulasPorGrado).length === 0 ? (
        <div className="empty-state">
          <svg width="80" height="80" fill="none" viewBox="0 0 24 24" stroke="#d1d5db" strokeWidth={1}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <p style={{ fontSize: 18, fontWeight: 600, color: '#6b7280', marginBottom: 4 }}>No hay aulas</p>
        </div>
      ) : (
        <div className="grados-container">
          {[1,2,3,4,5].map(grado => {
            const aulasGrado = aulasPorGrado[grado];
            if (!aulasGrado || aulasGrado.length === 0) return null;
            return (
              <div key={grado} className="grado-section">
                <div className="grado-title">
                  <span>{grado}° Grado</span>
                  <div className="line" />
                </div>
                <div className="aulas-grid">
                  {aulasGrado.map(aula => {
                    const tutor = getTutorAula(aula.id);
                    return (
                      <div key={aula.id} className="aula-card">
                        <div className="aula-card-header">
                          <div className="top-row">
                            <div className="seccion">{aula.seccion}</div>
                            <div className="anio">{aula.anio_escolar}</div>
                          </div>
                          <div className="turno-badge">{aula.turno === 'mañana' ? '☀️ Mañana' : '🌙 Tarde'}</div>
                        </div>
                        <div className="aula-card-body">
                          <div className="tutor-section">
                            {tutor ? (
                              <div className="tutor-info">
                                <div className="tutor-avatar" style={{ background: '#059669' }}>
                                  {tutor.nombres?.charAt(0)}{tutor.apellidos?.charAt(0)}
                                </div>
                                <div>
                                  <div className="tutor-name">{tutor.nombres} {tutor.apellidos}</div>
                                  <div className="tutor-dni">DNI: {tutor.dni}</div>
                                </div>
                              </div>
                            ) : (
                              <div className="no-tutor">Sin tutor asignado</div>
                            )}
                            <button className="change-btn" onClick={() => abrirAsignarTutor(aula)}>
                              {tutor ? 'Cambiar' : 'Asignar'}
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal Crear Aula */}
      {modalAulaOpen && (
        <div className="modal-overlay" onClick={() => setModalAulaOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Registrar Nueva Aula</h2>
              <button onClick={() => setModalAulaOpen(false)} className="btn-ghost">
                <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleCrearAula}>
                {error && <div className="alert alert-error"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>{error}</div>}
                <div className="form-group">
                  <label>Grado (1-5)</label>
                  <select value={formAula.grado} onChange={(e) => setFormAula({ ...formAula, grado: parseInt(e.target.value) })} className="select">
                    {[1,2,3,4,5].map(g => <option key={g} value={g}>{g}° de Secundaria</option>)}
                  </select>
                </div>
                <div className="form-group"><label>Sección *</label><input required maxLength={2} value={formAula.seccion} onChange={(e) => setFormAula({ ...formAula, seccion: e.target.value.toUpperCase() })} className="input" placeholder="A, B, C..." /></div>
                <div className="form-group"><label>Año Escolar *</label><input type="number" required value={formAula.anio_escolar} onChange={(e) => setFormAula({ ...formAula, anio_escolar: parseInt(e.target.value) })} className="input" /></div>
                <div className="form-group">
                  <label>Turno</label>
                  <select value={formAula.turno} onChange={(e) => setFormAula({ ...formAula, turno: e.target.value })} className="select">
                    <option value="mañana">Mañana</option>
                    <option value="tarde">Tarde</option>
                  </select>
                </div>
                <div className="form-actions">
                  <button type="button" onClick={() => setModalAulaOpen(false)} className="btn btn-secondary">Cancelar</button>
                  <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Creando...' : 'Crear Aula'}</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Modal Asignar Tutor */}
      {modalTutorOpen && aulaSeleccionada && (
        <div className="modal-overlay" onClick={() => setModalTutorOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Asignar Tutor - {aulaSeleccionada.grado}° "{aulaSeleccionada.seccion}"</h2>
              <button onClick={() => setModalTutorOpen(false)} className="btn-ghost">
                <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="modal-body">
              {error && <div className="alert alert-error"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>{error}</div>}

              <p style={{ fontSize: 14, color: '#6b7280', marginBottom: 16 }}>Selecciona un docente para ser tutor de esta sección:</p>

              <div className="tutor-list">
                {docentes.length === 0 ? (
                  <p style={{ color: '#9ca3af', textAlign: 'center', padding: 20 }}>No hay docentes registrados</p>
                ) : (
                  docentes.map(docente => (
                    <div key={docente.id}
                      className={`tutor-item ${tutorSeleccionado?.id === docente.id ? 'selected' : ''}`}
                      onClick={() => setTutorSeleccionado(docente)}>
                      <div className="tutor-left">
                        <div className="tutor-avatar" style={{ background: '#7c3aed', width: 32, height: 32, fontSize: 12 }}>
                          {docente.nombres?.charAt(0)}{docente.apellidos?.charAt(0)}
                        </div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 14 }}>{docente.nombres} {docente.apellidos}</div>
                          <div style={{ fontSize: 12, color: '#6b7280' }}>DNI: {docente.dni}</div>
                        </div>
                      </div>
                      {tutorSeleccionado?.id === docente.id && (
                        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#f97316" strokeWidth={2.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  ))
                )}
              </div>

              <div className="form-actions">
                <button onClick={() => setModalTutorOpen(false)} className="btn btn-secondary">Cancelar</button>
                <button onClick={guardarTutor} className="btn btn-primary" disabled={saving || !tutorSeleccionado}>
                  {saving ? 'Guardando...' : 'Asignar Tutor'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GestionAulas;