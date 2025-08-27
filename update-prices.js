const fs = require('fs');
const axios = require('axios');

const updatePrices = async () => {
  try {
    const response = await axios.get('https://api.example.com/prices'); // URL de la API de precios actuales
    const newPrices = response.data;
    const fileContent = await fs.promises.readFile('prices.json', 'utf8');
    const updatedContent = fileContent.replace(
      /(<!-- PRICES -->)([\s\S]*?)(<!-- \/PRICES -->)/g,
      `<!-- PRICES -->\n${JSON.stringify(newPrices)}\n<!-- \/PRICES -->`
    );
    await fs.promises.writeFile('prices.json', updatedContent);
    console.log('Prices updated successfully');
  } catch (error) {
    console.error('Error updating prices:', error);
  }
};

updatePrices();
