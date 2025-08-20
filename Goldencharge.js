document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('contactForm');
  const formMessage = document.getElementById('form-message');

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value.trim();
    
    // Mostrar mensaje de éxito
    formMessage.style.display = 'block';
    formMessage.innerHTML = `<strong>✅ Thank you, ${name}!</strong> We'll contact you soon via your preferred channel.`;
    formMessage.style.backgroundColor = '#d4edda';
    formMessage.style.color = '#155724';
    formMessage.style.padding = '15px';
    formMessage.style.borderRadius = '10px';
    formMessage.style.textAlign = 'center';
    formMessage.style.marginTop = '20px';
    
    // Resetear formulario
    form.reset();
    
    // Ocultar mensaje después de 5 segundos
    setTimeout(() => {
      formMessage.style.display = 'none';
    }, 5000);
  });
});
