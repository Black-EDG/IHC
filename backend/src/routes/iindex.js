import express from 'express';
import authRoutes from '../modules/auth/auth.routes.js';
import studentRoutes from '../modules/students/student.routes.js';
// Importaremos más módulos después

const router = express.Router();

// Health check
router.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV
  });
});

// Módulos
router.use('/auth', authRoutes);
router.use('/students', studentRoutes);
// router.use('/teachers', teacherRoutes);
// router.use('/attendance', attendanceRoutes);
// router.use('/reports', reportRoutes);
// router.use('/dashboard', dashboardRoutes);

export default router;