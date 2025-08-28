const twilio = require('twilio');

// Configuración de Twilio desde variables de entorno
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const twilioPhoneNumber = process.env.TWILIO_PHONE_NUMBER;

let client;
if (accountSid && authToken) {
  client = twilio(accountSid, authToken);
}

// Función para enviar SMS de verificación
const sendVerificationSMS = async (to, code) => {
  if (!client || !twilioPhoneNumber) {
    console.log('Twilio not configured. Skipping SMS.');
    return { success: false, message: 'Twilio not configured' };
  }

  try {
    const message = await client.messages.create({
      body: `Golden Charge verification code: ${code}. Valid for 5 minutes.`,
      from: twilioPhoneNumber,
      to: to
    });
    
    console.log(`Verification SMS sent to ${to}: ${message.sid}`);
    return { success: true, messageId: message.sid };
  } catch (error) {
    console.error(`Failed to send SMS to ${to}:`, error);
    return { success: false, error: error.message };
  }
};

// Función para enviar SMS con cotización
const sendQuoteSMS = async (to, quoteDetails) => {
  if (!client || !twilioPhoneNumber) {
    console.log('Twilio not configured. Skipping SMS.');
    return { success: false, message: 'Twilio not configured' };
  }

  try {
    const message = await client.messages.create({
      body: `Golden Charge Quote: ${quoteDetails.service} for ${quoteDetails.size} home. Estimated cost: $${quoteDetails.total}. Call ${twilioPhoneNumber} for details.`,
      from: twilioPhoneNumber,
      to: to
    });
    
    console.log(`Quote SMS sent to ${to}: ${message.sid}`);
    return { success: true, messageId: message.sid };
  } catch (error) {
    console.error(`Failed to send quote SMS to ${to}:`, error);
    return { success: false, error: error.message };
  }
};

module.exports = { sendVerificationSMS, sendQuoteSMS };
