// AJAX Functions for Archify Platform

// Generic AJAX request function
function ajaxRequest(url, method, data, successCallback, errorCallback) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (successCallback) successCallback(data);
            showToast(data.message || 'Operation completed successfully', 'success');
        } else {
            if (errorCallback) errorCallback(data);
            showToast(data.error || 'An error occurred', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (errorCallback) errorCallback(error);
        showToast('Network error. Please try again.', 'danger');
    });
}

// Load notifications from API
function loadNotifications() {
    const notificationContainer = document.getElementById('notificationList');
    const notificationCount = document.getElementById('notificationCount');
    const markAllBtn = document.getElementById('markAllReadBtn');
    
    if (!notificationContainer) return;
    
    fetch('/api/notifications/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.notifications && data.notifications.length > 0) {
            let html = '';
            data.notifications.forEach(notification => {
                let iconClass = 'fa-bell';
                let redirectUrl = '#';
                
                // Determine icon and redirect URL based on notification type
                if (notification.notification_type === 'CONSULTATION_REQUEST') {
                    iconClass = 'fa-comment';
                    redirectUrl = `/consultations/${notification.id}/`;
                } else if (notification.notification_type === 'PROJECT_UPDATE') {
                    iconClass = 'fa-building';
                    redirectUrl = `/projects/${notification.metadata?.project_id || '#'}/`;
                } else if (notification.notification_type === 'PLAN_APPROVED') {
                    iconClass = 'fa-check-circle';
                    redirectUrl = `/plans/${notification.metadata?.plan_id || '#'}/`;
                } else if (notification.notification_type === 'WAGE_PAYMENT') {
                    iconClass = 'fa-money-bill';
                    redirectUrl = `/payments/${notification.metadata?.payment_id || '#'}/`;
                } else if (notification.notification_type === 'NEW_MESSAGE') {
                    iconClass = 'fa-envelope';
                    redirectUrl = `/messages/${notification.metadata?.conversation_id || '#'}/`;
                }
                
                html += `
                    <a href="${redirectUrl}" class="notification-item ${!notification.is_read ? 'bg-light' : ''}" data-id="${notification.id}" onclick="markNotificationAsRead('${notification.id}', event)">
                        <div class="d-flex">
                            <div class="flex-shrink-0">
                                <i class="fas ${iconClass} text-primary mt-1"></i>
                            </div>
                            <div class="flex-grow-1 ms-3">
                                <strong>${escapeHtml(notification.title)}</strong>
                                <div class="small text-muted">${escapeHtml(notification.message)}</div>
                                <small class="text-muted">${notification.time_ago || notification.created_at}</small>
                            </div>
                            ${!notification.is_read ? '<div class="flex-shrink-0"><span class="badge bg-primary rounded-pill">New</span></div>' : ''}
                        </div>
                    </a>
                    <div class="dropdown-divider"></div>
                `;
            });
            notificationContainer.innerHTML = html;
            if (notificationCount) {
                notificationCount.textContent = data.unread_count || 0;
                if (data.unread_count > 0) {
                    notificationCount.style.display = 'inline-block';
                } else {
                    notificationCount.style.display = 'none';
                }
            }
            if (markAllBtn) {
                markAllBtn.style.display = data.unread_count > 0 ? 'block' : 'none';
            }
        } else {
            notificationContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-bell-slash fa-2x text-muted mb-2"></i>
                    <p class="text-muted mb-0">No new notifications</p>
                </div>
            `;
            if (notificationCount) {
                notificationCount.textContent = '0';
                notificationCount.style.display = 'none';
            }
        }
    })
    .catch(error => console.error('Error loading notifications:', error));
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Mark notification as read and redirect
function markNotificationAsRead(notificationId, event) {
    // Prevent the link from navigating immediately
    if (event) {
        event.preventDefault();
    }
    
    const link = event ? event.currentTarget : null;
    const redirectUrl = link ? link.getAttribute('href') : '#';
    
    fetch(`/api/notifications/${notificationId}/read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload notifications to update count
            loadNotifications();
            
            // Show success message
            showToast('Notification marked as read', 'success');
            
            // Redirect to the consultation page
            if (redirectUrl && redirectUrl !== '#') {
                window.location.href = redirectUrl;
            }
        } else {
            showToast('Error marking notification as read', 'danger');
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
        // Still redirect even if API fails
        if (redirectUrl && redirectUrl !== '#') {
            window.location.href = redirectUrl;
        }
    });
}

// Mark all notifications as read
function markAllNotificationsAsRead() {
    if (!confirm('Mark all notifications as read?')) return;
    
    fetch('/api/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            loadNotifications();
        }
    })
    .catch(error => console.error('Error marking all notifications:', error));
}

// Auto-save form data
function autoSaveForm(formId, url, interval = 30000) {
    let form = document.getElementById(formId);
    if (!form) return;
    
    let saveTimeout;
    
    form.addEventListener('input', function() {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            ajaxRequest(url, 'POST', data,
                function(response) {
                    showToast('Auto-saved', 'info');
                },
                function(error) {
                    console.error('Auto-save failed:', error);
                }
            );
        }, interval);
    });
}

// Show toast notification
function showToast(message, type = 'success') {
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    let icon = 'check-circle';
    if (type === 'danger') icon = 'exclamation-circle';
    else if (type === 'warning') icon = 'warning';
    else if (type === 'info') icon = 'info-circle';
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${icon} me-2"></i>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize AJAX functionality
document.addEventListener('DOMContentLoaded', function() {
    // Load notifications
    if (document.getElementById('notificationList')) {
        loadNotifications();
        // Refresh notifications every 30 seconds
        setInterval(loadNotifications, 30000);
    }
    
    // Mark all read button
    const markAllBtn = document.getElementById('markAllReadBtn');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', markAllNotificationsAsRead);
    }
});

// Export functions
window.ajaxRequest = ajaxRequest;
window.loadNotifications = loadNotifications;
window.markNotificationAsRead = markNotificationAsRead;
window.markAllNotificationsAsRead = markAllNotificationsAsRead;
window.autoSaveForm = autoSaveForm;
window.showToast = showToast;
window.getCookie = getCookie;