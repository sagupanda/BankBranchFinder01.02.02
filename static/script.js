// Custom JavaScript for IFSC Finder

document.addEventListener('DOMContentLoaded', function() {
    // Initialize autocomplete
    initializeAutocomplete();
    
    // Initialize example code clicks
    initializeExampleCodes();
    
    // Initialize tooltips
    initializeTooltips();
});

// Autocomplete functionality
function initializeAutocomplete() {
    const searchInput = document.getElementById('searchInput');
    const autocompleteResults = document.getElementById('autocomplete-results');
    let debounceTimer;
    let activeIndex = -1;
    
    if (!searchInput || !autocompleteResults) return;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = this.value.trim();
        
        if (query.length < 2) {
            hideAutocomplete();
            return;
        }
        
        debounceTimer = setTimeout(() => {
            fetchSuggestions(query);
        }, 300);
    });
    
    searchInput.addEventListener('keydown', function(e) {
        const items = autocompleteResults.querySelectorAll('.autocomplete-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            activeIndex = Math.min(activeIndex + 1, items.length - 1);
            updateActiveItem(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            activeIndex = Math.max(activeIndex - 1, -1);
            updateActiveItem(items);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (activeIndex >= 0 && items[activeIndex]) {
                selectSuggestion(items[activeIndex]);
            } else {
                document.querySelector('.search-form').submit();
            }
        } else if (e.key === 'Escape') {
            hideAutocomplete();
        }
    });
    
    // Hide autocomplete when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !autocompleteResults.contains(e.target)) {
            hideAutocomplete();
        }
    });
    
    function fetchSuggestions(query) {
        fetch(`/autocomplete?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displaySuggestions(data);
            })
            .catch(error => {
                console.error('Error fetching suggestions:', error);
                hideAutocomplete();
            });
    }
    
    function displaySuggestions(suggestions) {
        if (suggestions.length === 0) {
            hideAutocomplete();
            return;
        }
        
        autocompleteResults.innerHTML = '';
        activeIndex = -1;
        
        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.innerHTML = `
                <div>${suggestion.label}</div>
                <div class="autocomplete-type">${suggestion.type.toUpperCase()}</div>
            `;
            item.addEventListener('click', () => selectSuggestion(item, suggestion));
            autocompleteResults.appendChild(item);
        });
        
        showAutocomplete();
    }
    
    function selectSuggestion(item, suggestion) {
        if (!suggestion) {
            // Extract suggestion data from item
            const value = item.querySelector('div').textContent.split(' - ')[0];
            searchInput.value = value;
        } else {
            searchInput.value = suggestion.value;
        }
        hideAutocomplete();
        document.querySelector('.search-form').submit();
    }
    
    function updateActiveItem(items) {
        items.forEach((item, index) => {
            item.classList.toggle('active', index === activeIndex);
        });
    }
    
    function showAutocomplete() {
        autocompleteResults.style.display = 'block';
    }
    
    function hideAutocomplete() {
        autocompleteResults.style.display = 'none';
        activeIndex = -1;
    }
}

// Example code click functionality
function initializeExampleCodes() {
    const exampleCodes = document.querySelectorAll('.example-code');
    
    exampleCodes.forEach(code => {
        code.addEventListener('click', function() {
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.value = this.textContent;
                searchInput.focus();
                
                // Optional: Auto-submit the form
                setTimeout(() => {
                    document.querySelector('.search-form').submit();
                }, 500);
            }
        });
    });
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('IFSC code copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('IFSC code copied to clipboard!', 'success');
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
        showToast('Failed to copy IFSC code', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Toast notification system
function showToast(message, type = 'info') {
    // Remove existing toast
    const existingToast = document.querySelector('.custom-toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = `custom-toast alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 250px;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        animation: slideInRight 0.3s ease;
    `;
    
    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Initialize tooltips
function initializeTooltips() {
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .custom-toast {
            animation: slideInRight 0.3s ease;
        }
    `;
    document.head.appendChild(style);
}

// Search form enhancement
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('.search-form');
    const searchButton = searchForm?.querySelector('button[type="submit"]');
    
    if (searchForm && searchButton) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('searchInput');
            const query = searchInput?.value.trim();
            
            if (!query) {
                e.preventDefault();
                showToast('Please enter a search term', 'error');
                searchInput?.focus();
                return;
            }
            
            // Add loading state
            const originalText = searchButton.innerHTML;
            searchButton.innerHTML = '<span class="loading me-2"></span>Searching...';
            searchButton.disabled = true;
            
            // Reset button after a delay (in case of slow navigation)
            setTimeout(() => {
                searchButton.innerHTML = originalText;
                searchButton.disabled = false;
            }, 5000);
        });
    }
});

// Enhanced search input validation
function validateSearchInput(input) {
    const value = input.value.trim();
    
    if (value.length === 0) {
        return { valid: false, message: 'Please enter a search term' };
    }
    
    if (value.length < 2) {
        return { valid: false, message: 'Search term must be at least 2 characters' };
    }
    
    return { valid: true };
}

// Performance optimization: Debounce scroll events
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

// Smooth scroll for internal links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
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
});
