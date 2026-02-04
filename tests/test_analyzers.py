"""
Unit Tests for SEO Analyzers
Run with: python -m pytest tests/ -v
"""

import pytest
from bs4 import BeautifulSoup

# Import analyzers
import sys
sys.path.insert(0, '..')
from analyzers.title_analyzer import TitleAnalyzer
from analyzers.meta_analyzer import MetaAnalyzer
from analyzers.url_analyzer import URLAnalyzer
from analyzers.heading_analyzer import HeadingAnalyzer
from analyzers.content_analyzer import ContentAnalyzer
from analyzers.image_analyzer import ImageAnalyzer
from analyzers.seo_scorer import SEOScorer


# ============================================
# Test Fixtures
# ============================================

@pytest.fixture
def good_html():
    """HTML with good SEO practices"""
    return BeautifulSoup("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultimate Guide to Python Programming | MyBlog</title>
        <meta name="description" content="Learn Python programming from scratch with our comprehensive guide. Discover best practices, tips, and real-world examples to become a Python expert.">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>Ultimate Guide to Python Programming</h1>
        <h2>Getting Started</h2>
        <p>Python is a versatile programming language that's great for beginners and experts alike.</p>
        <h3>Installing Python</h3>
        <p>First, download Python from the official website...</p>
        <h2>Basic Concepts</h2>
        <h3>Variables and Data Types</h3>
        <p>Variables in Python are easy to use...</p>
        <img src="python-logo.webp" alt="Python programming language logo" width="200" height="200">
        <a href="/other-article">Read more about programming</a>
        <a href="https://python.org" rel="noopener">Official Python Website</a>
    </body>
    </html>
    """, 'lxml')


@pytest.fixture
def bad_html():
    """HTML with SEO issues"""
    return BeautifulSoup("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hi</title>
    </head>
    <body>
        <h1>First Title</h1>
        <h1>Second Title</h1>
        <h3>Skipped H2</h3>
        <p>Short content.</p>
        <img src="IMG_1234.jpg">
    </body>
    </html>
    """, 'lxml')


@pytest.fixture
def no_title_html():
    """HTML without title tag"""
    return BeautifulSoup("""
    <!DOCTYPE html>
    <html>
    <head></head>
    <body><p>No title here</p></body>
    </html>
    """, 'lxml')


# ============================================
# Title Analyzer Tests
# ============================================

class TestTitleAnalyzer:
    
    def test_good_title(self, good_html):
        """Test analysis of a good title"""
        analyzer = TitleAnalyzer(good_html)
        result = analyzer.analyze()
        
        assert result['exists'] == True
        assert result['score'] >= 70
        assert 'Ultimate Guide' in result['value']
        assert result['length'] > 30
    
    def test_short_title(self, bad_html):
        """Test detection of short title"""
        analyzer = TitleAnalyzer(bad_html)
        result = analyzer.analyze()
        
        assert result['exists'] == True
        assert result['score'] < 80  # Should be penalized
        assert len(result['issues']) > 0
        assert any('short' in issue['message'].lower() for issue in result['issues'])
    
    def test_missing_title(self, no_title_html):
        """Test detection of missing title"""
        analyzer = TitleAnalyzer(no_title_html)
        result = analyzer.analyze()
        
        assert result['exists'] == False
        assert result['score'] == 0
        assert len(result['issues']) > 0


# ============================================
# Meta Analyzer Tests
# ============================================

class TestMetaAnalyzer:
    
    def test_good_meta(self, good_html):
        """Test analysis of good meta description"""
        analyzer = MetaAnalyzer(good_html)
        result = analyzer.analyze()
        
        assert result['exists'] == True
        assert result['score'] >= 70
        assert result['length'] > 100
    
    def test_missing_meta(self, bad_html):
        """Test detection of missing meta description"""
        analyzer = MetaAnalyzer(bad_html)
        result = analyzer.analyze()
        
        assert result['exists'] == False
        assert result['score'] == 0


# ============================================
# URL Analyzer Tests
# ============================================

class TestURLAnalyzer:
    
    def test_good_url(self):
        """Test analysis of good URL"""
        analyzer = URLAnalyzer('https://example.com/python-guide')
        result = analyzer.analyze()
        
        assert result['details']['is_https'] == True
        assert result['score'] >= 70
    
    def test_http_url(self):
        """Test detection of non-HTTPS URL"""
        analyzer = URLAnalyzer('http://example.com/page')
        result = analyzer.analyze()
        
        assert result['details']['is_https'] == False
        assert any('HTTPS' in issue['message'] for issue in result['issues'])
    
    def test_double_extension(self):
        """Test detection of double file extension"""
        analyzer = URLAnalyzer('https://example.com/page.html.html')
        result = analyzer.analyze()
        
        assert result['details'].get('double_extension') == True
        assert result['score'] < 80
    
    def test_underscore_in_url(self):
        """Test detection of underscores in URL"""
        analyzer = URLAnalyzer('https://example.com/my_page_here')
        result = analyzer.analyze()
        
        assert result['details']['has_underscores'] == True


