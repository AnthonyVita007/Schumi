/**
 * Driver Management System - Main JavaScript
 * 
 * This file contains the core JavaScript functionality for the application,
 * including API communication, UI interactions, and utility functions.
 * 
 * Author: Schumi Development Team
 * Date: 2024
 */

// ===== GLOBAL VARIABLES =====
let isLoading = false;
let flashMessageTimeout = null;

// ===== APPLICATION INITIALIZATION =====

/**
 * Initialize the application
 * Called when the DOM is fully loaded
 */
function initializeApp() {
    console.log('🚗 Driver Management System - Initializing...');
    
    // Set up global event listeners
    setupGlobalEventListeners();
    
    // Initialize mobile menu
    initializeMobileMenu();
    
    // Check for API health
    checkApiHealth();
    
    console.log('✅ Application initialized successfully');
}

/**
 * Set up global event listeners
 */
function setupGlobalEventListeners() {
    // Handle mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    }
    
    // Handle escape key for modals
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeAllModals();
        }
    });
    
    // Handle clicks outside modals
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal-overlay')) {
            const modal = event.target.closest('.modal');
            if (modal) {
                closeModal(modal);
            }
        }
    });
}

// ===== MOBILE MENU =====

/**
 * Initialize mobile menu functionality
 */
function initializeMobileMenu() {
    const mobileNav = document.getElementById('mobileNav');
    if (mobileNav) {
        // Close mobile menu when clicking on links
        const mobileLinks = mobileNav.querySelectorAll('.mobile-nav-link');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                toggleMobileMenu();
            });
        });
    }
}

/**
 * Toggle mobile menu visibility
 */
function toggleMobileMenu() {
    const mobileNav = document.getElementById('mobileNav');
    const menuBtn = document.querySelector('.mobile-menu-btn');
    
    if (mobileNav && menuBtn) {
        const isOpen = mobileNav.classList.contains('active');
        
        if (isOpen) {
            mobileNav.classList.remove('active');
            menuBtn.classList.remove('active');
        } else {
            mobileNav.classList.add('active');
            menuBtn.classList.add('active');
        }
    }
}

// ===== API COMMUNICATION =====

/**
 * Make an API request with error handling
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} - Response data
 */
async function apiRequest(url, options = {}) {
    try {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        // Merge options, excluding Content-Type for FormData
        const mergedOptions = {
            ...defaultOptions,
            ...options
        };
        
        // Remove Content-Type for FormData requests
        if (options.body instanceof FormData) {
            delete mergedOptions.headers['Content-Type'];
        }
        
        const response = await fetch(url, mergedOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Check API health status
 */
async function checkApiHealth() {
    try {
        const response = await apiRequest('/api/health');
        if (response.success) {
            console.log('✅ API is healthy:', response.message);
        }
    } catch (error) {
        console.error('❌ API health check failed:', error);
        showFlashMessage('Attenzione: problemi di connessione con il server', 'warning');
    }
}

// ===== LOADING STATES =====

/**
 * Show or hide global loading overlay
 * @param {boolean} show - Whether to show the loading overlay
 */
function showLoading(show = true) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        if (show) {
            overlay.classList.remove('hidden');
            isLoading = true;
        } else {
            overlay.classList.add('hidden');
            isLoading = false;
        }
    }
}

/**
 * Show button loading state
 * @param {HTMLElement} button - Button element
 * @param {boolean} loading - Whether button is in loading state
 * @param {string} loadingText - Text to show during loading
 */
function setButtonLoading(button, loading, loadingText = 'Caricamento...') {
    if (!button) return;
    
    const originalText = button.dataset.originalText || button.textContent;
    
    if (loading) {
        button.dataset.originalText = originalText;
        button.disabled = true;
        button.innerHTML = `
            <div class="spinner-small"></div>
            ${loadingText}
        `;
    } else {
        button.disabled = false;
        button.textContent = originalText;
        delete button.dataset.originalText;
    }
}

// ===== FLASH MESSAGES =====

/**
 * Show a flash message to the user
 * @param {string} message - Message to display
 * @param {string} type - Message type (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds (0 for persistent)
 */
function showFlashMessage(message, type = 'info', duration = 5000) {
    const container = document.getElementById('flashMessages');
    if (!container) {
        console.warn('Flash messages container not found');
        return;
    }
    
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.className = `flash-message ${type}`;
    messageElement.innerHTML = `
        <div class="flash-content">
            <p>${message}</p>
        </div>
        <button class="flash-close" onclick="closeFlashMessage(this)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
    `;
    
    // Add to container
    container.appendChild(messageElement);
    
    // Auto-close after duration
    if (duration > 0) {
        setTimeout(() => {
            closeFlashMessage(messageElement.querySelector('.flash-close'));
        }, duration);
    }
}

/**
 * Close a flash message
 * @param {HTMLElement} closeButton - Close button element
 */
function closeFlashMessage(closeButton) {
    const message = closeButton.closest('.flash-message');
    if (message) {
        message.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            message.remove();
        }, 300);
    }
}

