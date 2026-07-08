const nodemailer = require('nodemailer');
const env = require('../../config/environment');

class EmailService {
  constructor() {
    this.transporter = nodemailer.createTransport({
      host: env.email.host,
      port: env.email.port,
      secure: env.email.port === 465,
      auth: {
        user: env.email.user,
        pass: env.email.pass
      }
    });
  }
  
  /**
   * Envía un email
   */
  async send({ to, subject, html, attachments = [] }) {
    try {
      const mailOptions = {
        from: `"School Pro" <${env.email.from}>`,
        to,
        subject,
        html,
        attachments
      };
      
      const info = await this.transporter.sendMail(mailOptions);
      console.log('📧 Email enviado:', info.messageId);
      return info;
    } catch (error) {
      console.error('❌ Error enviando email:', error);
      throw error;
    }
  }
  
  /**
   * Envía email de restablecimiento de contraseña
   */
  async sendPasswordReset(user, resetUrl) {
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #1E293B; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background-color: #2563EB; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
          .content { background-color: #F8FAFC; padding: 30px; border-radius: 0 0 8px 8px; border: 1px solid #E2E8F0; }
          .btn { display: inline-block; background-color: #2563EB; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
          .footer { margin-top: 20px; font-size: 12px; color: #64748B; text-align: center; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>Restablecer Contraseña</h1>
          </div>
          <div class="content">
            <p>Hola <strong>${user.nombre} ${user.apellido}</strong>,</p>
            <p>Hemos recibido una solicitud para restablecer la contraseña de su cuenta en <strong>School Pro</strong>.</p>
            <p>Haga clic en el botón de abajo para restablecer su contraseña:</p>
            <div style="text-align: center;">
              <a href="${resetUrl}" class="btn">Restablecer Contraseña</a>
            </div>
            <p>Si no solicitó este cambio, ignore este correo.</p>
            <p>Este enlace expirará en <strong>1 hora</strong>.</p>
            <hr>
            <p style="font-size: 12px; color: #64748B;">
              Si el botón no funciona, copie y pegue este enlace en su navegador:<br>
              ${resetUrl}
            </p>
          </div>
          <div class="footer">
            <p>&copy; ${new Date().getFullYear()} School Pro. Todos los derechos reservados.</p>
          </div>
        </div>
      </body>
      </html>
    `;
    
    return this.send({
      to: user.email,
      subject: 'Restablecer contraseña - School Pro',
      html
    });
  }
  
  /**
   * Envía notificación de inasistencia al tutor
   */
  async sendAttendanceAlert(tutorEmail, estudiante, detalles) {
    const html = `
      <!DOCTYPE html>
      <html>
      <head><meta charset="utf-8"></head>
      <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto;">
          <h2 style="color: #EF4444;">⚠️ Alerta de Inasistencia</h2>
          <p>Estimado tutor de <strong>${estudiante.nombre} ${estudiante.apellido}</strong>,</p>
          <p>Se ha registrado una inasistencia para el estudiante:</p>
          <ul>
            <li><strong>Fecha:</strong> ${detalles.fecha}</li>
            <li><strong>Curso:</strong> ${detalles.curso}</li>
            <li><strong>Estado:</strong> ${detalles.estado}</li>
          </ul>
          <p>Por favor, comuníquese con la institución si tiene alguna consulta.</p>
        </div>
      </body>
      </html>
    `;
    
    return this.send({
      to: tutorEmail,
      subject: `Alerta de Inasistencia - ${estudiante.nombre} ${estudiante.apellido}`,
      html
    });
  }
  
  /**
   * Verifica la conexión con el servidor SMTP
   */
  async verifyConnection() {
    try {
      await this.transporter.verify();
      console.log('✅ Servidor de correo conectado');
      return true;
    } catch (error) {
      console.error('❌ Error en conexión SMTP:', error.message);
      return false;
    }
  }
}

module.exports = new EmailService();