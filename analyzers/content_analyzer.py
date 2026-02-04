"""
Content Analyzer Module
Analyzes page content for SEO best practices including readability
"""

from bs4 import BeautifulSoup
import textstat
import re


class ContentAnalyzer:
    """Analyzes page content for SEO optimization"""
    
    MIN_WORD_COUNT = 300
    OPTIMAL_WORD_COUNT = 1500
    MAX_KEYWORD_DENSITY = 3.0
    
    def __init__(self, soup: BeautifulSoup, target_keyword: str = None):
        self.soup = soup
        self.target_keyword = target_keyword
        self.text_content = ""
        self._extract_content()
    
    def _extract_content(self):
        """Extract text content from HTML"""
        # Remove script and style elements
        for element in self.soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Get text content
        self.text_content = self.soup.get_text(separator=' ', strip=True)
        # Clean up whitespace
        self.text_content = re.sub(r'\s+', ' ', self.text_content)
    
    def _count_words(self, text: str) -> int:
        """Count words in text"""
        words = text.split()
        return len([w for w in words if len(w) > 1])
    
    def _calculate_keyword_density(self, keyword: str) -> float:
        """Calculate keyword density percentage"""
        if not keyword or not self.text_content:
            return 0.0
        
        text_lower = self.text_content.lower()
        keyword_lower = keyword.lower()
        
        keyword_count = text_lower.count(keyword_lower)
        word_count = self._count_words(self.text_content)
        
        if word_count == 0:
            return 0.0
        
        return (keyword_count / word_count) * 100
    
    def analyze(self) -> dict:
        """Perform complete content analysis"""
        result = {
            'score': 0,
            'word_count': 0,
            'issues': [],
            'recommendations': [],
            'details': {}
        }
        
        score = 100
        word_count = self._count_words(self.text_content)
        result['word_count'] = word_count
        result['details']['word_count'] = word_count
        
        # Word count analysis
        if word_count < self.MIN_WORD_COUNT:
            score -= 30
            result['issues'].append({
                'type': 'warning',
                'message': f'Content is thin ({word_count} words). Aim for at least {self.MIN_WORD_COUNT} words'
            })
            result['recommendations'].append(f'Expand your content to at least {self.MIN_WORD_COUNT} words for better ranking')
        elif word_count < self.OPTIMAL_WORD_COUNT:
            score -= 10
            result['details']['word_count_status'] = 'acceptable'
        else:
            result['details']['word_count_status'] = 'optimal'
        
        # Readability analysis
        if self.text_content and word_count > 50:
            try:
                flesch_score = textstat.flesch_reading_ease(self.text_content)
                result['details']['flesch_reading_ease'] = round(flesch_score, 1)
                
                # Interpret score
                if flesch_score >= 60:
                    result['details']['readability'] = 'Easy to read'
                elif flesch_score >= 30:
                    result['details']['readability'] = 'Moderately difficult'
                else:
                    result['details']['readability'] = 'Difficult to read'
                    score -= 15
                    result['issues'].append({
                        'type': 'warning',
                        'message': 'Content is difficult to read'
                    })
                    result['recommendations'].append('Simplify your writing. Use shorter sentences and simpler words')
                
                # Grade level
                grade_level = textstat.flesch_kincaid_grade(self.text_content)
                result['details']['grade_level'] = round(grade_level, 1)
                
                # Sentence count and average
                sentence_count = textstat.sentence_count(self.text_content)
                result['details']['sentence_count'] = sentence_count
                
                if sentence_count > 0:
                    avg_sentence_length = word_count / sentence_count
                    result['details']['avg_sentence_length'] = round(avg_sentence_length, 1)
                    
                    if avg_sentence_length > 25:
                        score -= 10
                        result['issues'].append({
                            'type': 'info',
                            'message': f'Average sentence length is high ({round(avg_sentence_length)} words)'
                        })
                        result['recommendations'].append('Break up long sentences for better readability')
                
            except Exception:
                result['details']['readability'] = 'Unable to analyze'
        
        # Keyword density (if target keyword provided)
        if self.target_keyword:
            density = self._calculate_keyword_density(self.target_keyword)
            result['details']['keyword_density'] = round(density, 2)
            result['details']['target_keyword'] = self.target_keyword
            
            if density > self.MAX_KEYWORD_DENSITY:
                score -= 20
                result['issues'].append({
                    'type': 'warning',
                    'message': f'Keyword density is too high ({round(density, 1)}%). Risk of keyword stuffing'
                })
                result['recommendations'].append('Reduce keyword usage to avoid over-optimization')
            elif density < 0.5 and density > 0:
                result['issues'].append({
                    'type': 'info',
                    'message': f'Keyword density is low ({round(density, 1)}%)'
                })
        
        # Check for paragraphs
        paragraphs = self.soup.find_all('p')
        result['details']['paragraph_count'] = len(paragraphs)
        
        if len(paragraphs) < 3:
            score -= 10
            result['issues'].append({
                'type': 'info',
                'message': 'Few paragraphs detected. Content may not be well-structured'
            })
            result['recommendations'].append('Break content into multiple paragraphs for better readability')
        
        # Check for lists
        lists = self.soup.find_all(['ul', 'ol'])
        result['details']['list_count'] = len(lists)
        
        if len(lists) == 0 and word_count > 500:
            result['recommendations'].append('Consider adding bullet points or numbered lists to improve scannability')
        
        result['score'] = max(0, min(100, score))
        return result
