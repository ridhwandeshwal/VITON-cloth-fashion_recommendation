const recommendedItems = [
  { image: "images/00001_00.jpg", title: "00001_00.jpg" },
  { image: "images/00002_00.jpg", title: "00002_00.jpg" },
  { image: "images/00003_00.jpg", title: "00003_00.jpg" },
  { image: "images/00005_00.jpg", title: "00005_00.jpg" },
  { image: "images/00006_00.jpg", title: "00006_00.jpg" },
  { image: "images/00008_00.jpg", title: "00008_00.jpg" },
  { image: "images/00008_00.jpg", title: "00008_00.jpg" },
  { image: "images/00008_00.jpg", title: "00008_00.jpg" },
  { image: "images/00008_00.jpg", title: "00008_00.jpg" },
  { image: "images/00008_00.jpg", title: "00008_00.jpg" },
  { image: "images/00008_00.jpg", title: "00008_00.jpg" }
  // Add more as needed
];

const scrollContainer = document.getElementById('recommendation-scroll');
function getImageId(imagePath) {
  const filename = imagePath.split('/').pop();        // "00001_00.jpg"
  return filename.replace('.jpg', '');                // "00001_00"
}

recommendedItems.forEach(item => {
  const cardLink = document.createElement('a');
  cardLink.href = `cloth-page.html?id=${getImageId(item.image)}`;
  cardLink.className = 'card';

  const img = document.createElement('img');
  img.src = item.image;

  const title = document.createElement('div');
  title.className = 'card-title';
  title.textContent = item.title;

  cardLink.appendChild(img);
  cardLink.appendChild(title);
  scrollContainer.appendChild(cardLink);
});

document.getElementById('scroll-right').addEventListener('click', () => {
  scrollContainer.scrollLeft += 200;
});

document.getElementById('scroll-left').addEventListener('click', () => {
  scrollContainer.scrollLeft -= 200;
});
