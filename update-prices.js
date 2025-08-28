const fs = require('fs');
const axios = require('axios');
const twilio = require('twilio');

// Configuración de Twilio desde variables de entorno
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const twilioPhoneNumber = process.env.TWILIO_PHONE_NUMBER;

let client;
if (accountSid && authToken) {
  client = twilio(accountSid, authToken);
}

const updatePrices = async () => {
  try {
    // Aquí deberías reemplazar con la URL real de tu API de precios
    const response = await axios.get('https://api.example.com/prices');
    const newPrices = response.data;
    
    // Leer el archivo HTML actual
    let htmlContent = await fs.promises.readFile('index.html', 'utf8');
    
    // Actualizar los precios en el HTML
    htmlContent = htmlContent.replace(
      /(const prices = \{)([\s\S]*?)(\};)/,
      `const prices = ${JSON.stringify(newPrices, null, 2)};`
    );
    
    // Guardar el archivo HTML actualizado
    await fs.promises.writeFile('index.html', htmlContent);
    console.log('Prices updated successfully in HTML file');
    
    // Guardar también en un archivo JSON para referencia
    await fs.promises.writeFile('prices.json', JSON.stringify(newPrices, null, 2));
    console.log('Prices saved to prices.json');
    
    return newPrices;
  } catch (error) {
    console.error('Error updating prices:', error);
    throw error;
  }
};

// Función para enviar SMS (si se necesita notificación de actualización)
const sendPriceUpdateSMS = async (prices) => {
  if (!client || !twilioPhoneNumber) {
    console.log('Twilio not configured. Skipping SMS notifications.');
    return;
  }

  try {
    // Aquí puedes definir números de teléfono para notificar
    // sobre actualizaciones importantes de precios
    const adminNumbers = []; // Agrega números de administradores aquí si es necesario
    
    for (const number of adminNumbers) {
      await client.messages.create({
        body: `Golden Charge: Prices have been updated. Panel upgrades now start at $${prices['panel-100'].base.small}`,
        from: twilioPhoneNumber,
        to: number
      });
      console.log(`Price update notification sent to ${number}`);
    }
  } catch (error) {
    console.error('Error sending SMS notification:', error);
  }
};

// Ejecutar la actualización de precios
const main = async () => {
  try {
    const updatedPrices = await updatePrices();
    await sendPriceUpdateSMS(updatedPrices);
    console.log('Price update process completed successfully');
  } catch (error) {
    console.error('Price update process failed:', error);
    process.exit(1);
  }
};

if (require.main === module) {
  main();
}

module.exports = { updatePrices, sendPriceUpdateSMS };
