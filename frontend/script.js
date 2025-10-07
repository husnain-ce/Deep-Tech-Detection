let currentAnalysis = null;
let allTechnologies = [];
let filteredTechnologies = [];
class ClientLogger {
    constructor() {
        this.logs = [];
        this.maxLogs = 1000;
        this.logLevel = 'info';
    }
    
    log(level, message, data = null) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            data,
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        
        this.logs.push(logEntry);
        
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(-this.maxLogs);
        }
        const consoleMessage = `[${timestamp}] ${level.toUpperCase()}: ${message}`;
        if (data) {
            console[level](consoleMessage, data);
        } else {
            console[level](consoleMessage);
        }
        
        if (level === 'error' || level === 'warn') {
            this.sendToServer(logEntry);
        }
    }
    
    debug(message, data = null) {
        this.log('debug', message, data);
    }
    
    info(message, data = null) {
        this.log('info', message, data);
    }
    
    warn(message, data = null) {
        this.log('warn', message, data);
    }
    
    error(message, data = null) {
        this.log('error', message, data);
    }
    
    async sendToServer(logEntry) {
        try {
            await fetch('/api/logs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(logEntry)
            });
        } catch (error) {
            console.error('Failed to send log to server:', error);
        }
    }
    
    getLogs(level = null) {
        if (level) {
            return this.logs.filter(log => log.level === level);
        }
        return this.logs;
    }
    
    clearLogs() {
        this.logs = [];
    }
    
    exportLogs() {
        const dataStr = JSON.stringify(this.logs, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `client-logs-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }
}

// Initialize client logger
const clientLogger = new ClientLogger();

// DOM elements
const domainInput = document.getElementById('domainInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const searchSuggestions = document.getElementById('searchSuggestions');
const loadingState = document.getElementById('loadingState');
const resultsSection = document.getElementById('resultsSection');
const errorState = document.getElementById('errorState');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    clientLogger.info('Application initialized');
    initializeEventListeners();
    initializeSidebar();
    loadSuggestions();
    hideAllSections();
    
    // Ensure Font Awesome is loaded
    checkFontAwesome();
    
    clientLogger.info('DOM loaded and event listeners attached');
});

// Check if Font Awesome is loaded properly
function checkFontAwesome() {
    // Wait a bit for Font Awesome to load
    setTimeout(() => {
        const testIcon = document.createElement('i');
        testIcon.className = 'fas fa-check';
        testIcon.style.position = 'absolute';
        testIcon.style.left = '-9999px';
        testIcon.style.visibility = 'hidden';
        document.body.appendChild(testIcon);
        
        // Check if Font Awesome is loaded by testing the computed style
        const computedStyle = window.getComputedStyle(testIcon, ':before');
        const fontFamily = computedStyle.getPropertyValue('font-family');
        const content = computedStyle.getPropertyValue('content');
        
        console.log('Font Awesome check:', { fontFamily, content });
        
        if (!fontFamily.includes('Font Awesome') && !fontFamily.includes('FontAwesome') && content === 'none') {
            console.warn('Font Awesome not loaded properly, applying comprehensive fallback');
            applyComprehensiveFontAwesomeFallback();
        }
        
        document.body.removeChild(testIcon);
    }, 1000);
}

// Apply comprehensive Font Awesome fallback
function applyComprehensiveFontAwesomeFallback() {
    // Add comprehensive fallback CSS
    const fallbackCSS = `
        /* Font Awesome fallback styles */
        .fas, .fab, .far, .fal, .fad {
            font-family: "Font Awesome 6 Free", "Font Awesome 6 Brands", "FontAwesome", sans-serif !important;
            font-weight: 900 !important;
            font-style: normal !important;
            font-variant: normal !important;
            text-rendering: auto !important;
            line-height: 1 !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
            display: inline-block !important;
            width: 1em !important;
            height: 1em !important;
            text-align: center !important;
        }
        
        /* Specific icon fallbacks using Unicode symbols */
        .fas.fa-globe::before { content: "🌐" !important; }
        .fas.fa-search::before { content: "🔍" !important; }
        .fas.fa-search-plus::before { content: "🔍+" !important; }
        .fas.fa-cogs::before { content: "⚙️" !important; }
        .fas.fa-cloud::before { content: "☁️" !important; }
        .fas.fa-chart-line::before { content: "📈" !important; }
        .fas.fa-plus-circle::before { content: "➕" !important; }
        .fas.fa-microscope::before { content: "🔬" !important; }
        .fas.fa-clock::before { content: "🕐" !important; }
        .fas.fa-link::before { content: "🔗" !important; }
        .fas.fa-exclamation-triangle::before { content: "⚠️" !important; }
        .fas.fa-layer-group::before { content: "📚" !important; }
        .fas.fa-shield-alt::before { content: "🛡️" !important; }
        .fas.fa-question-circle::before { content: "❓" !important; }
        .fas.fa-spinner::before { content: "⏳" !important; }
        .fas.fa-server::before { content: "🖥️" !important; }
        .fas.fa-database::before { content: "🗄️" !important; }
        .fas.fa-palette::before { content: "🎨" !important; }
        .fas.fa-shopping-cart::before { content: "🛒" !important; }
        .fas.fa-blog::before { content: "📝" !important; }
        .fas.fa-comments::before { content: "💬" !important; }
        .fas.fa-bug::before { content: "🐛" !important; }
        .fas.fa-edit::before { content: "✏️" !important; }
        .fas.fa-play::before { content: "▶️" !important; }
        .fas.fa-tools::before { content: "🔧" !important; }
        .fas.fa-tags::before { content: "🏷️" !important; }
        .fas.fa-font::before { content: "🔤" !important; }
        .fas.fa-bug::before { content: "🐛" !important; }
        .fab.fa-js-square::before { content: "🟨" !important; }
        .fab.fa-php::before { content: "🐘" !important; }
        .fab.fa-linux::before { content: "🐧" !important; }
    `;
    
    const style = document.createElement('style');
    style.textContent = fallbackCSS;
    style.id = 'fontawesome-fallback';
    document.head.appendChild(style);
    
    // Also try to reload Font Awesome from a different CDN
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://use.fontawesome.com/releases/v6.5.1/css/all.css';
    link.id = 'fontawesome-backup';
    document.head.appendChild(link);
    
    console.log('Font Awesome fallback applied');
}

// Get selected detection engines
function getSelectedEngines() {
    const engines = [];
    
    if (document.getElementById('engine-pattern').checked) {
        engines.push('pattern');
    }
    if (document.getElementById('engine-whatweb').checked) {
        engines.push('whatweb');
    }
    if (document.getElementById('engine-cmseek').checked) {
        engines.push('cmseek');
    }
    if (document.getElementById('engine-whatcms').checked) {
        engines.push('whatcms');
    }
    if (document.getElementById('engine-wappalyzer').checked) {
        engines.push('wappalyzer');
    }
    if (document.getElementById('engine-additional').checked) {
        engines.push('additional');
    }
    if (document.getElementById('engine-deep').checked) {
        engines.push('deep');
    }
    
    return engines;
}

// Event listeners
function initializeEventListeners() {
    // Domain input events
    domainInput.addEventListener('input', handleDomainInput);
    domainInput.addEventListener('focus', showSuggestions);
    domainInput.addEventListener('blur', hideSuggestions);
    
    // Analyze button
    analyzeBtn.addEventListener('click', analyzeDomain);
    
    // Enter key for domain input
    domainInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeDomain();
        }
    });
    
    // Filter controls
    document.getElementById('categoryFilter').addEventListener('change', applyFilters);
    document.getElementById('confidenceFilter').addEventListener('change', applyFilters);
    document.getElementById('searchTech').addEventListener('input', applyFilters);
    
    // Suggestion clicks
    searchSuggestions.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-item')) {
            domainInput.value = e.target.dataset.domain;
            hideSuggestions();
            analyzeDomain();
        }
    });
}

// Handle domain input
function handleDomainInput() {
    const query = domainInput.value.toLowerCase();
    const suggestions = document.querySelectorAll('.suggestion-item');
    
    suggestions.forEach(suggestion => {
        const domain = suggestion.dataset.domain.toLowerCase();
        if (domain.includes(query)) {
            suggestion.style.display = 'block';
        } else {
            suggestion.style.display = 'none';
        }
    });
    
    showSuggestions();
}

// Show/hide suggestions
function showSuggestions() {
    if (domainInput.value.trim()) {
        searchSuggestions.style.display = 'block';
    }
}

function hideSuggestions() {
    setTimeout(() => {
        searchSuggestions.style.display = 'none';
    }, 200);
}

// Load suggestions
function loadSuggestions() {
    // Suggestions are already in HTML
}

// Analyze domain
async function analyzeDomain() {
    const domain = domainInput.value.trim();
    if (!domain) {
        clientLogger.warn('No domain provided for analysis');
        alert('Please enter a domain');
        return;
    }
    
    // Clean domain input
    const cleanDomain = domain.replace(/^https?:\/\//, '').replace(/\/$/, '');
    clientLogger.info(`Starting analysis for domain: ${cleanDomain}`);
    
    hideAllSections();
    showLoading();
    
    try {
        // Get selected engines
        const selectedEngines = getSelectedEngines();
        clientLogger.info(`Selected engines: ${selectedEngines.join(', ')}`);
        
        const startTime = Date.now();
        clientLogger.debug('Sending analysis request to API');
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                domain: cleanDomain,
                engines: selectedEngines
            })
        });
        
        const requestTime = Date.now() - startTime;
        clientLogger.info(`API request completed in ${requestTime}ms`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentAnalysis = data;
        allTechnologies = data.technologies || [];
        filteredTechnologies = [...allTechnologies];
        
        clientLogger.info(`Analysis completed: ${allTechnologies.length} technologies detected`);
        clientLogger.debug('Analysis data received', {
            technologies: allTechnologies.length,
            analysisTime: data.analysis_time,
            engines: data.metadata?.detection_breakdown
        });
        
        displayResults(data);
        
    } catch (error) {
        clientLogger.error('Analysis failed', {
            domain: cleanDomain,
            error: error.message,
            stack: error.stack
        });
        console.error('Analysis failed:', error);
        showError(error.message);
    }
}

// Show loading state
function showLoading() {
    loadingState.style.display = 'block';
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    
    // Simulate progress
    let progress = 0;
    const progressBar = document.getElementById('progressBar');
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressBar.style.width = progress + '%';
    }, 200);
    
    // Store interval ID for cleanup
    loadingState.dataset.intervalId = interval;
}

// Hide loading state
function hideLoading() {
    loadingState.style.display = 'none';
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze';
    
    // Clear progress interval
    const intervalId = loadingState.dataset.intervalId;
    if (intervalId) {
        clearInterval(intervalId);
    }
}

// Show error state
function showError(message) {
    hideLoading();
    errorState.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

// Hide all sections
function hideAllSections() {
    loadingState.style.display = 'none';
    resultsSection.style.display = 'none';
    errorState.style.display = 'none';
}

// Display results
function displayResults(data) {
    hideLoading();
    resultsSection.style.display = 'block';
    resultsSection.classList.add('fade-in');
    
    try {
        updateDomainInfo(data);
        updateOverview(data);
        updateTechnologies();
        updateCharts();
        updateEngines(data);
        updateFilters();
        
        // Show success message
        showMessage('Analysis completed successfully!', 'success');
    } catch (error) {
        console.error('Error displaying results:', error);
        showMessage('Error displaying results: ' + error.message, 'error');
    }
}

// Update domain information
function updateDomainInfo(data) {
    document.getElementById('domainName').textContent = data.url || 'Unknown';
    document.getElementById('finalUrl').textContent = data.final_url || data.url || 'Unknown';
    document.getElementById('analysisTimeDetail').textContent = formatTime(data.analysis_time || 0);
    document.getElementById('errorCount').textContent = data.errors ? data.errors.length : 0;
    
    const statusBadge = document.getElementById('domainStatus');
    statusBadge.textContent = data.errors && data.errors.length > 0 ? 'Error' : 'Success';
    statusBadge.className = `status-badge ${data.errors && data.errors.length > 0 ? 'error' : 'success'}`;
}

// Update overview statistics
function updateOverview(data) {
    const technologies = data.technologies || [];
    
    // Count technologies by category
    const categoryCounts = {};
    technologies.forEach(tech => {
        const category = tech.category || 'Unknown';
        categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });
    
    // Update overview cards
    document.getElementById('cmsCount').textContent = categoryCounts['CMS'] || 0;
    document.getElementById('frameworkCount').textContent = 
        (categoryCounts['Web Frameworks'] || 0) + 
        (categoryCounts['JavaScript Frameworks'] || 0) + 
        (categoryCounts['PHP Frameworks'] || 0);
    document.getElementById('securityCount').textContent = categoryCounts['Security'] || 0;
    document.getElementById('analyticsCount').textContent = 
        (categoryCounts['Analytics'] || 0) + 
        (categoryCounts['Tag Managers'] || 0);
    
    // Update header stats
    document.getElementById('totalTechnologies').textContent = technologies.length;
    document.getElementById('totalCategories').textContent = Object.keys(categoryCounts).length;
    document.getElementById('analysisTime').textContent = formatTime(data.analysis_time || 0);
}

// Update technologies display
function updateTechnologies() {
    const grid = document.getElementById('technologiesGrid');
    grid.innerHTML = '';
    
    if (filteredTechnologies.length === 0) {
        grid.innerHTML = '<div class="no-results">No technologies found matching your filters.</div>';
        return;
    }
    
    filteredTechnologies.forEach(tech => {
        const card = createTechnologyCard(tech);
        grid.appendChild(card);
    });
}

// Create technology card
function createTechnologyCard(tech) {
    const card = document.createElement('div');
    card.className = 'technology-card slide-up';
    
    const confidenceClass = getConfidenceClass(tech.confidence);
    const categoryIcon = getCategoryIcon(tech.category);
    
    // Create unique ID for each card's JSON section
    const jsonId = `json-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    card.innerHTML = `
        <div class="tech-header" onclick="openSidebar(${JSON.stringify(tech).replace(/"/g, '&quot;')})" style="cursor: pointer;">
            <div>
                <div class="tech-name">${tech.name}</div>
                <div class="tech-category"><i class="${categoryIcon}"></i> ${tech.category || 'Unknown'}</div>
            </div>
            <div class="confidence-badge ${confidenceClass}">${tech.confidence}%</div>
        </div>
        
        <div class="tech-details">
            <div class="tech-detail-item">
                <span class="tech-detail-label">Source:</span>
                <span class="tech-detail-value">${tech.source || 'Unknown'}</span>
            </div>
            <div class="tech-detail-item">
                <span class="tech-detail-label">Website:</span>
                <span class="tech-detail-value">
                    ${tech.website ? `<a href="${tech.website}" target="_blank" rel="noopener">${tech.website}</a>` : 'N/A'}
                </span>
            </div>
        </div>
        
        ${tech.versions && tech.versions.length > 0 ? `
            <div class="tech-versions">
                <h4>Versions</h4>
                <div class="version-tags">
                    ${tech.versions.map(version => `<span class="version-tag">${version}</span>`).join('')}
                </div>
            </div>
        ` : ''}
        
        ${tech.evidence && tech.evidence.length > 0 ? `
            <div class="tech-evidence">
                <h4>Evidence</h4>
                ${tech.evidence.slice(0, 3).map(evidence => `
                    <div class="evidence-item">
                        <strong>${evidence.field}:</strong> ${evidence.detail}
                    </div>
                `).join('')}
                ${tech.evidence.length > 3 ? `<div class="evidence-item">... and ${tech.evidence.length - 3} more</div>` : ''}
            </div>
        ` : ''}
        
        <div class="tech-actions">
            <button class="json-toggle-btn" onclick="toggleRawJson('${jsonId}')">
                <i class="fas fa-code"></i> Raw JSON
            </button>
        </div>
        
        <div class="raw-json-section" id="${jsonId}" style="display: none;">
            <div class="json-header">
                <h4><i class="fas fa-database"></i> Raw Detection Data</h4>
                <button class="copy-json-btn" onclick="copyToClipboard('${jsonId}')">
                    <i class="fas fa-copy"></i> Copy JSON
                </button>
            </div>
            <pre class="json-content">${JSON.stringify(tech, null, 2)}</pre>
        </div>
        
        <div class="tech-source">
            <span class="source-badge ${tech.source || 'unknown'}">${tech.source || 'Unknown'}</span>
            <span class="detection-time">${new Date(tech.detection_time * 1000).toLocaleTimeString()}</span>
        </div>
    `;
    
    return card;
}

// Get confidence class
function getConfidenceClass(confidence) {
    if (confidence >= 90) return 'high';
    if (confidence >= 70) return 'medium';
    return 'low';
}

// Get category icon
function getCategoryIcon(category) {
    const icons = {
        'CMS': 'fas fa-cogs',
        'Web Frameworks': 'fas fa-layer-group',
        'JavaScript Frameworks': 'fab fa-js-square',
        'PHP Frameworks': 'fab fa-php',
        'Security': 'fas fa-shield-alt',
        'Analytics': 'fas fa-chart-line',
        'Tag Managers': 'fas fa-tags',
        'Web Servers': 'fas fa-server',
        'Databases': 'fas fa-database',
        'CDN': 'fas fa-cloud',
        'Fonts': 'fas fa-font',
        'UI Frameworks': 'fas fa-palette',
        'E-commerce': 'fas fa-shopping-cart',
        'Blogs': 'fas fa-blog',
        'Message Boards': 'fas fa-comments',
        'Issue Trackers': 'fas fa-bug',
        'Rich Text Editors': 'fas fa-edit',
        'Video Players': 'fas fa-play',
        'DevOps/CI': 'fas fa-tools',
        'Unknown': 'fas fa-question-circle'
    };
    
    return icons[category] || icons['Unknown'];
}

// Update charts
function updateCharts() {
    safeChartUpdate(updateCategoryChart);
    safeChartUpdate(updateConfidenceChart);
}

// Update category chart
function updateCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (window.categoryChart && typeof window.categoryChart.destroy === 'function') {
        window.categoryChart.destroy();
        window.categoryChart = null;
    }
    
    // Count technologies by category
    const categoryCounts = {};
    filteredTechnologies.forEach(tech => {
        const category = tech.category || 'Unknown';
        categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });
    
    const labels = Object.keys(categoryCounts);
    const data = Object.values(categoryCounts);
    
    // Sort by count for better visualization
    const sortedData = labels.map((label, index) => ({
        label,
        count: data[index]
    })).sort((a, b) => b.count - a.count);
    
    const sortedLabels = sortedData.map(item => item.label);
    const sortedCounts = sortedData.map(item => item.count);
    
    window.categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: sortedLabels,
            datasets: [{
                data: sortedCounts,
                backgroundColor: [
                    '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
                    '#00f2fe', '#43e97b', '#38f9d7', '#ffecd2', '#fcb69f',
                    '#a8edea', '#fed6e3', '#d299c2', '#fad0c4', '#ffd1ff'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// Update confidence chart
function updateConfidenceChart() {
    const ctx = document.getElementById('confidenceChart');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (window.confidenceChart && typeof window.confidenceChart.destroy === 'function') {
        window.confidenceChart.destroy();
        window.confidenceChart = null;
    }
    
    const high = filteredTechnologies.filter(tech => tech.confidence >= 90).length;
    const medium = filteredTechnologies.filter(tech => tech.confidence >= 70 && tech.confidence < 90).length;
    const low = filteredTechnologies.filter(tech => tech.confidence < 70).length;
    
    window.confidenceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['High (90-100%)', 'Medium (70-89%)', 'Low (<70%)'],
            datasets: [{
                label: 'Technologies',
                data: [high, medium, low],
                backgroundColor: ['#4ecdc4', '#feca57', '#ff6b6b'],
                borderWidth: 0,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            }
        }
    });
}

// Update engines display
function updateEngines(data) {
    const grid = document.getElementById('enginesGrid');
    grid.innerHTML = '';
    
    const engines = [
        { name: 'Pattern Matching', available: true, icon: 'fas fa-search' },
        { name: 'WhatWeb', available: data.metadata?.detection_breakdown?.whatweb > 0, icon: 'fab fa-linux' },
        { name: 'CMSeeK', available: data.metadata?.detection_breakdown?.cmseek > 0, icon: 'fas fa-bug' },
        { name: 'Additional Patterns', available: data.metadata?.detection_breakdown?.additional_patterns > 0, icon: 'fas fa-plus-circle' },
        { name: 'Deep Analysis', available: data.metadata?.detection_breakdown?.deep_analysis > 0, icon: 'fas fa-microscope' }
    ];
    
    engines.forEach(engine => {
        const card = document.createElement('div');
        card.className = 'engine-card';
        
        card.innerHTML = `
            <div class="engine-icon ${engine.available ? 'available' : 'unavailable'}">
                <i class="${engine.icon}"></i>
            </div>
            <div class="engine-info">
                <h4>${engine.name}</h4>
                <div class="engine-status">${engine.available ? 'Active' : 'Inactive'}</div>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// Update filters
function updateFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const categories = [...new Set(allTechnologies.map(tech => tech.category || 'Unknown'))].sort();
    
    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
}

// Apply filters
function applyFilters() {
    const categoryFilter = document.getElementById('categoryFilter').value;
    const confidenceFilter = document.getElementById('confidenceFilter').value;
    const searchQuery = document.getElementById('searchTech').value.toLowerCase();
    
    filteredTechnologies = allTechnologies.filter(tech => {
        // Category filter
        if (categoryFilter && tech.category !== categoryFilter) {
            return false;
        }
        
        // Confidence filter
        if (confidenceFilter) {
            const [min, max] = confidenceFilter.split('-').map(Number);
            if (tech.confidence < min || tech.confidence > max) {
                return false;
            }
        }
        
        // Search filter
        if (searchQuery && !tech.name.toLowerCase().includes(searchQuery)) {
            return false;
        }
        
        return true;
    });
    
    updateTechnologies();
}

// Retry analysis
function retryAnalysis() {
    analyzeDomain();
}

// Message display function
function showMessage(message, type = 'info') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    messageDiv.textContent = message;
    
    // Add to top of results section
    const resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.insertBefore(messageDiv, resultsSection.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }
}

// Utility functions
function formatNumber(num) {
    return num.toLocaleString();
}

function formatTime(seconds) {
    if (seconds < 60) {
        return `${seconds.toFixed(1)}s`;
    } else {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds.toFixed(1)}s`;
    }
}

// JSON display functions
function toggleRawJson(jsonId) {
    const jsonSection = document.getElementById(jsonId);
    if (!jsonSection) return;
    
    const isVisible = jsonSection.style.display !== 'none';
    jsonSection.style.display = isVisible ? 'none' : 'block';
    
    // Update button text
    const button = jsonSection.previousElementSibling.querySelector('.json-toggle-btn');
    if (button) {
        button.innerHTML = isVisible ? 
            '<i class="fas fa-code"></i> Raw JSON' : 
            '<i class="fas fa-eye-slash"></i> Hide JSON';
    }
}

function copyToClipboard(jsonId) {
    const jsonSection = document.getElementById(jsonId);
    if (!jsonSection) return;
    
    const jsonContent = jsonSection.querySelector('.json-content');
    if (!jsonContent) return;
    
    const text = jsonContent.textContent;
    
    // Use the Clipboard API if available
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showCopySuccess(jsonId);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            fallbackCopyTextToClipboard(text, jsonId);
        });
    } else {
        fallbackCopyTextToClipboard(text, jsonId);
    }
}

