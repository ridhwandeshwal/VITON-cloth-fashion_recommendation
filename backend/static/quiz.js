const categoriesContainer = document.querySelector('.categories');
const categories = document.querySelectorAll('.category');
const ratings = document.querySelectorAll('.rating');
let draggedItem = null;
let allQuizData = [];
// Handle drag start
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

    // Get existing data or initialize
    const savedData = JSON.parse(localStorage.getItem('quizData') || '[]');
    savedData.push(result);
    localStorage.setItem('quizData', JSON.stringify(savedData));

    const currentPage = window.location.pathname;
    const base = currentPage.substring(0, currentPage.lastIndexOf('/'));
    
    const match = currentPage.match(/quiz(\d+)\.html$/);
    if (match) {
        const currentNum = parseInt(match[1]);
        const nextNum = currentNum + 1;
        window.location.href = `${base}/quiz${nextNum}.html`;
    }
}
// Submit
function submitRatings() {
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
    console.log(savedData); // <-- now logs full quiz data across all pages

    localStorage.removeItem('quizData'); // clear after submission

    // Send to server (uncomment when ready)
    // fetch('http://your-api-endpoint.com/submit', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify(savedData)
    // })
    // .then(res => res.json())
    // .then(data => alert('Submitted successfully!'))
    // .catch(err => alert('Submission failed.'));
}
