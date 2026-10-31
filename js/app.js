/**
 * BUSMITRA - Core Application Framework & Shared Utilities
 * Manages global navigation, accessibility preferences, toasts, and demo state.
 */

// Toast notification helper
window.showToast = function(message, duration = 3200) {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22D3EE" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, duration);
};

// Application Init & Preference Loading
document.addEventListener("DOMContentLoaded", function() {
  // Load Accessibility Preferences
  const highContrast = localStorage.getItem("busmitra_high_contrast") === "true";
  if (highContrast) document.body.classList.add("high-contrast");

  const largeText = localStorage.getItem("busmitra_large_text") === "true";
  if (largeText) document.body.classList.add("large-text");

  // Mobile Menu Toggle
  const mobileToggle = document.getElementById("mobile-menu-btn");
  const navLinks = document.querySelector(".nav-links");
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener("click", () => {
      navLinks.classList.toggle("mobile-open");
    });
  }

  // Demo / Live Mode switcher
  const modeToggles = document.querySelectorAll(".mode-toggle-action");
  modeToggles.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const currentMode = window.BUSMITRA_API ? window.BUSMITRA_API.mode : "demo";
      const nextMode = currentMode === "demo" ? "live" : "demo";
      if (window.BUSMITRA_API) {
        window.BUSMITRA_API.setMode(nextMode);
      }
    });
  });

  // Apply translations
  if (window.applyTranslations) {
    window.applyTranslations();
  }
});