function fallbackCopyTextToClipboard(text, jsonId) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopySuccess(jsonId);
        } else {
            showCopyError(jsonId);
        }
    } catch (err) {
        console.error('Fallback copy failed: ', err);
        showCopyError(jsonId);
    }
    
    document.body.removeChild(textArea);
}

function showCopySuccess(jsonId) {
    const button = document.querySelector(`#${jsonId} .copy-json-btn`);
    if (button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        button.style.backgroundColor = '#4CAF50';
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.style.backgroundColor = '';
        }, 2000);
    }
}

function showCopyError(jsonId) {
    const button = document.querySelector(`#${jsonId} .copy-json-btn`);
    if (button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-times"></i> Failed';
        button.style.backgroundColor = '#f44336';
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.style.backgroundColor = '';
        }, 2000);
    }
}

// Error handling for charts
function safeChartUpdate(chartFunction) {
    try {
        chartFunction();
    } catch (error) {
        console.error('Chart update error:', error);
        showMessage('Chart rendering error: ' + error.message, 'error');
    }
}

// Sidebar functionality
function initializeSidebar() {
    const sidebar = document.getElementById('aiSidebar');
    const closeBtn = document.getElementById('closeSidebar');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closeSidebar);
    }
    
    // Close sidebar when clicking outside
    document.addEventListener('click', function(e) {
        if (sidebar && sidebar.classList.contains('open') && 
            !sidebar.contains(e.target) && 
            !e.target.closest('.technology-card')) {
            closeSidebar();
        }
    });
}

