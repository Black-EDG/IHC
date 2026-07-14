import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const styles = `
  .matricula-container { padding: 24px; max-width: 1340px; margin: 0 auto; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; color: #1f2937; }
  .matricula-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 28px; flex-wrap: wrap; gap: 16px; }
  .matricula-header h1 { font-size: 28px; font-weight: 800; color: #111827; margin: 0; letter-spacing: -0.5px; }
  .matricula-header p { font-size: 14px; color: #6b7280; margin: 4px 0 0 0; }
  
  .btn { padding: 10px 20px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }
  .btn-primary { background: #2563eb; color: #fff; }
  .btn-primary:hover { background: #1d4ed8; box-shadow: 0 4px 15px rgba(37,99,235,0.3); }
  .btn-secondary { background: #fff; color: #374151; border: 1px solid #d1d5db; }
  .btn-secondary:hover { background: #f9fafb; }
  .btn-ghost { background: transparent; color: #6b7280; padding: 8px; border-radius: 8px; border: none; cursor: pointer; }
  .btn-ghost:hover { background: #f3f4f6; color: #374151; }
  .btn-danger { background: #ef4444; color: #fff; }
  .btn-danger:hover { background: #dc2626; }
  .btn-success { background: #059669; color: #fff; }
  .btn-success:hover { background: #047857; }
  .btn-warning { background: #f59e0b; color: #fff; }
  .btn-warning:hover { background: #d97706; }
  
  .stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 28px; }
  @media (max-width: 1100px) { .stats-grid { grid-template-columns: repeat(3, 1fr); } }
  @media (max-width: 640px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
  
  .stat-card { background: #fff; border-radius: 14px; padding: 20px 24px; border: 1px solid #e5e7eb; transition: all 0.2s; cursor: default; }
  .stat-card:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.06); transform: translateY(-2px); }
  .stat-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; }
  .stat-value { font-size: 32px; font-weight: 800; color: #111827; line-height: 1; }
  .stat-label { font-size: 13px; color: #6b7280; margin-top: 6px; font-weight: 500; }
  
  .filters-bar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }
  .search-box { position: relative; flex: 1; min-width: 220px; }
  .search-box svg { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); width: 18px; height: 18px; color: #9ca3af; pointer-events: none; }
  .input { width: 100%; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 10px; font-size: 14px; outline: none; transition: all 0.2s; background: #fff; box-sizing: border-box; color: #1f2937; }
  .input:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
  .input-search { padding-left: 42px; }
  .select { padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 10px; font-size: 14px; outline: none; background: #fff; cursor: pointer; color: #1f2937; min-width: 150px; }
  .select:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
  
  .table-wrapper { background: #fff; border-radius: 16px; border: 1px solid #e5e7eb; overflow: hidden; }
  .table-scroll { overflow-x: auto; }
  .table { width: 100%; border-collapse: collapse; min-width: 1200px; }
  .table th { background: #f9fafb; padding: 14px 16px; font-size: 11px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e5e7eb; text-align: left; }
  .table td { padding: 14px 16px; font-size: 13px; color: #374151; border-bottom: 1px solid #f3f4f6; vertical-align: middle; }
  .table tr:hover td { background: #fafbfc; }
  .table tr.row-suspended td { background: #fff7ed; }
  
  .badge { display: inline-flex; padding: 5px 10px; border-radius: 8px; font-size: 12px; font-weight: 600; white-space: nowrap; }
  .badge-blue { background: #dbeafe; color: #1e40af; }
  .badge-green { background: #d1fae5; color: #065f46; }
  .badge-amber { background: #fef3c7; color: #92400e; }
  .badge-red { background: #fee2e2; color: #991b1b; }
  .badge-orange { background: #fff7ed; color: #c2410c; }
  .badge-pink { background: #fce7f3; color: #9d174d; }
  
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 20px; }
  .modal { background: #fff; border-radius: 20px; width: 100%; max-width: 850px; max-height: 90vh; overflow-y: auto; box-shadow: 0 25px 60px rgba(0,0,0,0.2); }
  .modal-sm { max-width: 500px; }
  .modal-header { display: flex; align-items: center; justify-content: space-between; padding: 24px 28px; border-bottom: 1px solid #e5e7eb; position: sticky; top: 0; background: #fff; z-index: 1; border-radius: 20px 20px 0 0; }
  .modal-header h2 { font-size: 20px; font-weight: 700; color: #111827; margin: 0; }
  .modal-body { padding: 28px; }
  
  .section-box { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 14px; padding: 24px; margin-bottom: 24px; }
  .section-box h3 { font-size: 15px; font-weight: 700; color: #111827; margin: 0 0 18px 0; display: flex; align-items: center; gap: 8px; }
  
  .form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; }
  @media (max-width: 640px) { .form-grid { grid-template-columns: 1fr; } }
  .form-group { display: flex; flex-direction: column; gap: 6px; }
  .form-group label { font-size: 13px; font-weight: 600; color: #374151; }
  .form-group.full { grid-column: 1 / -1; }
  .form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 28px; padding-top: 20px; border-top: 1px solid #f3f4f6; }
  
  .alert { padding: 12px 16px; border-radius: 12px; font-size: 14px; display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
  .alert-error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
  .alert-success { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
  .alert-info { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
  
  .result-count { font-size: 13px; color: #6b7280; font-weight: 500; white-space: nowrap; }
  
  .spinner { width: 40px; height: 40px; border: 3px solid #dbeafe; border-top-color: #2563eb; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 40px auto; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .empty-state { text-align: center; padding: 60px 24px; color: #9ca3af; }
  
  .confirm-box { background: #fff; border-radius: 20px; padding: 32px; text-align: center; max-width: 420px; box-shadow: 0 25px 60px rgba(0,0,0,0.25); }
  .confirm-icon { width: 64px; height: 64px; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
  .confirm-title { font-size: 20px; font-weight: 700; color: #111827; margin-bottom: 8px; }
  .confirm-text { color: #6b7280; font-size: 14px; margin-bottom: 24px; line-height: 1.5; }
  .confirm-actions { display: flex; gap: 12px; justify-content: center; }
  
  .suspension-info { background: #fff7ed; border: 1px solid #fed7aa; border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; display: flex; align-items: center; gap: 12px; }
  .suspension-info .icon { width: 40px; height: 40px; background: #ffedd5; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .suspension-info .text strong { color: #c2410c; display: block; margin-bottom: 2px; }
  .suspension-info .text span { font-size: 13px; color: #9a3412; }
  
  .radio-group { display: flex; gap: 12px; }
  .radio-card { flex: 1; border: 2px solid #e5e7eb; border-radius: 12px; padding: 16px; cursor: pointer; transition: all 0.2s; text-align: center; }
  .radio-card:hover { border-color: #93c5fd; background: #eff6ff; }
  .radio-card.active { border-color: #2563eb; background: #eff6ff; }
  .radio-card .radio-icon { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-size: 22px; }
  .radio-card .radio-label { font-weight: 600; font-size: 14px; color: #374151; }
  .radio-card .radio-desc { font-size: 12px; color: #6b7280; margin-top: 4px; }
`;

