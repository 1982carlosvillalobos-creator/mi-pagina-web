const twilio = require('twilio');

// Configuración de las credenciales de Twilio
const accountSid = 'ACd49100e1053db003f37809c7e1f80739';
const authToken = '259d5c64985f0514f929f3c8cb741cc';
const twilioPhoneNumber = '+15107377549';

// Crear una instancia del cliente Twilio
const client = new twilio(accountSid, authToken);

async function sendSMS(prices) {
  // Aquí puedes definir números de teléfono para notificar
  // Por ejemplo, notificamos al propietario de la actualización de precios
  const adminNumbers = ['+1234567890']; // Agrega el número de teléfono aquí

  for (const number of adminNumbers) {
    await client.messages.create({
      body: `Golden Charge: Prices have been updated. Panel upgrades now start at $${prices['panel-100'].base.small}`,
      from: twilioPhoneNumber,
      to: number
    });
    console.log(`Price update notification sent to ${number}`);
  }
}

async function main() {
  try {
    const prices = require('./prices.json'); // Supon que prices.json esté en la misma carpeta
    await sendSMS(prices);
  } catch (error) {
    console.error('Error sending SMS notification:', error);
  }
}

main();
