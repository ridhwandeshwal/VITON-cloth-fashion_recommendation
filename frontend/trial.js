// Get recommended cloth IDs from localStorage or fallback list
const ids = JSON.parse(localStorage.getItem('recommendedClothIDs')) || [
  "00001_00.jpg", "00002_00.jpg", "00003_00.jpg"
];

// Build image objects
const images = ids.map(id => ({
  src: id,
  label: `ID:${id.replace('.jpg', '')}`
}));

let loadedCount = 0;
const batchSize = 12;

function loadImages() {
  const container = document.getElementById("recommendation-container");

  for (let i = loadedCount; i < loadedCount + batchSize && i < images.length; i++) {
    const card = document.createElement("div");
    card.className = "recommendation-card";

    const link = document.createElement("a");
    const id = images[i].src.replace('.jpg', '');
    link.href = `cloth-page.html?id=${id}`;
    link.style.textDecoration = 'none';
    link.style.color = 'inherit';

    const img = document.createElement("img");
    img.src = "images/" + images[i].src;
    img.alt = images[i].label;
    img.dataset.id = id; // save ID for swapping

    // Hover effect: change image source
    img.addEventListener("mouseenter", () => {
      img.src = "cloth/" + img.dataset.id + ".jpg";
    });

    img.addEventListener("mouseleave", () => {
      img.src = "images/" + img.dataset.id + ".jpg";
    });

    const label = document.createElement("p");
    label.textContent = images[i].label;

    link.appendChild(img);
    link.appendChild(label);
    card.appendChild(link);
    container.appendChild(card);
  }

  loadedCount += batchSize;

  if (loadedCount >= images.length) {
    const loadMoreBtn = document.getElementById("load-more-button");
    if (loadMoreBtn) loadMoreBtn.style.display = "none";
  }
}

document.getElementById("load-more-button").addEventListener("click", loadImages);

// Initial load
loadImages();

// // Optional: clear stored IDs after load
// window.addEventListener("beforeunload", () => {
//   localStorage.removeItem("recommendedClothIDs");
// });
