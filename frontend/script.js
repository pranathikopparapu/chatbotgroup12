const API_URL = "http://127.0.0.1:8000/chat";

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("question");
const sendBtn = document.getElementById("send");
const voiceBtn = document.getElementById("voice-btn");

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `msg ${sender}`;
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(question) {
  // Don't clear input if typing (keep cursor)
  addMessage(question, "user");
  
  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    addMessage(data.answer, "bot");
  } catch {
    addMessage("❌ Backend not running", "bot");
  }
}

// ========== TEXT INPUT (Always works) ==========
sendBtn.onclick = () => {
  const question = input.value.trim();
  if (question) {
    sendMessage(question);
    input.value = "";  // Clear only on Send button
  }
};

input.onkeypress = (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    const question = input.value.trim();
    if (question) sendMessage(question);
    input.value = "";
  }
};

// ========== VOICE INPUT (Separate) ==========
let recognition;
if ('webkitSpeechRecognition' in window) {
  const SpeechRecognition = window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = 'en-IN';
  recognition.interimResults = false;
  
  recognition.onstart = () => {
    voiceBtn.textContent = "🔴";
    voiceBtn.classList.add("recording");
    input.placeholder = "Listening... Speak now!";
  };
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    sendMessage(transcript);  // Send voice directly (no input.value change)
  };
  
  recognition.onend = () => {
    voiceBtn.textContent = "🎤";
    voiceBtn.classList.remove("recording");
    input.placeholder = "Type or click 🎤 to speak...";
  };
  
  voiceBtn.onclick = () => recognition.start();
  
} else {
  voiceBtn.disabled = true;
  voiceBtn.textContent = "❌";
  voiceBtn.title = "Voice not supported";
}

// Welcome
addMessage("Welcome to the KLU Chatbot! I’m here to help, what can I do for you today? 😊", "bot");
