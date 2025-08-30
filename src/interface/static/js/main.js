// Finshield Main JavaScript File
// This file contains common functionality used across all pages

class FinshieldUI {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupFormValidation();
        this.initializeTooltips();
        this.setupProgressBars();
    }

    setupEventListeners() {
        // Mobile menu toggle
        const mobileMenuButton = document.querySelector('.mobile-menu-button');
        const mobileMenu = document.querySelector('.mobile-menu');

        if (mobileMenuButton && mobileMenu) {
            mobileMenuButton.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
                this.animateMenuIcon(mobileMenuButton);
            });
        }

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Close modals on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

        // Close modals on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.closeAllModals();
            }
        });
    }

    animateMenuIcon(button) {
        const icon = button.querySelector('svg');
        if (icon) {
            icon.style.transform = 'rotate(90deg)';
            setTimeout(() => {
                icon.style.transform = 'rotate(0deg)';
            }, 200);
        }
    }

    initializeAnimations() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fadeInUp');
                }
            });
        }, observerOptions);

        // Observe elements with animation class
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });

        // Parallax effect for hero sections
        window.addEventListener('scroll', this.handleParallax.bind(this));
    }

    handleParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');

        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }

    setupFormValidation() {
        // Real-time form validation
        const forms = document.querySelectorAll('form');

        forms.forEach(form => {
            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

            inputs.forEach(input => {
                // Validate on blur
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });

                // Clear validation on focus
                input.addEventListener('focus', () => {
                    this.clearFieldValidation(input);
                });
            });

            // Form submission handling
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showFormErrors(form);
                } else {
                    this.showLoadingState(form);
                }
            });
        });
    }

    validateField(field) {
        const isValid = field.checkValidity();
        const errorElement = this.getOrCreateErrorElement(field);

        if (!isValid) {
            field.classList.add('border-red-500', 'bg-red-50');
            field.classList.remove('border-gray-300');
            errorElement.textContent = field.validationMessage;
            errorElement.classList.remove('hidden');
        } else {
            field.classList.remove('border-red-500', 'bg-red-50');
            field.classList.add('border-green-500', 'bg-green-50');
            errorElement.classList.add('hidden');
        }

        return isValid;
    }

    clearFieldValidation(field) {
        field.classList.remove('border-red-500', 'bg-red-50', 'border-green-500', 'bg-green-50');
        field.classList.add('border-gray-300');

        const errorElement = field.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.classList.add('hidden');
        }
    }

    getOrCreateErrorElement(field) {
        let errorElement = field.parentNode.querySelector('.field-error');

        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error text-red-500 text-sm mt-1 hidden';
            field.parentNode.appendChild(errorElement);
        }

        return errorElement;
    }

    validateForm(form) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isFormValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isFormValid = false;
            }
        });

        return isFormValid;
    }

    showFormErrors(form) {
        // Scroll to first error
        const firstError = form.querySelector('.border-red-500');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }

        // Show toast notification
        this.showToast('Please correct the highlighted errors', 'error');
    }

    showLoadingState(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            const originalText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = `
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
            `;

            // Reset after timeout (fallback)
            setTimeout(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }, 10000);
        }
    }

    initializeTooltips() {
        // Initialize tooltips for elements with data-tooltip attribute
        const tooltipElements = document.querySelectorAll('[data-tooltip]');

        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.dataset.tooltip);
            });

            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(element, text) {
        // Remove existing tooltip
        this.hideTooltip();

        const tooltip = document.createElement('div');
        tooltip.className = 'absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg tooltip-element';
        tooltip.textContent = text;
        tooltip.id = 'current-tooltip';

        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();

        // Position tooltip above element
        tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltipRect.width / 2)}px`;
        tooltip.style.top = `${rect.top - tooltipRect.height - 8}px`;

        // Add arrow
        const arrow = document.createElement('div');
        arrow.className = 'absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900';
        tooltip.appendChild(arrow);

        // Fade in
        tooltip.style.opacity = '0';
        tooltip.style.transform = 'translateY(10px)';
        setTimeout(() => {
            tooltip.style.opacity = '1';
            tooltip.style.transform = 'translateY(0)';
            tooltip.style.transition = 'all 0.2s ease';
        }, 10);
    }

    hideTooltip() {
        const tooltip = document.getElementById('current-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    setupProgressBars() {
        // Animate progress bars when they come into view
        const progressBars = document.querySelectorAll('.progress-bar');

        const progressObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressFill = entry.target.querySelector('.progress-fill');
                    const targetWidth = progressFill.dataset.width || '0%';

                    setTimeout(() => {
                        progressFill.style.width = targetWidth;
                    }, 200);
                }
            });
        });

        progressBars.forEach(bar => {
            progressObserver.observe(bar);
        });
    }

    // Modal management
    closeAllModals() {
        const modals = document.querySelectorAll('.modal-backdrop');
        modals.forEach(modal => {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        });
    }

    // Toast notifications
    showToast(message, type = 'info', duration = 5000) {
        // Remove existing toast
        const existingToast = document.getElementById('current-toast');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.id = 'current-toast';
        toast.className = `fixed top-4 right-4 z-50 max-w-sm p-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full ${this.getToastClasses(type)}`;

        toast.innerHTML = `
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    ${this.getToastIcon(type)}
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <div class="ml-4 flex-shrink-0 flex">
                    <button onclick="finshieldUI.hideToast()" class="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(toast);

        // Slide in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // Auto hide
        if (duration > 0) {
            setTimeout(() => {
                this.hideToast();
            }, duration);
        }
    }

    hideToast() {
        const toast = document.getElementById('current-toast');
        if (toast) {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    }

    getToastClasses(type) {
        const classes = {
            success: 'bg-green-50 border border-green-200 text-green-800',
            error: 'bg-red-50 border border-red-200 text-red-800',
            warning: 'bg-yellow-50 border border-yellow-200 text-yellow-800',
            info: 'bg-blue-50 border border-blue-200 text-blue-800'
        };
        return classes[type] || classes.info;
    }

    getToastIcon(type) {
        const icons = {
            success: '<svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
            error: '<svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
            warning: '<svg class="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path></svg>',
            info: '<svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
        };
        return icons[type] || icons.info;
    }

    // Utility functions
    formatCurrency(amount, currency = 'INR') {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0
        }).format(amount);
    }

    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        return new Intl.DateTimeFormat('en-IN', {...defaultOptions, ...options}).format(new Date(date));
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // API utilities
    async apiCall(endpoint, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = {...defaultOptions, ...options};

        try {
            const response = await fetch(endpoint, config);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            this.showToast('Network error. Please try again.', 'error');
            throw error;
        }
    }

    // Local storage utilities
    setStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.warn('Failed to save to localStorage:', error);
        }
    }

    getStorage(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.warn('Failed to read from localStorage:', error);
            return null;
        }
    }

    removeStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.warn('Failed to remove from localStorage:', error);
        }
    }

    // Performance monitoring
    performanceLog(label, fn) {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        console.log(`${label}: ${end - start} milliseconds`);
        return result;
    }

    // Error handling
    handleError(error, context = 'Unknown') {
        console.error(`Error in ${context}:`, error);

        // Show user-friendly message
        let message = 'Something went wrong. Please try again.';

        if (error.message) {
            if (error.message.includes('network') || error.message.includes('fetch')) {
                message = 'Network error. Please check your connection.';
            } else if (error.message.includes('timeout')) {
                message = 'Request timed out. Please try again.';
            }
        }

        this.showToast(message, 'error');
    }
}

// Initialize Finshield UI when DOM is loaded
let finshieldUI;

document.addEventListener('DOMContentLoaded', () => {
    finshieldUI = new FinshieldUI();

    // Add global error handler
    window.addEventListener('error', (e) => {
        finshieldUI.handleError(e.error, 'Global');
    });

    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (e) => {
        finshieldUI.handleError(e.reason, 'Promise');
    });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FinshieldUI;
}