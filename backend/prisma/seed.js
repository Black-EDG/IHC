import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Iniciando seed de la base de datos...');

  // 1. Crear Roles
  console.log('📋 Creando roles...');
  
  const rolesData = [
    { nombre: 'ADMIN', descripcion: 'Administrador del sistema - control total' },
    { nombre: 'DIRECTOR', descripcion: 'Director de la institución' },
    { nombre: 'DOCENTE', descripcion: 'Personal docente' },
    { nombre: 'APODERADO', descripcion: 'Padre, madre o tutor del estudiante' },
    { nombre: 'ESTUDIANTE', descripcion: 'Estudiante del colegio' }
  ];

  const roles = [];
  for (const data of rolesData) {
    const rol = await prisma.rol.upsert({
      where: { nombre: data.nombre },
      update: {},
      create: data
    });
    roles.push(rol);
  }
  console.log(`✅ ${roles.length} roles creados/verificados`);

  // 2. Crear Permisos
  console.log('📋 Creando permisos...');
  
  const permisosData = [
    { nombre: 'ver_dashboard', descripcion: 'Ver dashboard', modulo: 'dashboard' },
    { nombre: 'gestionar_usuarios', descripcion: 'Gestionar usuarios', modulo: 'usuarios' },
    { nombre: 'gestionar_estudiantes', descripcion: 'Gestionar estudiantes', modulo: 'estudiantes' },
    { nombre: 'gestionar_docentes', descripcion: 'Gestionar docentes', modulo: 'docentes' },
    { nombre: 'registrar_asistencia', descripcion: 'Registrar asistencia', modulo: 'asistencia' },
    { nombre: 'ver_reportes', descripcion: 'Ver reportes', modulo: 'reportes' },
    { nombre: 'gestionar_cursos', descripcion: 'Gestionar cursos', modulo: 'cursos' },
    { nombre: 'configurar_sistema', descripcion: 'Configurar sistema', modulo: 'configuracion' }
  ];

  const permisos = [];
  for (const data of permisosData) {
    const permiso = await prisma.permiso.upsert({
      where: { nombre: data.nombre },
      update: {},
      create: data
    });
    permisos.push(permiso);
  }
  console.log(`✅ ${permisos.length} permisos creados/verificados`);

  // 3. Asignar Permisos a Roles
  console.log('📋 Asignando permisos a roles...');
  
  const adminRole = roles.find(r => r.nombre === 'ADMIN');
  const directorRole = roles.find(r => r.nombre === 'DIRECTOR');
  const docenteRole = roles.find(r => r.nombre === 'DOCENTE');

  await prisma.rolPermiso.deleteMany({});

  // Admin: todos los permisos
  for (const permiso of permisos) {
    await prisma.rolPermiso.create({
      data: { rolId: adminRole.id, permisoId: permiso.id }
    });
  }

  // Director: permisos específicos
  const directorPermisos = ['ver_dashboard', 'gestionar_estudiantes', 'gestionar_docentes', 'registrar_asistencia', 'ver_reportes', 'gestionar_cursos'];
  for (const permiso of permisos) {
    if (directorPermisos.includes(permiso.nombre)) {
      await prisma.rolPermiso.create({
        data: { rolId: directorRole.id, permisoId: permiso.id }
      });
    }
  }

  // Docente: permisos limitados
  const docentePermisos = ['ver_dashboard', 'registrar_asistencia', 'ver_reportes'];
  for (const permiso of permisos) {
    if (docentePermisos.includes(permiso.nombre)) {
      await prisma.rolPermiso.create({
        data: { rolId: docenteRole.id, permisoId: permiso.id }
      });
    }
  }
  console.log('✅ Permisos asignados correctamente');

  // 4. Crear Usuario Administrador
  console.log('📋 Creando usuario administrador...');
  const hashedPassword = await bcrypt.hash('admin123', 10);
  
  const adminUser = await prisma.usuario.upsert({
    where: { email: 'admin@schoolpro.com' },
    update: {},
    create: {
      email: 'admin@schoolpro.com',
      passwordHash: hashedPassword,
      nombre: 'Administrador',
      apellido: 'Sistema',
      telefono: '999888777',
      rolId: adminRole.id,
      activo: true
    }
  });
  console.log('✅ Usuario administrador creado/verificado:');
  console.log('   👤 Email: admin@schoolpro.com');
  console.log('   🔑 Contraseña: admin123');

  // 5. Crear Grados y Secciones
  console.log('📋 Creando grados y secciones...');
  
  const gradosData = [
    { nombre: '1ro', orden: 1 },
    { nombre: '2do', orden: 2 },
    { nombre: '3ro', orden: 3 },
    { nombre: '4to', orden: 4 },
    { nombre: '5to', orden: 5 }
  ];

  const grados = [];
  for (const data of gradosData) {
    const grado = await prisma.grado.upsert({
      where: { nombre: data.nombre },
      update: {},
      create: data
    });
    grados.push(grado);
  }

  for (const grado of grados) {
    for (const seccionNombre of ['A', 'B']) {
      await prisma.seccion.upsert({
        where: {
          nombre_gradoId: {
            nombre: seccionNombre,
            gradoId: grado.id
          }
        },
        update: {},
        create: {
          nombre: seccionNombre,
          gradoId: grado.id,
          capacidad: 30
        }
      });
    }
  }
  console.log(`✅ ${grados.length} grados creados/verificados con sus secciones`);

  // 6. Crear Cursos
  console.log('📋 Creando cursos...');
  
  const cursosData = [
    { nombre: 'Matemáticas', descripcion: 'Matemáticas y Razonamiento', creditos: 4, color: '#2563EB' },
    { nombre: 'Comunicación', descripcion: 'Lenguaje y Literatura', creditos: 4, color: '#22C55E' },
    { nombre: 'Ciencias', descripcion: 'Ciencia y Tecnología', creditos: 3, color: '#F59E0B' },
    { nombre: 'Historia', descripcion: 'Ciencias Sociales', creditos: 3, color: '#EF4444' },
    { nombre: 'Inglés', descripcion: 'Idioma Extranjero', creditos: 3, color: '#8B5CF6' }
  ];

  const cursos = [];
  for (const data of cursosData) {
    const curso = await prisma.curso.upsert({
      where: { nombre: data.nombre },
      update: {},
      create: data
    });
    cursos.push(curso);
  }

  for (const grado of grados) {
    for (const curso of cursos) {
      await prisma.gradoCurso.upsert({
        where: {
          gradoId_cursoId: {
            gradoId: grado.id,
            cursoId: curso.id
          }
        },
        update: {},
        create: {
          gradoId: grado.id,
          cursoId: curso.id
        }
      });
    }
  }
  console.log(`✅ ${cursos.length} cursos creados/verificados y asignados`);

  // 7. Crear Período Académico
  console.log('📋 Creando período académico...');
  
  let periodo = await prisma.periodo.findFirst({
    where: { nombre: 'Año Escolar 2026' }
  });

  if (!periodo) {
    periodo = await prisma.periodo.create({
      data: {
        nombre: 'Año Escolar 2026',
        fechaInicio: new Date('2026-03-01'),
        fechaFin: new Date('2026-12-20'),
        activo: true
      }
    });
  }
  console.log('✅ Período académico creado/verificado');

  // 8. Crear Aulas
  console.log('📋 Creando aulas...');
  
  const aulasData = [
    { codigo: 'A101', nombre: 'Aula 101', capacidad: 30, ubicacion: 'Primer Piso' },
    { codigo: 'A102', nombre: 'Aula 102', capacidad: 30, ubicacion: 'Primer Piso' },
    { codigo: 'A201', nombre: 'Aula 201', capacidad: 35, ubicacion: 'Segundo Piso' },
    { codigo: 'A202', nombre: 'Aula 202', capacidad: 35, ubicacion: 'Segundo Piso' },
    { codigo: 'LAB1', nombre: 'Laboratorio 1', capacidad: 25, ubicacion: 'Tercer Piso' }
  ];

  for (const data of aulasData) {
    await prisma.aula.upsert({
      where: { codigo: data.codigo },
      update: {},
      create: data
    });
  }
  console.log(`✅ ${aulasData.length} aulas creadas/verificadas`);

  // 9. Crear Configuraciones
  console.log('📋 Creando configuraciones...');
  
  const configuracionesData = [
    { clave: 'nombre_institucion', valor: 'School Attendance Pro', tipo: 'texto', descripcion: 'Nombre de la institución' },
    { clave: 'direccion', valor: 'Av. Principal 123', tipo: 'texto', descripcion: 'Dirección de la institución' },
    { clave: 'telefono', valor: '01 555-1234', tipo: 'texto', descripcion: 'Teléfono de contacto' },
    { clave: 'email', valor: 'info@schoolpro.edu', tipo: 'texto', descripcion: 'Email institucional' },
    { clave: 'color_primario', valor: '#2563EB', tipo: 'texto', descripcion: 'Color primario' },
    { clave: 'logo', valor: '', tipo: 'texto', descripcion: 'Logo de la institución' },
    { clave: 'tolerancia_tardanza', valor: '15', tipo: 'texto', descripcion: 'Minutos de tolerancia para tardanza' },
    { clave: 'max_inasistencias', valor: '10', tipo: 'texto', descripcion: 'Máximo de inasistencias permitidas' }
  ];

  for (const data of configuracionesData) {
    await prisma.configuracion.upsert({
      where: { clave: data.clave },
      update: {},
      create: data
    });
  }
  console.log(`✅ ${configuracionesData.length} configuraciones creadas/verificadas`);

  // 10. Crear usuario docente de ejemplo
  console.log('📋 Creando usuario docente de ejemplo...');
  const docentePassword = await bcrypt.hash('docente123', 10);
  
  const docenteUser = await prisma.usuario.upsert({
    where: { email: 'docente@schoolpro.com' },
    update: {},
    create: {
      email: 'docente@schoolpro.com',
      passwordHash: docentePassword,
      nombre: 'Juan',
      apellido: 'Pérez',
      telefono: '998877665',
      rolId: docenteRole.id,
      activo: true
    }
  });

  await prisma.docente.upsert({
    where: { usuarioId: docenteUser.id },
    update: {},
    create: {
      usuarioId: docenteUser.id,
      codigoDocente: 'DOC001',
      especialidad: 'Matemáticas',
      tituloAcademico: 'Lic. Matemáticas',
      experiencia: 5
    }
  });
  console.log('✅ Usuario docente creado/verificado:');
  console.log('   👤 Email: docente@schoolpro.com');
  console.log('   🔑 Contraseña: docente123');

  console.log('=================================');
  console.log('🎉 SEED COMPLETADO EXITOSAMENTE');
  console.log('=================================');
  console.log('🔑 CREDENCIALES DE ACCESO:');
  console.log('   Admin: admin@schoolpro.com / admin123');
  console.log('   Docente: docente@schoolpro.com / docente123');
  console.log('=================================');
}

main()
  .catch((e) => {
    console.error('❌ Error en el seed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });