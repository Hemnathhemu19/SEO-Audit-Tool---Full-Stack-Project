/**
 * Chart.js Configuration for SEO Audit Tool
 * Creates category breakdown and issues distribution charts
 */

// Chart.js default configuration
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#a0a0b0';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.08)';
    Chart.defaults.font.family = 'Inter, sans-serif';
}

// Chart instances
let categoryChart = null;
let issuesChart = null;

/**
 * Category icons mapping
 */
const CATEGORY_ICONS = {
    title: '📝',
    meta_description: '📋',
    url_structure: '🔗',
    headings: '📑',
    content: '📄',
    images: '🖼️',
    links: '🔗',
    performance: '⚡'
};

/**
 * Category display names
 */
const CATEGORY_NAMES = {
    title: 'Title Tag',
    meta_description: 'Meta Description',
    url_structure: 'URL Structure',
    headings: 'Headings',
    content: 'Content',
    images: 'Images',
    links: 'Links',
    performance: 'Performance'
};

/**
 * Get score color class
 */
function getScoreColor(score) {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    return 'red';
}

/**
 * Get score color hex value
 */
function getScoreColorHex(score) {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
}

/**
 * Create category breakdown bar chart
 */
function createCategoryChart(categoryScores) {
    const ctx = document.getElementById('category-chart');
    if (!ctx) return;

    // Destroy existing chart
    if (categoryChart) {
        categoryChart.destroy();
    }

    const labels = Object.keys(categoryScores).map(key => CATEGORY_NAMES[key] || key);
    const data = Object.values(categoryScores);
    const colors = data.map(score => getScoreColorHex(score));

    categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score',
                data: data,
                backgroundColor: colors.map(c => c + '80'),
                borderColor: colors,
                borderWidth: 2,
                borderRadius: 6,
                barThickness: 30
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1a1a24',
                    titleColor: '#ffffff',
                    bodyColor: '#a0a0b0',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function (context) {
                            return `Score: ${context.raw}/100`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create issues distribution doughnut chart
 */
function createIssuesChart(priorityIssues) {
    const ctx = document.getElementById('issues-chart');
    if (!ctx) return;

    // Destroy existing chart
    if (issuesChart) {
        issuesChart.destroy();
    }

    const highCount = priorityIssues.high?.length || 0;
    const mediumCount = priorityIssues.medium?.length || 0;
    const lowCount = priorityIssues.low?.length || 0;

    issuesChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['High Priority', 'Medium Priority', 'Low Priority'],
            datasets: [{
                data: [highCount, mediumCount, lowCount],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(16, 185, 129, 0.8)'
                ],
                borderColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#10b981'
                ],
                borderWidth: 2,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: '#1a1a24',
                    titleColor: '#ffffff',
                    bodyColor: '#a0a0b0',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function (context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? Math.round((context.raw / total) * 100) : 0;
                            return `${context.raw} issues (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update all charts with new data
 */
function updateCharts(analysisData) {
    if (analysisData.summary?.category_scores) {
        createCategoryChart(analysisData.summary.category_scores);
    }

    if (analysisData.priority_issues) {
        createIssuesChart(analysisData.priority_issues);
    }
}

// Export functions for use in app.js
window.SEOCharts = {
    CATEGORY_ICONS,
    CATEGORY_NAMES,
    getScoreColor,
    getScoreColorHex,
    createCategoryChart,
    createIssuesChart,
    updateCharts
};
