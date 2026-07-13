import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import AdminLayout from './components/AdminLayout';

// Páginas del admin
import DashboardAdmin from './pages/admin/DashboardAdmin';
import MatriculaAlumno from './pages/admin/MatriculaAlumno';
import MatriculaApoderado from './pages/admin/MatriculaApoderado';
import GestionUsuarios from './pages/admin/GestionUsuarios';
import GestionAulas from './pages/admin/GestionAulas';
import ControlAlertas from './pages/admin/ControlAlertas';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Login />} />

        {/* Panel de Administración con layout compartido */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute rolesPermitidos={['admin']}>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardAdmin />} />
          <Route path="alumnos" element={<MatriculaAlumno />} />
          <Route path="apoderados" element={<MatriculaApoderado />} />
          <Route path="usuarios" element={<GestionUsuarios />} />
          <Route path="aulas" element={<GestionAulas />} />
          <Route path="alertas" element={<ControlAlertas />} />
        </Route>

        {/* Fallback: cualquier ruta no existente vuelve al login */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;