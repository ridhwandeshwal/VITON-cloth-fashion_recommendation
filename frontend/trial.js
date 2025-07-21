const images = [
  { src: "00001_00.jpg", label: "ID:00001_00" },
  { src: "00002_00.jpg", label: "ID:00002_00" },
  { src: "00003_00.jpg", label: "ID:00003_00" },
  { src: "00005_00.jpg", label: "ID:00005_00" },
  { src: "00006_00.jpg", label: "ID:00006_00" },
  { src: "00008_00.jpg", label: "ID:00008_00" },
  { src: "00013_00.jpg", label: "ID:00013_00" },
  { src: "00017_00.jpg", label: "ID:00017_00" },
  { src: "00034_00.jpg", label: "ID:00034_00" },
  { src: "00035_00.jpg", label: "ID:00035_00" },
  { src: "00055_00.jpg", label: "ID:00055_00" },
  { src: "00057_00.jpg", label: "ID:00057_00" },
  { src: "00064_00.jpg", label: "ID:00064_00" },
  { src: "00067_00.jpg", label: "ID:00067_00" },
  { src: "00069_00.jpg", label: "ID:00069_00" },
  { src: "00071_00.jpg", label: "ID:00071_00" },
  { src: "00074_00.jpg", label: "ID:00074_00" },
  { src: "00075_00.jpg", label: "ID:00075_00" },
  // Add more filenames as you get them
];

let loadedCount = 0;
const batchSize = 12;

function loadImages() {
  const container = document.getElementById("recommendation-container");
  for (let i = loadedCount; i < loadedCount + batchSize && i < images.length; i++) {
    const card = document.createElement("div");
    card.className = "recommendation-card";

    const link = document.createElement("a");
    const id = images[i].src.replace('.jpg', '');
    link.href = `details.html?id=${id}`;
    link.style.textDecoration = 'none';
    link.style.color = 'inherit';

    const img = document.createElement("img");
    img.src =  "images/" + images[i].src;
    img.alt = images[i].label;

    const label = document.createElement("p");
    label.textContent = images[i].label;

    link.appendChild(img);
    link.appendChild(label);
    card.appendChild(link);
    container.appendChild(card);
  }
  loadedCount += batchSize;

  if (loadedCount >= images.length) {
    document.getElementById("load-more-button").style.display = "none";
  }
}

document.getElementById("load-more-button").addEventListener("click", loadImages);

// Initial load
loadImages();
