const database = require('../../config/database');
const prisma = database.getClient();

class AuthRepository {
  /**
   * Busca un usuario por email
   */
  async findByEmail(email) {
    return prisma.usuario.findUnique({
      where: { email: email.toLowerCase().trim() },
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
  }
  
  /**
   * Busca un usuario por ID
   */
  async findById(id) {
    return prisma.usuario.findUnique({
      where: { id },
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
        estudiante: true,
        docente: true
      }
    });
  }
  
  /**
   * Actualiza los intentos fallidos de login
   */
  async updateLoginAttempts(userId, increment = true) {
    if (increment) {
      const user = await prisma.usuario.findUnique({ where: { id: userId } });
      const intentos = (user.intentosFallidos || 0) + 1;
      const bloqueadoHasta = intentos >= 5 
        ? new Date(Date.now() + 30 * 60 * 1000) // Bloquear por 30 minutos
        : null;
      
      return prisma.usuario.update({
        where: { id: userId },
        data: {
          intentosFallidos: intentos,
          bloqueadoHasta
        }
      });
    } else {
      return prisma.usuario.update({
        where: { id: userId },
        data: {
          intentosFallidos: 0,
          bloqueadoHasta: null,
          ultimoAcceso: new Date()
        }
      });
    }
  }
  
  /**
   * Actualiza el refresh token del usuario
   */
  async updateRefreshToken(userId, refreshToken) {
    return prisma.usuario.update({
      where: { id: userId },
      data: { refreshToken }
    });
  }
  
  /**
   * Guarda token de reseteo de contraseña
   */
  async saveResetToken(userId, hashedToken, expires) {
    return prisma.usuario.update({
      where: { id: userId },
      data: {
        resetPasswordToken: hashedToken,
        resetPasswordExpira: expires
      }
    });
  }
  
  /**
   * Busca usuario por token de reseteo
   */
  async findByResetToken(hashedToken) {
    return prisma.usuario.findFirst({
      where: {
        resetPasswordToken: hashedToken,
        resetPasswordExpira: {
          gt: new Date()
        }
      }
    });
  }
  
  /**
   * Actualiza la contraseña del usuario
   */
  async updatePassword(userId, hashedPassword) {
    return prisma.usuario.update({
      where: { id: userId },
      data: {
        passwordHash: hashedPassword,
        resetPasswordToken: null,
        resetPasswordExpira: null
      }
    });
  }
  
  /**
   * Crea una sesión para el usuario
   */
  async createSession(userId, token, ipAddress, userAgent, expiresIn) {
    return prisma.sesion.create({
      data: {
        usuarioId: userId,
        token,
        ipAddress,
        userAgent,
        expiracion: new Date(Date.now() + expiresIn)
      }
    });
  }
  
  /**
   * Invalida una sesión
   */
  async invalidateSession(sessionId) {
    return prisma.sesion.update({
      where: { id: sessionId },
      data: { activo: false }
    });
  }
  
  /**
   * Invalida todas las sesiones de un usuario
   */
  async invalidateAllSessions(userId) {
    return prisma.sesion.updateMany({
      where: { usuarioId: userId, activo: true },
      data: { activo: false }
    });
  }
}

module.exports = new AuthRepository();