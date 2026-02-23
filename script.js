// Hamburger Menu Toggle
function toggleMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    }
}

// Close menu when clicking on a link
function closeMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }
}

// Light/Dark Mode Toggle (Default is Dark)
function toggleDarkMode() {
    document.body.classList.toggle('light-mode');
    localStorage.setItem('lightMode', document.body.classList.contains('light-mode'));
}

function initTheme() {
    // Default is dark mode, so if light-mode is not in localStorage, it's dark
    if (localStorage.getItem('lightMode') === 'true') {
        document.body.classList.add('light-mode');
    }
}

// Image Lightbox
function initLightbox() {
    // Create overlay if not exists
    if (!document.getElementById('lightboxOverlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'lightboxOverlay';
        overlay.className = 'lightbox-overlay';
        overlay.innerHTML = '<span class="lightbox-close">&times;</span><img src="" alt="Preview">';
        document.body.appendChild(overlay);

        overlay.addEventListener('click', function() {
            overlay.classList.remove('active');
        });
    }

    // Delegate click on table images
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'IMG' && e.target.closest('table')) {
            const overlay = document.getElementById('lightboxOverlay');
            overlay.querySelector('img').src = e.target.src;
            overlay.classList.add('active');
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const overlay = document.getElementById('lightboxOverlay');
            if (overlay) overlay.classList.remove('active');
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initLightbox();
    
    // Add click handlers to all nav links to close menu
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', closeMenu);
    });
});
