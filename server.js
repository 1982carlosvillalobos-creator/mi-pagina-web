// server.js  – backend con verificación SMS + actualización automática de precios
// =============================================================================

// 1. Dependencias
const express       = require('express');
const bodyParser    = require('body-parser');
const twilio        = require('twilio');
const fs            = require('fs');
const path          = require('path');

// 2. Credenciales Twilio
const accountSid = 'ACd49100e1053db003f37809c7e1f80739';
const authToken  = 'fbf83f9a31d084c6a15f589f851c87d4';   // ← tu Auth Token real
const client     = new twilio(accountSid, authToken);
const verifySid  = 'VA53c5aad159020163db91ee6bcc9f225c';   // Service SID de Verify

// 3. Inicializa Express
const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// ------------------------------------------------------------
// 4. ENDPOINTS  SMS / VERIFY
// ------------------------------------------------------------

// 4A. Enviar código SMS
app.post('/send-code', async (req, res) => {
  const { phone } = req.body;
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

// 4B. Verificar código
app.post('/check-code', async (req, res) => {
  const { phone, code } = req.body;
  if (!phone || !code) return res.status(400).send('Faltan datos');

  try {
    const check = await client.verify.services(verifySid)
      .verificationChecks.create({ to: phone, code });
    res.json({ success: check.status === 'approved', status: check.status });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ------------------------------------------------------------
// 5. ACTUALIZACIÓN AUTOMÁTICA DE PRECIOS
//    (se ejecuta al llamar POST /update-prices o vía GitHub Action)
// ------------------------------------------------------------
const pricesFile = path.join(__dirname, 'prices.json');

app.post('/update-prices', async (req, res) => {
  try {
    // Lógica de scraping/API que ya usas
    const newPrices = await fetchUpdatedPrices(); // tu función existente
    fs.writeFileSync(pricesFile, JSON.stringify(newPrices, null, 2), 'utf8');
    res.json({ ok: true, message: 'Precios actualizados' });
  } catch (e) {
    console.error(e);
    res.status(500).json({ ok: false, error: e.message });
  }
});

// Si ya tienes la función fetchUpdatedPrices() en otro archivo,
// simplemente impórtala o pégala aquí debajo.
// Ejemplo mínimo de placeholder:
async function fetchUpdatedPrices() {
  // Aquí va tu código real (axios, scraping,