function openSidebar(techData) {
    const sidebar = document.getElementById('aiSidebar');
    const loadingDiv = document.getElementById('sidebarLoading');
    const contentDiv = document.getElementById('sidebarContent');
    
    if (!sidebar) return;
    
    // Show loading state
    loadingDiv.style.display = 'block';
    contentDiv.style.display = 'none';
    
    // Open sidebar
    sidebar.classList.add('open');
    
    // Update tech info
    document.getElementById('sidebarTechName').textContent = techData.name || 'Unknown';
    document.getElementById('sidebarTechCategory').textContent = techData.category || 'Unknown';
    document.getElementById('sidebarTechConfidence').textContent = `${techData.confidence || 0}%`;
    
    // Generate AI summary
    generateAISummary(techData);
}

function closeSidebar() {
    const sidebar = document.getElementById('aiSidebar');
    if (sidebar) {
        sidebar.classList.remove('open');
    }
}

function formatAISummary(summary) {
    if (!summary) return '<div class="no-summary">No summary available</div>';
    
    // Convert markdown-like formatting to HTML
    let formatted = summary
        // Convert **bold** to <strong>
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Convert *italic* to <em>
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Convert bullet points to proper list items
        .replace(/^\s*\*\s+/gm, '<li>')
        .replace(/^\s*\+\s+/gm, '<li>')
        // Convert numbered sections to headers
        .replace(/^\*\*(\d+\.\s+.*?)\*\*/gm, '<h4 class="section-header">$1</h4>')
        // Convert subsections
        .replace(/^\*\*(.*?)\*\*:/gm, '<h5 class="subsection-header">$1</h5>')
        // Convert line breaks
        .replace(/\n/g, '<br>')
        // Handle tabs and indentation
        .replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;')
        // Wrap consecutive list items in ul tags
        .replace(/(<li>.*?<\/li>)(\s*<li>.*?<\/li>)*/g, function(match) {
            return '<ul class="ai-list">' + match + '</ul>';
        });
    
    // Split into sections for better organization
    const sections = formatted.split(/<h4 class="section-header">/);
    let result = '';
    
    sections.forEach((section, index) => {
        if (index === 0) {
            result += section;
        } else {
            result += '<div class="ai-section">';
            result += '<h4 class="section-header">' + section;
            result += '</div>';
        }
    });
    
    return result || formatted;
}

