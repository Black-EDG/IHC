import rateLimit from 'express-rate-limit';
import { config } from '../../config/environment.js';

export const limiter = rateLimit({
  windowMs: config.rateLimit.window * 60 * 1000,
  max: config.rateLimit.max,
  message: {
    success: false,
    message: 'Demasiadas peticiones, por favor intenta más tarde',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: {
    success: false,
    message: 'Demasiados intentos de login, espera 15 minutos',
  },
});