// Global variables
let currentAnalysis = null;
let allTechnologies = [];
let filteredTechnologies = [];

// DOM elements
const domainInput = document.getElementById('domainInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const searchSuggestions = document.getElementById('searchSuggestions');
const loadingState = document.getElementById('loadingState');
const resultsSection = document.getElementById('resultsSection');
const errorState = document.getElementById('errorState');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadSuggestions();
    hideAllSections();
});

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
        alert('Please enter a domain');
        return;
    }
    
    // Clean domain input
    const cleanDomain = domain.replace(/^https?:\/\//, '').replace(/\/$/, '');
    
    hideAllSections();
    showLoading();
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain: cleanDomain })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentAnalysis = data;
        allTechnologies = data.technologies || [];
        filteredTechnologies = [...allTechnologies];
        
        displayResults(data);
        
    } catch (error) {
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
    document.getElementById('analysisTimeDetail').textContent = `${data.analysis_time || 0}s`;
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
    document.getElementById('analysisTime').textContent = `${data.analysis_time || 0}s`;
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
    
    card.innerHTML = `
        <div class="tech-header">
            <div>
                <div class="tech-name">${tech.name}</div>
                <div class="tech-category">${categoryIcon} ${tech.category || 'Unknown'}</div>
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
    if (window.categoryChart) {
        window.categoryChart.destroy();
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
    if (window.confidenceChart) {
        window.confidenceChart.destroy();
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

// Error handling for charts
function safeChartUpdate(chartFunction) {
    try {
        chartFunction();
    } catch (error) {
        console.error('Chart update error:', error);
        showMessage('Chart rendering error: ' + error.message, 'error');
    }
}
