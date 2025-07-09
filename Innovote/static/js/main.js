// Main JavaScript for InnoVote
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Touch-friendly enhancements
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
        
        // Add touch feedback
        const touchElements = document.querySelectorAll('.btn, .card, .list-group-item');
        touchElements.forEach(element => {
            element.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.98)';
            });
            
            element.addEventListener('touchend', function() {
                this.style.transform = 'scale(1)';
            });
        });
    }

    // Form validation enhancements
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
});

// Utility functions
function showNotification(message, type = 'info', duration = 5000) {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    const iconMap = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };

    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-${iconMap[type]} text-${type} me-2"></i>
            <strong class="me-auto">Notification</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    toastContainer.appendChild(toast);

    const bootstrapToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });

    bootstrapToast.show();

    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

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

// Voting specific functions
function validateVotingCode(code) {
    const regex = /^[A-Za-z0-9]{5}$/;
    return regex.test(code);
}

function formatVotingCode(code) {
    return code.toUpperCase().replace(/[^A-Z0-9]/g, '');
}

// Export functions for use in other scripts
window.InnoVote = {
    showNotification,
    getCookie,
    validateVotingCode,
    formatVotingCode
};

function showVotingModal(projectId, projectTitle) {
    const modal = document.getElementById('voteModal');
    const modalTitle = modal.querySelector('.modal-title');
    const projectIdInput = modal.querySelector('#projectId');
    const votingCodeInput = modal.querySelector('#votingCode');
    
    modalTitle.textContent = `Vote for "${projectTitle}"`;
    projectIdInput.value = projectId;
    votingCodeInput.value = '';
    votingCodeInput.focus();
    
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

function handleVoteSubmission(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const projectId = formData.get('projectId');
    const votingCode = formData.get('votingCode').trim().toUpperCase();
    
    if (!votingCode) {
        showAlert('Please enter your voting code.', 'danger');
        return;
    }
    
    // Show loading state
    const submitButton = e.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';
    
    // Submit vote
    fetch('/vote/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            project_id: projectId,
            voting_code: votingCode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('voteModal')).hide();
            // Reset form
            e.target.reset();
        } else {
            showAlert(data.message, 'danger');
        }
    })
    .catch(error => {
        showAlert('An error occurred. Please try again.', 'danger');
        console.error('Error:', error);
    })
    .finally(() => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
}

function initializeFeedback() {
    // Handle feedback button clicks
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('feedback-btn')) {
            const projectId = e.target.dataset.projectId;
            const projectTitle = e.target.dataset.projectTitle;
            showFeedbackModal(projectId, projectTitle);
        }
    });
    
    // Handle feedback form submission
    const feedbackForm = document.getElementById('feedbackForm');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', handleFeedbackSubmission);
    }
}

function showFeedbackModal(projectId, projectTitle) {
    const modal = document.getElementById('feedbackModal');
    const modalTitle = modal.querySelector('.modal-title');
    const projectIdInput = modal.querySelector('#feedbackProjectId');
    const feedbackTextarea = modal.querySelector('#feedbackText');
    
    modalTitle.textContent = `Feedback for "${projectTitle}"`;
    projectIdInput.value = projectId;
    feedbackTextarea.value = '';
    
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Focus on textarea after modal is shown
    modal.addEventListener('shown.bs.modal', function() {
        feedbackTextarea.focus();
    });
}

function handleFeedbackSubmission(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const projectId = formData.get('projectId');
    const feedbackText = formData.get('feedbackText').trim();
    
    if (!feedbackText) {
        showAlert('Please enter your feedback.', 'danger');
        return;
    }
    
    // Show loading state
    const submitButton = e.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';
    
    // Submit feedback
    fetch('/feedback/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            project_id: projectId,
            feedback_text: feedbackText
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('feedbackModal')).hide();
            // Reset form
            e.target.reset();
        } else {
            showAlert(data.message, 'danger');
        }
    })
    .catch(error => {
        showAlert('An error occurred. Please try again.', 'danger');
        console.error('Error:', error);
    })
    .finally(() => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
}

function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.project-card, .results-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

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

// Utility functions
function formatNumber(num) {
    return num.toLocaleString();
}

function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
}

// Touch-friendly features for kiosks
function enableTouchFeatures() {
    // Add touch feedback to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Prevent double-tap zoom
    document.addEventListener('touchend', function(e) {
        const now = new Date().getTime();
        const timeSince = now - lastTouchEnd;
        if (timeSince < 300 && timeSince > 0) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
}

let lastTouchEnd = 0;

// Initialize touch features if on mobile/tablet
if ('ontouchstart' in window) {
    enableTouchFeatures();
}
