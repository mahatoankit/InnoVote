// Main JavaScript for InnoVote
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Check voting status periodically
    checkVotingStatus();
    setInterval(checkVotingStatus, 30000); // Check every 30 seconds
    
    // Initialize vote functionality
    initializeVoting();
    
    // Initialize feedback functionality
    initializeFeedback();
    
    // Initialize animations
    initializeAnimations();
}

function checkVotingStatus() {
    fetch('/status/')
        .then(response => response.json())
        .then(data => {
            updateVotingStatus(data.is_active, data.show_results);
        })
        .catch(error => {
            console.error('Error checking voting status:', error);
        });
}

function updateVotingStatus(isActive, showResults) {
    const statusElements = document.querySelectorAll('.voting-status');
    statusElements.forEach(element => {
        element.className = `voting-status status-badge ${isActive ? 'active' : 'inactive'}`;
        element.textContent = isActive ? 'Voting Active' : 'Voting Inactive';
    });
    
    // Update voting buttons
    const voteButtons = document.querySelectorAll('.vote-btn');
    voteButtons.forEach(button => {
        button.disabled = !isActive;
        if (!isActive) {
            button.textContent = 'Voting Closed';
            button.classList.add('btn-secondary');
            button.classList.remove('btn-primary');
        } else {
            button.textContent = 'Vote Now';
            button.classList.add('btn-primary');
            button.classList.remove('btn-secondary');
        }
    });
}

function initializeVoting() {
    // Handle vote button clicks
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('vote-btn')) {
            const projectId = e.target.dataset.projectId;
            const projectTitle = e.target.dataset.projectTitle;
            showVotingModal(projectId, projectTitle);
        }
    });
    
    // Handle voting form submission
    const voteForm = document.getElementById('voteForm');
    if (voteForm) {
        voteForm.addEventListener('submit', handleVoteSubmission);
    }
}

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
