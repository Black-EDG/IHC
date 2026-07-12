import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const GestionUsuarios = () => {
  const { token } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    dni: '', nombres: '', apellidos: '', celular: '', correo: '',
    rol: 'docente', contrasena: '', estado: 'activo',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const headers = { Authorization: `Bearer ${token}` };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await axios.post(`${API_URL}/usuarios`, formData, { headers });
      setSuccess('Usuario creado correctamente');
      setFormData({ dni: '', nombres: '', apellidos: '', celular: '', correo: '', rol: 'docente', contrasena: '', estado: 'activo' });
      setTimeout(() => { setModalOpen(false); setSuccess(''); }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al crear usuario');
    }
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Gestión de Usuarios</h1>
          <p className="text-gray-500 text-sm mt-1">Administra al personal del colegio</p>
        </div>
        <button onClick={() => setModalOpen(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition cursor-pointer">
          + Nuevo Usuario
        </button>
      </div>

      <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-lg font-medium mb-1">Listado de usuarios</p>
        <p className="text-sm">Para ver los usuarios registrados, agrega el endpoint GET /usuarios en el backend.</p>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Crear Usuario del Sistema">
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="bg-red-50 text-red-600 p-3 rounded text-sm">{error}</div>}
          {success && <div className="bg-green-50 text-green-600 p-3 rounded text-sm">{success}</div>}
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div><label className="block text-sm font-medium mb-1">DNI</label><input required pattern="\d{8}" maxLength={8} value={formData.dni} onChange={(e) => setFormData({ ...formData, dni: e.target.value })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none" /></div>
            <div><label className="block text-sm font-medium mb-1">Celular</label><input pattern="\d{9}" maxLength={9} value={formData.celular} onChange={(e) => setFormData({ ...formData, celular: e.target.value })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none" /></div>
            <div><label className="block text-sm font-medium mb-1">Nombres</label><input required value={formData.nombres} onChange={(e) => setFormData({ ...formData, nombres: e.target.value })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none" /></div>
            <div><label className="block text-sm font-medium mb-1">Apellidos</label><input required value={formData.apellidos} onChange={(e) => setFormData({ ...formData, apellidos: e.target.value })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none" /></div>
            <div><label className="block text-sm font-medium mb-1">Correo</label><input type="email" required value={formData.correo} onChange={(e) => setFormData({ ...formData, correo: e.target.value })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none" /></div>
            <div>
              <label className="block text-sm font-medium mb-1">Rol</label>
              <select value={formData.rol} onChange={(e) => setFormData({ ...formData, rol: e.target.value })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none bg-white">
                <option value="docente">Docente</option><option value="auxiliar">Auxiliar</option><option value="admin">Administrador</option>
              </select>
            </div>
            <div><label className="block text-sm font-medium mb-1">Contraseña</label><input type="password" required minLength={6} value={formData.contrasena} onChange={(e) => setFormData({ ...formData, contrasena: e.target.value })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none" /></div>
            <div>
              <label className="block text-sm font-medium mb-1">Estado</label>
              <select value={formData.estado} onChange={(e) => setFormData({ ...formData, estado: e.target.value })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none bg-white">
                <option value="activo">Activo</option><option value="licencia">Licencia</option><option value="inactivo">Inactivo</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setModalOpen(false)} className="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-50 cursor-pointer">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 cursor-pointer">Crear Usuario</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default GestionUsuarios;