(function () {
  const toggle = document.getElementById("menuToggle");
  const sidebar = document.getElementById("sidebar");
  if (toggle && sidebar) {
    toggle.addEventListener("click", () => sidebar.classList.toggle("open"));
    document.addEventListener("click", (event) => {
      if (window.innerWidth <= 950 && sidebar.classList.contains("open") && !sidebar.contains(event.target) && event.target !== toggle) {
        sidebar.classList.remove("open");
      }
    });
  }

  const clientSelect = document.getElementById("id_cliente");
  const manualFields = document.getElementById("manualFields");
  if (clientSelect && manualFields) {
    const syncMode = () => manualFields.classList.toggle("hide-manual", Boolean(clientSelect.value));
    clientSelect.addEventListener("change", syncMode);
    syncMode();
  }
})();
