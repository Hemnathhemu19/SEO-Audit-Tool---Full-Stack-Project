/**
 * PDF Export Module for SEO Audit Tool
 * Generates PDF reports using jsPDF
 */

/**
 * Generate PDF report from analysis data
 */
function generatePDFReport(analysisData) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    let yPos = 20;
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 20;
    const contentWidth = pageWidth - (margin * 2);

    // Helper function to add new page if needed
    function checkPageBreak(requiredSpace = 30) {
        if (yPos + requiredSpace > 270) {
            doc.addPage();
            yPos = 20;
            return true;
        }
        return false;
    }

    // Title
    doc.setFontSize(24);
    doc.setTextColor(99, 102, 241);
    doc.text('SEO Audit Report', margin, yPos);
    yPos += 15;

    // URL
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.text(`URL: ${analysisData.url}`, margin, yPos);
    yPos += 8;
    doc.text(`Generated: ${new Date().toLocaleString()}`, margin, yPos);
    yPos += 15;

    // Overall Score Box
    doc.setFillColor(26, 26, 36);
    doc.roundedRect(margin, yPos, contentWidth, 35, 3, 3, 'F');

    doc.setFontSize(18);
    doc.setTextColor(255, 255, 255);
    doc.text('Overall SEO Score', margin + 10, yPos + 15);

    // Score with color
    const score = analysisData.overall_score;
    if (score >= 80) {
        doc.setTextColor(16, 185, 129);
    } else if (score >= 60) {
        doc.setTextColor(245, 158, 11);
    } else {
        doc.setTextColor(239, 68, 68);
    }

    doc.setFontSize(28);
    doc.text(`${score}/100`, pageWidth - margin - 40, yPos + 20);

    doc.setFontSize(14);
    doc.text(`Grade: ${analysisData.grade}`, pageWidth - margin - 40, yPos + 30);

    yPos += 45;

    // Summary Stats
    doc.setFontSize(14);
    doc.setTextColor(255, 255, 255);
    doc.text('Issues Summary', margin, yPos);
    yPos += 10;

    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);

    const summary = analysisData.summary;
    doc.text(`High Priority: ${summary.high_priority}`, margin, yPos);
    doc.text(`Medium Priority: ${summary.medium_priority}`, margin + 60, yPos);
    doc.text(`Low Priority: ${summary.low_priority}`, margin + 130, yPos);
    yPos += 15;

    // Category Scores
    doc.setFontSize(14);
    doc.setTextColor(255, 255, 255);
    doc.text('Category Breakdown', margin, yPos);
    yPos += 10;

    doc.setFontSize(10);
    const categoryNames = {
        title: 'Title Tag',
        meta_description: 'Meta Description',
        url_structure: 'URL Structure',
        headings: 'Headings',
        content: 'Content',
        images: 'Images',
        links: 'Links',
        performance: 'Performance'
    };

    Object.entries(analysisData.summary.category_scores).forEach(([key, value]) => {
        checkPageBreak(10);

        const name = categoryNames[key] || key;

        // Score color
        if (value >= 80) {
            doc.setTextColor(16, 185, 129);
        } else if (value >= 60) {
            doc.setTextColor(245, 158, 11);
        } else {
            doc.setTextColor(239, 68, 68);
        }

        doc.text(`${name}: ${value}/100`, margin, yPos);
        yPos += 7;
    });

    yPos += 10;

    // High Priority Issues
    checkPageBreak(30);
    doc.setFontSize(14);
    doc.setTextColor(239, 68, 68);
    doc.text('High Priority Issues', margin, yPos);
    yPos += 10;

    doc.setFontSize(9);
    doc.setTextColor(100, 100, 100);

    if (analysisData.priority_issues.high.length === 0) {
        doc.text('No high priority issues found!', margin, yPos);
        yPos += 7;
    } else {
        analysisData.priority_issues.high.forEach((issue, index) => {
            checkPageBreak(15);
            const text = `${index + 1}. [${issue.category}] ${issue.message}`;
            const lines = doc.splitTextToSize(text, contentWidth);
            doc.text(lines, margin, yPos);
            yPos += lines.length * 5 + 3;
        });
    }

    yPos += 10;

    // Recommendations
    checkPageBreak(30);
    doc.setFontSize(14);
    doc.setTextColor(99, 102, 241);
    doc.text('Top Recommendations', margin, yPos);
    yPos += 10;

    doc.setFontSize(9);
    doc.setTextColor(100, 100, 100);

    const topRecs = analysisData.recommendations.slice(0, 10);
    topRecs.forEach((rec, index) => {
        checkPageBreak(15);
        const text = `${index + 1}. [${rec.category}] ${rec.recommendation}`;
        const lines = doc.splitTextToSize(text, contentWidth);
        doc.text(lines, margin, yPos);
        yPos += lines.length * 5 + 3;
    });

    // Footer
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(128, 128, 128);
        doc.text(
            `SEO Audit Tool - Page ${i} of ${pageCount}`,
            pageWidth / 2,
            285,
            { align: 'center' }
        );
    }

    // Save the PDF
    const filename = `seo-audit-${new URL(analysisData.url).hostname}-${Date.now()}.pdf`;
    doc.save(filename);
}

/**
 * Export data as JSON file
 */
function exportAsJSON(analysisData) {
    const dataStr = JSON.stringify(analysisData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `seo-audit-${new URL(analysisData.url).hostname}-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Export functions
window.SEOExport = {
    generatePDFReport,
    exportAsJSON
};