const MatriculaAlumno = () => {
  const { token } = useAuth();
  const [aulas, setAulas] = useState([]);
  const [apoderados, setApoderados] = useState([]);
  const [alumnos, setAlumnos] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingAlumno, setEditingAlumno] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAula, setFilterAula] = useState('todos');
  const [filterEstado, setFilterEstado] = useState('todos');
  const [filterGenero, setFilterGenero] = useState('todos');
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Modal de suspensión
  const [suspensionModal, setSuspensionModal] = useState(false);
  const [alumnoASuspender, setAlumnoASuspender] = useState(null);
  const [suspensionData, setSuspensionData] = useState({ suspendido_desde: '', suspendido_hasta: '' });

  // Modal de cambio de estado
  const [estadoModal, setEstadoModal] = useState(false);
  const [alumnoAEstado, setAlumnoAEstado] = useState(null);
  const [nuevoEstado, setNuevoEstado] = useState('matriculado');

  const [formData, setFormData] = useState({
    dni_alumno: '', nombres_alumno: '', apellidos_alumno: '', genero: 'M',
    fecha_nacimiento: '', aula_id: '', estado: 'matriculado',
    dni_apoderado: '', nombres_apoderado: '', apellidos_apoderado: '',
    celular_apoderado: '', parentesco: 'Padre', correo_apoderado: '',
  });

  const headers = { Authorization: `Bearer ${token}` };

  const cargarDatos = useCallback(async () => {
    try {
      setLoading(true);
      const [aulasRes, apoderadosRes, alumnosRes] = await Promise.all([
        axios.get(`${API_URL}/aulas`, { headers }),
        axios.get(`${API_URL}/apoderados`, { headers }),
        axios.get(`${API_URL}/alumnos`, { headers }),
      ]);
      setAulas(Array.isArray(aulasRes.data) ? aulasRes.data : []);
      setApoderados(Array.isArray(apoderadosRes.data) ? apoderadosRes.data : []);
      setAlumnos(Array.isArray(alumnosRes.data) ? alumnosRes.data : []);
    } catch (err) {
      console.error('Error al cargar datos:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { cargarDatos(); }, [cargarDatos]);

  const resetForm = () => {
    setFormData({
      dni_alumno: '', nombres_alumno: '', apellidos_alumno: '', genero: 'M',
      fecha_nacimiento: '', aula_id: '', estado: 'matriculado',
      dni_apoderado: '', nombres_apoderado: '', apellidos_apoderado: '',
      celular_apoderado: '', parentesco: 'Padre', correo_apoderado: '',
    });
    setEditingAlumno(null);
    setError('');
    setSuccess('');
  };

  const handleEdit = (alumno) => {
    const apo = apoderados.find(a => a.id === alumno.apoderado_id);
    setEditingAlumno(alumno);
    setFormData({
      dni_alumno: alumno.dni || '',
      nombres_alumno: alumno.nombres || '',
      apellidos_alumno: alumno.apellidos || '',
      genero: alumno.genero || 'M',
      fecha_nacimiento: alumno.fecha_nacimiento || '',
      aula_id: alumno.aula_id?.toString() || '',
      estado: alumno.estado || 'matriculado',
      dni_apoderado: apo?.dni || '',
      nombres_apoderado: apo?.nombres || '',
      apellidos_apoderado: apo?.apellidos || '',
      celular_apoderado: apo?.celular || '',
      parentesco: apo?.parentesco || 'Padre',
      correo_apoderado: apo?.correo || '',
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      let apoderadoId = null;
      try {
        const resApoderado = await axios.get(`${API_URL}/apoderados/dni/${formData.dni_apoderado}`, { headers });
        apoderadoId = resApoderado.data.id;
      } catch (err) {
        if (err.response?.status === 404) {
          const nuevoApoderado = await axios.post(`${API_URL}/apoderados`, {
            dni: formData.dni_apoderado, nombres: formData.nombres_apoderado,
            apellidos: formData.apellidos_apoderado, celular: formData.celular_apoderado,
            parentesco: formData.parentesco, correo: formData.correo_apoderado || null,
          }, { headers });
          apoderadoId = nuevoApoderado.data.id;
        } else { throw err; }
      }

      const payload = {
        nombres: formData.nombres_alumno,
        apellidos: formData.apellidos_alumno,
        genero: formData.genero,
        fecha_nacimiento: formData.fecha_nacimiento,
        aula_id: parseInt(formData.aula_id),
        apoderado_id: apoderadoId,
      };

      if (editingAlumno) {
        await axios.patch(`${API_URL}/alumnos/${editingAlumno.id}`, payload, { headers });
        setSuccess('Alumno actualizado correctamente');
      } else {
        payload.dni = formData.dni_alumno;
        payload.estado = 'matriculado';
        await axios.post(`${API_URL}/alumnos`, payload, { headers });
        setSuccess('Alumno registrado correctamente');
      }

      resetForm();
      cargarDatos();
      setTimeout(() => { setModalOpen(false); setSuccess(''); }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  // Abrir modal de suspensión
  const abrirSuspension = (alumno) => {
    setAlumnoASuspender(alumno);
    setSuspensionData({
      suspendido_desde: alumno.suspendido_desde || '',
      suspendido_hasta: alumno.suspendido_hasta || '',
    });
    setSuspensionModal(true);
  };

  // Guardar suspensión
  const guardarSuspension = async () => {
    if (!suspensionData.suspendido_desde || !suspensionData.suspendido_hasta) {
      setError('Debe seleccionar ambas fechas');
      return;
    }
    if (suspensionData.suspendido_desde > suspensionData.suspendido_hasta) {
      setError('La fecha de inicio no puede ser mayor a la fecha final');
      return;
    }
    setSaving(true);
    try {
      await axios.patch(`${API_URL}/alumnos/${alumnoASuspender.id}`, {
        suspendido_desde: suspensionData.suspendido_desde,
        suspendido_hasta: suspensionData.suspendido_hasta,
      }, { headers });
      setSuccess('Suspensión actualizada correctamente');
      setSuspensionModal(false);
      cargarDatos();
      setTimeout(() => setSuccess(''), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar suspensión');
    } finally {
      setSaving(false);
    }
  };

  // Quitar suspensión
  const quitarSuspension = async () => {
    setSaving(true);
    try {
      await axios.patch(`${API_URL}/alumnos/${alumnoASuspender.id}`, {
        suspendido_desde: null,
        suspendido_hasta: null,
      }, { headers });
      setSuccess('Suspensión removida correctamente');
      setSuspensionModal(false);
      cargarDatos();
      setTimeout(() => setSuccess(''), 2000);
    } catch (err) {
      setError('Error al quitar suspensión');
    } finally {
      setSaving(false);
    }
  };

  // Abrir modal de cambio de estado
  const abrirEstado = (alumno) => {
    setAlumnoAEstado(alumno);
    setNuevoEstado(alumno.estado || 'matriculado');
    setEstadoModal(true);
  };

  // Guardar cambio de estado
  const guardarEstado = async () => {
    setSaving(true);
    try {
      await axios.patch(`${API_URL}/alumnos/${alumnoAEstado.id}`, {
        estado: nuevoEstado,
      }, { headers });
      setSuccess('Estado actualizado correctamente');
      setEstadoModal(false);
      cargarDatos();
      setTimeout(() => setSuccess(''), 2000);
    } catch (err) {
      setError('Error al cambiar estado');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`${API_URL}/alumnos/${id}`, { headers });
      setDeleteConfirm(null);
      cargarDatos();
      setSuccess('Alumno eliminado correctamente');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) { setError('Error al eliminar alumno'); }
  };

  const getAulaText = (aulaId) => {
    const aula = aulas.find(a => a.id === aulaId);
    return aula ? `${aula.grado}° "${aula.seccion}"` : '—';
  };

  const getApoderadoInfo = (apoderadoId) => apoderados.find(a => a.id === apoderadoId) || null;

  const estaSuspendido = (alumno) => {
    if (!alumno.suspendido_desde || !alumno.suspendido_hasta) return false;
    const hoy = new Date();
    return hoy >= new Date(alumno.suspendido_desde) && hoy <= new Date(alumno.suspendido_hasta);
  };

  const filteredAlumnos = alumnos.filter(alumno => {
    const search = searchTerm.toLowerCase();
    const apo = getApoderadoInfo(alumno.apoderado_id);
    const matchSearch = !searchTerm || 
      alumno.nombres.toLowerCase().includes(search) ||
      alumno.apellidos.toLowerCase().includes(search) ||
      alumno.dni.includes(search) ||
      (apo && (apo.nombres.toLowerCase().includes(search) || apo.apellidos.toLowerCase().includes(search) || apo.dni.includes(search)));
    const matchAula = filterAula === 'todos' || alumno.aula_id?.toString() === filterAula;
    const matchEstado = filterEstado === 'todos' || alumno.estado === filterEstado;
    const matchGenero = filterGenero === 'todos' || alumno.genero === filterGenero;
    return matchSearch && matchAula && matchEstado && matchGenero;
  });

  const exportToCSV = () => {
    const headers = ['DNI Alumno', 'Apellidos', 'Nombres', 'Género', 'Fecha Nac.', 'Aula', 'Estado', 'DNI Apoderado', 'Apoderado', 'Parentesco', 'Celular'];
    const rows = filteredAlumnos.map(a => {
      const apo = getApoderadoInfo(a.apoderado_id);
      return [a.dni, a.apellidos, a.nombres, a.genero, a.fecha_nacimiento, getAulaText(a.aula_id), a.estado || 'matriculado', apo?.dni || '', `${apo?.nombres || ''} ${apo?.apellidos || ''}`, apo?.parentesco || '', apo?.celular || ''];
    });
    const csv = [headers, ...rows].map(r => r.map(c => `"${c || ''}"`).join(',')).join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = `alumnos_${new Date().toISOString().slice(0, 10)}.csv`; link.click();
    URL.revokeObjectURL(url);
  };

  const stats = {
    total: alumnos.length,
    activos: alumnos.filter(a => a.estado === 'matriculado').length,
    trasladados: alumnos.filter(a => a.estado === 'trasladado').length,
    retirados: alumnos.filter(a => a.estado === 'retirado').length,
    suspendidos: alumnos.filter(a => estaSuspendido(a)).length,
  };

  return (
    <div className="matricula-container">
      <style>{styles}</style>

      <div className="matricula-header">
        <div>
          <h1>Matrícula de Alumnos</h1>
          <p>Registra, edita, suspende y gestiona el estado de cada estudiante</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button onClick={exportToCSV} className="btn btn-success" disabled={filteredAlumnos.length === 0}>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Exportar CSV
          </button>
          <button onClick={() => { resetForm(); setModalOpen(true); }} className="btn btn-primary">
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Nuevo Alumno
          </button>
        </div>
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
          { d: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197', c: '#2563eb', b: '#dbeafe', v: stats.total, l: 'Total' },
          { d: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', c: '#059669', b: '#d1fae5', v: stats.activos, l: 'Matriculados' },
          { d: 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4', c: '#d97706', b: '#fef3c7', v: stats.trasladados, l: 'Trasladados' },
          { d: 'M6 18L18 6M6 6l12 12', c: '#dc2626', b: '#fee2e2', v: stats.retirados, l: 'Retirados' },
          { d: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z', c: '#ea580c', b: '#fff7ed', v: stats.suspendidos, l: 'Suspendidos' },
        ].map((s, i) => (
          <div className="stat-card" key={i}>
            <div className="stat-icon" style={{ background: s.b }}>
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke={s.c} strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d={s.d} />
              </svg>
            </div>
            <div className="stat-value" style={{ color: s.c }}>{s.v}</div>
            <div className="stat-label">{s.l}</div>
          </div>
        ))}
      </div>

      <div className="filters-bar">
        <div className="search-box">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input type="text" placeholder="Buscar alumno o apoderado..." value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)} className="input input-search" />
        </div>
        <select value={filterAula} onChange={(e) => setFilterAula(e.target.value)} className="select">
          <option value="todos">Todas las aulas</option>
          {aulas.map(a => <option key={a.id} value={a.id}>{a.grado}° "{a.seccion}"</option>)}
        </select>
        <select value={filterEstado} onChange={(e) => setFilterEstado(e.target.value)} className="select">
          <option value="todos">Todos los estados</option>
          <option value="matriculado">Matriculado</option>
          <option value="trasladado">Trasladado</option>
          <option value="retirado">Retirado</option>
        </select>
        <select value={filterGenero} onChange={(e) => setFilterGenero(e.target.value)} className="select" style={{ minWidth: '120px' }}>
          <option value="todos">Todos ♂♀</option>
          <option value="M">Masculino</option>
          <option value="F">Femenino</option>
        </select>
        <span className="result-count">{filteredAlumnos.length} de {alumnos.length} alumnos</span>
      </div>

      <div className="table-wrapper">
        {loading ? <div className="spinner" /> : filteredAlumnos.length === 0 ? (
          <div className="empty-state">
            <svg width="80" height="80" fill="none" viewBox="0 0 24 24" stroke="#d1d5db" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197" />
            </svg>
            <p style={{ fontSize: 18, fontWeight: 600, color: '#6b7280', marginBottom: 4 }}>Sin resultados</p>
          </div>
        ) : (
          <div className="table-scroll">
            <table className="table">
              <thead>
                <tr>
                  <th>DNI</th><th>Apellidos y Nombres</th><th>Gén.</th><th>Fecha Nac.</th>
                  <th>Aula</th><th>Estado</th><th>DNI Apod.</th><th>Apoderado</th>
                  <th>Parentesco</th><th>Celular</th><th style={{ textAlign: 'center', width: 130 }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredAlumnos.map(alumno => {
                  const apo = getApoderadoInfo(alumno.apoderado_id);
                  return (
                    <tr key={alumno.id} className={estaSuspendido(alumno) ? 'row-suspended' : ''}>
                      <td style={{ fontFamily: 'monospace', fontWeight: 600, fontSize: 13 }}>{alumno.dni}</td>
                      <td style={{ fontWeight: 600 }}>{alumno.apellidos}, {alumno.nombres}</td>
                      <td><span className={`badge ${alumno.genero === 'M' ? 'badge-blue' : 'badge-pink'}`}>{alumno.genero === 'M' ? 'M' : 'F'}</span></td>
                      <td style={{ fontSize: 13, color: '#6b7280' }}>{alumno.fecha_nacimiento}</td>
                      <td><span className="badge badge-blue">{getAulaText(alumno.aula_id)}</span></td>
                      <td>
                        <span className={`badge ${alumno.estado === 'matriculado' ? 'badge-green' : alumno.estado === 'trasladado' ? 'badge-amber' : 'badge-red'}`}>
                          {alumno.estado || 'matriculado'}
                        </span>
                        {estaSuspendido(alumno) && <span className="badge badge-orange" style={{ marginLeft: 6 }}>Suspendido</span>}
                      </td>
                      <td style={{ fontFamily: 'monospace', fontSize: 13 }}>{apo?.dni || '—'}</td>
                      <td style={{ fontWeight: 500 }}>{apo ? `${apo.nombres} ${apo.apellidos}` : '—'}</td>
                      <td>{apo?.parentesco || '—'}</td>
                      <td>{apo?.celular || '—'}</td>
                      <td>
                        <div style={{ display: 'flex', justifyContent: 'center', gap: 4 }}>
                          <button onClick={() => handleEdit(alumno)} className="btn-ghost" title="Editar datos" style={{ color: '#2563eb' }}>
                            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          <button onClick={() => abrirSuspension(alumno)} className="btn-ghost" title="Suspender" style={{ color: estaSuspendido(alumno) ? '#ea580c' : '#f59e0b' }}>
                            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                          </button>
                          <button onClick={() => abrirEstado(alumno)} className="btn-ghost" title="Cambiar estado" style={{ color: '#7c3aed' }}>
                            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                          </button>
                          <button onClick={() => setDeleteConfirm(alumno)} className="btn-ghost" style={{ color: '#ef4444' }} title="Eliminar">
                            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Registrar/Editar Alumno */}
      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingAlumno ? 'Editar Alumno' : 'Registrar Nuevo Alumno'}</h2>
              <button onClick={() => setModalOpen(false)} className="btn-ghost">
                <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleSubmit}>
                {error && <div className="alert alert-error"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>{error}</div>}
                <div className="section-box">
                  <h3><svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>Datos del Apoderado</h3>
                  <div className="form-grid">
                    <div className="form-group"><label>DNI *</label><input required value={formData.dni_apoderado} onChange={(e) => setFormData({ ...formData, dni_apoderado: e.target.value.replace(/\D/g, '').slice(0, 8) })} className="input" placeholder="12345678" maxLength={8} /></div>
                    <div className="form-group"><label>Celular *</label><input required value={formData.celular_apoderado} onChange={(e) => setFormData({ ...formData, celular_apoderado: e.target.value.replace(/\D/g, '').slice(0, 9) })} className="input" placeholder="999999999" maxLength={9} /></div>
                    <div className="form-group"><label>Nombres *</label><input required value={formData.nombres_apoderado} onChange={(e) => setFormData({ ...formData, nombres_apoderado: e.target.value })} className="input" placeholder="Nombres" /></div>
                    <div className="form-group"><label>Apellidos *</label><input required value={formData.apellidos_apoderado} onChange={(e) => setFormData({ ...formData, apellidos_apoderado: e.target.value })} className="input" placeholder="Apellidos" /></div>
                    <div className="form-group"><label>Parentesco *</label><select value={formData.parentesco} onChange={(e) => setFormData({ ...formData, parentesco: e.target.value })} className="select"><option>Padre</option><option>Madre</option><option>Tío</option><option>Tía</option><option>Abuelo</option><option>Abuela</option><option>Hermano Mayor</option><option>Tutor Legal</option></select></div>
                    <div className="form-group"><label>Correo</label><input type="email" value={formData.correo_apoderado} onChange={(e) => setFormData({ ...formData, correo_apoderado: e.target.value })} className="input" placeholder="correo@ejemplo.com" /></div>
                  </div>
                </div>
                <div className="section-box">
                  <h3><svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197" /></svg>Datos del Alumno</h3>
                  <div className="form-grid">
                    <div className="form-group"><label>DNI *</label><input required value={formData.dni_alumno} onChange={(e) => setFormData({ ...formData, dni_alumno: e.target.value.replace(/\D/g, '').slice(0, 8) })} className="input" placeholder="12345678" maxLength={8} disabled={!!editingAlumno} /></div>
                    <div className="form-group"><label>Fecha Nac. *</label><input type="date" required value={formData.fecha_nacimiento} onChange={(e) => setFormData({ ...formData, fecha_nacimiento: e.target.value })} className="input" /></div>
                    <div className="form-group"><label>Nombres *</label><input required value={formData.nombres_alumno} onChange={(e) => setFormData({ ...formData, nombres_alumno: e.target.value })} className="input" placeholder="Nombres" /></div>
                    <div className="form-group"><label>Apellidos *</label><input required value={formData.apellidos_alumno} onChange={(e) => setFormData({ ...formData, apellidos_alumno: e.target.value })} className="input" placeholder="Apellidos" /></div>
                    <div className="form-group"><label>Género *</label><select value={formData.genero} onChange={(e) => setFormData({ ...formData, genero: e.target.value })} className="select"><option value="M">Masculino</option><option value="F">Femenino</option></select></div>
                    <div className="form-group"><label>Aula *</label><select required value={formData.aula_id} onChange={(e) => setFormData({ ...formData, aula_id: e.target.value })} className="select"><option value="">Seleccionar</option>{aulas.map(a => <option key={a.id} value={a.id}>{a.grado}° "{a.seccion}" - {a.anio_escolar}</option>)}</select></div>
                  </div>
                </div>
                <div className="form-actions">
                  <button type="button" onClick={() => setModalOpen(false)} className="btn btn-secondary">Cancelar</button>
                  <button type="submit" className="btn btn-primary" disabled={saving}>
                    {saving ? 'Guardando...' : editingAlumno ? 'Guardar Cambios' : 'Registrar Alumno'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Suspensión */}
      {suspensionModal && alumnoASuspender && (
        <div className="modal-overlay" onClick={() => setSuspensionModal(false)}>
          <div className="modal modal-sm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Suspensión de Alumno</h2>
              <button onClick={() => setSuspensionModal(false)} className="btn-ghost">
                <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="modal-body">
              {error && <div className="alert alert-error"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>{error}</div>}

              <div className="suspension-info">
                <div className="icon">
                  <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#ea580c" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <div className="text">
                  <strong>{alumnoASuspender.apellidos}, {alumnoASuspender.nombres}</strong>
                  <span>DNI: {alumnoASuspender.dni} | {getAulaText(alumnoASuspender.aula_id)}</span>
                </div>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label>Fecha de inicio de suspensión *</label>
                  <input type="date" value={suspensionData.suspendido_desde}
                    onChange={(e) => setSuspensionData({ ...suspensionData, suspendido_desde: e.target.value })}
                    className="input" />
                </div>
                <div className="form-group">
                  <label>Fecha de fin de suspensión *</label>
                  <input type="date" value={suspensionData.suspendido_hasta}
                    onChange={(e) => setSuspensionData({ ...suspensionData, suspendido_hasta: e.target.value })}
                    className="input" />
                </div>
              </div>

              <div className="form-actions">
                {alumnoASuspender.suspendido_desde && (
                  <button type="button" onClick={quitarSuspension} className="btn btn-danger" disabled={saving}>
                    Quitar Suspensión
                  </button>
                )}
                <button type="button" onClick={() => setSuspensionModal(false)} className="btn btn-secondary">Cancelar</button>
                <button type="button" onClick={guardarSuspension} className="btn btn-warning" disabled={saving}>
                  {saving ? 'Guardando...' : 'Guardar Suspensión'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Cambio de Estado */}
      {estadoModal && alumnoAEstado && (
        <div className="modal-overlay" onClick={() => setEstadoModal(false)}>
          <div className="modal modal-sm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Cambiar Estado del Alumno</h2>
              <button onClick={() => setEstadoModal(false)} className="btn-ghost">
                <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="modal-body">
              <div className="suspension-info" style={{ background: '#f0fdf4', borderColor: '#bbf7d0' }}>
                <div className="icon" style={{ background: '#dcfce7' }}>
                  <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#059669" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </div>
                <div className="text">
                  <strong>{alumnoAEstado.apellidos}, {alumnoAEstado.nombres}</strong>
                  <span>Estado actual: <span className={`badge ${alumnoAEstado.estado === 'matriculado' ? 'badge-green' : alumnoAEstado.estado === 'trasladado' ? 'badge-amber' : 'badge-red'}`}>{alumnoAEstado.estado || 'matriculado'}</span></span>
                </div>
              </div>

              <div className="radio-group" style={{ marginBottom: '24px' }}>
                {[
                  { value: 'matriculado', icon: '✓', color: '#059669', bg: '#d1fae5', label: 'Matriculado', desc: 'Alumno activo' },
                  { value: 'trasladado', icon: '→', color: '#d97706', bg: '#fef3c7', label: 'Trasladado', desc: 'Cambió de colegio' },
                  { value: 'retirado', icon: '✕', color: '#dc2626', bg: '#fee2e2', label: 'Retirado', desc: 'Ya no estudia' },
                ].map(opt => (
                  <div key={opt.value} className={`radio-card ${nuevoEstado === opt.value ? 'active' : ''}`}
                    onClick={() => setNuevoEstado(opt.value)}>
                    <div className="radio-icon" style={{ background: opt.bg, color: opt.color }}>{opt.icon}</div>
                    <div className="radio-label">{opt.label}</div>
                    <div className="radio-desc">{opt.desc}</div>
                  </div>
                ))}
              </div>

              <div className="form-actions">
                <button type="button" onClick={() => setEstadoModal(false)} className="btn btn-secondary">Cancelar</button>
                <button type="button" onClick={guardarEstado} className="btn btn-primary" disabled={saving}>
                  {saving ? 'Guardando...' : 'Cambiar Estado'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      {deleteConfirm && (
        <div className="modal-overlay" style={{ zIndex: 60, background: 'rgba(0,0,0,0.6)' }} onClick={() => setDeleteConfirm(null)}>
          <div className="confirm-box" onClick={(e) => e.stopPropagation()}>
            <div className="confirm-icon" style={{ background: '#fee2e2' }}>
              <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="#dc2626" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="confirm-title">¿Eliminar alumno?</h3>
            <p className="confirm-text">Se eliminará a <strong>{deleteConfirm.nombres} {deleteConfirm.apellidos}</strong>.</p>
            <div className="confirm-actions">
              <button onClick={() => setDeleteConfirm(null)} className="btn btn-secondary">Cancelar</button>
              <button onClick={() => handleDelete(deleteConfirm.id)} className="btn btn-danger">Eliminar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MatriculaAlumno;