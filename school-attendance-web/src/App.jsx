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
import JustificacionesAdmin from './pages/admin/JustificacionesAdmin';
import AsignacionCargos from './pages/admin/AsignacionCargos';

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Ruta pública del Login */}
        <Route path="/" element={<Login />} />

        {/* Panel de Administración */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute rolesPermitidos={['admin']}>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<DashboardAdmin />} />
          <Route path="alumnos" element={<MatriculaAlumno />} />
          <Route path="apoderados" element={<MatriculaApoderado />} />
          <Route path="usuarios" element={<GestionUsuarios />} />
          <Route path="aulas" element={<GestionAulas />} />
          <Route path="asignaciones" element={<AsignacionCargos />} />
          <Route path="alertas" element={<ControlAlertas />} />
          <Route path="justificaciones" element={<JustificacionesAdmin />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;