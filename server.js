// server.js  – backend para enviar verificación SMS con Twilio
// ============================================================
// 1. Dependencias
const express = require('express');
const bodyParser = require('body-parser');
const twilio = require('twilio');

// 2. Tus credenciales de Twilio
const accountSid = 'ACd49100e1053db003f37809c7e1f80739';
const authToken  = 'fbf83f9a31d084c6a15f589f851c87d4';   // ← aquí va tu Auth Token real
const client     = new twilio(accountSid, authToken);
const verifySid  = 'VA53c5aad159020163db91ee6bcc9f225c'; // Service SID de Verify

// 3. Inicializa Express
const app = express();
app.use(bodyParser.json());               // para leer JSON que llegue del front-end
app.use(bodyParser.urlencoded({ extended: true }));

// 4. Ruta que recibe la petición de mandar el código
app.post('/send-code', async (req, res) => {
  const { phone } = req.body;           // teléfono en formato +1XXXXXXXXXX
  if (!phone) return res.status(400).send('Falta el teléfono');

  try {
    const verification = await client.verify.services(verifySid)
      .verifications.create({ to: phone, channel: 'sms' });
    res.json({ success: true, status: verification.status });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, error: err.message });
  }
});

// 5. Ruta que recibe el código que el usuario introduce
app.post('/check-code', async (req, res) => {
  const { phone, code } = req.body;
  if (!phone || !code) return res.status(400).send('Faltan datos');

  try {
    const check = await client.verify.services(verifySid)
      .verificationChecks.create({ to: phone, code: code });
    res.json({ success: check.status === 'approved', status: check.status });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 6. Pone a escuchar el servidor (importante para despliegues como Heroku / Glitch)
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor corriendo en puerto ${PORT}`));
