import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const MatriculaAlumno = () => {
  const { token } = useAuth();
  const [aulas, setAulas] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    dni: '',
    nombres: '',
    apellidos: '',
    fecha_nacimiento: '',
    aula_id: '',
    apoderado_id: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const headers = { Authorization: `Bearer ${token}` };

  const cargarAulas = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/aulas`, { headers });
      setAulas(res.data);
    } catch (err) {
      console.error('Error al cargar aulas', err);
    }
  }, [token]);

  useEffect(() => {
    cargarAulas();
  }, [cargarAulas]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const payload = {
        dni: formData.dni,
        nombres: formData.nombres,
        apellidos: formData.apellidos,
        fecha_nacimiento: formData.fecha_nacimiento,
        aula_id: parseInt(formData.aula_id),
        apoderado_id: parseInt(formData.apoderado_id),
      };
      await axios.post(`${API_URL}/alumnos`, payload, { headers });
      setSuccess('Alumno registrado correctamente');
      setFormData({ dni: '', nombres: '', apellidos: '', fecha_nacimiento: '', aula_id: '', apoderado_id: '' });
      setTimeout(() => {
        setModalOpen(false);
        setSuccess('');
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar alumno');
    }
  };

  const resetForm = () => {
    setFormData({ dni: '', nombres: '', apellidos: '', fecha_nacimiento: '', aula_id: '', apoderado_id: '' });
    setError('');
    setSuccess('');
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Matrícula de Alumnos</h1>
          <p className="text-gray-500 text-sm mt-1">Registra nuevos estudiantes en el sistema</p>
        </div>
        <button
          onClick={() => { resetForm(); setModalOpen(true); }}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition cursor-pointer"
        >
          + Nuevo Alumno
        </button>
      </div>

      <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <p className="text-lg font-medium mb-1">Listado de alumnos</p>
        <p className="text-sm">Para ver los alumnos registrados, agrega el endpoint GET /alumnos en el backend.</p>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Registrar Nuevo Alumno">
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="bg-red-50 text-red-600 p-3 rounded text-sm">{error}</div>}
          {success && <div className="bg-green-50 text-green-600 p-3 rounded text-sm">{success}</div>}
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">DNI (8 dígitos)</label>
              <input type="text" required pattern="\d{8}" maxLength={8} value={formData.dni}
                onChange={(e) => setFormData({ ...formData, dni: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Nacimiento</label>
              <input type="date" required value={formData.fecha_nacimiento}
                onChange={(e) => setFormData({ ...formData, fecha_nacimiento: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombres</label>
              <input type="text" required value={formData.nombres}
                onChange={(e) => setFormData({ ...formData, nombres: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Apellidos</label>
              <input type="text" required value={formData.apellidos}
                onChange={(e) => setFormData({ ...formData, apellidos: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Aula</label>
              <select required value={formData.aula_id}
                onChange={(e) => setFormData({ ...formData, aula_id: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white">
                <option value="">Seleccionar aula</option>
                {aulas.map((aula) => (
                  <option key={aula.id} value={aula.id}>{aula.grado}° {aula.seccion} ({aula.anio_escolar})</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ID del Apoderado</label>
              <input type="number" required value={formData.apoderado_id}
                onChange={(e) => setFormData({ ...formData, apoderado_id: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                placeholder="ID del apoderado" />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setModalOpen(false)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition cursor-pointer">Cancelar</button>
            <button type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition cursor-pointer">Guardar Alumno</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default MatriculaAlumno;