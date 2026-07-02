// Custom search-suggestion dropdown shared by every page that has the header
// search box. Replaces the native <datalist> (which looked plain and also let
// the browser mix in the user's own cached search history) with a styled,
// self-contained list of curated example searches.
(function () {
  const input = document.getElementById("search-input");
  const button = document.getElementById("search-button");
  const wrap = input && input.closest(".header-search");
  if (!input || !wrap) return;

  const SUGGESTIONS = [
    "Adidas T-shirts",
    "Floral dress",
    "Black Sequin tops",
    "Mesh tops",
    "Puma tops",
  ];

  const dropdown = document.createElement("div");
  dropdown.className = "search-suggestions";
  dropdown.innerHTML = '<p class="search-suggestions-label">Search suggestions</p>';
  const list = document.createElement("div");
  list.className = "search-suggestions-list";
  dropdown.appendChild(list);
  wrap.appendChild(dropdown);

  function render() {
    const q = input.value.trim().toLowerCase();
    const matches = SUGGESTIONS.filter((s) => s.toLowerCase().includes(q));
    list.innerHTML = "";

    if (!matches.length) {
      dropdown.classList.remove("open");
      return;
    }

    matches.forEach((text) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "search-suggestion";
      item.innerHTML = `<i class="fas fa-magnifying-glass"></i><span></span>`;
      item.querySelector("span").textContent = text;

      // mousedown (not click) so the pick registers before the input blurs.
      item.addEventListener("mousedown", (e) => {
        e.preventDefault();
        input.value = text;
        dropdown.classList.remove("open");
        if (button) button.click();
      });

      list.appendChild(item);
    });

    dropdown.classList.add("open");
  }

  input.addEventListener("focus", render);
  input.addEventListener("input", render);
  input.addEventListener("blur", () => {
    setTimeout(() => dropdown.classList.remove("open"), 120);
  });
})();
