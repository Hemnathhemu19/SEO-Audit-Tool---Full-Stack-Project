"""
URL Structure Analyzer Module
Analyzes URL for SEO best practices
"""

from urllib.parse import urlparse
import re


class URLAnalyzer:
    """Analyzes URL structure for SEO optimization"""
    
    MAX_LENGTH = 75
    OPTIMAL_MAX = 60
    
    def __init__(self, url: str):
        self.url = url
        self.parsed = urlparse(url)
    
    def analyze(self) -> dict:
        """Perform complete URL analysis"""
        result = {
            'score': 0,
            'value': self.url,
            'path': self.parsed.path,
            'length': len(self.url),
            'issues': [],
            'recommendations': [],
            'details': {}
        }
        
        score = 100
        path = self.parsed.path
        
        # Check HTTPS
        result['details']['is_https'] = self.parsed.scheme == 'https'
        if self.parsed.scheme != 'https':
            score -= 20
            result['issues'].append({
                'type': 'critical',
                'message': 'URL is not using HTTPS'
            })
            result['recommendations'].append('Migrate to HTTPS for security and SEO benefits')
        
        # URL length
        url_length = len(self.url)
        result['details']['length'] = url_length
        
        if url_length > self.MAX_LENGTH:
            score -= 15
            result['issues'].append({
                'type': 'warning',
                'message': f'URL is too long ({url_length} chars). Keep under {self.OPTIMAL_MAX} chars'
            })
            result['recommendations'].append('Shorten your URL by removing unnecessary words')
        
        # Check for underscores (should use hyphens)
        if '_' in path:
            score -= 10
            result['issues'].append({
                'type': 'warning',
                'message': 'URL contains underscores. Use hyphens instead'
            })
            result['recommendations'].append('Replace underscores with hyphens in URLs')
            result['details']['has_underscores'] = True
        else:
            result['details']['has_underscores'] = False
        
        # Check for special characters
        special_chars = re.findall(r'[^a-zA-Z0-9\-\/\.]', path)
        if special_chars:
            score -= 10
            result['details']['special_chars'] = list(set(special_chars))
            result['issues'].append({
                'type': 'warning',
                'message': f'URL contains special characters: {", ".join(set(special_chars))}'
            })
            result['recommendations'].append('Remove special characters from URL')
        
        # Check for uppercase letters
        if path != path.lower():
            score -= 5
            result['details']['has_uppercase'] = True
            result['issues'].append({
                'type': 'info',
                'message': 'URL contains uppercase letters. Use lowercase only'
            })
            result['recommendations'].append('Convert URL to lowercase')
        else:
            result['details']['has_uppercase'] = False
        
        # Check for double extensions (.html.html)
        if '.html.html' in path or '.php.php' in path:
            score -= 30
            result['issues'].append({
                'type': 'critical',
                'message': 'URL contains double file extension (e.g., .html.html)'
            })
            result['recommendations'].append('Fix URL configuration to remove duplicate extensions')
            result['details']['double_extension'] = True
        
        # Check for keyword in URL
        result['details']['path_segments'] = [seg for seg in path.split('/') if seg]
        
        # Check for dates in URL (may limit evergreen content)
        date_pattern = r'/\d{4}/\d{2}/'
        if re.search(date_pattern, path):
            result['details']['has_date'] = True
            result['issues'].append({
                'type': 'info',
                'message': 'URL contains date structure. This may make content appear outdated'
            })
        else:
            result['details']['has_date'] = False
        
        # Check for parameters
        if self.parsed.query:
            score -= 10
            result['details']['has_parameters'] = True
            result['issues'].append({
                'type': 'info',
                'message': 'URL contains query parameters'
            })
            result['recommendations'].append('Use clean URLs without query parameters when possible')
        else:
            result['details']['has_parameters'] = False
        
        result['score'] = max(0, min(100, score))
        return result
