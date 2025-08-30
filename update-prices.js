const axios = require('axios');
const fs = require('fs');

async function fetchUpdatedPrices() {
  // URL de la API de precios (reemplaza con la URL real)
  const response = await axios.get('https://api.example.com/prices');
  return response.data;
}

async function writePricesToFile(prices) {
  // Guarda los precios en un archivo JSON
  fs.writeFileSync('prices.json', JSON.stringify(prices, null, 2), 'utf8');
}

async function main() {
  try {
    const newPrices = await fetchUpdatedPrices();
    await writePricesToFile(newPrices);
    console.log('Precios actualizados correctamente');
  } catch (error) {
    console.error('Error actualizando precios:', error);
  }
}

main();
