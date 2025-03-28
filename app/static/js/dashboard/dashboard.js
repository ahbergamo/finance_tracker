document.addEventListener("DOMContentLoaded", function() {
    // --- Dashboard Settings (Toggles & Save) ---
    const defaultSettings = {
      "card-monthlyCombined": true,
      "card-monthlyNet": true,
      "card-expenseCategoriesChart": true,
      "card-incomeCategoriesChart": true,
      "card-incomeCategoriesList": true,
      "card-expenseCategoriesList": true,
      "card-budgetActual": true,
      "card-recentTransactions": true,
      "card-cashFlow": true
    };
  
    // Retrieve saved settings or use defaults
    const settings = JSON.parse(localStorage.getItem("dashboardSettings")) || defaultSettings;
    Object.keys(settings).forEach(function(cardId) {
      const card = document.getElementById(cardId);
      if (card) {
        card.style.display = settings[cardId] ? "block" : "none";
      }
    });
    
    // Set the toggle switches based on saved settings
    document.querySelectorAll(".dashboard-toggle").forEach(function(toggle) {
      const cardId = toggle.getAttribute("data-card");
      toggle.checked = (settings[cardId] !== undefined) ? settings[cardId] : defaultSettings[cardId];
    });
    
    // Save new settings when the "Save Changes" button is clicked
    const saveButton = document.getElementById("saveDashboardSettings");
    if (saveButton) {
      saveButton.addEventListener("click", function() {
        const toggles = document.querySelectorAll(".dashboard-toggle");
        const newSettings = {};
        toggles.forEach(function(toggle) {
          newSettings[toggle.getAttribute("data-card")] = toggle.checked;
        });
        localStorage.setItem("dashboardSettings", JSON.stringify(newSettings));
        Object.keys(newSettings).forEach(function(cardId) {
          const card = document.getElementById(cardId);
          if (card) {
            card.style.display = newSettings[cardId] ? "block" : "none";
          }
        });
      });
    }
  
    // --- Dashboard Cards Sorting using Sortable ---
    const container = document.getElementById("dashboardContainer");
    if (container) {
      // Assumes Sortable is loaded via CDN or elsewhere before this script
      const sortable = new Sortable(container, {
        animation: 150,
        handle: '.drag-handle',
        onEnd: function(evt) {
          const orderedIDs = Array.from(container.children).map(card => card.id);
          localStorage.setItem("dashboardOrder", JSON.stringify(orderedIDs));
        }
      });
  
      // Apply saved order from localStorage if available
      const savedOrder = JSON.parse(localStorage.getItem("dashboardOrder") || "[]");
      if (savedOrder.length) {
        savedOrder.forEach(id => {
          if (!id) return;
          const card = document.getElementById(id);
          if (card) {
            container.appendChild(card);
          }
        });
      }
    }
  });
  