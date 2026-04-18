/**
 * POCKET LAWYER 2.0 — Main Application Script (Landing Page)
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Navbar Scroll Behavior
    const nav = document.getElementById('main-nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });

    // 2. Mobile Menu Toggle
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.getElementById('nav-links');
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }

    // 3. Counter Animation for Hero Stats
    const stats = document.querySelectorAll('.stat-number[data-count]');
    
    const animateCounter = (el) => {
        const countAttr = el.getAttribute('data-count');
        if (!countAttr) return; // Don't animate non-numeric stats
        
        const target = parseInt(countAttr);
        const isPercent = el.innerText.includes('%');
        let current = 0;
        const duration = 2000; // 2 seconds
        const stepTime = Math.abs(Math.floor(duration / target));
        
        const timer = setInterval(() => {
            current += 1;
            el.innerText = current + (isPercent ? '%' : '');
            if (current >= target) {
                clearInterval(timer);
                el.innerText = target + (isPercent ? '%' : '');
            }
        }, stepTime);
    };

    // Trigger animation when visible
    const observerOptions = { threshold: 0.5 };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    stats.forEach(s => observer.observe(s));
});
