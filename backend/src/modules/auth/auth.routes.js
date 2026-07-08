import express from 'express';
import { authController } from './auth.controller.js';
import { authMiddleware } from '../../core/middlewares/auth.js';
import { validate } from '../../core/middlewares/validate.js';
import { loginValidator, registerValidator } from './auth.validator.js';
import { authLimiter } from '../../core/middlewares/rateLimiter.js';

const router = express.Router();

router.post('/login', authLimiter, validate(loginValidator), authController.login);
router.post('/refresh-token', authController.refreshToken);

router.use(authMiddleware.authenticate);
router.post('/logout', authController.logout);
router.get('/profile', authController.getProfile);
router.put('/change-password', authController.changePassword);

export default router;