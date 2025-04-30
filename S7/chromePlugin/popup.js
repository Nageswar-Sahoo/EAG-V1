document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const resultsDiv = document.getElementById('results');

    searchButton.addEventListener('click', function() {
        const query = searchInput.value;
        if (!query) return;

        fetch('http://localhost:5000/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                k: 1  // Only get the top result
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }

            if (data.results && data.results.length > 0) {
                const result = data.results[0];
                if (result.url) {
                    // Open the URL in a new tab
                    chrome.tabs.create({ url: result.url }, function(tab) {
                        // Wait for the tab to load
                        chrome.tabs.onUpdated.addListener(function listener(tabId, changeInfo) {
                            if (tabId === tab.id && changeInfo.status === 'complete') {
                                chrome.tabs.onUpdated.removeListener(listener);
                                // Send message to content script to highlight the text
                                chrome.tabs.sendMessage(tabId, {
                                    type: 'highlight',
                                    text: query  // Highlight the original search query
                                });
                            }
                        });
                    });
                }
            } else {
                resultsDiv.innerHTML = `<div class="error">No results found</div>`;
            }
        })
        .catch(error => {
            resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        });
    });

    // Add enter key support for search
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchButton.click();
        }
    });
}); 