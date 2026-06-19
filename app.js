/**
 * SoulLanguages Avatar Gallery — App Logic
 * Handles data loading, filtering, lazy loading, and lightbox
 */

(function() {
  'use strict';

  // ——————————————————————————————————————————————————————————————————————
  // State
  // ——————————————————————————————————————————————————————————————————————
  let allImages = [];
  let currentFilter = 'all';
  let currentLightboxIndex = -1;
  let filteredImages = [];

  // ——————————————————————————————————————————————————————————————————————
  // DOM References
  // ——————————————————————————————————————————————————————————————————————
  const galleryGrid = document.getElementById('galleryGrid');
  const filterContainer = document.querySelector('.filter-controls');
  const noResults = document.getElementById('noResults');
  const lightbox = document.getElementById('lightbox');
  const lightboxImage = document.getElementById('lightboxImage');
  const lightboxTheme = document.getElementById('lightboxTheme');
  const lightboxPrompt = document.getElementById('lightboxPrompt');
  const lightboxClose = document.getElementById('lightboxClose');
  const lightboxPrev = document.getElementById('lightboxPrev');
  const lightboxNext = document.getElementById('lightboxNext');

  // ——————————————————————————————————————————————————————————————————————
  // Data Loading
  // ——————————————————————————————————————————————————————————————————————
  async function loadData() {
    try {
      const response = await fetch('assets/data.json');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      allImages = data.images || [];

      // Extract unique themes and sort them
      const themes = [...new Set(allImages.map(img => img.theme))].sort();

      // Build filter buttons
      buildFilterButtons(themes);

      // Initial render
      applyFilter('all');
    } catch (error) {
      console.error('Failed to load gallery data:', error);
      galleryGrid.innerHTML = '<p class="no-results">Failed to load gallery. Please try again later.</p>';
    }
  }

  // ——————————————————————————————————————————————————————————————————————
  // Filter Buttons
  // ——————————————————————————————————————————————————————————————————————
  function buildFilterButtons(themes) {
    // Clear existing buttons except "All"
    const allBtn = filterContainer.querySelector('[data-theme="all"]');
    filterContainer.innerHTML = '';
    filterContainer.appendChild(allBtn);

    themes.forEach(theme => {
      const btn = document.createElement('button');
      btn.className = 'filter-btn';
      btn.dataset.theme = theme;
      btn.setAttribute('aria-pressed', 'false');
      btn.textContent = capitalizeFirst(theme);
      filterContainer.appendChild(btn);
    });

    // Add click listeners
    filterContainer.addEventListener('click', handleFilterClick);
  }

  function handleFilterClick(event) {
    const btn = event.target.closest('.filter-btn');
    if (!btn) return;

    const theme = btn.dataset.theme;
    applyFilter(theme);
  }

  function applyFilter(theme) {
    currentFilter = theme;

    // Update active button state
    filterContainer.querySelectorAll('.filter-btn').forEach(btn => {
      const isActive = btn.dataset.theme === theme;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive);
    });

    // Filter images
    if (theme === 'all') {
      filteredImages = [...allImages];
    } else {
      filteredImages = allImages.filter(img => img.theme === theme);
    }

    // Render gallery
    renderGallery();
  }

  // ——————————————————————————————————————————————————————————————————————
  // Gallery Rendering
  // ——————————————————————————————————————————————————————————————————————
  function renderGallery() {
    if (filteredImages.length === 0) {
      galleryGrid.innerHTML = '';
      noResults.hidden = false;
      return;
    }

    noResults.hidden = true;
    galleryGrid.innerHTML = filteredImages.map((img, index) => createCardHTML(img, index)).join('');

    // Initialize lazy loading for new images
    initLazyLoading();

    // Add click listeners for lightbox
    galleryGrid.querySelectorAll('.card').forEach((card, index) => {
      card.addEventListener('click', () => openLightbox(index));
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openLightbox(index);
        }
      });
    });
  }

  function createCardHTML(img, index) {
    const themeDisplay = capitalizeFirst(img.theme);
    return `
      <article class="card" tabindex="0" role="listitem" data-index="${index}">
        <div class="card-image-wrapper">
          <img
            class="card-image loading"
            data-src="assets/images/${img.url}"
            data-index="${index}"
            alt="${themeDisplay} avatar: ${img.prompt.slice(0, 100)}"
            loading="lazy"
            width="600"
            height="600"
          >
          <div class="card-overlay">
            <span class="card-theme">${themeDisplay}</span>
          </div>
        </div>
        <div class="card-info">
          <p class="card-prompt">${img.prompt}</p>
        </div>
      </article>
    `;
  }

  // ——————————————————————————————————————————————————————————————————————
  // Lazy Loading (IntersectionObserver)
  // ——————————————————————————————————————————————————————————————————————
  function initLazyLoading() {
    if (!('IntersectionObserver' in window)) {
      // Fallback: load all images immediately
      document.querySelectorAll('.card-image[data-src]').forEach(img => {
        img.src = img.dataset.src;
        img.classList.remove('loading');
        img.classList.add('loaded');
      });
      return;
    }

    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.onload = () => {
            img.classList.remove('loading');
            img.classList.add('loaded');
          };
          img.onerror = () => {
            img.classList.remove('loading');
            img.alt = 'Failed to load image';
          };
          observer.unobserve(img);
        }
      });
    }, {
      rootMargin: '100px 0px',
      threshold: 0.01
    });

    document.querySelectorAll('.card-image[data-src]').forEach(img => {
      imageObserver.observe(img);
    });
  }

  // ——————————————————————————————————————————————————————————————————————
  // Lightbox
  // ——————————————————————————————————————————————————————————————————————
  function openLightbox(index) {
    currentLightboxIndex = index;
    updateLightboxContent();
    lightbox.hidden = false;
    // Force reflow for transition
    requestAnimationFrame(() => {
      lightbox.classList.add('active');
    });
    document.body.style.overflow = 'hidden';

    // Focus trap
    lightboxClose.focus();

    // Keyboard navigation
    document.addEventListener('keydown', handleLightboxKeydown);
  }

  function closeLightbox() {
    lightbox.classList.remove('active');
    document.body.style.overflow = '';

    setTimeout(() => {
      lightbox.hidden = true;
    }, 250);

    document.removeEventListener('keydown', handleLightboxKeydown);
  }

  function handleLightboxKeydown(e) {
    switch (e.key) {
      case 'Escape':
        closeLightbox();
        break;
      case 'ArrowLeft':
        navigateLightbox(-1);
        break;
      case 'ArrowRight':
        navigateLightbox(1);
        break;
      case 'Tab':
        // Simple focus trap
        if (e.shiftKey && document.activeElement === lightboxClose) {
          e.preventDefault();
          lightboxNext.focus();
        } else if (!e.shiftKey && document.activeElement === lightboxNext) {
          e.preventDefault();
          lightboxClose.focus();
        }
        break;
    }
  }

  function navigateLightbox(direction) {
    const newIndex = currentLightboxIndex + direction;
    if (newIndex >= 0 && newIndex < filteredImages.length) {
      currentLightboxIndex = newIndex;
      updateLightboxContent();
    }
  }

  function updateLightboxContent() {
    const img = filteredImages[currentLightboxIndex];
    if (!img) return;

    lightboxImage.src = `assets/images/${img.url}`;
    lightboxImage.alt = `${capitalizeFirst(img.theme)} avatar: ${img.prompt}`;
    lightboxTheme.textContent = capitalizeFirst(img.theme);
    lightboxPrompt.textContent = img.prompt;
  }

  // ——————————————————————————————————————————————————————————————————————
  // Event Listeners (Lightbox)
  // ——————————————————————————————————————————————————————————————————————
  lightboxClose.addEventListener('click', closeLightbox);
  lightboxPrev.addEventListener('click', () => navigateLightbox(-1));
  lightboxNext.addEventListener('click', () => navigateLightbox(1));

  // Click outside to close
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
      closeLightbox();
    }
  });

  // ——————————————————————————————————————————————————————————————————————
  // Utility
  // ——————————————————————————————————————————————————————————————————————
  function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // ——————————————————————————————————————————————————————————————————————
  // Initialize
  // ——————————————————————————————————————————————————————————————————————
  document.addEventListener('DOMContentLoaded', loadData);
})();