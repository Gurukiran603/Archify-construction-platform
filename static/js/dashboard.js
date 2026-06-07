// Dashboard specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initDashboardCharts();
    }
    
    // Load recent activity
    loadRecentActivity();
    
    // Refresh stats every 5 minutes
    setInterval(refreshStats, 300000);
});

// Initialize dashboard charts
function initDashboardCharts() {
    // Project Progress Chart
    const progressCtx = document.getElementById('projectProgressChart');
    if (progressCtx) {
        new Chart(progressCtx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'In Progress', 'Pending'],
                datasets: [{
                    data: [30, 45, 25],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                }]
            }
        });
    }
    
    // Monthly Activity Chart
    const activityCtx = document.getElementById('monthlyActivityChart');
    if (activityCtx) {
        new Chart(activityCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Projects',
                    data: [12, 19, 15, 17, 14, 23],
                    borderColor: '#1a1a2e'
                }]
            }
        });
    }
}

// Load recent activity feed
function loadRecentActivity() {
    const activityFeed = document.getElementById('activityFeed');
    if (!activityFeed) return;
    
    fetch('/api/recent-activity/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.activities && data.activities.length > 0) {
            let html = '';
            data.activities.forEach(activity => {
                html += `
                    <div class="timeline-item mb-3">
                        <div class="d-flex">
                            <div class="flex-shrink-0">
                                <div class="rounded-circle bg-primary p-2">
                                    <i class="fas fa-${activity.icon} text-white"></i>
                                </div>
                            </div>
                            <div class="flex-grow-1 ms-3">
                                <p class="mb-0">${activity.message}</p>
                                <small class="text-muted">${activity.time_ago}</small>
                            </div>
                        </div>
                    </div>
                `;
            });
            activityFeed.innerHTML = html;
        } else {
            activityFeed.innerHTML = '<p class="text-muted text-center">No recent activity</p>';
        }
    })
    .catch(error => console.error('Error loading activity:', error));
}

// Refresh dashboard stats
function refreshStats() {
    fetch('/api/dashboard-stats/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update stat cards
        document.querySelectorAll('[data-stat]').forEach(element => {
            const statName = element.getAttribute('data-stat');
            if (data[statName] !== undefined) {
                element.textContent = data[statName];
            }
        });
    })
    .catch(error => console.error('Error refreshing stats:', error));
}