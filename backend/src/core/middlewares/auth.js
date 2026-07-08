import jwt from 'jsonwebtoken';
import { config } from '../../config/environment.js';
import { AppError } from '../errors/AppError.js';
import prisma from '../../config/database.js';

export const authMiddleware = {
  async authenticate(req, res, next) {
    try {
      const authHeader = req.headers.authorization;
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        throw new AppError('Token no proporcionado', 401, 'MISSING_TOKEN');
      }

      const token = authHeader.split(' ')[1];
      
      const decoded = jwt.verify(token, config.jwt.secret);
      
      const user = await prisma.usuario.findUnique({
        where: { id: decoded.id },
        include: {
          rol: {
            include: {
              permisos: {
                include: {
                  permiso: true
                }
              }
            }
          }
        }
      });

      if (!user || !user.activo) {
        throw new AppError('Usuario no encontrado o inactivo', 401, 'USER_INACTIVE');
      }

      req.user = user;
      req.user.permisos = user.rol.permisos.map(rp => rp.permiso.nombre);
      
      next();
    } catch (error) {
      next(error);
    }
  },

  hasRole(...allowedRoles) {
    return (req, res, next) => {
      if (!req.user) {
        return next(new AppError('No autenticado', 401, 'UNAUTHENTICATED'));
      }

      if (!allowedRoles.includes(req.user.rol.nombre)) {
        return next(new AppError('No tienes permisos para esta acción', 403, 'FORBIDDEN'));
      }

      next();
    };
  },

  hasPermission(requiredPermission) {
    return (req, res, next) => {
      if (!req.user || !req.user.permisos) {
        return next(new AppError('No autenticado', 401, 'UNAUTHENTICATED'));
      }

      if (!req.user.permisos.includes(requiredPermission)) {
        return next(new AppError('No tienes permiso para esta acción', 403, 'FORBIDDEN'));
      }

      next();
    };
  }
};