// cloth.js
function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

const id = getQueryParam("id");

if (id) {
  const box = document.getElementById("selected-image-1");  // this is your left panel box
  box.style.backgroundImage = `url('images/${id}.jpg')`;
  box.style.backgroundSize = "cover";
  box.style.backgroundPosition = "center";
} else {
  document.getElementById("selected-image-1").textContent = "No item selected.";
}


// Populate selected images from localStorage or any method
const button = document.getElementById("try-button");
const fileInput = document.getElementById("upload-input");

button.addEventListener("click", function () {
    fileInput.click(); // Simulate click on hidden input
        });

        // Optional: confirm image is selected
 fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
        alert("Image selected: " + fileInput.files[0].name);
            }
        });

// Show uploaded user image
document.getElementById('upload-input').addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            const preview = document.getElementById('preview-container');
            preview.innerHTML = ''; // clear previous image
            preview.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
});

// Chatbot logic
const chatbotPopup = document.getElementById('chatbot-popup');
const chatbotClose = document.getElementById('chatbot-close');
const chatbotInput = document.getElementById('chatbot-input');
const chatbotSend = document.getElementById('chatbot-send');
const chatbotMessages = document.getElementById('chatbot-messages');

// Open chatbot on "STYLE-IT!" button click
document.getElementById('style-button').addEventListener('click', () => {
  chatbotPopup.style.display = 'flex';
});

// Close popup
chatbotClose.addEventListener('click', () => {
  chatbotPopup.style.display = 'none';
});

// Append a message
function appendMessage(content, sender = 'bot') {
  const msg = document.createElement('div');
  msg.classList.add('chatbot-message', sender);
  msg.textContent = content;
  chatbotMessages.appendChild(msg);
  chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

// Handle send
chatbotSend.addEventListener('click', () => {
  const userMsg = chatbotInput.value.trim();
  if (!userMsg) return;

  appendMessage(userMsg, 'user');
  chatbotInput.value = '';

  // Simulated response
  setTimeout(() => {
    let response = "Interesting choice!";
    const lower = userMsg.toLowerCase();

    if (lower.includes("recommend")) {
      response = "I recommend pairing it with bold earrings or a sleek blazer!";
    } else if (lower.includes("color")) {
      response = "Shades like lavender or dusty rose would work great 🌷";
    } else if (lower.includes("match")) {
      response = "Try matching it with beige pants or layered gold jewelry.";
    }

    appendMessage(response, 'bot');
  }, 600);
});

// Send on Enter key
chatbotInput.addEventListener('keypress', e => {
  if (e.key === 'Enter') chatbotSend.click();
});

document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("image-select-overlay");
  const openBtn = document.getElementById("select-image-button");
  const submitBtn = document.getElementById("submit-selection");
  const gallery = document.getElementById("image-gallery");
  let selectedImage = null;

  const imageFilenames = [
    "00001_00.jpg", "00002_00.jpg", "00003_00.jpg",
    "00005_00.jpg", "00006_00.jpg", "00008_00.jpg",
    "00013_00.jpg", "00017_00.jpg", "00034_00.jpg",
    // Add more as needed
  ];

  openBtn.addEventListener("click", () => {
    overlay.style.display = "flex";
    gallery.innerHTML = ""; // clear previous content

    imageFilenames.forEach(filename => {
      const img = document.createElement("img");
      img.src = `images/${filename}`;
      img.classList.add("image-option");
      img.addEventListener("click", () => {
        document.querySelectorAll(".image-option").forEach(el => el.classList.remove("selected"));
        img.classList.add("selected");
        selectedImage = filename;
      });
      gallery.appendChild(img);
    });
  });

  submitBtn.addEventListener("click", () => {
    if (!selectedImage) {
      alert("Please select an image first!");
      return;
    }

    overlay.style.display = "none";
    console.log("Selected image:", selectedImage); // you can process/store this next
    // You could e.g. save to localStorage, or display it in the UI
  });
});

document.getElementById("CR-button").addEventListener("click", () => {
  window.location.href = "home-page.html";
});