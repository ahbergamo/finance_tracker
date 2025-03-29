(function() {
    const savedTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-bs-theme", savedTheme);
    if (savedTheme === "dark") {
      const darkBg = getComputedStyle(document.documentElement).getPropertyValue('--dark-bg').trim();
      document.documentElement.style.backgroundColor = darkBg;
    }
  })();
  
  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-bs-theme");
    const newTheme = (currentTheme === "dark") ? "light" : "dark";
    document.documentElement.setAttribute("data-bs-theme", newTheme);
    localStorage.setItem("theme", newTheme);
  
    if (newTheme === "dark") {
      const darkBg = getComputedStyle(document.documentElement).getPropertyValue('--dark-bg').trim();
      document.documentElement.style.backgroundColor = darkBg;
    } else {
      document.documentElement.style.backgroundColor = "";
    }
  }
  
  window.toggleTheme = toggleTheme;
  