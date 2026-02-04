"""
Speed/Performance Analyzer Module
Analyzes page performance factors
"""

from bs4 import BeautifulSoup


class SpeedAnalyzer:
    """Analyzes page performance factors"""
    
    def __init__(self, soup: BeautifulSoup, response_time: float = None):
        self.soup = soup
        self.response_time = response_time
    
    def analyze(self) -> dict:
        """Perform performance analysis"""
        result = {
            'score': 0,
            'issues': [],
            'recommendations': [],
            'details': {}
        }
        
        score = 100
        
        # Response time analysis
        if self.response_time:
            result['details']['response_time'] = round(self.response_time, 3)
            
            if self.response_time > 3:
                score -= 30
                result['issues'].append({
                    'type': 'critical',
                    'message': f'Page response time is slow ({round(self.response_time, 2)}s)'
                })
                result['recommendations'].append('Improve server response time. Consider caching and CDN')
            elif self.response_time > 1:
                score -= 15
                result['issues'].append({
                    'type': 'warning',
                    'message': f'Page response time could be improved ({round(self.response_time, 2)}s)'
                })
        
        # Count external scripts
        external_scripts = self.soup.find_all('script', src=True)
        inline_scripts = self.soup.find_all('script', src=False)
        
        result['details']['external_scripts'] = len(external_scripts)
        result['details']['inline_scripts'] = len(inline_scripts)
        
        if len(external_scripts) > 10:
            score -= 15
            result['issues'].append({
                'type': 'warning',
                'message': f'Too many external scripts ({len(external_scripts)})'
            })
            result['recommendations'].append('Combine and minify JavaScript files')
        
        # Count stylesheets
        stylesheets = self.soup.find_all('link', rel='stylesheet')
        inline_styles = self.soup.find_all('style')
        
        result['details']['external_stylesheets'] = len(stylesheets)
        result['details']['inline_styles'] = len(inline_styles)
        
        if len(stylesheets) > 5:
            score -= 10
            result['issues'].append({
                'type': 'info',
                'message': f'Multiple stylesheets detected ({len(stylesheets)})'
            })
            result['recommendations'].append('Combine CSS files to reduce HTTP requests')
        
        # Check for render-blocking resources
        head = self.soup.find('head')
        if head:
            head_scripts = head.find_all('script', src=True)
            blocking_scripts = [s for s in head_scripts if not s.get('defer') and not s.get('async')]
            
            result['details']['render_blocking_scripts'] = len(blocking_scripts)
            
            if blocking_scripts:
                score -= 10
                result['issues'].append({
                    'type': 'warning',
                    'message': f'{len(blocking_scripts)} render-blocking scripts in <head>'
                })
                result['recommendations'].append('Add defer or async attribute to non-critical scripts')
        
        # Check for preload/preconnect hints
        preloads = self.soup.find_all('link', rel='preload')
        preconnects = self.soup.find_all('link', rel='preconnect')
        
        result['details']['preload_hints'] = len(preloads)
        result['details']['preconnect_hints'] = len(preconnects)
        
        # Check for meta viewport (mobile optimization)
        viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        result['details']['has_viewport'] = bool(viewport)
        
        if not viewport:
            score -= 15
            result['issues'].append({
                'type': 'warning',
                'message': 'Missing viewport meta tag for mobile optimization'
            })
            result['recommendations'].append('Add <meta name="viewport" content="width=device-width, initial-scale=1">')
        
        # Check for charset
        charset = self.soup.find('meta', charset=True) or self.soup.find('meta', attrs={'http-equiv': 'Content-Type'})
        result['details']['has_charset'] = bool(charset)
        
        if not charset:
            result['issues'].append({
                'type': 'info',
                'message': 'Missing charset declaration'
            })
            result['recommendations'].append('Add <meta charset="UTF-8"> at the top of <head>')
        
        # Estimate page weight (very rough estimate)
        html_length = len(str(self.soup))
        result['details']['html_size_bytes'] = html_length
        result['details']['html_size_kb'] = round(html_length / 1024, 2)
        
        if html_length > 100000:  # 100KB
            score -= 10
            result['issues'].append({
                'type': 'info',
                'message': f'Large HTML document ({round(html_length/1024)}KB)'
            })
            result['recommendations'].append('Consider reducing HTML size by removing unnecessary code')
        
        result['score'] = max(0, min(100, score))
        return result
