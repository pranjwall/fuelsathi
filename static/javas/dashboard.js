// Dashboard JavaScript for navigation and interactions

document.addEventListener('DOMContentLoaded', function() {
    // Navigation functionality
    const navLinks = document.querySelectorAll('.nav-link');
    const contentSections = document.querySelectorAll('.content-section');

    // Function to show section
    function showSection(sectionId) {
        // Hide all sections
        contentSections.forEach(section => {
            section.classList.remove('active');
        });

        // Remove active class from all nav links
        navLinks.forEach(link => {
            link.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(sectionId + '-section');
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Add active class to clicked nav link
        const activeLink = document.querySelector(`[data-section="${sectionId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    // Add click event listeners to nav links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('data-section');
            showSection(sectionId);

            // Close sidebar on mobile after navigation
            if (window.innerWidth <= 768) {
                const sidebar = document.querySelector('.sidebar');
                sidebar.classList.remove('open');
            }
        });
    });

    // Mobile sidebar toggle (if needed)
    function initMobileSidebar() {
        // Create hamburger menu button for mobile
        const mainContent = document.querySelector('.main-content');
        const hamburgerBtn = document.createElement('button');
        hamburgerBtn.className = 'hamburger-btn';
        hamburgerBtn.innerHTML = '<i class="fas fa-bars"></i>';
        hamburgerBtn.style.cssText = `
            position: fixed;
            top: 1rem;
            left: 1rem;
            z-index: 1001;
            background: #2b67ff;
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 8px;
            cursor: pointer;
            display: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;

        mainContent.appendChild(hamburgerBtn);

        // Show hamburger on mobile
        function toggleHamburger() {
            if (window.innerWidth <= 768) {
                hamburgerBtn.style.display = 'block';
            } else {
                hamburgerBtn.style.display = 'none';
                document.querySelector('.sidebar').classList.remove('open');
            }
        }

        toggleHamburger();
        window.addEventListener('resize', toggleHamburger);

        // Toggle sidebar on hamburger click
        hamburgerBtn.addEventListener('click', function() {
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.toggle('open');
        });
    }

    // Initialize mobile sidebar
    initMobileSidebar();

    // Settings functionality
    const emailCheckbox = document.getElementById('email');
    const smsCheckbox = document.getElementById('sms');

    if (emailCheckbox) {
        emailCheckbox.addEventListener('change', function() {
            // Handle email notifications setting
            console.log('Email notifications:', this.checked);
        });
    }

    if (smsCheckbox) {
        smsCheckbox.addEventListener('change', function() {
            // Handle SMS notifications setting
            console.log('SMS notifications:', this.checked);
        });
    }

    // Settings buttons
    const changePasswordBtn = document.querySelector('.btn-secondary:nth-child(1)');
    const twoFactorBtn = document.querySelector('.btn-secondary:nth-child(2)');

    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', function() {
            alert('Change password functionality would be implemented here');
        });
    }

    if (twoFactorBtn) {
        twoFactorBtn.addEventListener('click', function() {
            alert('Two-factor authentication setup would be implemented here');
        });
    }

    // Smooth scrolling for any anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading animation for section transitions
    function addLoadingAnimation() {
        const style = document.createElement('style');
        style.textContent = `
            .content-section {
                transition: opacity 0.3s ease-in-out;
            }
            .content-section:not(.active) {
                opacity: 0;
                pointer-events: none;
            }
            .content-section.active {
                opacity: 1;
                pointer-events: auto;
            }
        `;
        document.head.appendChild(style);
    }

    addLoadingAnimation();

    // Initialize dashboard with profile section active
    showSection('profile');
});
