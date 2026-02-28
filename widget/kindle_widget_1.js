// Kindle Highlight #1 (Most Recent) - Copies on tap
// Setup: Add Medium widget, set "When Interacting" to "Run Script"

const GIST_RAW_URL = 'https://gist.githubusercontent.com/langlois33682/aeb0a9e901f55d999c46397e2213ef58/raw/latest.json';
const HIGHLIGHT_INDEX = 0; // First (most recent)

async function fetchHighlights() {
    const req = new Request(GIST_RAW_URL + '?t=' + Date.now());
    try { return await req.loadJSON(); } 
    catch { return null; }
}

function truncate(text, max) {
    if (!text) return '';
    return text.length <= max ? text : text.substring(0, max - 3).trim() + '...';
}

function timeAgo(iso) {
    if (!iso) return '';
    const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
    if (mins < 60) return `${mins}m ago`;
    if (mins < 1440) return `${Math.floor(mins/60)}h ago`;
    return `${Math.floor(mins/1440)}d ago`;
}

async function main() {
    const data = await fetchHighlights();
    const item = data?.items?.[HIGHLIGHT_INDEX];
    
    // When tapped (not in widget mode), copy to clipboard
    if (!config.runsInWidget && item) {
        Pasteboard.copy(item.highlight_text);
        const alert = new Alert();
        alert.title = "✓ Copied!";
        alert.message = truncate(item.highlight_text, 100);
        alert.addAction("OK");
        await alert.present();
        Script.complete();
        return;
    }
    
    const widget = new ListWidget();
    widget.backgroundColor = new Color('#1a1a1a');
    widget.setPadding(14, 14, 14, 14);
    
    if (!item) {
        const msg = widget.addText('📚 No highlight');
        msg.font = Font.systemFont(14);
        msg.textColor = Color.gray();
        Script.setWidget(widget);
        Script.complete();
        return;
    }
    
    // Book title row
    const titleRow = widget.addStack();
    titleRow.layoutHorizontally();
    titleRow.centerAlignContent();
    
    const icon = titleRow.addText('📖');
    icon.font = Font.systemFont(12);
    titleRow.addSpacer(4);
    
    const bookTitle = titleRow.addText(truncate(item.book_title, 28));
    bookTitle.font = Font.semiboldSystemFont(12);
    bookTitle.textColor = new Color('#a0a0a0');
    bookTitle.lineLimit = 1;
    
    widget.addSpacer(6);
    
    // Quote text
    const quote = widget.addText(truncate(item.highlight_text, 140));
    quote.font = Font.systemFont(14);
    quote.textColor = Color.white();
    quote.lineLimit = 5;
    
    widget.addSpacer();
    
    // Footer row
    const footer = widget.addStack();
    footer.layoutHorizontally();
    footer.bottomAlignContent();
    
    const time = footer.addText(timeAgo(item.highlight_time || item.fetched_at));
    time.font = Font.systemFont(10);
    time.textColor = new Color('#666666');
    
    footer.addSpacer();
    
    const hint = footer.addText('Tap to copy');
    hint.font = Font.mediumSystemFont(10);
    hint.textColor = new Color('#4f9cf9');
    
    Script.setWidget(widget);
}

await main();
Script.complete();
