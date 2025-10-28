async function checkUrl() {
    const urlInput = document.getElementById('urlInput');
    const checkBtn = document.getElementById('checkBtn');
    const btnText = document.getElementById('btnText');
    const errorBox = document.getElementById('errorBox');
    const resultSection = document.getElementById('resultSection');
    const infoBox = document.getElementById('infoBox');
    
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Please enter a URL to check');
        return;
    }
    
    // Show loading state
    checkBtn.disabled = true;
    btnText.innerHTML = '<div class="spinner"></div> Scanning...';
    errorBox.classList.add('hidden');
    if (resultSection) resultSection.classList.add('hidden');
    
    try {
        const response = await fetch('/api/check-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to check URL');
        }
        
        displayResults(data);
        if (infoBox) infoBox.classList.add('hidden');
    } catch (error) {
        showError(error.message);
    } finally {
        checkBtn.disabled = false;
        btnText.innerHTML = '🔍 Check URL';
    }
}

function showError(message) {
    const errorBox = document.getElementById('errorBox');
    errorBox.textContent = '❌ ' + message;
    errorBox.classList.remove('hidden');
}

function displayResults(data) {
    const resultSection = document.getElementById('resultSection');
    const { url, malicious, suspicious, harmless, undetected, total, details, safety_level } = data;
    
    let safetyClass = 'safe';
    let safetyIcon = '✅';
    let safetyTitle = 'SAFE - No Threats Detected';
    let safetyColor = '#2e7d32';
    
    if (safety_level === 'dangerous') {
        safetyClass = 'dangerous';
        safetyIcon = '⚠️';
        safetyTitle = 'DANGEROUS - Do Not Visit';
        safetyColor = '#c62828';
    } else if (safety_level === 'suspicious') {
        safetyClass = 'suspicious';
        safetyIcon = '⚡';
        safetyTitle = 'SUSPICIOUS - Proceed with Caution';
        safetyColor = '#e65100';
    }
    
    const vendorsHtml = Object.entries(details)
        .map(([vendor, info]) => `
            <div class="vendor-item">
                <span class="vendor-name">${escapeHtml(vendor)}</span>
                <span class="badge ${info.category}">${escapeHtml(info.category)}</span>
            </div>
        `).join('');
    
    resultSection.innerHTML = `
        <div class="result-card ${safetyClass}">
            <div class="result-header">
                <div class="result-icon">${safetyIcon}</div>
                <div>
                    <div class="result-title" style="color: ${safetyColor}">${safetyTitle}</div>
                    <div class="result-url">${escapeHtml(url)}</div>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-number" style="color: #f44336;">${malicious}</div>
                    <div class="stat-label">Malicious</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" style="color: #ff9800;">${suspicious}</div>
                    <div class="stat-label">Suspicious</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" style="color: #4caf50;">${harmless}</div>
                    <div class="stat-label">Harmless</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" style="color: #9e9e9e;">${undetected}</div>
                    <div class="stat-label">Undetected</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3 style="margin-bottom: 15px;">Security Vendor Analysis (${total} vendors)</h3>
            <div class="vendors-list">
                ${vendorsHtml}
            </div>
            
            <div class="actions">
                <button class="btn-secondary" onclick="resetForm()">
                    Check Another URL
                </button>
                <button onclick="window.open('https://www.virustotal.com/gui/url/' + btoa('${url}') + '/detection', '_blank')">
                    📊 View Full Report
                </button>
            </div>
        </div>
    `;
    
    resultSection.classList.remove('hidden');
}

function resetForm() {
    const urlInput = document.getElementById('urlInput');
    const resultSection = document.getElementById('resultSection');
    const errorBox = document.getElementById('errorBox');
    const infoBox = document.getElementById('infoBox');
    
    if (urlInput) urlInput.value = '';
    if (resultSection) resultSection.classList.add('hidden');
    if (errorBox) errorBox.classList.add('hidden');
    if (infoBox) infoBox.classList.remove('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('urlInput');
    const checkBtn = document.getElementById('checkBtn');
    
    if (urlInput) {
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                checkUrl();
            }
        });
    }
    
    if (checkBtn) {
        checkBtn.addEventListener('click', checkUrl);
    }
});
