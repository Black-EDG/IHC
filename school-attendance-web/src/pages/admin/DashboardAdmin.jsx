import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const DashboardAdmin = () => {
  const { token, user } = useAuth();
  const [stats, setStats] = useState({ aulas: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const aulasRes = await axios.get(`${API_URL}/aulas`, { headers });
        setStats({
          aulas: Array.isArray(aulasRes.data) ? aulasRes.data.length : 0,
        });
      } catch (error) {
        console.error('Error al cargar estadísticas', error);
      } finally {
        setLoading(false);
      }
    };
    if (token) fetchStats();
  }, [token]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Bienvenido, {user?.correo || 'Admin'}</h1>
        <p className="text-gray-500 mt-1">Panel de Administración del Sistema Escolar</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow p-6 border-l-4 border-blue-500">
              <p className="text-sm font-medium text-gray-500">Aulas Registradas</p>
              <p className="text-3xl font-bold text-gray-800 mt-1">{stats.aulas}</p>
            </div>
            <div className="bg-white rounded-xl shadow p-6 border-l-4 border-green-500">
              <p className="text-sm font-medium text-gray-500">Alumnos</p>
              <p className="text-3xl font-bold text-gray-800 mt-1">--</p>
            </div>
            <div className="bg-white rounded-xl shadow p-6 border-l-4 border-purple-500">
              <p className="text-sm font-medium text-gray-500">Personal</p>
              <p className="text-3xl font-bold text-gray-800 mt-1">--</p>
            </div>
            <div className="bg-white rounded-xl shadow p-6 border-l-4 border-orange-500">
              <p className="text-sm font-medium text-gray-500">Apoderados</p>
              <p className="text-3xl font-bold text-gray-800 mt-1">--</p>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4">Accesos rápidos</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <a href="/admin/alumnos" className="p-4 bg-blue-50 rounded-lg text-blue-700 hover:bg-blue-100 transition text-center font-medium">Matricular Alumno</a>
              <a href="/admin/apoderados" className="p-4 bg-green-50 rounded-lg text-green-700 hover:bg-green-100 transition text-center font-medium">Registrar Apoderado</a>
              <a href="/admin/usuarios" className="p-4 bg-purple-50 rounded-lg text-purple-700 hover:bg-purple-100 transition text-center font-medium">Crear Usuario</a>
              <a href="/admin/aulas" className="p-4 bg-orange-50 rounded-lg text-orange-700 hover:bg-orange-100 transition text-center font-medium">Gestionar Aulas</a>
            </div>
          </div>

          <p className="mt-6 text-sm text-gray-400">
            * Para estadísticas completas de alumnos, apoderados y usuarios, agrega endpoints GET en el backend.
          </p>
        </>
      )}
    </div>
  );
};

export default DashboardAdmin;