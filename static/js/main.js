// Main JavaScript for Archify Platform

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add active class to current navigation item
    setActiveNavItem();
    
    // Format currency inputs
    formatCurrencyInputs();
    
    // Initialize date pickers if any
    initDatePickers();
});

// Set active navigation item based on current URL
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('#sidebar ul li a');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.closest('li').classList.add('active');
        }
    });
}

// Format currency inputs
function formatCurrencyInputs() {
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function(e) {
            let value = this.value.replace(/[^0-9.]/g, '');
            if (value) {
                value = parseFloat(value).toFixed(2);
                this.value = '₹' + value;
            }
        });
        
        input.addEventListener('focus', function(e) {
            let value = this.value.replace('₹', '');
            this.value = value;
        });
    });
}

// Initialize date pickers
function initDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            // Set min date to today for future dates if needed
            // input.min = new Date().toISOString().split('T')[0];
        }
    });
}

// Confirm delete action
function confirmDelete(message, url) {
    if (confirm(message || 'Are you sure you want to delete this item?')) {
        window.location.href = url;
    }
    return false;
}

// Show toast notification
function showToast(message, type = 'success') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Format date
function formatDate(dateString, format = 'MM/DD/YYYY') {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    
    if (format === 'DD/MM/YYYY') {
        return `${day}/${month}/${year}`;
    }
    return `${month}/${day}/${year}`;
}

// Calculate and update progress
function updateProgress() {
    const progressElements = document.querySelectorAll('.progress[data-calc]');
    progressElements.forEach(progress => {
        const completed = parseInt(progress.dataset.completed || 0);
        const total = parseInt(progress.dataset.total || 1);
        const percentage = (completed / total) * 100;
        const progressBar = progress.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
            progressBar.textContent = `${Math.round(percentage)}%`;
        }
    });
}

// Export functions for global use
window.confirmDelete = confirmDelete;
window.showToast = showToast;
window.formatDate = formatDate;
window.updateProgress = updateProgress;