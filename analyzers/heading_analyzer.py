"""
Heading Structure Analyzer Module
Analyzes H1-H6 heading hierarchy for SEO
"""

from bs4 import BeautifulSoup


class HeadingAnalyzer:
    """Analyzes heading structure for SEO optimization"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        self._extract_headings()
    
    def _extract_headings(self):
        """Extract all headings from HTML"""
        for level in self.headings.keys():
            tags = self.soup.find_all(level)
            self.headings[level] = [tag.get_text().strip() for tag in tags]
    
    def analyze(self) -> dict:
        """Perform complete heading analysis"""
        result = {
            'score': 0,
            'headings': self.headings,
            'h1_count': len(self.headings['h1']),
            'total_headings': sum(len(h) for h in self.headings.values()),
            'issues': [],
            'recommendations': [],
            'details': {}
        }
        
        score = 100
        
        # H1 Analysis
        h1_count = len(self.headings['h1'])
        result['details']['h1_count'] = h1_count
        
        if h1_count == 0:
            score -= 40
            result['issues'].append({
                'type': 'critical',
                'message': 'No H1 tag found on the page'
            })
            result['recommendations'].append('Add a single, descriptive H1 tag that includes your main keyword')
        elif h1_count > 1:
            score -= 25
            result['issues'].append({
                'type': 'warning',
                'message': f'Multiple H1 tags found ({h1_count}). Use only one H1 per page'
            })
            result['recommendations'].append('Keep only one H1 tag and convert others to H2')
            result['details']['multiple_h1'] = True
        else:
            result['details']['h1_text'] = self.headings['h1'][0] if self.headings['h1'] else ''
            
            # Check H1 length
            if self.headings['h1']:
                h1_length = len(self.headings['h1'][0])
                result['details']['h1_length'] = h1_length
                if h1_length > 70:
                    score -= 10
                    result['issues'].append({
                        'type': 'info',
                        'message': 'H1 tag is quite long. Consider making it more concise'
                    })
        
        # H2 Analysis
        h2_count = len(self.headings['h2'])
        result['details']['h2_count'] = h2_count
        
        if h2_count == 0:
            score -= 15
            result['issues'].append({
                'type': 'warning',
                'message': 'No H2 tags found. Use H2s to structure your content'
            })
            result['recommendations'].append('Add H2 headings to organize your content into sections')
        
        # Check heading hierarchy
        has_hierarchy_issue = False
        
        # Check if H3 exists without H2
        if len(self.headings['h3']) > 0 and len(self.headings['h2']) == 0:
            has_hierarchy_issue = True
            score -= 15
            result['issues'].append({
                'type': 'warning',
                'message': 'H3 tags exist without any H2. Maintain proper heading hierarchy'
            })
        
        # Check if H4 exists without H3
        if len(self.headings['h4']) > 0 and len(self.headings['h3']) == 0:
            has_hierarchy_issue = True
            score -= 10
            result['issues'].append({
                'type': 'info',
                'message': 'H4 tags exist without H3. Consider review heading structure'
            })
        
        result['details']['proper_hierarchy'] = not has_hierarchy_issue
        
        # Calculate heading distribution
        result['details']['hierarchy'] = {
            'h1': h1_count,
            'h2': len(self.headings['h2']),
            'h3': len(self.headings['h3']),
            'h4': len(self.headings['h4']),
            'h5': len(self.headings['h5']),
            'h6': len(self.headings['h6'])
        }
        
        # Bonus for good structure
        if h1_count == 1 and h2_count >= 2 and not has_hierarchy_issue:
            result['details']['well_structured'] = True
        else:
            result['details']['well_structured'] = False
        
        result['score'] = max(0, min(100, score))
        return result
