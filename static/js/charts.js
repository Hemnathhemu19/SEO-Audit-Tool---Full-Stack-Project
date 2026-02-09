/**
 * Chart.js Configuration for SEO Audit Tool
 * Light theme dashboard charts
 */

// Chart.js default configuration
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#64748b';
    Chart.defaults.borderColor = '#e2e8f0';
    Chart.defaults.font.family = 'Poppins, sans-serif';
}

// Chart instances
let categoryChart = null;
let issuesChart = null;
let contentBreakdownChart = null;

/**
 * Category icons mapping
 */
const CATEGORY_ICONS = {
    title: 'fa-heading',
    meta_description: 'fa-align-left',
    url_structure: 'fa-link',
    headings: 'fa-list-ol',
    content: 'fa-file-alt',
    images: 'fa-image',
    links: 'fa-project-diagram',
    performance: 'fa-tachometer-alt'
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
 * Vibrant color palette for charts
 */
const CHART_COLORS = [
    '#6366f1', // Indigo
    '#8b5cf6', // Purple
    '#ec4899', // Pink
    '#06b6d4', // Cyan
    '#10b981', // Green
    '#f59e0b', // Orange
    '#3b82f6', // Blue
    '#ef4444'  // Red
];

/**
 * Get score color
 */
function getScoreColor(score) {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
}

/**
 * Create content breakdown donut chart
 */
function createContentBreakdownChart(categoryScores) {
    const ctx = document.getElementById('content-breakdown-chart');
    if (!ctx) return;

    if (contentBreakdownChart) {
        contentBreakdownChart.destroy();
    }

    const labels = Object.keys(categoryScores).map(key => CATEGORY_NAMES[key] || key);
    const data = Object.values(categoryScores);

    contentBreakdownChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: CHART_COLORS,
                borderWidth: 0,
                hoverOffset: 10,
                spacing: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#94a3b8',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function (context) {
                            return `${context.label}: ${context.raw}/100`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create category bar chart
 */
function createCategoryChart(categoryScores) {
    const ctx = document.getElementById('category-chart');
    if (!ctx) return;

    if (categoryChart) {
        categoryChart.destroy();
    }

    const labels = Object.keys(categoryScores).map(key => CATEGORY_NAMES[key] || key);
    const data = Object.values(categoryScores);

    categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score',
                data: data,
                backgroundColor: CHART_COLORS,
                borderRadius: 6,
                barThickness: 24
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: '#f1f5f9'
                    },
                    ticks: {
                        font: { size: 11 }
                    }
                },
                y: {
                    grid: { display: false },
                    ticks: {
                        font: { size: 11, weight: 500 }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1e293b',
                    padding: 12,
                    cornerRadius: 8,
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
 * Create issues breakdown chart
 */
function createIssuesChart(priorityIssues) {
    const ctx = document.getElementById('issues-chart');
    if (!ctx) return;

    if (issuesChart) {
        issuesChart.destroy();
    }

    const highCount = priorityIssues.high?.length || 0;
    const mediumCount = priorityIssues.medium?.length || 0;
    const lowCount = priorityIssues.low?.length || 0;

    issuesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Critical', 'Warnings', 'Notices'],
            datasets: [{
                data: [highCount, mediumCount, lowCount],
                backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
                borderRadius: 8,
                barThickness: 40
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: { stepSize: 1 }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1e293b',
                    padding: 12,
                    cornerRadius: 8
                }
            }
        }
    });
}

/**
 * Update all charts
 */
function updateCharts(analysisData) {
    if (analysisData.summary?.category_scores) {
        createContentBreakdownChart(analysisData.summary.category_scores);
        createCategoryChart(analysisData.summary.category_scores);
    }

    if (analysisData.priority_issues) {
        createIssuesChart(analysisData.priority_issues);
    }
}

// Export functions
window.SEOCharts = {
    CATEGORY_ICONS,
    CATEGORY_NAMES,
    CHART_COLORS,
    getScoreColor,
    createContentBreakdownChart,
    createCategoryChart,
    createIssuesChart,
    updateCharts
};
