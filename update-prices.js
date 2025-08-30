const fs = require('fs');
const axios = require('axios');

// Función para obtener precios desde tu API
async function fetchUpdatedPrices() {
  // Simula o reemplaza por tu llamada real
  // const { data } = await axios.get('https://api.example.com/prices');
  // return data;

  // ✅ Ejemplo con valores reales mientras defines tu API
  return {
    "panel-100": {
      "base": { "small": 3200, "medium": 3600, "large": 4000 },
      "factor": { "new": 0, "mid": 400, "old": 800 }
    },
    "panel-200": {
      "base": { "small": 4800, "medium": 5200, "large": 5800 },
      "factor": { "new": 0, "mid": 500, "old": 1000 }
    },
    "ev-charger": {
      "base": { "small": 850, "medium": 1200, "large": 1500 },
      "factor": { "new": 0, "mid": 200, "old": 400 }
    },
    "smart-home": {
      "base": { "small": 2000, "medium": 3500, "large": 5000 },
      "factor": { "new": 0, "mid": 300, "old": 600 }
    }
  };
}

// Actualización diaria
const updatePrices = async () => {
  try {
    const newPrices = await fetchUpdatedPrices();
    await fs.promises.writeFile('prices.json', JSON.stringify(newPrices, null, 2), 'utf8');
    console.log('✅ prices.json actualizado correctamente');
    return newPrices;
  } catch (error) {
    console.error('❌ Error actualizando precios:', error);
    throw error;
  }
};

// Ejecutar si se llama directamente
if (require.main === module) {
  updatePrices();
}

module.exports = { updatePrices };
