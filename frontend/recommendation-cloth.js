const scrollContainer = document.getElementById('recommendation-scroll');
const rawId = new URLSearchParams(window.location.search).get("id");
const clothId = rawId ? `${rawId}.jpg` : null;

if (clothId) {
  // Show loading message
  scrollContainer.innerHTML = `<div class="loading-message">Fetching recommendations...</div>`;

  fetch(`/recommend/${clothId}`)
    .then(res => res.json())
    .then(data => {
      const recommendedItems = data.recommendations;

      if (!recommendedItems || !Array.isArray(recommendedItems)) {
        throw new Error("Invalid recommendation format");
      }

      // Clear loading state
      scrollContainer.innerHTML = "";

      recommendedItems.forEach(itemId => {
        const cardLink = document.createElement('a');
        cardLink.href = `cloth-page.html?id=${itemId.replace(".jpg", "")}`;
        cardLink.className = 'card';

        const img = document.createElement('img');
        img.src = `images/${itemId}`;
        img.dataset.id = itemId.replace(".jpg", "");

        // Smooth swap to cloth image on hover
        img.addEventListener("mouseenter", () => {
          img.style.transition = "opacity 0.3s ease";
          img.src = `cloth/${img.dataset.id}.jpg`;
        });

        img.addEventListener("mouseleave", () => {
          img.style.transition = "opacity 0.3s ease";
          img.src = `images/${img.dataset.id}.jpg`;
        });

        const title = document.createElement('div');
        title.className = 'card-title';
        title.textContent = itemId;

        cardLink.appendChild(img);
        cardLink.appendChild(title);
        scrollContainer.appendChild(cardLink);
      });
    })
    .catch(err => {
      console.error("Error fetching recommendations:", err);
      scrollContainer.innerHTML = `<div class="loading-message">Failed to load recommendations.</div>`;
    });
}

// Scroll functionality
const scrollAmount = 250;

document.getElementById('scroll-right').addEventListener('click', () => {
  scrollContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
});

document.getElementById('scroll-left').addEventListener('click', () => {
  scrollContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
});
