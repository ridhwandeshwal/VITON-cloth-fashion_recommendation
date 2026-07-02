function renderSearchResults(items) {
  const container = document.getElementById("search-results");
  container.innerHTML = "";

  if (!items || items.length === 0) {
    container.innerHTML = "<p style='color:#a31967;'>No items found for your query.</p>";
    return;
  }

  items.forEach(id => {
    const card = document.createElement("div");
    card.className = "result-card";

    const link = document.createElement("a");
    link.href = `cloth-page.html?id=${id.replace(".jpg", "")}`;

    // Container to handle image swap on hover
    const imageContainer = document.createElement("div");
    imageContainer.className = "image-container";

    const mainImg = document.createElement("img");
    mainImg.src = `images/${id}`;
    mainImg.alt = id;
    mainImg.className = "main-image";

    const hoverImg = document.createElement("img");
    hoverImg.src = `cloth/${id}`;
    hoverImg.alt = id;
    hoverImg.className = "hover-image";

    imageContainer.appendChild(mainImg);
    imageContainer.appendChild(hoverImg);
    link.appendChild(imageContainer);

    const label = document.createElement("p");
    label.textContent = id;

    card.appendChild(link);
    card.appendChild(label);
    container.appendChild(card);
  });
}

// Initial render from whatever the previous page stored.
renderSearchResults(JSON.parse(localStorage.getItem("searchResults")) || []);

const prevQuery = localStorage.getItem("lastSearchQuery");
if (prevQuery) {
  const input = document.getElementById("search-input");
  if (input) input.value = prevQuery;
}
