"""
Meta Description Analyzer Module
Analyzes meta description for SEO best practices
"""

from bs4 import BeautifulSoup


class MetaAnalyzer:
    """Analyzes meta description for SEO optimization"""
    
    MIN_LENGTH = 120
    MAX_LENGTH = 160
    OPTIMAL_MIN = 150
    OPTIMAL_MAX = 160
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.meta_description = ""
        self.og_description = ""
        self._extract_meta()
    
    def _extract_meta(self):
        """Extract meta description from HTML"""
        # Standard meta description
        meta_tag = self.soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            self.meta_description = meta_tag.get('content', '').strip()
        
        # Open Graph description
        og_tag = self.soup.find('meta', attrs={'property': 'og:description'})
        if og_tag:
            self.og_description = og_tag.get('content', '').strip()
    
    def analyze(self) -> dict:
        """Perform complete meta description analysis"""
        result = {
            'score': 0,
            'value': self.meta_description,
            'og_description': self.og_description,
            'length': len(self.meta_description),
            'exists': bool(self.meta_description),
            'issues': [],
            'recommendations': [],
            'details': {}
        }
        
        if not self.meta_description:
            result['issues'].append({
                'type': 'critical',
                'message': 'No meta description found'
            })
            result['recommendations'].append('Add a compelling meta description (150-160 characters)')
            result['score'] = 0
            return result
        
        score = 100
        length = len(self.meta_description)
        result['details']['length'] = length
        
        # Length analysis
        if length < self.MIN_LENGTH:
            score -= 25
            result['issues'].append({
                'type': 'warning',
                'message': f'Meta description is too short ({length} chars). Optimal: {self.OPTIMAL_MIN}-{self.OPTIMAL_MAX} chars'
            })
            result['recommendations'].append(f'Expand your meta description to {self.OPTIMAL_MIN}-{self.OPTIMAL_MAX} characters')
        elif length > self.MAX_LENGTH:
            score -= 15
            result['issues'].append({
                'type': 'warning',
                'message': f'Meta description is too long ({length} chars). It may be truncated'
            })
            result['recommendations'].append(f'Shorten meta description to under {self.MAX_LENGTH} characters')
        else:
            result['details']['length_status'] = 'optimal'
        
        # Check for call-to-action words
        cta_words = ['learn', 'discover', 'find', 'get', 'read', 'try', 'start', 'explore', 'see', 'click']
        has_cta = any(word in self.meta_description.lower() for word in cta_words)
        result['details']['has_cta'] = has_cta
        
        if not has_cta:
            score -= 10
            result['recommendations'].append('Add a call-to-action like "Learn more", "Discover", or "Get started"')
        
        # Check for Open Graph consistency
        if self.og_description:
            result['details']['has_og_description'] = True
            if self.og_description != self.meta_description:
                result['details']['og_matches'] = False
        else:
            result['details']['has_og_description'] = False
            result['recommendations'].append('Add Open Graph meta description for better social sharing')
        
        # Check if description ends with ellipsis (truncated)
        if self.meta_description.endswith('...'):
            score -= 10
            result['issues'].append({
                'type': 'info',
                'message': 'Meta description appears to be truncated'
            })
        
        result['score'] = max(0, min(100, score))
        return result
