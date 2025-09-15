document.addEventListener('DOMContentLoaded', function () {
  const chatToggle = document.getElementById('chat-toggle');
  const chatBox = document.getElementById('chat-box');
  const aiChat = document.querySelector('.ai-chat');
  const humanOptions = document.getElementById('human-options');

  chatToggle.addEventListener('click', function () {
    chatBox.classList.toggle('show');
    aiChat.style.display = "none";
    humanOptions.style.display = "none";
  });
});

function showAiChat() {
  document.querySelector('.ai-chat').style.display = 'block';
  document.getElementById('human-options').style.display = 'none';
}

function toggleHumanOptions() {
  const human = document.getElementById('human-options');
  const ai = document.querySelector('.ai-chat');
  if (human.style.display === 'none') {
    human.style.display = 'block';
    ai.style.display = 'none';
  } else {
    human.style.display = 'none';
  }
}

function sendMessage() {
  const input = document.getElementById("user-input");
  const chatLog = document.getElementById("chat-log");

  if (input.value.trim() === "") return;

  const userMsg = document.createElement("div");
  userMsg.textContent = "You: " + input.value;
  chatLog.appendChild(userMsg);

  const aiMsg = document.createElement("div");
  aiMsg.textContent = "AI: [Placeholder response]";
  chatLog.appendChild(aiMsg);

  input.value = "";
}
