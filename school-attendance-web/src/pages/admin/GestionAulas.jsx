import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import Modal from '../../components/Modal';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const GestionAulas = () => {
  const { token } = useAuth();
  const [aulas, setAulas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [formData, setFormData] = useState({ grado: 1, seccion: '', anio_escolar: new Date().getFullYear(), turno: 'mañana' });
  const [error, setError] = useState('');

  const headers = { Authorization: `Bearer ${token}` };

  const cargarAulas = async () => {
    try {
      const res = await axios.get(`${API_URL}/aulas`, { headers });
      setAulas(res.data);
    } catch (err) {
      console.error('Error al cargar aulas', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { cargarAulas(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await axios.post(`${API_URL}/aulas`, { ...formData, seccion: formData.seccion.toUpperCase() }, { headers });
      setModalOpen(false);
      cargarAulas();
      setFormData({ grado: 1, seccion: '', anio_escolar: new Date().getFullYear(), turno: 'mañana' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al crear aula');
    }
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Aulas / Secciones</h1>
          <p className="text-gray-500 text-sm mt-1">{aulas.length} aulas registradas</p>
        </div>
        <button onClick={() => setModalOpen(true)}
          className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition cursor-pointer">
          + Nueva Aula
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-orange-500"></div></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {aulas.length === 0 && <p className="text-gray-500 col-span-full text-center py-8">No hay aulas registradas. Crea la primera.</p>}
          {aulas.map((aula) => (
            <div key={aula.id} className="bg-white rounded-xl shadow p-5 border-l-4 border-orange-400 hover:shadow-md transition">
              <h3 className="text-lg font-bold text-gray-800">{aula.grado}° "{aula.seccion}"</h3>
              <p className="text-sm text-gray-500">Año: {aula.anio_escolar} | Turno: {aula.turno}</p>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Nueva Aula">
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="bg-red-50 text-red-600 p-3 rounded text-sm">{error}</div>}
          <div><label className="block text-sm font-medium mb-1">Grado (1-5)</label><input type="number" min={1} max={5} required value={formData.grado} onChange={(e) => setFormData({ ...formData, grado: parseInt(e.target.value) })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 outline-none" /></div>
          <div><label className="block text-sm font-medium mb-1">Sección</label><input type="text" required maxLength={2} value={formData.seccion} onChange={(e) => setFormData({ ...formData, seccion: e.target.value })} placeholder="A, B, C..." className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 outline-none" /></div>
          <div><label className="block text-sm font-medium mb-1">Año Escolar</label><input type="number" required value={formData.anio_escolar} onChange={(e) => setFormData({ ...formData, anio_escolar: parseInt(e.target.value) })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 outline-none" /></div>
          <div><label className="block text-sm font-medium mb-1">Turno</label><input type="text" value={formData.turno} onChange={(e) => setFormData({ ...formData, turno: e.target.value })} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-orange-500 outline-none" /></div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setModalOpen(false)} className="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-50 cursor-pointer">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 cursor-pointer">Crear Aula</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default GestionAulas;