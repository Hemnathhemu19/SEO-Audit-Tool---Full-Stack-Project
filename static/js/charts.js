/**
 * Chart.js Configuration for SEO Audit Tool
 * Premium dark theme styling
 */

// Chart.js default configuration
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(148, 163, 184, 0.1)';
    Chart.defaults.font.family = 'Plus Jakarta Sans, system-ui, sans-serif';
}

// Chart instances
let categoryChart = null;
let issuesChart = null;

/**
 * Category icons mapping (Font Awesome classes)
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
                backgroundColor: colors.map(c => c + '40'),
                borderColor: colors,
                borderWidth: 2,
                borderRadius: 8,
                barThickness: 28
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
                        color: 'rgba(148, 163, 184, 0.05)'
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12,
                            weight: 500
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(148, 163, 184, 0.2)',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
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
            labels: ['Critical', 'Warnings', 'Notices'],
            datasets: [{
                data: [highCount, mediumCount, lowCount],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(16, 185, 129, 0.7)'
                ],
                borderColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#10b981'
                ],
                borderWidth: 2,
                hoverOffset: 8,
                spacing: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: {
                            size: 12,
                            weight: 500
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(148, 163, 184, 0.2)',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
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
