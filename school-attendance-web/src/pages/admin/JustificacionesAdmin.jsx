import React from 'react';
import NavbarLayout from '../../components/NavbarLayout';

const JustificacionesAdmin = () => {
  return (
    <NavbarLayout>
      <div style={{ padding: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
          📝 Justificaciones
        </h1>
        <p style={{ color: '#6b7280', fontSize: '14px' }}>
          Revisión de justificaciones de inasistencias enviadas por los padres de familia.
        </p>
        <div style={{ 
          marginTop: '32px', 
          padding: '40px', 
          background: 'white', 
          borderRadius: '14px', 
          border: '1px solid #e5e7eb',
          textAlign: 'center',
          color: '#9ca3af'
        }}>
          🚧 Módulo en desarrollo
        </div>
      </div>
    </NavbarLayout>
  );
};

export default JustificacionesAdmin;