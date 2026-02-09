/**
 * SEO Audit Tool - Main Application
 * Handles form submission, API calls, and result rendering
 */

// API Configuration
const API_BASE_URL = window.location.origin;

// DOM Elements
const elements = {
    form: document.getElementById('analyze-form'),
    urlInput: document.getElementById('url-input'),
    keywordInput: document.getElementById('keyword-input'),
    analyzeBtn: document.getElementById('analyze-btn'),
    btnContent: document.querySelector('.btn-content'),
    btnLoader: document.querySelector('.btn-loader'),
    errorContainer: document.getElementById('error-container'),
    errorMessage: document.getElementById('error-message'),
    errorClose: document.getElementById('error-close'),
    resultsSection: document.getElementById('results-section'),
    overallScore: document.getElementById('overall-score'),
    scoreProgress: document.getElementById('score-progress'),
    scoreGrade: document.getElementById('score-grade'),
    analyzedUrl: document.getElementById('analyzed-url'),
    highIssues: document.getElementById('high-issues'),
    mediumIssues: document.getElementById('medium-issues'),
    lowIssues: document.getElementById('low-issues'),
    categoryCards: document.getElementById('category-cards'),
    issuesList: document.getElementById('issues-list'),
    recommendationsList: document.getElementById('recommendations-list'),
    exportPdfBtn: document.getElementById('export-pdf-btn'),
    exportJsonBtn: document.getElementById('export-json-btn')
};

// Current analysis data
let currentAnalysis = null;

/**
 * Initialize the application
 */
function init() {
    // Form submission
    elements.form.addEventListener('submit', handleFormSubmit);

    // Error close button
    elements.errorClose.addEventListener('click', hideError);

    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', handleTabClick);
    });

    // Export buttons
    elements.exportPdfBtn.addEventListener('click', () => {
        if (currentAnalysis) {
            window.SEOExport.generatePDFReport(currentAnalysis);
        }
    });

    elements.exportJsonBtn.addEventListener('click', () => {
        if (currentAnalysis) {
            window.SEOExport.exportAsJSON(currentAnalysis);
        }
    });
}

/**
 * Handle form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    const url = elements.urlInput.value.trim();
    const keyword = elements.keywordInput.value.trim();

    if (!url) {
        showError('Please enter a URL to analyze');
        return;
    }

    await analyzeURL(url, keyword);
}

/**
 * Analyze URL via API
 */
async function analyzeURL(url, keyword = '') {
    setLoading(true);
    hideError();
    elements.resultsSection.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, keyword })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Analysis failed');
        }

        currentAnalysis = data;
        renderResults(data);

    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze URL. Please try again.');
    } finally {
        setLoading(false);
    }
}

/**
 * Set loading state
 */
function setLoading(isLoading) {
    elements.analyzeBtn.disabled = isLoading;
    elements.btnContent.style.display = isLoading ? 'none' : 'flex';
    elements.btnLoader.classList.toggle('hidden', !isLoading);
}

/**
 * Show error message
 */
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorContainer.classList.remove('hidden');
    elements.errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Hide error message
 */
function hideError() {
    elements.errorContainer.classList.add('hidden');
}

/**
 * Render analysis results
 */
