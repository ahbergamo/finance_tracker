document.addEventListener("DOMContentLoaded", function() {
    // Loop over each category select element to add event listener
    const selects = document.querySelectorAll("select[id^='category-select-']");
    selects.forEach(function(select) {
      const index = select.id.split("-").pop();
      const newCategoryInput = document.getElementById("new-category-" + index);
      
      // Show the new category input if "other" is initially selected
      if (select.value === "other") {
        newCategoryInput.style.display = "block";
        newCategoryInput.required = true;
      }
      
      select.addEventListener("change", function() {
        if (this.value === "other") {
          newCategoryInput.style.display = "block";
          newCategoryInput.required = true;
        } else {
          newCategoryInput.style.display = "none";
          newCategoryInput.required = false;
          newCategoryInput.value = "";
        }
      });
    });
  });
  