document.addEventListener("DOMContentLoaded", function() {
    const overrideCategorySelect = document.getElementById("override_category");
    const newCategoryDiv = document.getElementById("new-category-div");
  
    if (overrideCategorySelect && newCategoryDiv) {
      function toggleNewCategory() {
        newCategoryDiv.style.display = overrideCategorySelect.value === "other" ? "block" : "none";
      }
      overrideCategorySelect.addEventListener("change", toggleNewCategory);
      // Call once on load in case "other" is already selected.
      toggleNewCategory();
    }
  });
  