# ============================================
# Heading Analyzer Tests
# ============================================

class TestHeadingAnalyzer:
    
    def test_good_headings(self, good_html):
        """Test analysis of good heading structure"""
        analyzer = HeadingAnalyzer(good_html)
        result = analyzer.analyze()
        
        assert result['h1_count'] == 1
        assert result['score'] >= 80
        assert result['details']['proper_hierarchy'] == True
    
    def test_multiple_h1(self, bad_html):
        """Test detection of multiple H1 tags"""
        analyzer = HeadingAnalyzer(bad_html)
        result = analyzer.analyze()
        
        assert result['h1_count'] > 1
        assert result['score'] < 80
        assert any('Multiple H1' in issue['message'] for issue in result['issues'])
    
    def test_skipped_hierarchy(self, bad_html):
        """Test detection of skipped heading levels"""
        analyzer = HeadingAnalyzer(bad_html)
        result = analyzer.analyze()
        
        # H3 without H2
        assert result['details']['proper_hierarchy'] == False


# ============================================
# Content Analyzer Tests
# ============================================

class TestContentAnalyzer:
    
    def test_content_word_count(self, good_html):
        """Test word count calculation"""
        analyzer = ContentAnalyzer(good_html)
        result = analyzer.analyze()
        
        assert result['word_count'] > 0
        assert 'word_count' in result['details']
    
    def test_thin_content(self, bad_html):
        """Test detection of thin content"""
        analyzer = ContentAnalyzer(bad_html)
        result = analyzer.analyze()
        
        assert result['word_count'] < 300
        assert any('thin' in issue['message'].lower() or 'words' in issue['message'].lower() 
                   for issue in result['issues'])


# ============================================
# Image Analyzer Tests
# ============================================

class TestImageAnalyzer:
    
    def test_image_with_alt(self, good_html):
        """Test detection of images with alt text"""
        analyzer = ImageAnalyzer(good_html)
        result = analyzer.analyze()
        
        assert result['total_images'] > 0
        assert result['details']['with_alt'] > 0
    
    def test_image_without_alt(self, bad_html):
        """Test detection of images without alt text"""
        analyzer = ImageAnalyzer(bad_html)
        result = analyzer.analyze()
        
        assert result['total_images'] > 0
        assert result['details']['without_alt'] > 0


# ============================================
# SEO Scorer Tests
# ============================================

class TestSEOScorer:
    
    def test_score_calculation(self):
        """Test overall score calculation"""
        scorer = SEOScorer()
        scorer.set_results({
            'title': {'score': 80, 'issues': []},
            'meta_description': {'score': 70, 'issues': []},
            'url_structure': {'score': 90, 'issues': []},
            'headings': {'score': 85, 'issues': []},
            'content': {'score': 75, 'issues': []},
            'images': {'score': 60, 'issues': []},
            'links': {'score': 70, 'issues': []},
            'performance': {'score': 80, 'issues': []}
        })
        
        score = scorer.calculate_overall_score()
        assert 60 <= score <= 100
    
    def test_grade_calculation(self):
        """Test grade assignment"""
        scorer = SEOScorer()
        
        assert scorer.get_grade(95) == 'A'
        assert scorer.get_grade(85) == 'B'
        assert scorer.get_grade(75) == 'C'
        assert scorer.get_grade(65) == 'D'
        assert scorer.get_grade(50) == 'F'
    
    def test_priority_issues(self):
        """Test issue prioritization"""
        scorer = SEOScorer()
        scorer.set_results({
            'title': {
                'score': 30,
                'issues': [{'type': 'critical', 'message': 'Critical issue'}]
            },
            'content': {
                'score': 80,
                'issues': [{'type': 'info', 'message': 'Minor issue'}]
            }
        })
        
        priority = scorer.get_priority_issues()
        
        assert len(priority['high']) > 0
        assert len(priority['low']) > 0


# ============================================
# Integration Test
# ============================================

class TestIntegration:
    
    def test_full_analysis_pipeline(self, good_html):
        """Test complete analysis pipeline"""
        results = {}
        
        # Run all analyzers
        title_analyzer = TitleAnalyzer(good_html)
        results['title'] = title_analyzer.analyze()
        
        meta_analyzer = MetaAnalyzer(good_html)
        results['meta_description'] = meta_analyzer.analyze()
        
        heading_analyzer = HeadingAnalyzer(good_html)
        results['headings'] = heading_analyzer.analyze()
        
        content_analyzer = ContentAnalyzer(good_html)
        results['content'] = content_analyzer.analyze()
        
        image_analyzer = ImageAnalyzer(good_html)
        results['images'] = image_analyzer.analyze()
        
        # Calculate score
        scorer = SEOScorer()
        scorer.set_results(results)
        
        summary = scorer.get_summary()
        
        assert summary['overall_score'] > 0
        assert summary['categories_analyzed'] > 0
        assert 'category_scores' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