// ===== MODAL MANAGEMENT =====

/**
 * Open a modal
 * @param {string} modalId - ID of the modal to open
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Focus first input if available
        const firstInput = modal.querySelector('input, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

/**
 * Close a modal
 * @param {HTMLElement|string} modal - Modal element or ID
 */
function closeModal(modal) {
    let modalElement;
    
    if (typeof modal === 'string') {
        modalElement = document.getElementById(modal);
    } else {
        modalElement = modal;
    }
    
    if (modalElement) {
        modalElement.classList.add('hidden');
        document.body.style.overflow = 'auto';
        
        // Reset forms in modal
        const forms = modalElement.querySelectorAll('form');
        forms.forEach(form => {
            form.reset();
            clearFormErrors(form);
        });
    }
}

/**
 * Close all open modals
 */
function closeAllModals() {
    const openModals = document.querySelectorAll('.modal:not(.hidden)');
    openModals.forEach(modal => {
        closeModal(modal);
    });
}

// ===== FORM HANDLING =====

/**
 * Clear form validation errors
 * @param {HTMLElement} form - Form element
 */
function clearFormErrors(form) {
    if (!form) return;
    
    const errorElements = form.querySelectorAll('.form-error');
    errorElements.forEach(element => {
        element.textContent = '';
        element.classList.remove('visible');
    });
    
    const inputElements = form.querySelectorAll('.form-input, .form-select');
    inputElements.forEach(element => {
        element.classList.remove('error');
    });
}

/**
 * Show form field error
 * @param {string} fieldName - Name of the field
 * @param {string} message - Error message
 * @param {HTMLElement} form - Form element (optional)
 */
function showFormError(fieldName, message, form = null) {
    const container = form || document;
    const errorElement = container.querySelector(`#${fieldName}Error`);
    const inputElement = container.querySelector(`[name="${fieldName}"]`);
    
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('visible');
    }
    
    if (inputElement) {
        inputElement.classList.add('error');
    }
}

/**
 * Validate form field
 * @param {HTMLElement} field - Input field element
 * @returns {boolean} - Whether field is valid
 */
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    const fieldType = field.type;
    
    // Clear previous errors
    const form = field.closest('form');
    const errorElement = form?.querySelector(`#${fieldName}Error`);
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.remove('visible');
    }
    field.classList.remove('error');
    
    // Required field validation
    if (field.required && !value) {
        showFormError(fieldName, 'Questo campo è obbligatorio', form);
        return false;
    }
    
    // Specific field validations
    switch (fieldType) {
        case 'email':
            if (value && !isValidEmail(value)) {
                showFormError(fieldName, 'Inserisci un indirizzo email valido', form);
                return false;
            }
            break;
            
        case 'file':
            if (field.files.length > 0) {
                const file = field.files[0];
                if (field.accept && !field.accept.includes(file.type) && 
                    !field.accept.includes('.' + file.name.split('.').pop())) {
                    showFormError(fieldName, 'Tipo di file non supportato', form);
                    return false;
                }
                
                // Check file size (16MB limit)
                if (file.size > 16 * 1024 * 1024) {
                    showFormError(fieldName, 'Il file è troppo grande (max 16MB)', form);
                    return false;
                }
            }
            break;
            
        case 'text':
            // Name fields validation
            if (fieldName.includes('Name') && value.length < 2) {
                showFormError(fieldName, 'Deve contenere almeno 2 caratteri', form);
                return false;
            }
            break;
    }
    
    return true;
}

