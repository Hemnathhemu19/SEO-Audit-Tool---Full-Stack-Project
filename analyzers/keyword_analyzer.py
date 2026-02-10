"""
Keyword Density Analyzer
Analyzes keyword usage and density throughout the page
"""

import re
from collections import Counter
from bs4 import BeautifulSoup


class KeywordAnalyzer:
    """Analyzes keyword density and usage on a webpage"""
    
    def __init__(self, soup: BeautifulSoup, target_keyword: str = None):
        self.soup = soup
        self.target_keyword = target_keyword.lower().strip() if target_keyword else None
        self.issues = []
        self.recommendations = []
        
    def analyze(self) -> dict:
        """Run complete keyword analysis"""
        # Get all text content
        text_content = self._get_text_content()
        words = self._tokenize(text_content)
        
        # Calculate word frequency
        word_freq = Counter(words)
        total_words = len(words)
        
        # Get top keywords
        top_keywords = self._get_top_keywords(word_freq, total_words)
        
        # Initialize result
        result = {
            'total_words': total_words,
            'unique_words': len(word_freq),
            'top_keywords': top_keywords,
            'target_keyword_analysis': None,
            'score': 70,  # Base score
            'issues': [],
            'recommendations': []
        }
        
        # Analyze target keyword if provided
        if self.target_keyword:
            result['target_keyword_analysis'] = self._analyze_target_keyword(words, word_freq, total_words)
            result['score'] = self._calculate_keyword_score(result['target_keyword_analysis'])
        
        result['issues'] = self.issues
        result['recommendations'] = self.recommendations
        
        return result
    
    def _get_text_content(self) -> str:
        """Extract text content from the page"""
        # Remove script and style elements
        for element in self.soup(['script', 'style', 'meta', 'link', 'noscript']):
            element.decompose()
        
        # Get text
        text = self.soup.get_text(separator=' ')
        return text
    
    def _tokenize(self, text: str) -> list:
        """Tokenize text into words"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
            'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been', 'being',
            'some', 'than', 'them', 'then', 'this', 'that', 'these', 'those',
            'with', 'will', 'would', 'there', 'their', 'what', 'from', 'which',
            'when', 'where', 'who', 'how', 'why', 'each', 'she', 'they', 'had',
            'into', 'more', 'other', 'could', 'just', 'only', 'over', 'such',
            'also', 'back', 'after', 'use', 'two', 'way', 'about', 'many',
            'like', 'here', 'your', 'any', 'new', 'does', 'get', 'make'
        }
        
        return [w for w in words if w not in stop_words]
    
    def _get_top_keywords(self, word_freq: Counter, total_words: int) -> list:
        """Get top 10 keywords with density"""
        top = []
        for word, count in word_freq.most_common(10):
            density = round((count / total_words) * 100, 2) if total_words > 0 else 0
            top.append({
                'word': word,
                'count': count,
                'density': density
            })
        return top
    
    def _analyze_target_keyword(self, words: list, word_freq: Counter, total_words: int) -> dict:
        """Analyze target keyword usage"""
        keyword_lower = self.target_keyword.lower()
        keyword_words = keyword_lower.split()
        
        # Count occurrences
        if len(keyword_words) == 1:
            count = word_freq.get(keyword_lower, 0)
        else:
            # For multi-word keywords, search in original text
            text = ' '.join(words)
            count = text.count(keyword_lower)
        
        density = round((count / total_words) * 100, 2) if total_words > 0 else 0
        
        # Check keyword in important places
        in_title = self._keyword_in_title()
        in_h1 = self._keyword_in_h1()
        in_meta = self._keyword_in_meta()
        in_url = False  # Would need URL passed in
        in_first_paragraph = self._keyword_in_first_paragraph()
        
        # Calculate placement score
        placement_score = 0
        placements = []
        
        if in_title:
            placement_score += 25
            placements.append('Title')
        else:
            self.issues.append({
                'type': 'warning',
                'message': f'Target keyword "{self.target_keyword}" not found in page title'
            })
            self.recommendations.append(f'Add "{self.target_keyword}" to the page title')
            
        if in_h1:
            placement_score += 25
            placements.append('H1')
        else:
            self.issues.append({
                'type': 'warning',
                'message': f'Target keyword "{self.target_keyword}" not found in H1 heading'
            })
            self.recommendations.append(f'Include "{self.target_keyword}" in your H1 heading')
            
        if in_meta:
            placement_score += 25
            placements.append('Meta Description')
        else:
            self.issues.append({
                'type': 'info',
                'message': f'Target keyword "{self.target_keyword}" not found in meta description'
            })
            self.recommendations.append(f'Add "{self.target_keyword}" to your meta description')
            
        if in_first_paragraph:
            placement_score += 25
            placements.append('First Paragraph')
        
        # Check density
        density_status = 'optimal'
        if density < 0.5:
            density_status = 'low'
            self.issues.append({
                'type': 'warning',
                'message': f'Keyword density ({density}%) is too low. Aim for 1-2%'
            })
            self.recommendations.append(f'Use "{self.target_keyword}" more frequently in your content')
        elif density > 3:
            density_status = 'high'
            self.issues.append({
                'type': 'warning',
                'message': f'Keyword density ({density}%) is too high. Risk of keyword stuffing'
            })
            self.recommendations.append('Reduce keyword usage to avoid keyword stuffing penalty')
        
        return {
            'keyword': self.target_keyword,
            'count': count,
            'density': density,
            'density_status': density_status,
            'placements': placements,
            'placement_score': placement_score,
            'in_title': in_title,
            'in_h1': in_h1,
            'in_meta': in_meta,
            'in_first_paragraph': in_first_paragraph
        }
    
    def _keyword_in_title(self) -> bool:
        """Check if keyword is in title"""
        title = self.soup.find('title')
        if title and title.string:
            return self.target_keyword.lower() in title.string.lower()
        return False
    
    def _keyword_in_h1(self) -> bool:
        """Check if keyword is in H1"""
        h1 = self.soup.find('h1')
        if h1:
            return self.target_keyword.lower() in h1.get_text().lower()
        return False
    
    def _keyword_in_meta(self) -> bool:
        """Check if keyword is in meta description"""
        meta = self.soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return self.target_keyword.lower() in meta['content'].lower()
        return False
    
    def _keyword_in_first_paragraph(self) -> bool:
        """Check if keyword is in first paragraph"""
        paragraphs = self.soup.find_all('p')
        if paragraphs:
            first_p = paragraphs[0].get_text().lower()
            return self.target_keyword.lower() in first_p
        return False
    
    def _calculate_keyword_score(self, analysis: dict) -> int:
        """Calculate overall keyword optimization score"""
        score = 50  # Base score
        
        # Add points for placements (up to 40 points)
        score += analysis['placement_score'] * 0.4
        
        # Add points for density (up to 20 points)
        density = analysis['density']
        if 1 <= density <= 2.5:
            score += 20
        elif 0.5 <= density < 1 or 2.5 < density <= 3:
            score += 10
        
        # Add points for count (up to 10 points)
        if analysis['count'] >= 5:
            score += 10
        elif analysis['count'] >= 2:
            score += 5
        
        return min(100, int(score))
