document.getElementById('contactForm').addEventListener('submit', function(e) {
  e.preventDefault();
  
  const name = document.getElementById('name').value.trim();
  alert(`Thank you, ${name}! Your message has been sent. We'll contact you soon via your preferred channel.`);
  
  this.reset();
});