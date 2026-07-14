import React from 'react';

const Modal = ({ open, onClose, title, children }) => {
  if (!open) return null;

  return (
    <div className="custom-modal-root">
      {/* CSS Inyectado para control total e inmune a Tailwind */}
      <style>{`
        .custom-modal-root {
          position: fixed !important;
          inset: 0 !important;
          z-index: 9999 !important; /* Prioridad máxima por encima de sidebars */
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          padding: 16px !important;
          box-sizing: border-box !important;
          font-family: 'Inter', -apple-system, sans-serif !important;
        }

        /* Asegurar absolutamente que el SVG de la X mida 20px */
        .custom-modal-root svg.modal-close-svg {
          width: 20px !important;
          height: 20px !important;
          min-width: 20px !important;
          min-height: 20px !important;
          display: inline-block !important;
          transition: transform 0.2s ease !important;
        }

        .custom-modal-root svg.modal-close-svg:hover {
          transform: rotate(90deg) !important;
        }

        /* Fondo Oscuro con Desenfoque (Backdrop blur) */
        .modal-backdrop {
          position: absolute !important;
          inset: 0 !important;
          background-color: rgba(15, 23, 42, 0.4) !important; /* Tono pizarra traslúcido */
          backdrop-filter: blur(4px) !important;
          transition: opacity 0.3s ease !important;
        }

        /* Contenedor del Contenido */
        .modal-content-card {
          position: relative !important;
          background-color: #ffffff !important;
          border-radius: 20px !important;
          width: 100% !important;
          max-width: 500px !important; /* max-w-lg equivalente */
          box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.2) !important;
          padding: 28px !important;
          box-sizing: border-box !important;
          z-index: 10 !important;
          animation: modalScaleUp 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
          border: 1px solid #f1f5f9 !important;
        }

        /* Cabecera del Modal */
        .modal-header {
          display: flex !important;
          align-items: center !important;
          justify-content: space-between !important;
          margin-bottom: 20px !important;
          gap: 16px !important;
        }

        .modal-title-text {
          font-size: 18px !important;
          font-weight: 800 !important;
          color: #0f172a !important;
          margin: 0 !important;
          line-height: 1.4 !important;
        }

        /* Botón cerrar X */
        .btn-modal-close {
          background: none !important;
          border: none !important;
          color: #94a3b8 !important;
          cursor: pointer !important;
          padding: 6px !important;
          border-radius: 50% !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          transition: all 0.2s ease !important;
        }

        .btn-modal-close:hover {
          background-color: #f1f5f9 !important;
          color: #475569 !important;
        }

        /* Cuerpo del Modal */
        .modal-body {
          color: #334155 !important;
          font-size: 14px !important;
          line-height: 1.5 !important;
        }

        /* Animación de entrada suave */
        @keyframes modalScaleUp {
          from {
            opacity: 0;
            transform: scale(0.95) translateY(10px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
      `}</style>

      {/* 1. FONDO OSCURO SÚPER ELEGANTE */}
      <div className="modal-backdrop" onClick={onClose}></div>

      {/* 2. TARJETA DE CONTENIDO */}
      <div className="modal-content-card">
        <div className="modal-header">
          <h2 className="modal-title-text">{title}</h2>
          <button
            onClick={onClose}
            className="btn-modal-close"
            aria-label="Cerrar modal"
          >
            {/* Icono X SVG Blindado con clase especial y tamaño inline de respaldo */}
            <svg
              className="modal-close-svg"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>

        {/* 3. HIJOS (CHILDREN) */}
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;