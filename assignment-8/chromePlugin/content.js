// Function to check if current page should be skipped
function shouldSkipPage() {
    const url = window.location.href;
    // Skip Google search pages
    if (url.includes('google.com/search')) {
        return true;
    }
    // Skip other search engines
    if (url.includes('bing.com/search') || 
        url.includes('yahoo.com/search') || 
        url.includes('duckduckgo.com/')) {
        return true;
    }
    return false;
}

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
function highlightText(text, color = 'yellow') {
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
    const regex = new RegExp(text, 'gi');
    let highlighted = false;

    while (node = walker.nextNode()) {
        if (node.textContent.match(regex)) {
            const span = document.createElement('span');
            span.className = 'search-highlight';
            span.style.backgroundColor = color;
            span.style.padding = '2px';
            span.style.borderRadius = '3px';
            
            const textContent = node.textContent;
            const matches = textContent.matchAll(regex);
            let lastIndex = 0;
            let newContent = '';

            for (const match of matches) {
                // Add text before the match
                newContent += textContent.substring(lastIndex, match.index);
                // Add the highlighted match
                newContent += `<span class="search-highlight" style="background-color: ${color}; padding: 2px; border-radius: 3px;">${match[0]}</span>`;
                lastIndex = match.index + match[0].length;
            }
            // Add remaining text
            newContent += textContent.substring(lastIndex);

            const temp = document.createElement('div');
            temp.innerHTML = newContent;
            
            // Replace the text node with the highlighted content
            while (temp.firstChild) {
                node.parentNode.insertBefore(temp.firstChild, node);
            }
            node.parentNode.removeChild(node);
            
            highlighted = true;
        }
    }

    if (highlighted) {
        // Scroll to the first highlight
        const firstHighlight = document.querySelector('.search-highlight');
        if (firstHighlight) {
            firstHighlight.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}

// Send page content to API
async function processPage() {
    // Skip if this is a search page
    if (shouldSkipPage()) {
        return;
    }

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
        highlightText(request.text, request.color);
        sendResponse({ success: true });
    }
}); 