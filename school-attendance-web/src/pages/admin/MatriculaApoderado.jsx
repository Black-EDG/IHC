import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const MatriculaApoderado = () => {
  const { token } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    dni: '',
    nombres: '',
    apellidos: '',
    celular: '',
    parentesco: '',
    correo: '',
    contacto_emergencia_nombre: '',
    contacto_emergencia_celular: '',
    contacto_emergencia_parentesco: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const headers = { Authorization: `Bearer ${token}` };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await axios.post(`${API_URL}/apoderados`, formData, { headers });
      setSuccess('Apoderado registrado correctamente');
      setFormData({
        dni: '', nombres: '', apellidos: '', celular: '', parentesco: '', correo: '',
        contacto_emergencia_nombre: '', contacto_emergencia_celular: '', contacto_emergencia_parentesco: '',
      });
      setTimeout(() => { setModalOpen(false); setSuccess(''); }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar apoderado');
    }
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Apoderados</h1>
          <p className="text-gray-500 text-sm mt-1">Registra padres de familia y tutores</p>
        </div>
        <button onClick={() => setModalOpen(true)}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition cursor-pointer">
          + Nuevo Apoderado
        </button>
      </div>

      <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p className="text-lg font-medium mb-1">Listado de apoderados</p>
        <p className="text-sm">Para ver la lista completa, agrega el endpoint GET /apoderados en el backend.</p>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Registrar Nuevo Apoderado">
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="bg-red-50 text-red-600 p-3 rounded text-sm">{error}</div>}
          {success && <div className="bg-green-50 text-green-600 p-3 rounded text-sm">{success}</div>}
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">DNI</label>
              <input required pattern="\d{8}" maxLength={8} value={formData.dni}
                onChange={(e) => setFormData({ ...formData, dni: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Celular</label>
              <input required pattern="\d{9}" maxLength={9} value={formData.celular}
                onChange={(e) => setFormData({ ...formData, celular: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombres</label>
              <input required value={formData.nombres}
                onChange={(e) => setFormData({ ...formData, nombres: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Apellidos</label>
              <input required value={formData.apellidos}
                onChange={(e) => setFormData({ ...formData, apellidos: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Parentesco</label>
              <input required value={formData.parentesco}
                onChange={(e) => setFormData({ ...formData, parentesco: e.target.value })}
                placeholder="Padre, Madre, Tutor"
                className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Correo (opcional)</label>
              <input type="email" value={formData.correo}
                onChange={(e) => setFormData({ ...formData, correo: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 outline-none" />
            </div>
          </div>

          <fieldset className="border border-gray-200 p-3 rounded-lg">
            <legend className="text-sm font-medium text-gray-700 px-2">Contacto de emergencia (opcional)</legend>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-2">
              <input placeholder="Nombre" value={formData.contacto_emergencia_nombre}
                onChange={(e) => setFormData({ ...formData, contacto_emergencia_nombre: e.target.value })}
                className="border rounded-lg px-3 py-2 text-sm" />
              <input placeholder="Celular" value={formData.contacto_emergencia_celular}
                onChange={(e) => setFormData({ ...formData, contacto_emergencia_celular: e.target.value })}
                className="border rounded-lg px-3 py-2 text-sm" />
              <input placeholder="Parentesco" value={formData.contacto_emergencia_parentesco}
                onChange={(e) => setFormData({ ...formData, contacto_emergencia_parentesco: e.target.value })}
                className="border rounded-lg px-3 py-2 text-sm" />
            </div>
          </fieldset>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setModalOpen(false)}
              className="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-50 cursor-pointer">Cancelar</button>
            <button type="submit"
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 cursor-pointer">Guardar Apoderado</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default MatriculaApoderado;