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

function showPersonPreview(url) {
  const box = document.getElementById("selected-image-1");
  box.style.backgroundImage = `url('${url}')`;
  box.style.backgroundSize = "cover";
  box.style.backgroundPosition = "center";
  box.textContent = "";
}

async function runTryOnWithPhoto(blob) {
  if (!clothFullId) {
    alert("No item selected to try on.");
    return;
  }
  const preview = document.getElementById("preview-container");
  preview.innerHTML = `
    <div class="tryon-loader-wrapper">
      <div class="fancy-loader"></div>
      <p class="loader-text">Trying on your outfit... Please wait</p>
    </div>
  `;

  const formData = new FormData();
  formData.append("person_img", blob, "person.jpg");
  formData.append("cloth_id", clothFullId);

  try {
    const res = await fetch("/vton", { method: "POST", body: formData });
    if (!res.ok) throw new Error("Request failed");
    const resultBlob = await res.blob();
    const url = URL.createObjectURL(resultBlob);
    preview.innerHTML = "";
    const img = document.createElement("img");
    img.src = url;
    img.alt = "Result Image";
    preview.appendChild(img);
  } catch (err) {
    console.error(err);
    preview.innerHTML = `<p style='color:red;'>Try-on failed. Please try again.</p>`;
  }
}

// Upload a photo of yourself for try-on
const fileInput = document.getElementById("upload-input");
document.getElementById("upload-photo-btn").addEventListener("click", () => {
  fileInput.click();
});
fileInput.addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (!file) return;
  selectedModel = null;
  showPersonPreview(URL.createObjectURL(file));
  runTryOnWithPhoto(file);
});

// Take a photo with the camera for try-on
let cameraStream = null;

async function openCamera() {
  const overlay = document.getElementById("camera-overlay");
  const video = document.getElementById("camera-video");
  const canvas = document.getElementById("camera-canvas");

  overlay.style.display = "flex";
  video.style.display = "block";
  canvas.style.display = "none";
  document.getElementById("camera-capture").style.display = "inline-block";
  document.getElementById("camera-retake").style.display = "none";
  document.getElementById("camera-use").style.display = "none";

  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
    video.srcObject = cameraStream;
  } catch (err) {
    console.error("Camera access failed:", err);
    alert("Couldn't access your camera. Check browser permissions and try again.");
    closeCamera();
  }
}

function closeCamera() {
  document.getElementById("camera-overlay").style.display = "none";
  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }
}

document.getElementById("camera-btn").addEventListener("click", openCamera);
document.getElementById("camera-cancel").addEventListener("click", closeCamera);

document.getElementById("camera-capture").addEventListener("click", () => {
  const video = document.getElementById("camera-video");
  const canvas = document.getElementById("camera-canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);

  video.style.display = "none";
  canvas.style.display = "block";
  document.getElementById("camera-capture").style.display = "none";
  document.getElementById("camera-retake").style.display = "inline-block";
  document.getElementById("camera-use").style.display = "inline-block";
});

document.getElementById("camera-retake").addEventListener("click", () => {
  document.getElementById("camera-video").style.display = "block";
  document.getElementById("camera-canvas").style.display = "none";
  document.getElementById("camera-capture").style.display = "inline-block";
  document.getElementById("camera-retake").style.display = "none";
  document.getElementById("camera-use").style.display = "none";
});

document.getElementById("camera-use").addEventListener("click", () => {
  const canvas = document.getElementById("camera-canvas");
  canvas.toBlob((blob) => {
    selectedModel = null;
    showPersonPreview(URL.createObjectURL(blob));
    closeCamera();
    runTryOnWithPhoto(blob);
  }, "image/jpeg", 0.92);
});

// Open image selector from PICK A MODEL
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
  if (!clothFullId) {
    alert("No item selected to base recommendations on.");
    return;
  }
  try {
    // Recommend items sharing attributes (colour, pattern, category, etc.)
    // with the garment currently being viewed.
    const res = await fetch(`/recommend/${encodeURIComponent(clothFullId)}`);
    if (!res.ok) throw new Error(`Request failed with status ${res.status}`);

    const data = await res.json();
    const ids = data.recommendations || [];

    localStorage.setItem("customResults", JSON.stringify(ids));
    window.location.href = "home-page.html";
  } catch (err) {
    alert("Could not fetch recommendations.");
    console.error(err);
  }
});
