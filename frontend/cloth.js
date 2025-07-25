// Get cloth ID from URL
function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

const id = getQueryParam("id");
const clothFullId = id ? `${id}.jpg` : null;
let selectedModel = null;
let triggerSource = null; // NEW: to track which button triggered it

if (id) {
  const box = document.getElementById("selected-image-1");
  box.style.backgroundImage = `url('images/${id}.jpg')`;
  box.style.backgroundSize = "cover";
  box.style.backgroundPosition = "center";
} else {
  document.getElementById("selected-image-1").textContent = "No item selected.";
}

// Restore file upload functionality
const fileInput = document.getElementById("upload-input");
fileInput.addEventListener("change", function () {
  if (fileInput.files.length > 0) {
    alert("Image selected: " + fileInput.files[0].name);
  }
});
document.getElementById("upload-input").addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const img = document.createElement("img");
      img.src = e.target.result;
      const preview = document.getElementById("preview-container");
      preview.innerHTML = "";
      preview.appendChild(img);
    };
    reader.readAsDataURL(file);
  }
});

// Open image selector from TRY IT ON
document.getElementById("try-button").addEventListener("click", async () => {
  triggerSource = "tryon";
  openModelSelector();
});

// Open image selector from SELECT button for style transfer
document.getElementById("select-image-button").addEventListener("click", async () => {
  triggerSource = "styletransfer";
  openModelSelector();
});

async function openModelSelector() {
  const overlay = document.getElementById("image-select-overlay");
  const gallery = document.getElementById("image-gallery");
  overlay.style.display = "flex";
  gallery.innerHTML = "";

  try {
    const res = await fetch("/models");
    const data = await res.json();

    data.models.forEach((filename) => {
      const img = document.createElement("img");
      img.src = `/model-images/${filename}`;
      img.classList.add("image-option");

      img.addEventListener("click", () => {
        document.querySelectorAll(".image-option").forEach((el) =>
          el.classList.remove("selected")
        );
        img.classList.add("selected");
        selectedModel = filename;
      });

      gallery.appendChild(img);
    });
  } catch (err) {
    console.error("Failed to load model images:", err);
    gallery.innerHTML = `<p>Error loading model images</p>`;
  }
}

// Submit for either try-on or style transfer
document.getElementById("submit-selection").addEventListener("click", () => {
  const overlay = document.getElementById("image-select-overlay");
  const preview = document.getElementById("preview-container");

  if (!selectedModel) {
    alert("Please select a model image.");
    return;
  }

  overlay.style.display = "none";

  preview.innerHTML = `
    <div class="tryon-loader-wrapper">
      <div class="fancy-loader"></div>
      <p class="loader-text">${triggerSource === "styletransfer" ? "Blending your outfit..." : "Trying on your outfit..."} Please wait</p>
    </div>
  `;

  const endpoint = triggerSource === "styletransfer"
    ? "/styletransfer/selected"
    : "/tryon/selected";

  fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      person_id: selectedModel,
      cloth_id: clothFullId,
    }),
  })
    .then((res) => {
      if (!res.ok) throw new Error("Request failed");
      return res.blob();
    })
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      preview.innerHTML = "";
      const img = document.createElement("img");
      img.src = url;
      img.alt = "Result Image";
      preview.appendChild(img);
    })
    .catch((err) => {
      console.error(err);
      preview.innerHTML = `<p style='color:red;'>${triggerSource === "styletransfer" ? "Style transfer" : "Try-on"} failed. Please try again.</p>`;
    })
    .finally(() => {
      triggerSource = null;
    });
});

// Chatbot logic
const chatbotPopup = document.getElementById("chatbot-popup");
const chatbotClose = document.getElementById("chatbot-close");
const chatbotInput = document.getElementById("chatbot-input");
const chatbotSend = document.getElementById("chatbot-send");
const chatbotMessages = document.getElementById("chatbot-messages");

document.getElementById("style-button").addEventListener("click", () => {
  chatbotPopup.style.display = "flex";
});
chatbotClose.addEventListener("click", () => {
  chatbotPopup.style.display = "none";
});
function appendMessage(content, sender = "bot") {
  const msg = document.createElement("div");
  msg.classList.add("chatbot-message", sender);
  msg.textContent = content;
  chatbotMessages.appendChild(msg);
  chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}
chatbotSend.addEventListener("click", () => {
  const userMsg = chatbotInput.value.trim();
  if (!userMsg) return;

  appendMessage(userMsg, "user");
  chatbotInput.value = "";

  setTimeout(() => {
    let response = `🧠 Styling Advice:
 🎉🎉🎉 Vibe Summary: Bold & Glam Night Out 🌟

👖 Bottoms: Black leather pants (comfortable, slimming, and complement the outfit)
👟 Footwear: High heels (add height and confidence)
🧥 Outerwear: A statement blazer or shrug (add texture and style)
💄 Makeup: Bold lipstick, dramatic eyeshadow, and a smoky eye look (enhance the glam vibe)
💇 Hairstyle: Straight, sleek hair (match the vibe and practicality)
💍 Accessories: Earrings (add sparkle), a statement necklace (add drama), and a clutch (complete the look)

Remember to have fun and enjoy the night out! 🎉🎉🎉
`;
    // Chatbot could not be included due to system requirements, check fashio-bot.ipynb in the root dir for it's implementation

    const lower = userMsg.toLowerCase();

    if (lower.includes("recommend")) {
      response = "I recommend pairing it with bold earrings or a sleek blazer!";
    } else if (lower.includes("color")) {
      response = "Shades like lavender or dusty rose would work great 🌷";
    } else if (lower.includes("match")) {
      response = "Try matching it with beige pants or layered gold jewelry.";
    }

    appendMessage(response, "bot");
  }, 3000);
});
chatbotInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") chatbotSend.click();
});

document.getElementById("CR-button").addEventListener("click", async () => {
  const filters = {
    Category: ["Bodysuit/Leotard"],
    Pattern: ["Floral"],
    Colour: ["White"],
    Material: ["Mesh"],
    Occasion: ["Casual"],
    Season: ["Summer"],
    NeckType: ["Deep"],
    SleeveLength: ["Sleeveless"]
  };
  try {
    const res = await fetch("/custom_recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(filters),
    });

    const data = await res.json();
    const ids = data.recommendations || [];

    localStorage.setItem("customResults", JSON.stringify(ids));
    window.location.href = "home-page.html";
  } catch (err) {
    alert("Could not fetch custom recommendations.");
    console.error(err);
  }
});
