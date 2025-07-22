const container = document.getElementById("search-results");
const items = JSON.parse(localStorage.getItem("searchResults")) || [];

if (items.length === 0) {
  container.innerHTML = "<p style='color:#a31967;'>No items found for your query.</p>";
} else {
  items.forEach(id => {
    const card = document.createElement("div");
    card.className = "result-card";

    const link = document.createElement("a");
    link.href = `cloth-page.html?id=${id.replace(".jpg", "")}`;

    const img = document.createElement("img");
    img.src = `images/${id}`;
    img.alt = id;

    const label = document.createElement("p");
    label.textContent = id;

    link.appendChild(img);
    card.appendChild(link);
    card.appendChild(label);
    container.appendChild(card);
  });
}

const prevQuery = localStorage.getItem("lastSearchQuery");
if (prevQuery) {
  const input = document.getElementById("search-input");
  if (input) input.value = prevQuery;
}
