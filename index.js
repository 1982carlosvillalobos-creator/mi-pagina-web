const express = require('express');
const cors = require('cors');
const twilio = require('twilio');

const app = express();

// Configuración de Twilio usando variables de entorno
// Asegúrate de que estas variables estén configuradas en tu servicio de despliegue (Render)
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;

// Verificación básica para asegurar que las credenciales estén presentes
if (!accountSid || !authToken) {
  console.error("CRÍTICO: TWILIO_ACCOUNT_SID o TWILIO_AUTH_TOKEN no están definidos en las variables de entorno.");
  process.exit(1); // Detiene la aplicación si no hay credenciales
}

const client = new twilio(accountSid, authToken);
const twilioPhoneNumber = process.env.TWILIO_PHONE_NUMBER;

// Verificación básica para el número de teléfono
if (!twilioPhoneNumber) {
  console.error("CRÍTICO: TWILIO_PHONE_NUMBER no está definido en las variables de entorno.");
  process.exit(1);
}

// Middleware
app.use(cors());
app.use(express.json());

// Endpoint para enviar código de verificación
app.post('/send-code', async (req, res) => {
  console.log("Solicitud recibida en /send-code"); // Log para depuración
  const { phone } = req.body;

  if (!phone) {
    console.log("Error: Número de teléfono no proporcionado.");
    return res.status(400).json({ success: false, error: 'Número de teléfono requerido' });
  }

  // Generar código de 6 dígitos
  const code = Math.floor(100000 + Math.random() * 900000).toString();
  console.log(`Código generado para ${phone}: ${code}`); // Log para depuración

  try {
    const message = await client.messages.create({
      body: `Golden Charge: Tu código de verificación es: ${code}`,
      from: twilioPhoneNumber,
      to: phone
    });

    console.log(`Mensaje enviado exitosamente. SID: ${message.sid}`);
    res.json({ success: true });
  } catch (error) {
    console.error('Error enviando SMS:', error.message);
    // Proporciona un mensaje de error más específico si es posible
    if (error.code === 21211) { // Twilio error code for invalid 'To' number
       res.status(400).json({ success: false, error: 'Número de teléfono inválido. Por favor, verifica el número e intenta nuevamente.' });
    } else {
       res.status(500).json({ success: false, error: 'No se pudo enviar el SMS. Por favor, inténtalo más tarde.' });
    }
  }
});

// Puerto (usará el puerto de Render o 3000 localmente)
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
  console.log(`TWILIO_ACCOUNT_SID está definido: ${!!accountSid}`);
  console.log(`TWILIO_PHONE_NUMBER: ${twilioPhoneNumber}`);
});