function renderResults(data) {
    // Show results section
    elements.resultsSection.classList.remove('hidden');

    // Scroll to results
    setTimeout(() => {
        elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    // Update score
    animateScore(data.overall_score);

    // Update grade
    elements.scoreGrade.textContent = `Grade ${data.grade}`;
    elements.scoreGrade.style.color = getGradeColor(data.grade);

    // Update URL
    elements.analyzedUrl.textContent = data.url;

    // Update summary stats
    elements.highIssues.textContent = data.summary.high_priority;
    elements.mediumIssues.textContent = data.summary.medium_priority;
    elements.lowIssues.textContent = data.summary.low_priority;

    // Render category cards
    renderCategoryCards(data.analysis, data.summary.category_scores);

    // Render issues
    renderIssues(data.priority_issues, 'high');

    // Render recommendations
    renderRecommendations(data.recommendations);

    // Update charts
    window.SEOCharts.updateCharts(data);
}

/**
 * Get grade color
 */
function getGradeColor(grade) {
    const colors = {
        'A': '#10b981',
        'B': '#06b6d4',
        'C': '#f59e0b',
        'D': '#f97316',
        'F': '#ef4444'
    };
    return colors[grade] || '#94a3b8';
}

/**
 * Animate score counter
 */
function animateScore(targetScore) {
    const scoreElement = elements.overallScore;
    const progressElement = elements.scoreProgress;
    const duration = 1500;
    const startTime = performance.now();

    // Calculate stroke offset (circumference = 2 * PI * 85)
    const circumference = 534;
    const offset = circumference - (targetScore / 100) * circumference;

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out cubic
        const easeProgress = 1 - Math.pow(1 - progress, 3);

        const currentScore = Math.round(easeProgress * targetScore);
        scoreElement.textContent = currentScore;

        const currentOffset = circumference - (easeProgress * targetScore / 100) * circumference;
        progressElement.style.strokeDashoffset = currentOffset;

        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }

    requestAnimationFrame(animate);
}

/**
 * Render category cards
 */
function renderCategoryCards(analysis, categoryScores) {
    const container = elements.categoryCards;
    container.innerHTML = '';

    const categories = Object.keys(categoryScores);

    categories.forEach(category => {
        const score = categoryScores[category];
        const data = analysis[category] || {};
        const issues = data.issues?.length || 0;
        const color = window.SEOCharts.getScoreColor(score);
        const iconClass = window.SEOCharts.CATEGORY_ICONS[category] || 'fa-chart-bar';
        const name = window.SEOCharts.CATEGORY_NAMES[category] || category;

        const card = document.createElement('div');
        card.className = 'category-card';
        card.innerHTML = `
            <div class="category-header">
                <div class="category-icon-box">
                    <i class="fas ${iconClass}"></i>
                </div>
                <span class="category-score ${color}">${score}</span>
            </div>
            <h4 class="category-name">${name}</h4>
            <div class="category-bar">
                <div class="category-bar-fill ${color}" style="width: 0%"></div>
            </div>
            <div class="category-issues">${issues} issue${issues !== 1 ? 's' : ''} found</div>
        `;

        container.appendChild(card);

        // Animate bar fill
        setTimeout(() => {
            card.querySelector('.category-bar-fill').style.width = `${score}%`;
        }, 100);
    });
}

/**
 * Render issues list
 */
function renderIssues(priorityIssues, priority = 'high') {
    const container = elements.issuesList;
    container.innerHTML = '';

    const issues = priorityIssues[priority] || [];

    if (issues.length === 0) {
        container.innerHTML = `
            <div class="issue-item">
                <span class="issue-badge ${priority}">${getPriorityLabel(priority)}</span>
                <div class="issue-content">
                    <p class="issue-message">No ${getPriorityLabel(priority).toLowerCase()} issues found! 🎉</p>
                </div>
            </div>
        `;
        return;
    }

    issues.forEach(issue => {
        const item = document.createElement('div');
        item.className = 'issue-item';
        item.innerHTML = `
            <span class="issue-badge ${priority}">${getPriorityLabel(priority)}</span>
            <div class="issue-content">
                <p class="issue-category">${issue.category}</p>
                <p class="issue-message">${issue.message}</p>
            </div>
        `;
        container.appendChild(item);
    });
}

/**
 * Get priority label
 */
function getPriorityLabel(priority) {
    const labels = {
        'high': 'Critical',
        'medium': 'Warning',
        'low': 'Notice'
    };
    return labels[priority] || priority;
}

/**
 * Handle tab click for issues
 */
function handleTabClick(e) {
    const tab = e.target.closest('.tab-btn').dataset.tab;

    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });

    // Render issues for selected priority
    if (currentAnalysis?.priority_issues) {
        renderIssues(currentAnalysis.priority_issues, tab);
    }
}

/**
 * Render recommendations list
 */
function renderRecommendations(recommendations) {
    const container = elements.recommendationsList;
    container.innerHTML = '';

    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No recommendations at this time.</p>';
        return;
    }

    // Show top 10 recommendations
    const topRecs = recommendations.slice(0, 10);

    topRecs.forEach((rec, index) => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';
        item.innerHTML = `
            <span class="recommendation-number">${index + 1}</span>
            <div class="recommendation-content">
                <p class="recommendation-category">${rec.category}</p>
                <p class="recommendation-text">${rec.recommendation}</p>
            </div>
        `;
        container.appendChild(item);
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
