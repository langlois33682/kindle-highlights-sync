/**
 * Kindle Highlights Viewer
 * Fetches and displays highlights from a GitHub Gist
 */

// CONFIGURATION - Update this with your Gist raw URL
const GIST_RAW_URL = 'https://gist.githubusercontent.com/langlois33682/aeb0a9e901f55d999c46397e2213ef58/raw/latest.json';
// Example: 'https://gist.githubusercontent.com/USERNAME/GIST_ID/raw/latest.json'

const container = document.getElementById('highlights-container');
const updatedAtEl = document.getElementById('updated-at');
const toast = document.getElementById('toast');

function formatDate(isoString) {
    if (!isoString) return 'Unknown';
    
    try {
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
        });
    } catch {
        return 'Unknown';
    }
}

function showToast(message = 'Copied!') {
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

async function copyToClipboard(text, button) {
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(text);
        } else {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
        
        if (button) {
            const originalText = button.innerHTML;
            button.classList.add('copied');
            button.innerHTML = '<span class="copy-btn-icon">✓</span> Copied!';
            
            setTimeout(() => {
                button.classList.remove('copied');
                button.innerHTML = originalText;
            }, 1500);
        }
        
        showToast();
        return true;
    } catch (err) {
        console.error('Failed to copy:', err);
        showToast('Failed to copy');
        return false;
    }
}

function createBookCard(item) {
    const card = document.createElement('article');
    card.className = 'book-card';
    
    const timeDisplay = formatDate(item.highlight_time || item.fetched_at);
    
    card.innerHTML = `
        <div class="book-title">
            <span class="book-title-text">${escapeHtml(item.book_title)}</span>
            <button class="copy-title-btn" data-copy-title>Copy</button>
        </div>
        <p class="highlight-text">${escapeHtml(item.highlight_text)}</p>
        <div class="highlight-meta">
            <span class="highlight-time">${timeDisplay}</span>
        </div>
        <button class="copy-btn" data-copy-highlight>
            <span class="copy-btn-icon">📋</span>
            COPY HIGHLIGHT
        </button>
    `;
    
    const copyHighlightBtn = card.querySelector('[data-copy-highlight]');
    copyHighlightBtn.addEventListener('click', () => {
        copyToClipboard(item.highlight_text, copyHighlightBtn);
    });
    
    const copyTitleBtn = card.querySelector('[data-copy-title]');
    copyTitleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        copyToClipboard(item.book_title, null);
    });
    
    return card;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderError(message) {
    container.innerHTML = `
        <div class="error">
            <div class="error-icon">⚠️</div>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}

function renderEmpty() {
    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">📖</div>
            <p class="empty-state-text">No highlights yet</p>
        </div>
    `;
}

function renderHighlights(data) {
    if (!data.items || data.items.length === 0) {
        renderEmpty();
        return;
    }
    
    updatedAtEl.textContent = `Updated ${formatDate(data.updated_at)}`;
    
    container.innerHTML = '';
    
    data.items.forEach(item => {
        const card = createBookCard(item);
        container.appendChild(card);
    });
}

async function fetchHighlights() {
    if (GIST_RAW_URL === 'YOUR_GIST_RAW_URL_HERE') {
        renderError('Please configure GIST_RAW_URL in app.js');
        return;
    }
    
    try {
        const cacheBuster = `?t=${Date.now()}`;
        const response = await fetch(GIST_RAW_URL + cacheBuster);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        renderHighlights(data);
    } catch (err) {
        console.error('Failed to fetch highlights:', err);
        renderError('Failed to load highlights. Check console for details.');
    }
}

document.addEventListener('DOMContentLoaded', fetchHighlights);

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Service worker registration could go here for offline support
    });
}
