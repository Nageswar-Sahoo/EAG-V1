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
                k: 5
            })
        })
        .then(response => response.json())
        .then(data => {
            resultsDiv.innerHTML = ''; // Clear previous results
            
            if (data.error) {
                resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }

            // Display total results count
            resultsDiv.innerHTML = `<div class="total-results">Found ${data.total_results} results for "${data.query}"</div>`;

            // Display each result
            data.results.forEach(result => {
                const resultElement = document.createElement('div');
                resultElement.className = 'result-item';
                
                // Create result HTML with proper formatting
                resultElement.innerHTML = `
                    <div class="result-header">
                        <a href="${result.url || '#'}" target="_blank" class="result-url">
                            ${result.url || 'No URL available'}
                        </a>
                        <span class="similarity-score">Similarity: ${result.similarity}</span>
                    </div>
                    <div class="result-content">
                        ${result.chunk || result.content || 'No content available'}
                    </div>
                `;
                
                resultsDiv.appendChild(resultElement);
            });
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