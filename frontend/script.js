const API_URL = "https://chatbotgroup12.onrender.com";

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("question");
const sendBtn = document.getElementById("send");
const voiceBtn = document.getElementById("voice-btn");

// 🧠 Add message
function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `msg ${sender}`;
  div.innerHTML = text.replace(/\n/g, "<br>");
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// 🚀 SEND MESSAGE (FIXED)
async function sendMessage(question) {
  if (!question) return;

  addMessage(question, "user");

  const loading = document.createElement("div");
  loading.className = "msg bot";
  loading.textContent = "⏳ Checking...";
  chatBox.appendChild(loading);

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    const raw = await res.json();
    chatBox.removeChild(loading);

    const data = raw.answer || raw;

    console.log("API RESPONSE:", data);

    // 🛒 ADD TO CART
    if (data.type === "add_to_cart") {
      addMessage(
        `🛒 Added <b>${data.product.name}</b><br>₹${data.product.price}`,
        "bot"
      );

      window.parent.postMessage(
        {
          type: "ADD_TO_CART",
          product: data.product
        },
        "*"
      );
    }

    // 📊 CHART (IMPORTANT)
    else if (data.type === "chart") {
      addMessage("📊 Showing data insights...", "bot");

      window.parent.postMessage(
        {
          type: "SHOW_CHART",
          chartData: data.chartData
        },
        "*"
      );
    }

    // 💬 TEXT
    else if (data.type === "text") {
      addMessage(data.message, "bot");
    }

    // 🔄 STRING FALLBACK
    else if (typeof data === "string") {
      addMessage(data, "bot");
    }

    // ❌ UNKNOWN
    else {
      console.warn("Unknown format:", data);
      addMessage("⚠️ Something went wrong. Try again.", "bot");
    }

  } catch (err) {
    console.error("ERROR:", err);
    chatBox.removeChild(loading);
    addMessage("❌ Backend error. Check server.", "bot");
  }
}

// ================= INPUT =================
sendBtn.onclick = () => {
  const question = input.value.trim();
  if (question) {
    sendMessage(question);
    input.value = "";
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

// ================= 🎤 VOICE =================
let recognition;

if ("webkitSpeechRecognition" in window) {
  const SpeechRecognition = window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();

  recognition.lang = "en-IN";
  recognition.continuous = false;

  recognition.onstart = () => {
    voiceBtn.textContent = "🔴";
    voiceBtn.classList.add("recording");
    input.placeholder = "Listening...";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    sendMessage(transcript);
  };

  recognition.onend = () => {
    voiceBtn.textContent = "🎤";
    voiceBtn.classList.remove("recording");
    input.placeholder = "Ask something...";
  };

  voiceBtn.onclick = () => recognition.start();

} else {
  voiceBtn.disabled = true;
  voiceBtn.textContent = "❌";
}

// ================= WELCOME =================
addMessage(
  `👋 Welcome to Smart Retail Assistant 🤖<br><br>
   Try:<br>
   • 🛒 add pizza<br>
   • ⭐ recommend items<br>
   • 💰 cheap items<br>
   • 📊 data insights`,
  "bot"
);