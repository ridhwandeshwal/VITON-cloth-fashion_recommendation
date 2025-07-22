const categoriesContainer = document.querySelector('.categories');
const categories = document.querySelectorAll('.category');
const ratings = document.querySelectorAll('.rating');
let draggedItem = null;
let allQuizData = [];
// Handle drag 

console.log("yes")
function handleDragStart(e) {
    draggedItem = e.target;
    setTimeout(() => draggedItem.style.display = 'none', 0);
}

// Handle drag end
function handleDragEnd(e) {
    if (draggedItem) draggedItem.style.display = 'inline-block';
    draggedItem = null;
}

categories.forEach(item => {
    item.addEventListener('dragstart', handleDragStart);
    item.addEventListener('dragend', handleDragEnd);
});

// Allow drop
function allowDrop(e) {
    e.preventDefault();
}

function handleDrop(e) {
    e.preventDefault();
    if (draggedItem) {
        draggedItem.style.display = 'inline-block';
        e.currentTarget.appendChild(draggedItem);
    }
}

ratings.forEach(box => {
    box.addEventListener('dragover', allowDrop);
    box.addEventListener('drop', handleDrop);
});

categoriesContainer.addEventListener('dragover', allowDrop);
categoriesContainer.addEventListener('drop', handleDrop);

function goToNextPage() {
    const result = [];
    ratings.forEach(box => {
        const category = box.querySelector('.category');
        if (category) {
            result.push({
                category: category.textContent.trim(),
                rating: parseInt(box.dataset.rating)
            });
        }
    });

    // Store results
    const savedData = JSON.parse(localStorage.getItem('quizData') || '[]');
    savedData.push(result);
    localStorage.setItem('quizData', JSON.stringify(savedData));

    // Detect current quiz number from script or URL fallback
    const current = document.location.pathname.split('/').pop() || 'quiz1.html';

    const match = current.match(/quiz(\d+)\.html/);
    if (match) {
        const currentNum = parseInt(match[1]);
        const nextNum = currentNum + 1;
        const nextPage = `quiz${nextNum}.html`;

        // Forward to next quiz
        window.location.href = `/new/${nextPage}`;
    } else {
        // fallback: first page
        window.location.href = '/new/quiz1.html';
    }
}

// Submit
function submitRatings() {
    document.getElementById('loading-overlay').style.display = 'flex';

    const result = [];
    ratings.forEach(box => {
        const category = box.querySelector('.category');
        if (category) {
            result.push({
                category: category.textContent.trim(),
                rating: parseInt(box.dataset.rating)
            });
        }
    });

    const savedData = JSON.parse(localStorage.getItem('quizData') || '[]');
    savedData.push(result);
    localStorage.removeItem('quizData');

    const attributeMap = ["Category", "Colour", "Material", "Pattern", "Brand"];
    const formattedData = {};

    for (let i = 0; i < savedData.length; i++) {
        const entry = savedData[i];
        const attributeName = attributeMap[i] || `Attribute${i+1}`;
        const rankedValues = {};
        entry.forEach(item => {
            rankedValues[item.rating] = item.category;
        });
        formattedData[attributeName] = rankedValues;
    }

    fetch('/stylequiz/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formattedData)
    })
    .then(res => res.json())
    .then(data => {
        localStorage.setItem('recommendedClothIDs', JSON.stringify(data.recommendations));
        window.location.href = '/new/home-page.html';  // or just 'home-page.html' if on same folder
    })
    .catch(err => {
        console.error("Submission failed:", err);
        alert("Submission failed!");
    });
}
