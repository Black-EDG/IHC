import prisma from '../../config/database.js';
import { AppError } from '../../core/errors/AppError.js';
import { generateCode } from '../../core/utils/helpers.js';

export const studentController = {
  // Listar estudiantes con filtros
  async getAll(req, res, next) {
    try {
      const { page = 1, limit = 10, search, grado, seccion } = req.query;
      
      const skip = (parseInt(page) - 1) * parseInt(limit);
      const take = parseInt(limit);

      const where = {};
      
      if (search) {
        where.OR = [
          { usuario: { nombre: { contains: search, mode: 'insensitive' } } },
          { usuario: { apellido: { contains: search, mode: 'insensitive' } } },
          { codigoEstudiante: { contains: search, mode: 'insensitive' } },
          { usuario: { email: { contains: search, mode: 'insensitive' } } }
        ];
      }

      if (grado) {
        where.matriculas = { some: { gradoId: parseInt(grado) } };
      }

      if (seccion) {
        where.matriculas = { some: { seccionId: parseInt(seccion) } };
      }

      const [students, total] = await Promise.all([
        prisma.estudiante.findMany({
          where,
          include: {
            usuario: true,
            matriculas: {
              include: {
                grado: true,
                seccion: true,
                periodo: true
              }
            },
            apoderados: {
              include: {
                apoderado: {
                  include: {
                    usuario: true
                  }
                }
              }
            }
          },
          skip,
          take,
          orderBy: {
            usuario: {
              apellido: 'asc'
            }
          }
        }),
        prisma.estudiante.count({ where })
      ]);

      res.json({
        success: true,
        data: students,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          totalPages: Math.ceil(total / parseInt(limit))
        }
      });
    } catch (error) {
      next(error);
    }
  },

  // Obtener estudiante por ID
  async getById(req, res, next) {
    try {
      const { id } = req.params;

      const student = await prisma.estudiante.findUnique({
        where: { id: parseInt(id) },
        include: {
          usuario: true,
          matriculas: {
            include: {
              grado: true,
              seccion: true,
              periodo: true
            }
          },
          apoderados: {
            include: {
              apoderado: {
                include: {
                  usuario: true
                }
              }
            }
          },
          asistencias: {
            take: 10,
            orderBy: { fecha: 'desc' },
            include: {
              horario: {
                include: {
                  curso: true
                }
              }
            }
          }
        }
      });

      if (!student) {
        throw new AppError('Estudiante no encontrado', 404, 'STUDENT_NOT_FOUND');
      }

      res.json({
        success: true,
        data: student
      });
    } catch (error) {
      next(error);
    }
  },

  // Crear estudiante
  async create(req, res, next) {
    try {
      const { email, password, nombre, apellido, telefono, direccion, fechaNacimiento, genero, alergias, observaciones, gradoId, seccionId, periodoId, apoderados } = req.body;

      // Verificar si el email ya existe
      const existingUser = await prisma.usuario.findUnique({
        where: { email }
      });

      if (existingUser) {
        throw new AppError('El email ya está registrado', 409, 'EMAIL_EXISTS');
      }

      // Obtener rol de estudiante
      const studentRole = await prisma.rol.findFirst({
        where: { nombre: 'ESTUDIANTE' }
      });

      if (!studentRole) {
        throw new AppError('Rol de estudiante no encontrado', 500);
      }

      // Crear usuario y estudiante en transacción
      const result = await prisma.$transaction(async (tx) => {
        // Crear usuario
        const user = await tx.usuario.create({
          data: {
            email,
            passwordHash: await bcrypt.hash(password, 10),
            nombre,
            apellido,
            telefono,
            direccion,
            rolId: studentRole.id,
            activo: true
          }
        });

        // Crear estudiante
        const student = await tx.estudiante.create({
          data: {
            usuarioId: user.id,
            codigoEstudiante: generateCode('EST', 6),
            fechaNacimiento: fechaNacimiento ? new Date(fechaNacimiento) : null,
            genero,
            alergias,
            observaciones
          }
        });

        // Crear matrícula
        if (gradoId && seccionId && periodoId) {
          await tx.matricula.create({
            data: {
              estudianteId: student.id,
              gradoId: parseInt(gradoId),
              seccionId: parseInt(seccionId),
              periodoId: parseInt(periodoId),
              fechaMatricula: new Date(),
              estado: 'ACTIVO'
            }
          });
        }

        // Asignar apoderados
        if (apoderados && apoderados.length > 0) {
          for (const apod of apoderados) {
            await tx.estudianteApoderado.create({
              data: {
                estudianteId: student.id,
                apoderadoId: parseInt(apod.apoderadoId),
                parentesco: apod.parentesco,
                esContactoPrincipal: apod.esContactoPrincipal || false
              }
            });
          }
        }

        return {
          ...student,
          usuario: user
        };
      });

      res.status(201).json({
        success: true,
        data: result,
        message: 'Estudiante creado exitosamente'
      });
    } catch (error) {
      next(error);
    }
  },

  // Actualizar estudiante
  async update(req, res, next) {
    try {
      const { id } = req.params;
      const { nombre, apellido, telefono, direccion, fechaNacimiento, genero, alergias, observaciones, activo } = req.body;

      const student = await prisma.estudiante.findUnique({
        where: { id: parseInt(id) },
        include: { usuario: true }
      });

      if (!student) {
        throw new AppError('Estudiante no encontrado', 404, 'STUDENT_NOT_FOUND');
      }

      const updated = await prisma.$transaction(async (tx) => {
        // Actualizar usuario
        const user = await tx.usuario.update({
          where: { id: student.usuarioId },
          data: {
            nombre,
            apellido,
            telefono,
            direccion,
            activo
          }
        });

        // Actualizar estudiante
        const studentUpdated = await tx.estudiante.update({
          where: { id: parseInt(id) },
          data: {
            fechaNacimiento: fechaNacimiento ? new Date(fechaNacimiento) : null,
            genero,
            alergias,
            observaciones
          },
          include: {
            usuario: true,
            matriculas: {
              include: {
                grado: true,
                seccion: true,
                periodo: true
              }
            }
          }
        });

        return studentUpdated;
      });

      res.json({
        success: true,
        data: updated,
        message: 'Estudiante actualizado exitosamente'
      });
    } catch (error) {
      next(error);
    }
  },

  // Eliminar estudiante (soft delete)
  async delete(req, res, next) {
    try {
      const { id } = req.params;

      const student = await prisma.estudiante.findUnique({
        where: { id: parseInt(id) }
      });

      if (!student) {
        throw new AppError('Estudiante no encontrado', 404, 'STUDENT_NOT_FOUND');
      }

      await prisma.$transaction(async (tx) => {
        // Desactivar usuario
        await tx.usuario.update({
          where: { id: student.usuarioId },
          data: { activo: false }
        });

        // Actualizar matrículas a INACTIVO
        await tx.matricula.updateMany({
          where: { estudianteId: parseInt(id) },
          data: { estado: 'INACTIVO' }
        });
      });

      res.json({
        success: true,
        message: 'Estudiante desactivado exitosamente'
      });
    } catch (error) {
      next(error);
    }
  }
};