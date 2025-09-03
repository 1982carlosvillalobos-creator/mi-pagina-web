let helperCount = 1;
let prices = {}, laborRates = {}, permits = {}, materialsDB = {};

// Verificar contraseña
function checkPassword() {
  const pwd = document.getElementById('password').value;
  if (pwd === 'MiClaveElectrica!2025') { // Cambia esto por tu contraseña
    localStorage.setItem('estimatorAccess', 'true');
    document.getElementById('login').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    loadAllData();
  } else {
    alert('Contraseña incorrecta');
  }
}

// Verificar acceso al cargar
window.onload = function () {
  if (localStorage.getItem('estimatorAccess') === 'true') {
    document.getElementById('login').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    loadAllData();
  }
};

// Cargar todos los datos
async function loadAllData() {
  try {
    // Usamos materials-prices.json para costos reales
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

// Control de ayudantes
function addHelper() { if (helperCount < 5) helperCount++; document.getElementById('helperCount').textContent = helperCount; }
function removeHelper() { if (helperCount > 0) helperCount--; document.getElementById('helperCount').textContent = helperCount; }

// Cálculo principal
async function calculateQuote() {
  const projectKey = document.getElementById('projectType').value;
  const city = document.getElementById('city').value;
  const clientType = document.getElementById('clientType').value;
  const hours = parseFloat(document.getElementById('hours').value) || 1;
  const markup = parseFloat(document.getElementById('materialMarkup').value) / 100;
  const taxRate = 0.0925;

  const project = materialsDB[projectKey];
  const labor = laborRates[city];
  const permitCost = permits[city][projectKey.split('-')[0]] || 0;

  // Materiales
  let materialCost = 0;
  for (const [item, qty] of Object.entries(project.materials)) {
    materialCost += qty * (prices[item] || 0);
  }
  const materialSell = materialCost * (1 + markup);
  const taxAmount = clientType === 'homeowner' ? materialSell * taxRate : 0;

  // Mano de obra
  const contractorCost = hours * labor.labor_cost.contractor_c10;
  const helperCost = hours * helperCount * labor.labor_cost.helper;
  const totalLaborCost = contractorCost + helperCost;

  const contractorSell = hours * labor.labor_rate.contractor_c10;
  const helperSell = hours * helperCount * labor.labor_rate.helper;
  const totalLaborSell = contractorSell + helperSell;

  // Totales
  const totalCost = materialCost + totalLaborCost + permitCost;
  const totalPrice = materialSell + taxAmount + totalLaborSell + permitCost;
  const profit = totalPrice - totalCost;

  // Mostrar
  displayResult({
    materialCost, materialSell, taxAmount,
    totalLaborCost, totalLaborSell,
    permitCost, totalCost, totalPrice, profit,
    hours, helperCount, markup: markup * 100, city, projectKey
  });
}

function displayResult(data) {
  const results = document.getElementById('results');
  results.innerHTML = `
    <div id="quote-result" style="background:#fff;padding:20px;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1);">
      <h2>Cotización: ${data.projectKey.replace('-', ' ').replace('-', ' ').toUpperCase()}</h2>
      <p><strong>Ciudad:</strong> ${data.city}</p>
      <p><strong>Horas:</strong> ${data.hours} × (Tú + ${data.helperCount} ayudante${data.helperCount !== 1 ? 's' : ''})</p>
      <p><strong>Markup Materiales:</strong> ${data.markup}%</p>
      
      <table border="1" cellpadding="8" style="border-collapse:collapse;width:100%;margin:20px 0;">
        <tr><th>Concepto</th><th>Costo Real</th><th>Precio Venta</th></tr>
        <tr><td>Materiales</td><td>$${data.materialCost.toFixed(2)}</td><td>$${data.materialSell.toFixed(2)}</td></tr>
        <tr><td>Impuesto (9.25%)</td><td>-</td><td>$${data.taxAmount.toFixed(2)}</td></tr>
        <tr><td>Mano de Obra</td><td>$${data.totalLaborCost.toFixed(2)}</td><td>$${data.totalLaborSell.toFixed(2)}</td></tr>
        <tr><td>Permisos</td><td>$${data.permitCost.toFixed(2)}</td><td>$${data.permitCost.toFixed(2)}</td></tr>
        <tr style="font-weight:bold;background:#f0f0f0;"><td>Total</td><td>$${data.totalCost.toFixed(2)}</td><td>$${data.totalPrice.toFixed(2)}</td></tr>
      </table>
      <p><strong>Ganancia Neta:</strong> $${data.profit.toFixed(2)} (${((data.profit / data.totalCost) * 100).toFixed(1)}%)</p>
    </div>
  `;
}

// Exportar a PDF
function generatePDF() {
  const element = document.getElementById('quote-result');
  const opt = {
    margin: 1,
    filename: 'goldencharge-cotizacion.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };
  html2pdf().from(element).set(opt).save();
}
