// Autocomplete functionality for search input

let autocompleteTimeout;
let currentFocus = -1;

function initializeAutocomplete(inputId, resultsId) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);
    
    if (!input || !results) return;
    
    // Handle input events
    input.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Clear previous timeout
        clearTimeout(autocompleteTimeout);
        
        if (query.length < 2) {
            hideResults();
            return;
        }
        
        // Debounce the API call
        autocompleteTimeout = setTimeout(() => {
            fetchSuggestions(query, results);
        }, 300);
    });
    
    // Handle keyboard navigation
    input.addEventListener('keydown', function(e) {
        const items = results.querySelectorAll('.autocomplete-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            currentFocus++;
            if (currentFocus >= items.length) currentFocus = 0;
            setActive(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            currentFocus--;
            if (currentFocus < 0) currentFocus = items.length - 1;
            setActive(items);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (currentFocus > -1 && items[currentFocus]) {
                const value = items[currentFocus].querySelector('span').textContent;
                selectItem(value, input, results);
            } else {
                // Submit the form
                input.closest('form').submit();
            }
        } else if (e.key === 'Escape') {
            hideResults();
        }
    });
    
    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !results.contains(e.target)) {
            hideResults();
        }
    });
    
    function fetchSuggestions(query, resultsContainer) {
        fetch(`/api/autocomplete?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displaySuggestions(data, resultsContainer, input);
            })
            .catch(error => {
                console.error('Autocomplete error:', error);
                hideResults();
            });
    }
    
    function displaySuggestions(suggestions, resultsContainer, inputElement) {
        resultsContainer.innerHTML = '';
        currentFocus = -1;
        
        if (suggestions.length === 0) {
            hideResults();
            return;
        }
        
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            
            // Handle both string and object suggestions
            const displayText = typeof suggestion === 'string' ? suggestion : suggestion.label;
            const value = typeof suggestion === 'string' ? suggestion : suggestion.value;
            
            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <span>${displayText}</span>
                    <small class="text-muted">${suggestion.type || ''}</small>
                </div>
            `;
            
            item.addEventListener('click', function() {
                selectItem(value, inputElement, resultsContainer);
            });
            
            resultsContainer.appendChild(item);
        });
        
        showResults();
    }
    
    function setActive(items) {
        // Remove active class from all items
        items.forEach(item => item.classList.remove('active'));
        
        // Add active class to current item
        if (currentFocus >= 0 && currentFocus < items.length) {
            items[currentFocus].classList.add('active');
        }
    }
    
    function selectItem(value, inputElement, resultsContainer) {
        inputElement.value = value;
        hideResults();
        
        // Optional: Trigger search immediately
        inputElement.closest('form').submit();
    }
    
    function showResults() {
        results.style.display = 'block';
    }
    
    function hideResults() {
        results.style.display = 'none';
        currentFocus = -1;
    }
}

// Utility function to highlight matching text
function highlightMatch(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<strong>$1</strong>');
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
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
        
        return new Promise((resolve, reject) => {
            document.execCommand('copy') ? resolve() : reject();
            textArea.remove();
        });
    }
}

// Show loading state
function showLoading(element) {
    element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    element.disabled = true;
}

// Hide loading state
function hideLoading(element, originalText) {
    element.innerHTML = originalText;
    element.disabled = false;
}

// Format IFSC code display
function formatIFSC(ifsc) {
    return ifsc.toUpperCase().replace(/(.{4})(.{7})/, '$1 $2');
}

// Validate IFSC code format
function isValidIFSC(ifsc) {
    const ifscPattern = /^[A-Z]{4}[0-9]{7}$/;
    return ifscPattern.test(ifsc.toUpperCase());
}

// Validate MICR code format
function isValidMICR(micr) {
    const micrPattern = /^[0-9]{9}$/;
    return micrPattern.test(micr);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any additional functionality here
    console.log('IFSC Finder loaded successfully');
});
