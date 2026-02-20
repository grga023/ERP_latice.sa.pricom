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

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    
    // Add click handlers to all nav links to close menu
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', closeMenu);
    });
});
