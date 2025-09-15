document.getElementById('contactForm').addEventListener('submit', function (e) {
  e.preventDefault();
  alert('Thank you for your message. Our support team will contact you shortly!');
  this.reset();
});
