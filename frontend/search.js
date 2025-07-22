const items = [
  { image: "images/00001_00.jpg", label: "Floral Dress", link: "cloth-page.html?id=00001" },
  { image: "images/00002_00.jpg", label: "Pink Top", link: "cloth-page.html?id=00002" },
  { image: "images/00003_00.jpg", label: "Silk Shirt", link: "cloth-page.html?id=00003" },
  // Add more items here with different links
];

const container = document.getElementById("search-results");
items.forEach(item => {
  const card = document.createElement("div");
  card.className = "result-card";

  // Wrap image in a link
  const link = document.createElement("a");
  link.href = item.link;

  const img = document.createElement("img");
  img.src = item.image;
  img.alt = item.label;

  const label = document.createElement("p");
  label.textContent = item.label;

  link.appendChild(img);
  card.appendChild(link);
  card.appendChild(label);
  container.appendChild(card);
});

