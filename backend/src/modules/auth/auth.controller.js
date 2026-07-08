import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { config } from '../../config/environment.js';
import prisma from '../../config/database.js';
import { AppError } from '../../core/errors/AppError.js';

export const authController = {
  async login(req, res, next) {
    try {
      const { email, password } = req.body;

      const user = await prisma.usuario.findUnique({
        where: { email },
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

      if (!user) {
        throw new AppError('Credenciales inválidas', 401, 'INVALID_CREDENTIALS');
      }

      if (user.bloqueadoHasta && user.bloqueadoHasta > new Date()) {
        throw new AppError(`Cuenta bloqueada hasta ${user.bloqueadoHasta}`, 403, 'ACCOUNT_BLOCKED');
      }

      const isValid = await bcrypt.compare(password, user.passwordHash);
      if (!isValid) {
        await prisma.usuario.update({
          where: { id: user.id },
          data: {
            intentosFallidos: user.intentosFallidos + 1,
            bloqueadoHasta: user.intentosFallidos + 1 >= 5 
              ? new Date(Date.now() + 30 * 60 * 1000)
              : undefined
          }
        });
        throw new AppError('Credenciales inválidas', 401, 'INVALID_CREDENTIALS');
      }

      await prisma.usuario.update({
        where: { id: user.id },
        data: {
          intentosFallidos: 0,
          ultimoAcceso: new Date()
        }
      });

      const token = jwt.sign(
        { id: user.id, email: user.email, rol: user.rol.nombre },
        config.jwt.secret,
        { expiresIn: config.jwt.expiresIn }
      );

      const refreshToken = jwt.sign(
        { id: user.id },
        config.jwt.refreshSecret,
        { expiresIn: config.jwt.refreshExpiresIn }
      );

      const refreshTokenHash = await bcrypt.hash(refreshToken, 10);
      await prisma.usuario.update({
        where: { id: user.id },
        data: { refreshTokenHash }
      });

      const permisos = user.rol.permisos.map(rp => rp.permiso.nombre);

      const { passwordHash: _, refreshTokenHash: __, ...userData } = user;

      res.json({
        success: true,
        data: {
          user: userData,
          token,
          refreshToken,
          permisos
        }
      });
    } catch (error) {
      next(error);
    }
  },

  async refreshToken(req, res, next) {
    try {
      const { refreshToken } = req.body;

      if (!refreshToken) {
        throw new AppError('Refresh token requerido', 400, 'REFRESH_TOKEN_REQUIRED');
      }

      const decoded = jwt.verify(refreshToken, config.jwt.refreshSecret);
      
      const user = await prisma.usuario.findUnique({
        where: { id: decoded.id }
      });

      if (!user || !user.refreshTokenHash) {
        throw new AppError('Refresh token inválido', 401, 'INVALID_REFRESH_TOKEN');
      }

      const isValid = await bcrypt.compare(refreshToken, user.refreshTokenHash);
      if (!isValid) {
        throw new AppError('Refresh token inválido', 401, 'INVALID_REFRESH_TOKEN');
      }

      const newToken = jwt.sign(
        { id: user.id, email: user.email },
        config.jwt.secret,
        { expiresIn: config.jwt.expiresIn }
      );

      res.json({
        success: true,
        data: { token: newToken }
      });
    } catch (error) {
      next(error);
    }
  },

  async logout(req, res, next) {
    try {
      const userId = req.user.id;
      
      await prisma.usuario.update({
        where: { id: userId },
        data: { refreshTokenHash: null }
      });

      res.json({
        success: true,
        message: 'Sesión cerrada exitosamente'
      });
    } catch (error) {
      next(error);
    }
  },

  async getProfile(req, res, next) {
    try {
      const userId = req.user.id;

      const user = await prisma.usuario.findUnique({
        where: { id: userId },
        include: {
          rol: {
            include: {
              permisos: {
                include: {
                  permiso: true
                }
              }
            }
          },
          estudiante: {
            include: {
              apoderados: {
                include: {
                  apoderado: {
                    include: {
                      usuario: true
                    }
                  }
                }
              }
            }
          },
          docente: true,
          apoderado: {
            include: {
              estudiantes: {
                include: {
                  estudiante: {
                    include: {
                      usuario: true
                    }
                  }
                }
              }
            }
          }
        }
      });

      if (!user) {
        throw new AppError('Usuario no encontrado', 404, 'USER_NOT_FOUND');
      }

      const { passwordHash, refreshTokenHash, ...userData } = user;

      res.json({
        success: true,
        data: userData
      });
    } catch (error) {
      next(error);
    }
  },

  async changePassword(req, res, next) {
    try {
      const userId = req.user.id;
      const { currentPassword, newPassword } = req.body;

      const user = await prisma.usuario.findUnique({
        where: { id: userId }
      });

      if (!user) {
        throw new AppError('Usuario no encontrado', 404, 'USER_NOT_FOUND');
      }

      const isValid = await bcrypt.compare(currentPassword, user.passwordHash);
      if (!isValid) {
        throw new AppError('Contraseña actual incorrecta', 401, 'INVALID_PASSWORD');
      }

      const hashedPassword = await bcrypt.hash(newPassword, 10);

      await prisma.usuario.update({
        where: { id: userId },
        data: { passwordHash: hashedPassword }
      });

      res.json({
        success: true,
        message: 'Contraseña actualizada exitosamente'
      });
    } catch (error) {
      next(error);
    }
  }
};