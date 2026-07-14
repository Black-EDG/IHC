import React, { useState, useEffect, useId, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

// ═══════════════════════════════════════════════════════════════
// ILUSTRACIÓN DECORATIVA
// ═══════════════════════════════════════════════════════════════
const RollCallLedger = () => {
  const rows = [72, 88, 64, 92, 56, 80, 68];
  return (
    <svg viewBox="0 0 320 230" style={{ width: '100%', maxWidth: '230px', display: 'block', margin: '0 auto' }} role="img" aria-label="Ilustración de asistencia escolar">
      {rows.map((w, i) => (
        <g key={i} transform={`translate(0 ${i * 32})`}>
          <line x1="40" y1="10" x2="300" y2="10" stroke="#3A4D80" strokeWidth="1" opacity="0.3" />
          <rect x="40" y="14" width={w} height="6" rx="3" fill="#8F9BB3" opacity="0.35" />
          <circle cx="16" cy="10" r="9" fill="none" stroke="#F5A623" strokeWidth="1.6" />
          <path d="M11.5 10.2 L15 13.5 L20.5 6.5" fill="none" stroke="#F5A623" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" pathLength="1" className="ledger-check" style={{ animationDelay: `${i * 0.3}s` }} />
        </g>
      ))}
    </svg>
  );
};

// ═══════════════════════════════════════════════════════════════
// ICONO OJO
// ═══════════════════════════════════════════════════════════════
const EyeIcon = ({ open }) => (
  <svg viewBox="0 0 20 20" fill="none" style={{ width: '20px', height: '20px' }} aria-hidden="true">
    {open ? (
      <>
        <path d="M1.5 10S4.5 4 10 4s8.5 6 8.5 6-3 6-8.5 6-8.5-6-8.5-6Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
        <circle cx="10" cy="10" r="2.5" stroke="currentColor" strokeWidth="1.6" />
      </>
    ) : (
      <path d="M2.5 2.5l15 15M8.3 8.4a2.4 2.4 0 0 0 3.3 3.3M6.2 5.1C3.6 6.4 1.5 10 1.5 10s3 6 8.5 6c1.4 0 2.6-.4 3.7-1M15.3 14.1c1.9-1.4 3.2-4.1 3.2-4.1s-3-6-8.5-6c-.7 0-1.4.1-2 .2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    )}
  </svg>
);

// ═══════════════════════════════════════════════════════════════
// COMPONENTE PRINCIPAL
// ═══════════════════════════════════════════════════════════════
const LoginPersonal = () => {
  const correoId = useId();
  const passId = useId();
  const errorId = useId();
  const capsId = useId();

  const [correo, setCorreo] = useState(() => localStorage.getItem('recordarCorreo') || '');
  const [contrasena, setContrasena] = useState('');
  const [recordar, setRecordar] = useState(() => !!localStorage.getItem('recordarCorreo'));
  const [mostrarClave, setMostrarClave] = useState(false);
  const [capsLockActivo, setCapsLockActivo] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { loginPersonal, error: authError, clearError } = useAuth();
  const errorRef = useRef(null);

  useEffect(() => {
    clearError?.();
  }, []);

  useEffect(() => {
    if (error && errorRef.current) errorRef.current.focus();
  }, [error]);

  useEffect(() => {
    if (authError) setError(authError);
  }, [authError]);

  const handleKeyEvent = (e) => {
    if (typeof e.getModifierState === 'function') {
      setCapsLockActivo(e.getModifierState('CapsLock'));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setError('');
    clearError?.();

    if (!correo || !correo.includes('@')) {
      setError('Ingrese un correo electrónico válido.');
      return;
    }

    if (!contrasena || contrasena.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres.');
      return;
    }

    setLoading(true);

    if (recordar) {
      localStorage.setItem('recordarCorreo', correo);
    } else {
      localStorage.removeItem('recordarCorreo');
    }

    const result = await loginPersonal(correo.trim(), contrasena);

    if (!result.success) {
      setError(result.error || 'Error al iniciar sesión.');
    }

    setLoading(false);
  };

  return (
    <div className="login-page-container">
      <style>{`
        .login-page-container {
          min-height: 100vh;
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
          font-family: system-ui, -apple-system, sans-serif;
          box-sizing: border-box;
          padding: 20px;
        }
        .login-card {
          width: 100%;
          max-width: 960px;
          min-height: 580px;
          background: #ffffff;
          border-radius: 20px;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
          display: flex;
          overflow: hidden;
        }
        .panel-left {
          width: 45%;
          background: #0F172A;
          color: #F8FAFC;
          padding: 40px 35px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          position: relative;
          overflow: hidden;
        }
        .panel-left::before {
          content: '';
          position: absolute;
          top: -50%;
          right: -50%;
          width: 100%;
          height: 100%;
          background: radial-gradient(circle, rgba(245, 166, 35, 0.08) 0%, transparent 70%);
          pointer-events: none;
        }
        .brand-logo {
          display: flex;
          align-items: center;
          gap: 10px;
          position: relative;
          z-index: 1;
        }
        .logo-box {
          width: 40px;
          height: 40px;
          background: #F5A623;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #0F172A;
          font-weight: 800;
          font-size: 16px;
        }
        .brand-text {
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 1.5px;
          color: #F5A623;
        }
        .left-headline {
          font-size: 22px;
          font-weight: 700;
          margin-bottom: 10px;
          color: #ffffff;
          position: relative;
          z-index: 1;
        }
        .left-sub {
          font-size: 13px;
          color: #94A3B8;
          line-height: 1.6;
          position: relative;
          z-index: 1;
        }
        .left-illustration {
          margin: auto 0;
          position: relative;
          z-index: 1;
        }
        .left-footer {
          font-size: 10px;
          color: #64748B;
          position: relative;
          z-index: 1;
        }
        .panel-right {
          flex: 1;
          padding: 40px 45px;
          display: flex;
          flex-direction: column;
          justify-content: center;
          background: #ffffff;
        }
        .right-title {
          font-size: 26px;
          font-weight: 800;
          color: #0F172A;
          margin: 0 0 4px 0;
        }
        .right-sub {
          font-size: 13px;
          color: #64748B;
          margin: 0 0 28px 0;
        }
        .right-sub strong {
          color: #F5A623;
        }
        .form-group {
          margin-bottom: 16px;
          display: flex;
          flex-direction: column;
          gap: 5px;
        }
        .form-label {
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #475569;
        }
        .form-input {
          width: 100%;
          padding: 12px 14px;
          border: 1.5px solid #E2E8F0;
          border-radius: 10px;
          font-size: 14px;
          background: #F8FAFC;
          transition: all 0.2s;
          box-sizing: border-box;
          color: #1E293B;
        }
        .form-input:focus {
          outline: none;
          border-color: #F5A623;
          background: #ffffff;
          box-shadow: 0 0 0 3px rgba(245, 166, 35, 0.12);
        }
        .form-input.error {
          border-color: #EF4444;
          background: #FEF2F2;
        }
        .password-container {
          position: relative;
        }
        .eye-button {
          position: absolute;
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          color: #94A3B8;
          cursor: pointer;
          display: flex;
          align-items: center;
          padding: 6px;
          border-radius: 6px;
          transition: all 0.2s;
        }
        .eye-button:hover {
          color: #475569;
          background: #F1F5F9;
        }
        .checkbox-container {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          color: #64748B;
          cursor: pointer;
          margin-bottom: 20px;
          user-select: none;
        }
        .submit-btn {
          width: 100%;
          background: #0F172A;
          color: #ffffff;
          border: none;
          padding: 14px;
          font-weight: 700;
          border-radius: 10px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }
        .submit-btn:hover:not(:disabled) {
          background: #1E293B;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(15, 23, 42, 0.3);
        }
        .submit-btn:disabled {
          background: #94A3B8;
          cursor: not-allowed;
        }
        .submit-btn .spinner {
          display: inline-block;
          width: 18px;
          height: 18px;
          border: 2px solid rgba(255,255,255,0.3);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin 0.6s linear infinite;
          margin-right: 8px;
          vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .error-banner {
          background: #FEF2F2;
          border: 1px solid #FCA5A5;
          color: #991B1B;
          padding: 12px 14px;
          border-radius: 10px;
          font-size: 13px;
          margin-bottom: 16px;
          display: flex;
          align-items: flex-start;
          gap: 8px;
          animation: shake 0.4s ease;
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-4px); }
          75% { transform: translateX(4px); }
        }
        @keyframes ledgerCheck {
          0%, 15% { stroke-dashoffset: 1; opacity: 0; }
          30% { opacity: 1; }
          45%, 100% { stroke-dashoffset: 0; opacity: 1; }
        }
        .ledger-check {
          stroke-dasharray: 1;
          stroke-dashoffset: 1;
          animation: ledgerCheck 6s ease-in-out infinite;
        }
        @media (max-width: 768px) {
          .panel-left { display: none; }
          .login-card { max-width: 420px; min-height: auto; }
          .panel-right { padding: 30px 25px; }
          .right-title { font-size: 22px; }
        }
      `}</style>

      <div className="login-card">
        {/* PANEL IZQUIERDO */}
        <div className="panel-left">
          <div className="brand-logo">
            <div className="logo-box">SE</div>
            <span className="brand-text">Sistema Escolar</span>
          </div>
          <div className="left-illustration">
            <RollCallLedger />
            <div style={{ marginTop: '20px' }}>
              <h2 className="left-headline">Control de Asistencia Escolar</h2>
              <p className="left-sub">Sistema integral para el monitoreo de asistencia, justificaciones y comunicación con padres de familia.</p>
            </div>
          </div>
          <div className="left-footer">Acceso exclusivo para personal autorizado del colegio.</div>
        </div>

        {/* PANEL DERECHO */}
        <div className="panel-right">
          <div>
            <h1 className="right-title">Iniciar Sesión</h1>
            <p className="right-sub">Ingresa tu <strong>correo institucional</strong> y <strong>contraseña</strong>.</p>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {error && (
              <div className="error-banner" ref={errorRef} id={errorId} role="alert">
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <div className="form-group">
              <label htmlFor={correoId} className="form-label">Correo Institucional</label>
              <input
                id={correoId}
                type="email"
                required
                value={correo}
                onChange={(e) => { setCorreo(e.target.value); if (error) setError(''); }}
                className={`form-input ${error ? 'error' : ''}`}
                placeholder="ejemplo@colegio.edu.pe"
                autoComplete="email"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor={passId} className="form-label">Contraseña</label>
              <div className="password-container">
                <input
                  id={passId}
                  type={mostrarClave ? 'text' : 'password'}
                  required
                  value={contrasena}
                  onChange={(e) => { setContrasena(e.target.value); if (error) setError(''); }}
                  onKeyDown={handleKeyEvent}
                  onKeyUp={handleKeyEvent}
                  className={`form-input ${error ? 'error' : ''}`}
                  placeholder="Ingresa tu contraseña"
                  autoComplete="current-password"
                  disabled={loading}
                />
                <button type="button" onClick={() => setMostrarClave((v) => !v)} className="eye-button" tabIndex={-1}>
                  <EyeIcon open={mostrarClave} />
                </button>
              </div>
              {capsLockActivo && (
                <p id={capsId} style={{ color: '#D97706', fontSize: '11px', margin: '4px 0 0 0' }}>⚠️ Bloq Mayús activado.</p>
              )}
            </div>

            <label className="checkbox-container">
              <input type="checkbox" checked={recordar} onChange={(e) => setRecordar(e.target.checked)} style={{ width: '15px', height: '15px', cursor: 'pointer', accentColor: '#F5A623' }} disabled={loading} />
              <span>Recordar correo en este dispositivo</span>
            </label>

            <button type="submit" disabled={loading} className="submit-btn">
              {loading ? <><span className="spinner"></span> Verificando...</> : 'Ingresar al Sistema'}
            </button>
          </form>

          <p style={{ textAlign: 'center', fontSize: '10px', color: '#94A3B8', marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #F1F5F9', marginBottom: 0 }}>
            Sistema seguro. El acceso no autorizado es registrado.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPersonal;