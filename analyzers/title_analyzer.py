"""
Title Tag Analyzer Module
Analyzes the <title> tag for SEO best practices
"""

from bs4 import BeautifulSoup


class TitleAnalyzer:
    """Analyzes page title for SEO optimization"""
    
    # Optimal title length range
    MIN_LENGTH = 30
    MAX_LENGTH = 60
    OPTIMAL_MIN = 50
    OPTIMAL_MAX = 60
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.title = None
        self.title_text = ""
        self._extract_title()
    
    def _extract_title(self):
        """Extract title tag from HTML"""
        self.title = self.soup.find('title')
        if self.title:
            self.title_text = self.title.get_text().strip()
    
    def analyze(self) -> dict:
        """Perform complete title analysis"""
        result = {
            'score': 0,
            'value': self.title_text,
            'length': len(self.title_text),
            'exists': bool(self.title),
            'issues': [],
            'recommendations': [],
            'details': {}
        }
        
        if not self.title:
            result['issues'].append({
                'type': 'critical',
                'message': 'No title tag found'
            })
            result['recommendations'].append('Add a descriptive title tag to your page')
            return result
        
        if not self.title_text:
            result['issues'].append({
                'type': 'critical',
                'message': 'Title tag is empty'
            })
            result['recommendations'].append('Add content to your title tag')
            return result
        
        # Calculate score based on multiple factors
        score = 100
        length = len(self.title_text)
        result['details']['length'] = length
        
        # Length analysis
        if length < self.MIN_LENGTH:
            score -= 30
            result['issues'].append({
                'type': 'warning',
                'message': f'Title is too short ({length} chars). Optimal: {self.OPTIMAL_MIN}-{self.OPTIMAL_MAX} chars'
            })
            result['recommendations'].append(f'Expand your title to {self.OPTIMAL_MIN}-{self.OPTIMAL_MAX} characters')
        elif length > self.MAX_LENGTH:
            score -= 20
            result['issues'].append({
                'type': 'warning', 
                'message': f'Title is too long ({length} chars). It may be truncated in search results'
            })
            result['recommendations'].append(f'Shorten your title to under {self.MAX_LENGTH} characters')
        elif length >= self.OPTIMAL_MIN and length <= self.OPTIMAL_MAX:
            result['details']['length_status'] = 'optimal'
        else:
            result['details']['length_status'] = 'acceptable'
            score -= 5
        
        # Check for keyword at beginning (first 10 chars usually important)
        result['details']['starts_with_keyword'] = len(self.title_text.split()) > 0
        
        # Check for branding pipe separator
        if '|' in self.title_text or '-' in self.title_text:
            result['details']['has_separator'] = True
        else:
            result['details']['has_separator'] = False
            result['recommendations'].append('Consider adding brand name with separator (e.g., "Title | Brand")')
        
        # Check for numbers (often improve CTR)
        has_numbers = any(char.isdigit() for char in self.title_text)
        result['details']['has_numbers'] = has_numbers
        
        # Check for power words
        power_words = ['ultimate', 'guide', 'best', 'top', 'how', 'why', 'what', 'complete', 'essential', 'proven', 'free']
        has_power_words = any(word in self.title_text.lower() for word in power_words)
        result['details']['has_power_words'] = has_power_words
        
        if not has_power_words:
            result['recommendations'].append('Consider adding power words like "Ultimate", "Complete", "Guide" to improve CTR')
        
        # Final score adjustment
        result['score'] = max(0, min(100, score))
        
        return result