/**
 * Validate entire form
 * @param {HTMLElement} form - Form element
 * @returns {boolean} - Whether form is valid
 */
function validateForm(form) {
    if (!form) return false;
    
    let isValid = true;
    const fields = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// ===== UTILITY FUNCTIONS =====

/**
 * Check if email is valid
 * @param {string} email - Email address to validate
 * @returns {boolean} - Whether email is valid
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Format file size in human readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} - Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Format duration in human readable format
 * @param {number} seconds - Duration in seconds
 * @returns {string} - Formatted duration
 */
function formatDuration(seconds) {
    if (seconds < 60) {
        return `${Math.round(seconds)}s`;
    } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.round(seconds % 60);
        return `${minutes}m ${remainingSeconds}s`;
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
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

/**
 * Throttle function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} - Throttled function
 */
function throttle(func, limit) {
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

/**
 * Generate a random ID
 * @param {number} length - Length of the ID
 * @returns {string} - Random ID
 */
function generateId(length = 8) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} - Whether copy was successful
 */
async function copyToClipboard(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            return true;
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            const successful = document.execCommand('copy');
            textArea.remove();
            return successful;
        }
    } catch (error) {
        console.error('Failed to copy text:', error);
        return false;
    }
}

// ===== ERROR HANDLING =====

/**
 * Global error handler
 * @param {Error} error - Error object
 * @param {string} context - Context where error occurred
 */
function handleError(error, context = 'Unknown') {
    console.error(`Error in ${context}:`, error);
    
    let message = 'Si è verificato un errore inaspettato.';
    
    if (error.message) {
        if (error.message.includes('fetch')) {
            message = 'Errore di connessione. Controlla la tua connessione internet.';
        } else if (error.message.includes('400')) {
            message = 'Richiesta non valida. Controlla i dati inseriti.';
        } else if (error.message.includes('401')) {
            message = 'Accesso non autorizzato.';
        } else if (error.message.includes('403')) {
            message = 'Accesso negato.';
        } else if (error.message.includes('404')) {
            message = 'Risorsa non trovata.';
        } else if (error.message.includes('500')) {
            message = 'Errore interno del server. Riprova più tardi.';
        }
    }
    
    showFlashMessage(message, 'error');
}

// ===== BROWSER COMPATIBILITY =====

/**
 * Check for required browser features
 */
function checkBrowserCompatibility() {
    const features = {
        fetch: typeof fetch !== 'undefined',
        promise: typeof Promise !== 'undefined',
        localStorage: typeof Storage !== 'undefined',
        mediaDevices: navigator.mediaDevices && navigator.mediaDevices.getUserMedia
    };
    
    const missingFeatures = Object.keys(features).filter(key => !features[key]);
    
    if (missingFeatures.length > 0) {
        console.warn('Missing browser features:', missingFeatures);
        showFlashMessage(
            'Il tuo browser potrebbe non supportare tutte le funzionalità. Ti consigliamo di aggiornarlo.',
            'warning',
            10000
        );
    }
}

// ===== INITIALIZATION ON LOAD =====

// Check browser compatibility when script loads
checkBrowserCompatibility();

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        0% {
            opacity: 1;
            transform: translateX(0);
        }
        100% {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    .form-input.error,
    .form-select.error {
        border-color: var(--color-error);
        box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
    }
`;
document.head.appendChild(style);

console.log('📱 Main JavaScript loaded successfully');

// Export functions for use in other scripts
window.DriverApp = {
    apiRequest,
    showLoading,
    setButtonLoading,
    showFlashMessage,
    closeFlashMessage,
    openModal,
    closeModal,
    validateField,
    validateForm,
    formatFileSize,
    formatDuration,
    debounce,
    throttle,
    handleError
};