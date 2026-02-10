"""
SEO Audit Tool - Flask Application
Main API server for the SEO analysis tool
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests as http_requests
import base64

from utils.crawler import WebCrawler
from utils.history_manager import HistoryManager
from analyzers import (
    TitleAnalyzer,
    MetaAnalyzer,
    URLAnalyzer,
    HeadingAnalyzer,
    ContentAnalyzer,
    ImageAnalyzer,
    LinkAnalyzer,
    SpeedAnalyzer,
    SEOScorer
)
from analyzers.keyword_analyzer import KeywordAnalyzer
from analyzers.social_analyzer import SocialAnalyzer
from analyzers.mobile_analyzer import MobileAnalyzer
from analyzers.schema_analyzer import SchemaAnalyzer
from analyzers.link_checker import LinkChecker
from analyzers.security_analyzer import SecurityAnalyzer
from analyzers.sitemap_analyzer import SitemapAnalyzer
from analyzers.vitals_analyzer import VitalsAnalyzer
from analyzers.i18n_analyzer import I18nAnalyzer
from analyzers.readability_analyzer import ReadabilityAnalyzer

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Initialize components
crawler = WebCrawler(timeout=15)
history = HistoryManager()


@app.route('/')
def serve_index():
    """Serve the main HTML page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'SEO Audit Tool',
        'version': '1.0.0'
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    """
    Main SEO analysis endpoint
    
    Request Body:
        {
            "url": "https://example.com/page",
            "keyword": "optional target keyword"
        }
    
    Returns:
        Complete SEO analysis report
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        url = data['url'].strip()
        target_keyword = data.get('keyword', '').strip() or None
        
        # Fetch the page
        fetch_result = crawler.fetch_page(url)
        
        if not fetch_result['success']:
            return jsonify({
                'success': False,
                'error': fetch_result['error'],
                'url': fetch_result['url']
            }), 400
        
        soup = fetch_result['soup']
        response_time = fetch_result.get('response_time')
        response_headers = fetch_result.get('response_headers', {})
        analyzed_url = fetch_result['url']
        
        # Run all analyzers
        results = {}
        
        # Title Analysis
        title_analyzer = TitleAnalyzer(soup)
        results['title'] = title_analyzer.analyze()
        
        # Meta Description Analysis
        meta_analyzer = MetaAnalyzer(soup)
        results['meta_description'] = meta_analyzer.analyze()
        
        # URL Structure Analysis
        url_analyzer = URLAnalyzer(analyzed_url)
        results['url_structure'] = url_analyzer.analyze()
        
        # Heading Analysis
        heading_analyzer = HeadingAnalyzer(soup)
        results['headings'] = heading_analyzer.analyze()
        
        # Content Analysis
        content_analyzer = ContentAnalyzer(soup, target_keyword)
        results['content'] = content_analyzer.analyze()
        
        # Image Analysis
        image_analyzer = ImageAnalyzer(soup)
        results['images'] = image_analyzer.analyze()
        
        # Link Analysis
        link_analyzer = LinkAnalyzer(soup, analyzed_url)
        results['links'] = link_analyzer.analyze()
        
        # Speed/Performance Analysis
        speed_analyzer = SpeedAnalyzer(soup, response_time)
        results['performance'] = speed_analyzer.analyze()
        
        # Keyword Density Analysis (NEW)
        keyword_analyzer = KeywordAnalyzer(soup, target_keyword)
        results['keyword'] = keyword_analyzer.analyze()
        
        # Social Media Analysis (NEW)
        social_analyzer = SocialAnalyzer(soup, analyzed_url)
        results['social'] = social_analyzer.analyze()
        
        # Mobile-Friendly Analysis (NEW)
        mobile_analyzer = MobileAnalyzer(soup)
        results['mobile'] = mobile_analyzer.analyze()
        
        # Schema Markup Analysis (NEW)
        schema_analyzer = SchemaAnalyzer(soup)
        results['schema'] = schema_analyzer.analyze()
        
        # Broken Link Check (NEW)
        link_checker = LinkChecker(soup, analyzed_url)
        results['broken_links'] = link_checker.analyze()
        
        # Security Analysis (NEW)
        security_analyzer = SecurityAnalyzer(soup, analyzed_url, response_headers)
        results['security'] = security_analyzer.analyze()
        
        # Sitemap & Robots.txt (NEW)
        sitemap_analyzer = SitemapAnalyzer(analyzed_url)
        results['sitemap'] = sitemap_analyzer.analyze()
        
        # Core Web Vitals (NEW)
        vitals_analyzer = VitalsAnalyzer(soup, response_time)
        results['vitals'] = vitals_analyzer.analyze()
        
        # i18n Check (NEW)
        i18n_analyzer = I18nAnalyzer(soup)
        results['i18n'] = i18n_analyzer.analyze()
        
        # Readability Analysis (NEW)
        readability = ReadabilityAnalyzer(soup)
        results['readability'] = readability.analyze()
        
        # Calculate overall score
        scorer = SEOScorer()
        scorer.set_results(results)
        
        summary = scorer.get_summary()
        priority_issues = scorer.get_priority_issues()
        all_recommendations = scorer.get_all_recommendations()
        
        # Save to history
        try:
            history.save_scan(
                url=analyzed_url,
                score=summary['overall_score'],
                grade=scorer.get_grade(),
                category_scores=summary.get('category_scores')
            )
        except Exception:
            pass  # Don't fail analysis if history save fails
        
        # Build response
        response = {
            'success': True,
            'url': analyzed_url,
            'overall_score': summary['overall_score'],
            'grade': scorer.get_grade(),
            'score_color': scorer.get_score_color(),
            'analysis': results,
            'summary': summary,
            'priority_issues': priority_issues,
            'recommendations': all_recommendations,
            'keyword_analysis': results.get('keyword'),
            'social_preview': results.get('social'),
            'mobile_friendly': results.get('mobile'),
            'schema_data': results.get('schema'),
            'broken_links_data': results.get('broken_links'),
            'security_data': results.get('security'),
            'sitemap_data': results.get('sitemap'),
            'vitals_data': results.get('vitals'),
            'i18n_data': results.get('i18n'),
            'readability_data': results.get('readability'),
            'meta': {
                'response_time': response_time,
                'analyzed_at': None
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500


@app.route('/api/quick-check', methods=['POST'])
def quick_check():
    """
    Quick URL validation and basic info
    Returns basic page info without full analysis
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        url = data['url'].strip()
        validation = crawler.validate_url(url)
        
        if not validation['is_valid']:
            return jsonify({
                'success': False,
                'error': validation['error']
            }), 400
        
        return jsonify({
            'success': True,
            'url': validation['url'],
            'is_valid': True
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compare', methods=['POST'])
def compare_urls():
    """
    Competitor Comparison Endpoint
    Compares SEO scores between two URLs
    
    Request Body:
        {
            "url": "https://yoursite.com",
            "competitor_url": "https://competitor.com",
            "keyword": "optional target keyword"
        }
    
    Returns:
        Side-by-side comparison of SEO metrics
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data or 'competitor_url' not in data:
            return jsonify({
                'success': False,
                'error': 'Both url and competitor_url are required'
            }), 400
        
        url1 = data['url'].strip()
        url2 = data['competitor_url'].strip()
        target_keyword = data.get('keyword', '').strip() or None
        
        # Analyze both URLs
        def analyze_single(url):
            fetch_result = crawler.fetch_page(url)
            if not fetch_result['success']:
                return {'success': False, 'error': fetch_result['error'], 'url': url}
            
            soup = fetch_result['soup']
            response_time = fetch_result.get('response_time')
            
            # Run analyzers
            results = {
                'title': TitleAnalyzer(soup).analyze(),
                'meta_description': MetaAnalyzer(soup).analyze(),
                'url_structure': URLAnalyzer(url).analyze(),
                'headings': HeadingAnalyzer(soup).analyze(),
                'content': ContentAnalyzer(soup, target_keyword).analyze(),
                'images': ImageAnalyzer(soup).analyze(),
                'links': LinkAnalyzer(soup, url).analyze(),
                'performance': SpeedAnalyzer(soup, response_time).analyze(),
                'keyword': KeywordAnalyzer(soup, target_keyword).analyze(),
                'social': SocialAnalyzer(soup, url).analyze(),
                'mobile': MobileAnalyzer(soup).analyze()
            }
            
            scorer = SEOScorer()
            scorer.set_results(results)
            
            return {
                'success': True,
                'url': url,
                'overall_score': scorer.get_summary()['overall_score'],
                'grade': scorer.get_grade(),
                'category_scores': scorer.get_summary()['category_scores'],
                'keyword_score': results['keyword']['score'],
                'social_score': results['social']['score'],
                'mobile_score': results['mobile']['score'],
                'issues_count': {
                    'high': len(scorer.get_priority_issues()['high']),
                    'medium': len(scorer.get_priority_issues()['medium']),
                    'low': len(scorer.get_priority_issues()['low'])
                }
            }
        
        # Analyze both
        your_site = analyze_single(url1)
        competitor = analyze_single(url2)
        
        if not your_site['success']:
            return jsonify({'success': False, 'error': f"Failed to analyze your URL: {your_site['error']}"}), 400
        if not competitor['success']:
            return jsonify({'success': False, 'error': f"Failed to analyze competitor: {competitor['error']}"}), 400
        
        # Calculate differences
        score_diff = your_site['overall_score'] - competitor['overall_score']
        
        # Build comparison
        comparison = {
            'categories': {}
        }
        
        for cat in your_site['category_scores']:
            your_score = your_site['category_scores'].get(cat, 0)
            comp_score = competitor['category_scores'].get(cat, 0)
            comparison['categories'][cat] = {
                'your_site': your_score,
                'competitor': comp_score,
                'difference': your_score - comp_score,
                'winner': 'you' if your_score > comp_score else ('competitor' if comp_score > your_score else 'tie')
            }
        
        return jsonify({
            'success': True,
            'your_site': your_site,
            'competitor': competitor,
            'score_difference': score_diff,
            'winner': 'your_site' if score_diff > 0 else ('competitor' if score_diff < 0 else 'tie'),
            'comparison': comparison
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Comparison failed: {str(e)}'
        }), 500



@app.route('/api/history', methods=['GET'])
def get_history():
    """Get scan history, optionally filtered by URL."""
    url = request.args.get('url')
    try:
        records = history.get_history(url=url)
        return jsonify({'success': True, 'history': records})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/history/trend', methods=['GET'])
def get_trend():
    """Get score trend for a specific URL."""
    url = request.args.get('url')
    if not url:
        return jsonify({'success': False, 'error': 'URL parameter required'}), 400
    try:
        trend = history.get_trend(url)
        return jsonify({'success': True, 'trend': trend})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/screenshot', methods=['POST'])
def take_screenshot():
    """
    Capture a screenshot of a URL using a free API.
    Returns base64-encoded image.
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        
        # Use free screenshot API
        api_url = f'https://image.thum.io/get/width/1280/crop/720/noanimate/{url}'
        
        resp = http_requests.get(api_url, timeout=15)
        if resp.status_code == 200:
            img_base64 = base64.b64encode(resp.content).decode('utf-8')
            return jsonify({
                'success': True,
                'screenshot': f'data:image/png;base64,{img_base64}',
                'url': url
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Screenshot service unavailable'
            }), 502
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Screenshot failed: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║       🔍 SEO Audit Tool v2.0.0               ║
    ║                                              ║
    ║   Server running at:                         ║
    ║   http://localhost:{port}                       ║
    ║                                              ║
    ║   API Endpoints:                             ║
    ║   POST /api/analyze    - Full SEO audit      ║
    ║   POST /api/compare    - Compare URLs        ║
    ║   POST /api/screenshot - Page screenshot     ║
    ║   GET  /api/history    - Scan history        ║
    ║   GET  /api/health     - Health check        ║
    ╚══════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
