// Kindle Highlights Widget for Scriptable
// Displays the most recent Kindle highlight on your iPhone home screen

// ============================================
// CONFIGURATION - UPDATE THESE VALUES
// ============================================

const GIST_RAW_URL = 'YOUR_GIST_RAW_URL_HERE';
// Example: 'https://gist.githubusercontent.com/USERNAME/GIST_ID/raw/latest.json'

const VIEWER_URL = 'YOUR_GITHUB_PAGES_URL_HERE';
// Example: 'https://USERNAME.github.io/REPO_NAME/viewer/'

// ============================================
// WIDGET CODE - No need to edit below
// ============================================

async function fetchHighlights() {
    const url = GIST_RAW_URL + '?t=' + Date.now();
    const req = new Request(url);
    req.headers = { 'Cache-Control': 'no-cache' };
    
    try {
        const data = await req.loadJSON();
        return data;
    } catch (error) {
        console.error('Failed to fetch:', error);
        return null;
    }
}

function formatRelativeTime(isoString) {
    if (!isoString) return '';
    
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
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3).trim() + '...';
}

async function createWidget() {
    const widget = new ListWidget();
    widget.backgroundColor = new Color('#1a1a1a');
    widget.setPadding(16, 16, 16, 16);
    
    if (VIEWER_URL && VIEWER_URL !== 'YOUR_GITHUB_PAGES_URL_HERE') {
        widget.url = VIEWER_URL;
    }
    
    const data = await fetchHighlights();
    
    if (!data || !data.items || data.items.length === 0) {
        const errorText = widget.addText('📚 No highlights');
        errorText.font = Font.mediumSystemFont(14);
        errorText.textColor = Color.gray();
        errorText.centerAlignText();
        return widget;
    }
    
    const item = data.items[0];
    
    const titleStack = widget.addStack();
    titleStack.layoutHorizontally();
    titleStack.centerAlignContent();
    
    const bookIcon = titleStack.addText('📖');
    bookIcon.font = Font.systemFont(12);
    
    titleStack.addSpacer(6);
    
    const titleText = titleStack.addText(truncateText(item.book_title, 30));
    titleText.font = Font.semiboldSystemFont(13);
    titleText.textColor = new Color('#a0a0a0');
    titleText.lineLimit = 1;
    
    widget.addSpacer(8);
    
    const widgetFamily = config.widgetFamily || 'medium';
    let maxHighlightLength;
    
    switch (widgetFamily) {
        case 'small':
            maxHighlightLength = 80;
            break;
        case 'large':
            maxHighlightLength = 300;
            break;
        default:
            maxHighlightLength = 150;
    }
    
    const highlightText = widget.addText(truncateText(item.highlight_text, maxHighlightLength));
    highlightText.font = Font.systemFont(15);
    highlightText.textColor = Color.white();
    highlightText.lineLimit = widgetFamily === 'small' ? 4 : 6;
    
    widget.addSpacer();
    
    const footerStack = widget.addStack();
    footerStack.layoutHorizontally();
    footerStack.bottomAlignContent();
    
    const timeText = footerStack.addText(formatRelativeTime(item.highlight_time || item.fetched_at));
    timeText.font = Font.systemFont(11);
    timeText.textColor = new Color('#666666');
    
    footerStack.addSpacer();
    
    const tapHint = footerStack.addText('Tap to view all →');
    tapHint.font = Font.systemFont(10);
    tapHint.textColor = new Color('#4f9cf9');
    
    return widget;
}

async function run() {
    if (GIST_RAW_URL === 'YOUR_GIST_RAW_URL_HERE') {
        const widget = new ListWidget();
        widget.backgroundColor = new Color('#1a1a1a');
        
        const text = widget.addText('⚠️ Configure GIST_RAW_URL');
        text.font = Font.mediumSystemFont(12);
        text.textColor = Color.orange();
        text.centerAlignText();
        
        if (config.runsInWidget) {
            Script.setWidget(widget);
        } else {
            widget.presentMedium();
        }
        return;
    }
    
    const widget = await createWidget();
    
    if (config.runsInWidget) {
        Script.setWidget(widget);
    } else {
        await widget.presentMedium();
    }
}

await run();
Script.complete();
