import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { theme } from '../../theme';

const ControlAlertas = () => {
  const [alertas, setAlertas] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });

  useEffect(() => {
    cargarAlertas();
  }, []);

  const cargarAlertas = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get('http://127.0.0.1:8000/alertas/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAlertas(res.data);
    } catch (err) {
      console.error("Error al obtener el historial de alertas:", err);
    }
  };

  const procesarAlertas = async () => {
    setCargando(true);
    setMensaje({ tipo: '', texto: '' });
    try {
      const token = localStorage.getItem('token');
      const res = await axios.post('http://127.0.0.1:8000/alertas/procesar', {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMensaje({ 
        tipo: 'exito', 
        texto: res.data.detail || '¡Proceso de notificaciones ejecutado correctamente!' 
      });
      cargarAlertas();
    } catch (err) {
      setMensaje({ 
        tipo: 'error', 
        texto: err.response?.data?.detail || 'Error al conectar con el servidor.' 
      });
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="alertas-modulo-limpio">
      {/* CSS Encapsulado */}
      <style>{`
        .alertas-modulo-limpio {
          font-family: 'Inter', -apple-system, sans-serif !important;
          width: 100% !important;
          box-sizing: border-box !important;
        }

        .alertas-header-clean {
          margin-bottom: 24px !important;
          display: flex !important;
          justify-content: space-between !important;
          align-items: center !important;
          flex-wrap: wrap !important;
          gap: 16px !important;
        }

        .alertas-header-clean h1 {
          color: #1e293b !important;
          font-size: 24px !important;
          font-weight: 800 !important;
          margin: 0 0 4px 0 !important;
          letter-spacing: -0.5px !important;
        }

        .alertas-header-clean p {
          color: #64748b !important;
          font-size: 14px !important;
          margin: 0 !important;
        }

        .btn-disparar-clean {
          background-color: #4f46e5 !important;
          color: #ffffff !important;
          border: none !important;
          padding: 10px 18px !important;
          border-radius: 10px !important;
          font-size: 14px !important;
          font-weight: 700 !important;
          cursor: pointer !important;
          transition: all 0.2s ease !important;
          box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2) !important;
        }

        .btn-disparar-clean:hover:not(:disabled) {
          background-color: #4338ca !important;
          transform: translateY(-1px) !important;
        }

        .btn-disparar-clean:disabled {
          background-color: #cbd5e1 !important;
          color: #94a3b8 !important;
          cursor: not-allowed !important;
          box-shadow: none !important;
        }

        .feedback-banner-clean {
          padding: 12px 16px !important;
          border-radius: 10px !important;
          margin-bottom: 20px !important;
          font-size: 14px !important;
          font-weight: 600 !important;
          border: 1px solid transparent !important;
        }

        .feedback-exito-clean { background-color: #ecfdf5 !important; color: #065f46 !important; border-color: #a7f3d0 !important; }
        .feedback-error-clean { background-color: #fef2f2 !important; color: #991b1b !important; border-color: #fca5a5 !important; }

        .alertas-card-clean {
          background-color: #ffffff !important;
          padding: 24px !important;
          border-radius: 12px !important;
          border: 1px solid #e2e8f0 !important;
          box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        }

        .card-title-clean {
          margin: 0 0 16px 0 !important;
          color: #0f172a !important;
          font-size: 16px !important;
          font-weight: 700 !important;
        }

        .table-wrapper-clean {
          overflow-x: auto !important;
        }

        .alertas-table-clean {
          width: 100% !important;
          border-collapse: separate !important;
          border-spacing: 0 !important;
          text-align: left !important;
        }

        .alertas-table-clean th {
          background-color: #f8fafc !important;
          color: #64748b !important;
          font-size: 12px !important;
          font-weight: 700 !important;
          text-transform: uppercase !important;
          padding: 12px 16px !important;
          border-bottom: 2px solid #e2e8f0 !important;
        }

        .alertas-table-clean td {
          padding: 14px 16px !important;
          font-size: 14px !important;
          color: #334155 !important;
          border-bottom: 1px solid #f1f5f9 !important;
        }

        .badge-status-clean {
          display: inline-block !important;
          padding: 4px 8px !important;
          border-radius: 6px !important;
          font-size: 11px !important;
          font-weight: 700 !important;
          text-transform: uppercase !important;
        }

        .status-enviado-clean { background-color: #d1fae5 !important; color: #065f46 !important; }
        .status-pendiente-clean { background-color: #fef3c7 !important; color: #b45309 !important; }
        .status-fallido-clean { background-color: #fef2f2 !important; color: #991b1b !important; }
      `}</style>

      {/* CABECERA LIMPIA */}
      <div className="alertas-header-clean">
        <div>
          <h1>📢 Control y Envío de Alertas</h1>
          <p>Monitorea y despacha las notificaciones automáticas por inasistencias críticas.</p>
        </div>
        <button 
          onClick={procesarAlertas} 
          disabled={cargando} 
          className="btn-disparar-clean"
        >
          {cargando ? '⌛ Procesando...' : '🚀 Despachar Pendientes'}
        </button>
      </div>

      {/* FEEDBACK */}
      {mensaje.texto && (
        <div className={`feedback-banner-clean ${mensaje.tipo === 'exito' ? 'feedback-exito-clean' : 'feedback-error-clean'}`}>
          {mensaje.tipo === 'exito' ? '✅ ' : '⚠️ '} {mensaje.texto}
        </div>
      )}

      {/* TABLA HISTÓRICA */}
      <div className="alertas-card-clean table-wrapper-clean">
        <h3 className="card-title-clean">Historial de Notificaciones a Apoderados</h3>
        <table className="alertas-table-clean">
          <thead>
            <tr>
              <th>Apoderado ID</th>
              <th>Tipo Alerta</th>
              <th>Destinatario / Canal</th>
              <th>Fecha Despacho</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {alertas.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', color: '#94a3b8', padding: '32px' }}>
                  No se registran alertas despachadas en las últimas 24 horas.
                </td>
              </tr>
            ) : (
              alertas.map((alerta) => (
                <tr key={alerta.id}>
                  <td style={{ fontWeight: '600' }}>👤 ID: {alerta.apoderado_id}</td>
                  <td>{alerta.tipo_medio || 'SMS'}</td>
                  <td>{alerta.destino || 'Sin registrar'}</td>
                  <td>{alerta.fecha_envio ? new Date(alerta.fecha_envio).toLocaleString() : 'En Cola'}</td>
                  <td>
                    <span className={`badge-status-clean status-${alerta.estado?.toLowerCase() || 'pendiente'}-clean`}>
                      {alerta.estado || 'Pendiente'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ControlAlertas;