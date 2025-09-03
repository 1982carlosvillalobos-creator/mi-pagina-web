async function loadAllData() {
  try {
    // ✅ Usamos materials-prices.json para costos reales
    const res1 = await fetch('data/materials-prices.json');
    prices = await res1.json();

    const res2 = await fetch('data/labor-rates.json');
    laborRates = await res2.json();

    const res3 = await fetch('data/permits.json');
    permits = await res3.json();

    const res4 = await fetch('data/materials-db.json');
    materialsDB = await res4.json();
  } catch (e) {
    console.error("Error cargando datos", e);
  }
}
