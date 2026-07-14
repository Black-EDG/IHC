import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const GestionUsuarios = () => {
  const { token } = useAuth();
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    dni: '', nombres: '', apellidos: '', celular: '', correo: '',
    rol: 'docente', contrasena: '', estado: 'activo',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRol, setFilterRol] = useState('todos');
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const headers = { Authorization: `Bearer ${token}` };

  const cargarUsuarios = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await axios.get(`${API_URL}/usuarios/`, { headers });
      setUsuarios(res.data);
    } catch (err) {
      setError('Error al cargar la lista de usuarios.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) cargarUsuarios();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (editingUser) {
        await axios.put(`${API_URL}/usuarios/${editingUser.id}`, formData, { headers });
        setSuccess('Usuario actualizado correctamente');
      } else {
        await axios.post(`${API_URL}/usuarios/`, formData, { headers });
        setSuccess('Usuario creado correctamente');
      }
      resetForm();
      cargarUsuarios();
      setTimeout(() => { setModalOpen(false); setSuccess(''); }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al procesar la solicitud');
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`${API_URL}/usuarios/${id}`, { headers });
      setDeleteConfirm(null);
      cargarUsuarios();
      setSuccess('Usuario eliminado correctamente');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Error al eliminar usuario');
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      dni: user.dni,
      nombres: user.nombres,
      apellidos: user.apellidos,
      celular: user.celular || '',
      correo: user.correo,
      rol: user.rol,
      contrasena: '',
      estado: user.estado,
    });
    setModalOpen(true);
  };

  const resetForm = () => {
    setFormData({
      dni: '', nombres: '', apellidos: '', celular: '', correo: '',
      rol: 'docente', contrasena: '', estado: 'activo',
    });
    setEditingUser(null);
  };

  const filteredUsers = usuarios.filter(user => {
    const matchSearch = 
      user.nombres?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.apellidos?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.dni?.includes(searchTerm) ||
      user.correo?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchRol = filterRol === 'todos' || user.rol === filterRol;
    return matchSearch && matchRol;
  });

  const stats = {
    total: usuarios.length,
    activos: usuarios.filter(u => u.estado === 'activo').length,
    docentes: usuarios.filter(u => u.rol === 'docente').length,
    auxiliares: usuarios.filter(u => u.rol === 'auxiliar').length,
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'system-ui, sans-serif' }}>
      
      {/* Estilos Globales Inyectados Limpios y Modernos */}
      <style>{`
        .gu-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 16px; }
        .gu-title { margin: 0; font-size: 28px; font-weight: 700; color: #111827; }
        .gu-subtitle { margin: 4px 0 0 0; font-size: 14px; color: #6b7280; }
        
        .gu-btn { padding: 10px 18px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; border: none; display: inline-flex; align-items: center; gap: 8px; transition: background 0.2s; }
        .gu-btn-primary { background: #2563eb; color: white; }
        .gu-btn-primary:hover { background: #1d4ed8; }
        .gu-btn-secondary { background: #ffffff; color: #374151; border: 1px solid #d1d5db; }
        .gu-btn-secondary:hover { background: #f9fafb; }
        .gu-btn-danger { background: #ef4444; color: white; }
        .gu-btn-danger:hover { background: #dc2626; }
        .gu-btn-icon { background: transparent; color: #9ca3af; padding: 6px; border-radius: 6px; }
        .gu-btn-icon:hover { background: #f3f4f6; color: #374151; }
        .gu-btn-icon.danger:hover { background: #fee2e2; color: #ef4444; }

        .gu-alert { padding: 12px 16px; border-radius: 10px; font-size: 14px; font-weight: 500; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; border: 1px solid; }
        .gu-alert-success { background: #ecfdf5; color: #065f46; border-color: #a7f3d0; }
        .gu-alert-error { background: #fef2f2; color: #991b1b; border-color: #fca5a5; }

        .gu-stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .gu-stat-card { background: white; padding: 20px; border-radius: 14px; border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
        .gu-stat-num { font-size: 32px; font-weight: 700; color: #1f2937; line-height: 1; }
        .gu-stat-label { font-size: 12px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 6px; }

        .gu-filters-bar { display: flex; gap: 12px; margin-bottom: 20px; background: #f9fafb; padding: 12px; border-radius: 14px; border: 1px solid #eee; }
        .gu-search-wrapper { position: relative; flex: 1; }
        .gu-search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #9ca3af; width: 16px; height: 16px; }
        .gu-input { width: 100%; padding: 10px 12px 10px 38px; border: 1px solid #e5e7eb; border-radius: 10px; font-size: 14px; outline: none; background: white; box-sizing: border-box; }
        .gu-input:focus, .gu-select:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
        .gu-select { padding: 10px 16px; border: 1px solid #e5e7eb; border-radius: 10px; font-size: 14px; background: white; color: #374151; cursor: pointer; outline: none; }

        .gu-table-card { background: white; border-radius: 14px; border: 1px solid #e5e7eb; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.01); }
        .gu-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
        .gu-table th { background: #f9fafb; padding: 14px 18px; font-size: 11px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e5e7eb; }
        .gu-table td { padding: 14px 18px; color: #374151; border-bottom: 1px solid #f3f4f6; vertical-align: middle; }
        .gu-table tr:hover td { background: #fdfdfd; }

        .gu-badge { display: inline-flex; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; text-transform: capitalize; }
        .gu-badge-admin { background: #fee2e2; color: #991b1b; }
        .gu-badge-docente { background: #dbeafe; color: #1e40af; }
        .gu-badge-auxiliar { background: #fef3c7; color: #92400e; }
        .gu-badge-activo { background: #d1fae5; color: #065f46; }
        .gu-badge-licencia { background: #f3e8ff; color: #6b21a8; }
        .gu-badge-inactivo { background: #e5e7eb; color: #374151; }

        .gu-modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); backdrop-filter: blur(3px); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 20px; }
        .gu-modal { background: white; border-radius: 16px; width: 100%; max-width: 600px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
        .gu-modal-header { display: flex; justify-content: space-between; align-items: center; padding: 18px 24px; border-bottom: 1px solid #f3f4f6; }
        .gu-modal-body { padding: 24px; }
        .gu-form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
        .gu-form-group { display: flex; flex-direction: column; gap: 6px; }
        .gu-form-group.full { grid-column: span 2; }
        .gu-form-group label { font-size: 13px; font-weight: 600; color: #4b5563; }
        .gu-form-group input, .gu-form-group select { width: 100%; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; box-sizing: border-box; outline: none; }
        
        .gu-dialog-box { background: white; border-radius: 14px; padding: 24px; max-width: 400px; width: 100%; text-align: center; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
        
        @media (max-width: 640px) {
          .gu-form-grid { grid-template-columns: 1fr; }
          .gu-form-group.full { grid-column: span 1; }
          .gu-filters-bar { flex-direction: column; }
        }
      `}</style>

      {/* Header */}
      <div className="gu-header">
        <div>
          <h1 className="gu-title">Gestión de Usuarios</h1>
          <p className="gu-subtitle">Administra al personal docente y administrativo de la institución</p>
        </div>
        <button className="gu-btn gu-btn-primary" onClick={() => { resetForm(); setModalOpen(true); }}>
          <svg style={{ width: '16px', height: '16px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          Nuevo Usuario
        </button>
      </div>

      {/* Alertas */}
      {success && <div className="gu-alert gu-alert-success">{success}</div>}
      {error && <div className="gu-alert gu-alert-error">{error}</div>}

      {/* Módulo de Analíticas */}
      <div className="gu-stats-grid">
        <div className="gu-stat-card">
          <div className="gu-stat-num">{stats.total}</div>
          <div className="gu-stat-label">Total Personal</div>
        </div>
        <div className="gu-stat-card">
          <div className="gu-stat-num" style={{ color: '#059669' }}>{stats.activos}</div>
          <div className="gu-stat-label">Activos</div>
        </div>
        <div className="gu-stat-card">
          <div className="gu-stat-num" style={{ color: '#2563eb' }}>{stats.docentes}</div>
          <div className="gu-stat-label">Docentes</div>
        </div>
        <div className="gu-stat-card">
          <div className="gu-stat-num" style={{ color: '#d97706' }}>{stats.auxiliares}</div>
          <div className="gu-stat-label">Auxiliares</div>
        </div>
      </div>

      {/* Filtros */}
      <div className="gu-filters-bar">
        <div className="gu-search-wrapper">
          <svg className="gu-search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            className="gu-input"
            placeholder="Buscar por nombre, DNI o correo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <select className="gu-select" value={filterRol} onChange={(e) => setFilterRol(e.target.value)}>
          <option value="todos">Todos los roles</option>
          <option value="admin">Administrador</option>
          <option value="docente">Docente</option>
          <option value="auxiliar">Auxiliar</option>
        </select>
      </div>

      {/* Tabla de Datos */}
      <div className="gu-table-card" style={{ overflowX: 'auto' }}>
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280', fontWeight: '500' }}>
            Cargando registros del servidor...
          </div>
        ) : (
          <table className="gu-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>DNI</th>
                <th>Contacto</th>
                <th>Rol</th>
                <th>Estado</th>
                <th style={{ textAlign: 'right' }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', color: '#9ca3af', padding: '40px 0' }}>
                    No se encontraron usuarios en el sistema.
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user) => (
                  <tr key={user.id}>
                    <td style={{ fontWeight: '600', color: '#111827' }}>{user.nombres} {user.apellidos}</td>
                    <td style={{ fontFamily: 'monospace', color: '#4b5563' }}>{user.dni}</td>
                    <td>
                      <div style={{ color: '#374151' }}>{user.correo}</div>
                      {user.celular && <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '2px' }}>{user.celular}</div>}
                    </td>
                    <td><span className={`gu-badge gu-badge-${user.rol}`}>{user.rol}</span></td>
                    <td><span className={`gu-badge gu-badge-${user.estado}`}>{user.estado}</span></td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '6px' }}>
                        <button className="gu-btn-icon" title="Editar" onClick={() => handleEdit(user)}>
                          <svg style={{ width: '18px', height: '18px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button className="gu-btn-icon danger" title="Eliminar" onClick={() => setDeleteConfirm(user)}>
                          <svg style={{ width: '18px', height: '18px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal Formulario */}
      {modalOpen && (
        <div className="gu-modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="gu-modal" onClick={(e) => e.stopPropagation()}>
            <div className="gu-modal-header">
              <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#111827' }}>
                {editingUser ? 'Modificar Información de Usuario' : 'Registrar Nuevo Usuario'}
              </h3>
              <button className="gu-btn-icon" onClick={() => setModalOpen(false)}>
                <svg style={{ width: '20px', height: '20px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="gu-modal-body">
              <form onSubmit={handleSubmit}>
                <div className="gu-form-grid">
                  <div className="gu-form-group">
                    <label>Número DNI *</label>
                    <input
                      required pattern="\d{8}" maxLength={8}
                      value={formData.dni} disabled={!!editingUser}
                      onChange={(e) => setFormData({ ...formData, dni: e.target.value })}
                    />
                  </div>
                  <div className="gu-form-group">
                    <label>Teléfono Celular</label>
                    <input
                      pattern="\d{9}" maxLength={9}
                      value={formData.celular}
                      onChange={(e) => setFormData({ ...formData, celular: e.target.value })}
                    />
                  </div>
                  <div className="gu-form-group">
                    <label>Nombres *</label>
                    <input
                      required value={formData.nombres}
                      onChange={(e) => setFormData({ ...formData, nombres: e.target.value })}
                    />
                  </div>
                  <div className="gu-form-group">
                    <label>Apellidos *</label>
                    <input
                      required value={formData.apellidos}
                      onChange={(e) => setFormData({ ...formData, apellidos: e.target.value })}
                    />
                  </div>
                  <div className="gu-form-group gu-form-group.full">
                    <label>Correo Electrónico *</label>
                    <input
                      type="email" required
                      value={formData.correo}
                      onChange={(e) => setFormData({ ...formData, correo: e.target.value })}
                    />
                  </div>
                  <div className="gu-form-group">
                    <label>Asignación de Rol *</label>
                    <select value={formData.rol} onChange={(e) => setFormData({ ...formData, rol: e.target.value })}>
                      <option value="docente">Docente</option>
                      <option value="auxiliar">Auxiliar</option>
                      <option value="admin">Administrador</option>
                    </select>
                  </div>
                  <div className="gu-form-group">
                    <label>Estado Laboral</label>
                    <select value={formData.estado} onChange={(e) => setFormData({ ...formData, estado: e.target.value })}>
                      <option value="activo">Activo</option>
                      <option value="licencia">Licencia</option>
                      <option value="inactivo">Inactivo</option>
                    </select>
                  </div>
                  <div className="gu-form-group gu-form-group.full">
                    <label>Contraseña {editingUser ? '(dejar en blanco para conservar)' : '*'}</label>
                    <input
                      type="password" required={!editingUser} minLength={6}
                      value={formData.contrasena}
                      onChange={(e) => setFormData({ ...formData, contrasena: e.target.value })}
                    />
                  </div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px', paddingTop: '16px', borderTop: '1px solid #f3f4f6' }}>
                  <button type="button" className="gu-btn gu-btn-secondary" onClick={() => setModalOpen(false)}>Cancelar</button>
                  <button type="submit" className="gu-btn gu-btn-primary">{editingUser ? 'Guardar Cambios' : 'Registrar Colaborador'}</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Ventana de Confirmación de Borrado */}
      {deleteConfirm && (
        <div className="gu-modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="gu-dialog-box" onClick={(e) => e.stopPropagation()}>
            <div style={{ width: '48px', height: '48px', background: '#fee2e2', borderRadius: '50%', display: 'flex', alignItems: 'center', justifycontent: 'center', margin: '0 auto 16px auto' }}>
              <svg style={{ width: '24px', height: '24px', color: '#dc2626' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: '700', color: '#111827' }}>¿Eliminar este registro?</h3>
            <p style={{ margin: '0 0 24px 0', fontSize: '14px', color: '#6b7280', lineHeight: '1.5' }}>
              Esta acción dará de baja permanentemente a <strong>{deleteConfirm.nombres} {deleteConfirm.apellidos}</strong> del sistema institucional.
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
              <button className="gu-btn gu-btn-secondary" onClick={() => setDeleteConfirm(null)}>Cancelar</button>
              <button className="gu-btn gu-btn-danger" onClick={() => handleDelete(deleteConfirm.id)}>Eliminar</button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default GestionUsuarios;