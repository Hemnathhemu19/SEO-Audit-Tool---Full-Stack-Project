/**
 * SEO Audit Tool - Main Application
 * Dashboard with page navigation
 */

const API_BASE_URL = window.location.origin;

// DOM Elements
const elements = {
    // Navigation
    navItems: document.querySelectorAll('.nav-item'),
    pages: document.querySelectorAll('.page'),
    navReport: document.getElementById('nav-report'),

    // Analyzer Form
    form: document.getElementById('analyze-form'),
    urlInput: document.getElementById('url-input'),
    keywordInput: document.getElementById('keyword-input'),
    analyzeBtn: document.getElementById('analyze-btn'),
    btnContent: document.querySelector('.btn-content'),
    btnLoader: document.querySelector('.btn-loader'),
    errorContainer: document.getElementById('error-container'),
    errorMessage: document.getElementById('error-message'),
    errorClose: document.getElementById('error-close'),

    // Report Page
    analyzedUrlDisplay: document.getElementById('analyzed-url-display'),
    overallScore: document.getElementById('overall-score'),
    mainAuditCircle: document.getElementById('main-audit-circle'),
    subCircle1: document.getElementById('sub-circle-1'),
    subCircle2: document.getElementById('sub-circle-2'),
    subCircle3: document.getElementById('sub-circle-3'),
    subScore1: document.getElementById('sub-score-1'),
    subScore2: document.getElementById('sub-score-2'),
    subScore3: document.getElementById('sub-score-3'),
    issuesList: document.getElementById('issues-list'),
    recommendationsList: document.getElementById('recommendations-list'),
    exportPdfBtn: document.getElementById('export-pdf-btn'),
    exportJsonBtn: document.getElementById('export-json-btn')
};

let currentAnalysis = null;

/**
 * Initialize the application
 */
function init() {
    // Navigation
    elements.navItems.forEach(item => {
        item.addEventListener('click', handleNavClick);
    });

    // Form submission
    elements.form.addEventListener('submit', handleFormSubmit);

    // Error close
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
 * Handle navigation click
 */
function handleNavClick(e) {
    e.preventDefault();
    const page = e.currentTarget.dataset.page;

    // Update active nav
    elements.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });

    // Show page
    elements.pages.forEach(p => {
        p.classList.toggle('active', p.id === `${page}-page`);
        p.classList.toggle('hidden', p.id !== `${page}-page`);
    });
}

/**
 * Switch to report page
 */
function switchToReportPage() {
    elements.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.page === 'report');
    });

    document.getElementById('analyzer-page').classList.remove('active');
    document.getElementById('analyzer-page').classList.add('hidden');
    document.getElementById('report-page').classList.add('active');
    document.getElementById('report-page').classList.remove('hidden');
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
 * Analyze URL
 */
async function analyzeURL(url, keyword = '') {
    setLoading(true);
    hideError();

    try {
        const response = await fetch(`${API_BASE_URL}/api/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, keyword })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Analysis failed');
        }

        currentAnalysis = data;
        renderResults(data);
        switchToReportPage();

    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze URL');
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
 * Show error
 */
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorContainer.classList.remove('hidden');
}

/**
 * Hide error
 */
function hideError() {
    elements.errorContainer.classList.add('hidden');
}

/**
 * Render results
 */
function renderResults(data) {
    // Update URL display
    elements.analyzedUrlDisplay.textContent = data.url;

    // Animate main score circle
    animateCircle(elements.mainAuditCircle, data.overall_score, 251);
    elements.overallScore.textContent = `${data.overall_score}%`;

    // Get category scores for sub circles
    const scores = data.summary?.category_scores || {};
    const scoreValues = Object.values(scores);

    // Calculate sub scores (average of different categories)
    const titleMeta = Math.round(((scores.title || 0) + (scores.meta_description || 0)) / 2);
    const structureContent = Math.round(((scores.url_structure || 0) + (scores.content || 0) + (scores.headings || 0)) / 3);
    const mediaLinks = Math.round(((scores.images || 0) + (scores.links || 0) + (scores.performance || 0)) / 3);

    animateCircle(elements.subCircle1, titleMeta, 151);
    animateCircle(elements.subCircle2, structureContent, 151);
    animateCircle(elements.subCircle3, mediaLinks, 151);

    elements.subScore1.textContent = `${titleMeta}%`;
    elements.subScore2.textContent = `${structureContent}%`;
    elements.subScore3.textContent = `${mediaLinks}%`;

    // Update charts
    window.SEOCharts.updateCharts(data);

    // Render issues
    renderIssues(data.priority_issues, 'high');

    // Render recommendations
    renderRecommendations(data.recommendations);

    // Update progress bars based on scores
    updateProgressBars(data);
}

/**
 * Animate SVG circle
 */
function animateCircle(element, score, circumference) {
    if (!element) return;

    const offset = circumference - (score / 100) * circumference;

    setTimeout(() => {
        element.style.strokeDashoffset = offset;
    }, 100);
}

/**
 * Update progress bars
 */
function updateProgressBars(data) {
    const scores = data.summary?.category_scores || {};

    // Update metric bars in logo card
    const metricBars = document.querySelectorAll('.metric-bar .bar-fill');
    if (metricBars[0]) metricBars[0].style.width = `${scores.title || 0}%`;
    if (metricBars[1]) metricBars[1].style.width = `${scores.content || 0}%`;
    if (metricBars[2]) metricBars[2].style.width = `${scores.links || 0}%`;

    // Update speed bars
    const speedBars = document.querySelectorAll('.speed-bar .bar-progress');
    if (speedBars[0]) speedBars[0].style.width = `${scores.performance || 0}%`;
    if (speedBars[1]) speedBars[1].style.width = `${scores.content || 0}%`;
    if (speedBars[2]) speedBars[2].style.width = `${scores.url_structure || 0}%`;

    // Update URL bars
    const urlBars = document.querySelectorAll('.url-bar .bar-fill');
    if (urlBars[0]) urlBars[0].style.width = `${scores.meta_description || 0}%`;
    if (urlBars[1]) urlBars[1].style.width = `${scores.headings || 0}%`;
    if (urlBars[2]) urlBars[2].style.width = `${scores.images || 0}%`;
    if (urlBars[3]) urlBars[3].style.width = `${scores.url_structure || 0}%`;
}

/**
 * Render issues
 */
function renderIssues(priorityIssues, priority = 'high') {
    const container = elements.issuesList;
    container.innerHTML = '';

    const issues = priorityIssues[priority] || [];

    if (issues.length === 0) {
        container.innerHTML = `
            <div class="issue-item ${priority}">
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
        item.className = `issue-item ${priority}`;
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
    const labels = { 'high': 'Critical', 'medium': 'Warning', 'low': 'Notice' };
    return labels[priority] || priority;
}

/**
 * Handle tab click
 */
function handleTabClick(e) {
    const tab = e.target.closest('.tab-btn').dataset.tab;

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });

    if (currentAnalysis?.priority_issues) {
        renderIssues(currentAnalysis.priority_issues, tab);
    }
}

/**
 * Render recommendations
 */
function renderRecommendations(recommendations) {
    const container = elements.recommendationsList;
    container.innerHTML = '';

    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">No recommendations at this time.</p>';
        return;
    }

    recommendations.slice(0, 8).forEach((rec, index) => {
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
