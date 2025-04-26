// Function to extract text content from the page
function extractPageContent() {
    // Get main content areas
    const mainContent = document.querySelector('main, article, .main-content, #content');
    const content = mainContent ? mainContent.innerText : document.body.innerText;
    const title = document.title;
    
    // Remove unnecessary whitespace and normalize
    return `${title}\n${content}`.replace(/\s+/g, ' ').trim();
}

// Function to highlight text on the page
function highlightText(text) {
    // Remove any existing highlights
    const existingHighlights = document.querySelectorAll('.search-highlight');
    existingHighlights.forEach(el => {
        const parent = el.parentNode;
        parent.replaceChild(document.createTextNode(el.textContent), el);
    });

    // Create a new highlight
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );

    let node;
    while (node = walker.nextNode()) {
        if (node.textContent.includes(text)) {
            const span = document.createElement('span');
            span.className = 'search-highlight';
            span.style.backgroundColor = 'yellow';
            span.style.padding = '2px';
            span.style.borderRadius = '3px';
            span.textContent = text;
            
            const range = document.createRange();
            const startIndex = node.textContent.indexOf(text);
            range.setStart(node, startIndex);
            range.setEnd(node, startIndex + text.length);
            
            range.deleteContents();
            range.insertNode(span);
        }
    }
}

// Send page content to API
async function processPage() {
    try {
        const response = await fetch('http://localhost:5000/process_page', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: window.location.href,
                content: extractPageContent()
            })
        });
        
        if (!response.ok) {
            console.error('Error processing page:', await response.text());
        }
    } catch (error) {
        console.error('Error processing page:', error);
    }
}

// Process page when it loads
processPage();

// Listen for highlight requests from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'highlight') {
        highlightText(request.text);
        sendResponse({ success: true });
    }
}); 