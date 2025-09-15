<script>
  function toggleChat() {
    const box = document.getElementById('chat-box');
    box.style.display = box.style.display === 'none' ? 'block' : 'none';
  }

  function talkToAI() {
    alert("This will connect to AI bot. (Coming soon!)");
    // Later: open chat interface or popup with your AI
  }

  function talkToWhatsApp() {
    window.open("https://wa.me/03173903014", "_blank");
  }

  function talkToGmail() {
    window.open("mailto:studenttech@example.com", "_blank");
  }
</script>
