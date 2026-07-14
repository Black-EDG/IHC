import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const styles = `
  .apoderado-container { padding: 24px; max-width: 1340px; margin: 0 auto; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; color: #1f2937; }
  .apoderado-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 28px; flex-wrap: wrap; gap: 16px; }
  .apoderado-header h1 { font-size: 28px; font-weight: 800; color: #111827; margin: 0; letter-spacing: -0.5px; }
  .apoderado-header p { font-size: 14px; color: #6b7280; margin: 4px 0 0 0; }
  
  .btn { padding: 10px 20px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }
  .btn-primary { background: #059669; color: #fff; }
  .btn-primary:hover { background: #047857; box-shadow: 0 4px 15px rgba(5,150,105,0.3); }
  .btn-secondary { background: #fff; color: #374151; border: 1px solid #d1d5db; }
  .btn-secondary:hover { background: #f9fafb; }
  .btn-ghost { background: transparent; color: #6b7280; padding: 8px; border-radius: 8px; border: none; cursor: pointer; }
  .btn-ghost:hover { background: #f3f4f6; color: #374151; }
  .btn-danger { background: #ef4444; color: #fff; }
  .btn-danger:hover { background: #dc2626; }
  .btn-outline { background: #fff; color: #059669; border: 2px solid #059669; }
  .btn-outline:hover { background: #ecfdf5; }
  
  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
  @media (max-width: 900px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
  
  .stat-card { background: #fff; border-radius: 14px; padding: 20px 24px; border: 1px solid #e5e7eb; transition: all 0.2s; cursor: default; }
  .stat-card:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.06); transform: translateY(-2px); }
  .stat-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; }
  .stat-value { font-size: 32px; font-weight: 800; color: #111827; line-height: 1; }
  .stat-label { font-size: 13px; color: #6b7280; margin-top: 6px; font-weight: 500; }
  
  .filters-bar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }
  .search-box { position: relative; flex: 1; min-width: 220px; }
  .search-box svg { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); width: 18px; height: 18px; color: #9ca3af; pointer-events: none; }
  .input { width: 100%; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 10px; font-size: 14px; outline: none; transition: all 0.2s; background: #fff; box-sizing: border-box; color: #1f2937; }
  .input:focus { border-color: #059669; box-shadow: 0 0 0 3px rgba(5,150,105,0.1); }
  .input-search { padding-left: 42px; }
  .select { padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 10px; font-size: 14px; outline: none; background: #fff; cursor: pointer; color: #1f2937; }
  .select:focus { border-color: #059669; box-shadow: 0 0 0 3px rgba(5,150,105,0.1); }
  
  .table-wrapper { background: #fff; border-radius: 16px; border: 1px solid #e5e7eb; overflow: hidden; }
  .table-scroll { overflow-x: auto; }
  .table { width: 100%; border-collapse: collapse; min-width: 1000px; }
  .table th { background: #f9fafb; padding: 14px 16px; font-size: 11px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e5e7eb; text-align: left; }
  .table td { padding: 14px 16px; font-size: 13px; color: #374151; border-bottom: 1px solid #f3f4f6; vertical-align: middle; }
  .table tr:hover td { background: #fafbfc; }
  
  .badge { display: inline-flex; padding: 5px 10px; border-radius: 8px; font-size: 12px; font-weight: 600; white-space: nowrap; }
  .badge-green { background: #d1fae5; color: #065f46; }
  .badge-blue { background: #dbeafe; color: #1e40af; }
  .badge-purple { background: #ede9fe; color: #5b21b6; }
  .badge-gray { background: #f3f4f6; color: #6b7280; }
  
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 20px; }
  .modal { background: #fff; border-radius: 20px; width: 100%; max-width: 800px; max-height: 90vh; overflow-y: auto; box-shadow: 0 25px 60px rgba(0,0,0,0.2); }
  .modal-sm { max-width: 500px; }
  .modal-header { display: flex; align-items: center; justify-content: space-between; padding: 24px 28px; border-bottom: 1px solid #e5e7eb; position: sticky; top: 0; background: #fff; z-index: 1; border-radius: 20px 20px 0 0; }
  .modal-header h2 { font-size: 20px; font-weight: 700; color: #111827; margin: 0; }
  .modal-body { padding: 28px; }
  
  .form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; }
  .form-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
  @media (max-width: 640px) { .form-grid, .form-grid-3 { grid-template-columns: 1fr; } }
  .form-group { display: flex; flex-direction: column; gap: 6px; }
  .form-group label { font-size: 13px; font-weight: 600; color: #374151; }
  .form-group.full { grid-column: 1 / -1; }
  .form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 28px; padding-top: 20px; border-top: 1px solid #f3f4f6; }
  
  .section-box { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 14px; padding: 24px; margin-bottom: 24px; }
  .section-box h3 { font-size: 15px; font-weight: 700; color: #111827; margin: 0 0 18px 0; display: flex; align-items: center; gap: 8px; }
  
  .alert { padding: 12px 16px; border-radius: 12px; font-size: 14px; display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
  .alert-error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
  .alert-success { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
  
  .result-count { font-size: 13px; color: #6b7280; font-weight: 500; white-space: nowrap; }
  
  .spinner { width: 40px; height: 40px; border: 3px solid #d1fae5; border-top-color: #059669; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 40px auto; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .empty-state { text-align: center; padding: 60px 24px; color: #9ca3af; }
  
  .confirm-box { background: #fff; border-radius: 20px; padding: 32px; text-align: center; max-width: 420px; box-shadow: 0 25px 60px rgba(0,0,0,0.25); }
  .confirm-icon { width: 64px; height: 64px; background: #fee2e2; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
  .confirm-title { font-size: 20px; font-weight: 700; color: #111827; margin-bottom: 8px; }
  .confirm-text { color: #6b7280; font-size: 14px; margin-bottom: 24px; line-height: 1.5; }
  .confirm-actions { display: flex; gap: 12px; justify-content: center; }
`;