async function generateAISummary(techData) {
    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                technology: techData
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Update sidebar content with formatted HTML
        document.getElementById('aiSummaryText').innerHTML = formatAISummary(result.summary || 'No summary available');
        
        // Populate technical details
        populateTechDetails(techData);
        
        // Hide loading, show content
        document.getElementById('sidebarLoading').style.display = 'none';
        document.getElementById('sidebarContent').style.display = 'block';
        
    } catch (error) {
        console.error('Error generating AI summary:', error);
        document.getElementById('aiSummaryText').innerHTML = '<div class="error-message">Error generating AI summary. Please try again.</div>';
        document.getElementById('sidebarLoading').style.display = 'none';
        document.getElementById('sidebarContent').style.display = 'block';
    }
}

function populateTechDetails(techData) {
    const detailsContainer = document.getElementById('sidebarTechDetails');
    let detailsHTML = '';
    
    // Add basic info
    if (techData.website) {
        detailsHTML += `<div class="detail-item">
            <span class="detail-label">Website:</span>
            <span class="detail-value"><a href="${techData.website}" target="_blank" style="color: #4ecdc4;">${techData.website}</a></span>
        </div>`;
    }
    
    if (techData.source) {
        detailsHTML += `<div class="detail-item">
            <span class="detail-label">Source:</span>
            <span class="detail-value">${techData.source}</span>
        </div>`;
    }
    
    if (techData.versions && techData.versions.length > 0) {
        detailsHTML += `<div class="detail-item">
            <span class="detail-label">Versions:</span>
            <span class="detail-value">${techData.versions.join(', ')}</span>
        </div>`;
    }
    
    // Add evidence
    if (techData.evidence && techData.evidence.length > 0) {
        detailsHTML += `<div class="detail-item">
            <span class="detail-label">Evidence:</span>
            <span class="detail-value">${techData.evidence.length} items found</span>
        </div>`;
    }
    
    detailsContainer.innerHTML = detailsHTML;
}

