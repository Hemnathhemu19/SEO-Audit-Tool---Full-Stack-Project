"""
SEO Audit Tool - Flask Application
Main API server for the SEO analysis tool
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from utils.crawler import WebCrawler
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

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Initialize components
crawler = WebCrawler(timeout=15)


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
        
        # Calculate overall score
        scorer = SEOScorer()
        scorer.set_results(results)
        
        summary = scorer.get_summary()
        priority_issues = scorer.get_priority_issues()
        all_recommendations = scorer.get_all_recommendations()
        
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
            'meta': {
                'response_time': response_time,
                'analyzed_at': None  # Could add timestamp
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
    ╔══════════════════════════════════════════╗
    ║       🔍 SEO Audit Tool v1.0.0           ║
    ║                                          ║
    ║   Server running at:                     ║
    ║   http://localhost:{port}                   ║
    ║                                          ║
    ║   API Endpoints:                         ║
    ║   POST /api/analyze    - Full SEO audit  ║
    ║   GET  /api/health     - Health check    ║
    ╚══════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
