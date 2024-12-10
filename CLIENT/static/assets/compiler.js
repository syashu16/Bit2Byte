async function runCode() {
    const code = document.getElementById('code').value;
    const language = document.getElementById('language').value;
    const outputDiv = document.getElementById('output');
    const loadingDiv = document.getElementById('loading');

    // Show loading message
    loadingDiv.style.display = 'block';
    outputDiv.textContent = '';

    try {
        const response = await fetch('/compile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code, language })
        });

        const result = await response.json();

        // Hide loading message
        loadingDiv.style.display = 'none';

        // Display output or error
        outputDiv.textContent = result.output || result.error;
    } catch (error) {
        loadingDiv.style.display = 'none';
        outputDiv.textContent = "Error: " + error.message;
    }
}

// Basic syntax highlighting (optional)
document.getElementById('code').addEventListener('input', function () {
    let code = this.value;
    // Simple syntax highlighting for Python (could be extended)
    code = code.replace(/(def|class|import|from|print)/g, '<span style="color: #3498db;">$1</span>');
    document.getElementById('code').innerHTML = code;
});