// Enhanced icon mapping with Grok AI suggestions
const enhancedIconMapping = {
    'Telerik UI': 'fas fa-palette',
    'Microsoft ASP.NET': 'fab fa-microsoft',
    'IIS': 'fas fa-server',
    'Windows Server': 'fab fa-windows',
    'Sitefinity': 'fas fa-globe',
    'PHP': 'fab fa-php',
    'Google Analytics': 'fab fa-google',
    'Google Tag Manager': 'fab fa-google',
    'Google Fonts': 'fab fa-google',
    'Cloudflare': 'fas fa-cloud',
    'HSTS': 'fas fa-shield-alt',
    'ASP.NET': 'fab fa-microsoft'
};

// Update getCategoryIcon function to use enhanced mapping
function getCategoryIcon(category) {
    // First check enhanced mapping
    const enhancedIcon = enhancedIconMapping[category];
    if (enhancedIcon) {
        return enhancedIcon;
    }
    
    // Fallback to original mapping
    const iconMap = {
        'Web Framework': 'fas fa-code',
        'CMS': 'fas fa-globe',
        'Web Server': 'fas fa-server',
        'Operating System': 'fas fa-desktop',
        'Analytics': 'fas fa-chart-line',
        'JavaScript Framework': 'fas fa-js',
        'UI Framework': 'fas fa-palette',
        'Database': 'fas fa-database',
        'CDN': 'fas fa-cloud',
        'Security': 'fas fa-shield-alt',
        'Unknown': 'fas fa-question-circle'
    };
    
    return iconMap[category] || 'fas fa-question-circle';
}
