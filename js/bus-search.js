/**
 * BUSMITRA - Bus Search & Route Navigation Module
 * Validates inputs, saves recent searches to LocalStorage, and routes queries.
 */

window.BUSMITRA_SEARCH = {
  RECENT_SEARCHES_KEY: "busmitra_recent_searches",

  init: function() {
    this.renderRecentSearches();
    this.setupListeners();
  },

  setupListeners: function() {
    const searchForm = document.getElementById("bus-search-form");
    if (searchForm) {
      searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        this.executeSearch();
      });
    }

    const swapBtn = document.getElementById("swap-locations-btn");
    if (swapBtn) {
      swapBtn.addEventListener("click", () => {
        const sourceInput = document.getElementById("source-input");
        const destInput = document.getElementById("dest-input");
        if (sourceInput && destInput) {
          const temp = sourceInput.value;
          sourceInput.value = destInput.value;
          destInput.value = temp;
          if (window.showToast) window.showToast("Locations swapped");
        }
      });
    }

    const clearDestBtn = document.getElementById("clear-dest-btn");
    if (clearDestBtn) {
      clearDestBtn.addEventListener("click", () => {
        const destInput = document.getElementById("dest-input");
        if (destInput) {
          destInput.value = "";
          destInput.focus();
        }
      });
    }
  },

  executeSearch: function() {
    const sourceInput = document.getElementById("source-input");
    const destInput = document.getElementById("dest-input");
    const errorEl = document.getElementById("search-error-msg");

    const source = sourceInput ? sourceInput.value.trim() : "";
    const destination = destInput ? destInput.value.trim() : "";

    if (!source) {
      this.showError("Please enter your departure bus stop or select current location.");
      if (sourceInput) sourceInput.focus();
      return;
    }

    if (!destination) {
      this.showError("Please enter your destination city or bus stop.");
      if (destInput) destInput.focus();
      return;
    }

    if (errorEl) errorEl.style.display = "none";

    // Save to Recent Searches
    this.addRecentSearch(source, destination);

    // Navigate to Available Buses page with query parameters
    const query = new URLSearchParams({
      from: source,
      to: destination
    }).toString();

    window.location.href = `buses.html?${query}`;
  },

  showError: function(msg) {
    const errorEl = document.getElementById("search-error-msg");
    if (errorEl) {
      errorEl.textContent = msg;
      errorEl.style.display = "block";
    }
    if (window.showToast) window.showToast(msg);
  },

  getRecentSearches: function() {
    try {
      const data = localStorage.getItem(this.RECENT_SEARCHES_KEY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      return [];
    }
  },

  addRecentSearch: function(from, to) {
    let searches = this.getRecentSearches();
    // Prevent duplicate adjacent
    searches = searches.filter(s => !(s.from.toLowerCase() === from.toLowerCase() && s.to.toLowerCase() === to.toLowerCase()));
    searches.unshift({ from, to, timestamp: Date.now() });
    // Keep max 5 recent searches
    if (searches.length > 5) searches = searches.slice(0, 5);
    localStorage.setItem(this.RECENT_SEARCHES_KEY, JSON.stringify(searches));
    this.renderRecentSearches();
  },

  renderRecentSearches: function() {
    const container = document.getElementById("recent-searches-list");
    if (!container) return;

    const searches = this.getRecentSearches();
    if (searches.length === 0) {
      container.innerHTML = `<p class="empty-hint text-muted" style="font-size:0.875rem;">No recent journeys yet. Search a route to save it here.</p>`;
      return;
    }

    container.innerHTML = searches.map(s => `
      <button class="recent-search-chip" onclick="BUSMITRA_SEARCH.applyRecent('${s.from.replace(/'/g, "\\'")}', '${s.to.replace(/'/g, "\\'")}')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        <span>${s.from} → ${s.to}</span>
      </button>
    `).join("");
  },

  applyRecent: function(from, to) {
    const sourceInput = document.getElementById("source-input");
    const destInput = document.getElementById("dest-input");
    if (sourceInput) sourceInput.value = from;
    if (destInput) destInput.value = to;
    this.executeSearch();
  },

  selectPopularDestination: function(destName) {
    const destInput = document.getElementById("dest-input");
    if (destInput) {
      destInput.value = destName;
    }
    const sourceInput = document.getElementById("source-input");
    if (sourceInput && !sourceInput.value.trim()) {
      sourceInput.value = "Vijayawada";
    }
    this.executeSearch();
  }
};

document.addEventListener("DOMContentLoaded", function() {
  if (document.getElementById("bus-search-form")) {
    window.BUSMITRA_SEARCH.init();
  }
});
