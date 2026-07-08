import app from './app.js';
import { config } from './config/environment.js';
import { initSocket } from './config/socket.js';
import http from 'http';

const PORT = config.port;

const server = http.createServer(app);

// Inicializar Socket.IO
const io = initSocket(server);

server.listen(PORT, () => {
  console.log('=================================');
  console.log('🚀 School Attendance System');
  console.log('=================================');
  console.log(`📡 Servidor: http://localhost:${PORT}`);
  console.log(`🔧 Entorno: ${config.nodeEnv}`);
  console.log(`📅 Fecha: ${new Date().toISOString()}`);
  console.log('=================================');
  console.log('📋 Endpoints disponibles:');
  console.log(`   POST  /api/auth/login`);
  console.log(`   POST  /api/auth/refresh-token`);
  console.log(`   GET   /api/auth/profile`);
  console.log(`   POST  /api/auth/logout`);
  console.log(`   GET   /api/health`);
  console.log(`   GET   /api/students`);
  console.log(`   POST  /api/students`);
  console.log('=================================');
});

// Manejo de errores
process.on('unhandledRejection', (err) => {
  console.error('❌ Unhandled Rejection:', err);
  server.close(() => process.exit(1));
});

process.on('uncaughtException', (err) => {
  console.error('❌ Uncaught Exception:', err);
  server.close(() => process.exit(1));
});

export default server;