const MatriculaApoderado = () => {
  const { token } = useAuth();
  const [apoderados, setApoderados] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingApoderado, setEditingApoderado] = useState(null);
  const [saving, setSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    dni: '', nombres: '', apellidos: '', celular: '', parentesco: 'Padre', correo: '',
    contacto_emergencia_nombre: '', contacto_emergencia_celular: '', contacto_emergencia_parentesco: '',
  });

  const headers = { Authorization: `Bearer ${token}` };

  const cargarApoderados = useCallback(async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_URL}/apoderados`, { headers });
      setApoderados(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error('Error al cargar apoderados:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { cargarApoderados(); }, [cargarApoderados]);

  const resetForm = () => {
    setFormData({
      dni: '', nombres: '', apellidos: '', celular: '', parentesco: 'Padre', correo: '',
      contacto_emergencia_nombre: '', contacto_emergencia_celular: '', contacto_emergencia_parentesco: '',
    });
    setEditingApoderado(null);
    setError('');
    setSuccess('');
  };

  const handleEdit = (apoderado) => {
    setEditingApoderado(apoderado);
    setFormData({
      dni: apoderado.dni || '',
      nombres: apoderado.nombres || '',
      apellidos: apoderado.apellidos || '',
      celular: apoderado.celular || '',
      parentesco: apoderado.parentesco || 'Padre',
      correo: apoderado.correo || '',
      contacto_emergencia_nombre: apoderado.contacto_emergencia_nombre || '',
      contacto_emergencia_celular: apoderado.contacto_emergencia_celular || '',
      contacto_emergencia_parentesco: apoderado.contacto_emergencia_parentesco || '',
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      if (editingApoderado) {
        await axios.patch(`${API_URL}/apoderados/${editingApoderado.id}`, formData, { headers });
        setSuccess('Apoderado actualizado correctamente');
      } else {
        await axios.post(`${API_URL}/apoderados`, formData, { headers });
        setSuccess('Apoderado registrado correctamente');
      }
      resetForm();
      cargarApoderados();
      setTimeout(() => { setModalOpen(false); setSuccess(''); }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar apoderado');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`${API_URL}/apoderados/${id}`, { headers });
      setDeleteConfirm(null);
      cargarApoderados();
      setSuccess('Apoderado eliminado correctamente');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) { setError('Error al eliminar apoderado'); }
  };

  const filteredApoderados = apoderados.filter(apo => {
    const search = searchTerm.toLowerCase();
    return !searchTerm || 
      apo.nombres.toLowerCase().includes(search) ||
      apo.apellidos.toLowerCase().includes(search) ||
      apo.dni.includes(search) ||
      apo.celular.includes(search);
  });

  const exportToCSV = () => {
    const headers = ['DNI', 'Nombres', 'Apellidos', 'Celular', 'Parentesco', 'Correo', 'Emergencia Nombre', 'Emergencia Celular', 'Emergencia Parentesco'];
    const rows = filteredApoderados.map(a => [a.dni, a.nombres, a.apellidos, a.celular, a.parentesco, a.correo || '', a.contacto_emergencia_nombre || '', a.contacto_emergencia_celular || '', a.contacto_emergencia_parentesco || '']);
    const csv = [headers, ...rows].map(r => r.map(c => `"${c || ''}"`).join(',')).join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = `apoderados_${new Date().toISOString().slice(0, 10)}.csv`; link.click();
    URL.revokeObjectURL(url);
  };

  const parentescos = ['Padre', 'Madre', 'Tío', 'Tía', 'Abuelo', 'Abuela', 'Hermano Mayor', 'Tutor Legal'];

  return (
    <div className="apoderado-container">
      <style>{styles}</style>

      <div className="apoderado-header">
        <div>
          <h1>Gestión de Apoderados</h1>
          <p>Registra, edita y administra los padres de familia y tutores del colegio</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button onClick={exportToCSV} className="btn btn-outline" disabled={filteredApoderados.length === 0}>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Exportar CSV
          </button>
          <button onClick={() => { resetForm(); setModalOpen(true); }} className="btn btn-primary">
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Nuevo Apoderado
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
          { icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z', color: '#059669', bg: '#d1fae5', value: apoderados.length, label: 'Total Apoderados' },
          { icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', color: '#2563eb', bg: '#dbeafe', value: apoderados.filter(a => a.correo).length, label: 'Con correo' },
          { icon: 'M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z', color: '#7c3aed', bg: '#ede9fe', value: apoderados.filter(a => a.celular).length, label: 'Con celular' },
          { icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z', color: '#d97706', bg: '#fef3c7', value: [...new Set(apoderados.map(a => a.parentesco))].length, label: 'Parentescos' },
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
        <div className="search-box">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input type="text" placeholder="Buscar por nombre, DNI o celular..." value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)} className="input input-search" />
        </div>
        <span className="result-count">{filteredApoderados.length} de {apoderados.length} apoderados</span>
      </div>

      <div className="table-wrapper">
        {loading ? <div className="spinner" /> : filteredApoderados.length === 0 ? (
          <div className="empty-state">
            <svg width="80" height="80" fill="none" viewBox="0 0 24 24" stroke="#d1d5db" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <p style={{ fontSize: 18, fontWeight: 600, color: '#6b7280', marginBottom: 4 }}>Sin resultados</p>
            <p style={{ fontSize: 14 }}>Registra un nuevo apoderado o ajusta los filtros</p>
          </div>
        ) : (
          <div className="table-scroll">
            <table className="table">
              <thead>
                <tr>
                  <th>DNI</th>
                  <th>Apellidos y Nombres</th>
                  <th>Celular</th>
                  <th>Parentesco</th>
                  <th>Correo</th>
                  <th>Emergencia</th>
                  <th style={{ textAlign: 'center', width: 100 }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredApoderados.map(apo => (
                  <tr key={apo.id}>
                    <td style={{ fontFamily: 'monospace', fontWeight: 600, fontSize: 13 }}>{apo.dni}</td>
                    <td style={{ fontWeight: 600 }}>{apo.apellidos}, {apo.nombres}</td>
                    <td>{apo.celular}</td>
                    <td><span className="badge badge-green">{apo.parentesco}</span></td>
                    <td style={{ fontSize: 13, color: '#6b7280' }}>{apo.correo || '—'}</td>
                    <td style={{ fontSize: 13 }}>
                      {apo.contacto_emergencia_nombre ? (
                        <div>
                          <span style={{ fontWeight: 500 }}>{apo.contacto_emergencia_nombre}</span>
                          <span style={{ color: '#9ca3af', marginLeft: 8 }}>{apo.contacto_emergencia_celular}</span>
                        </div>
                      ) : '—'}
                    </td>
                    <td>
                      <div style={{ display: 'flex', justifyContent: 'center', gap: 4 }}>
                        <button onClick={() => handleEdit(apo)} className="btn-ghost" title="Editar" style={{ color: '#2563eb' }}>
                          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button onClick={() => setDeleteConfirm(apo)} className="btn-ghost" style={{ color: '#ef4444' }} title="Eliminar">
                          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Registrar/Editar */}
      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingApoderado ? 'Editar Apoderado' : 'Registrar Nuevo Apoderado'}</h2>
              <button onClick={() => setModalOpen(false)} className="btn-ghost">
                <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleSubmit}>
                {error && <div className="alert alert-error"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>{error}</div>}
                {success && <div className="alert alert-success"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>{success}</div>}

                <div className="section-box">
                  <h3>
                    <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Datos del Titular
                  </h3>
                  <div className="form-grid">
                    <div className="form-group"><label>DNI *</label><input required value={formData.dni} onChange={(e) => setFormData({ ...formData, dni: e.target.value.replace(/\D/g, '').slice(0, 8) })} className="input" placeholder="12345678" maxLength={8} disabled={!!editingApoderado} /></div>
                    <div className="form-group"><label>Celular *</label><input required value={formData.celular} onChange={(e) => setFormData({ ...formData, celular: e.target.value.replace(/\D/g, '').slice(0, 9) })} className="input" placeholder="999999999" maxLength={9} /></div>
                    <div className="form-group"><label>Nombres *</label><input required value={formData.nombres} onChange={(e) => setFormData({ ...formData, nombres: e.target.value })} className="input" placeholder="Nombres" /></div>
                    <div className="form-group"><label>Apellidos *</label><input required value={formData.apellidos} onChange={(e) => setFormData({ ...formData, apellidos: e.target.value })} className="input" placeholder="Apellidos" /></div>
                    <div className="form-group">
                      <label>Parentesco *</label>
                      <select value={formData.parentesco} onChange={(e) => setFormData({ ...formData, parentesco: e.target.value })} className="select">
                        {parentescos.map(p => <option key={p} value={p}>{p}</option>)}
                      </select>
                    </div>
                    <div className="form-group"><label>Correo</label><input type="email" value={formData.correo} onChange={(e) => setFormData({ ...formData, correo: e.target.value })} className="input" placeholder="correo@ejemplo.com" /></div>
                  </div>
                </div>

                <div className="section-box">
                  <h3>
                    <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 5.636a9 9 0 010 12.728M5.636 18.364a9 9 0 010-12.728M8.464 15.536a5 5 0 010-7.072m7.072 0a5 5 0 010 7.072" />
                    </svg>
                    Contacto de Emergencia
                  </h3>
                  <div className="form-grid-3">
                    <div className="form-group"><label>Nombre completo</label><input value={formData.contacto_emergencia_nombre} onChange={(e) => setFormData({ ...formData, contacto_emergencia_nombre: e.target.value })} className="input" placeholder="Nombre del contacto" /></div>
                    <div className="form-group"><label>Celular</label><input value={formData.contacto_emergencia_celular} onChange={(e) => setFormData({ ...formData, contacto_emergencia_celular: e.target.value.replace(/\D/g, '').slice(0, 9) })} className="input" placeholder="999999999" maxLength={9} /></div>
                    <div className="form-group">
                      <label>Parentesco</label>
                      <select value={formData.contacto_emergencia_parentesco} onChange={(e) => setFormData({ ...formData, contacto_emergencia_parentesco: e.target.value })} className="select">
                        <option value="">Seleccionar</option>
                        {parentescos.map(p => <option key={p} value={p}>{p}</option>)}
                        <option value="Vecino">Vecino</option>
                        <option value="Madrina">Madrina</option>
                        <option value="Padrino">Padrino</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="form-actions">
                  <button type="button" onClick={() => setModalOpen(false)} className="btn btn-secondary">Cancelar</button>
                  <button type="submit" className="btn btn-primary" disabled={saving}>
                    {saving ? 'Guardando...' : editingApoderado ? 'Guardar Cambios' : 'Registrar Apoderado'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      {deleteConfirm && (
        <div className="modal-overlay" style={{ zIndex: 60, background: 'rgba(0,0,0,0.6)' }} onClick={() => setDeleteConfirm(null)}>
          <div className="confirm-box" onClick={(e) => e.stopPropagation()}>
            <div className="confirm-icon">
              <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="#dc2626" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="confirm-title">¿Eliminar apoderado?</h3>
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

export default MatriculaApoderado;