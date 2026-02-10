"""
Readability Analyzer
Calculates reading ease scores, sentence length, and word complexity.
"""

import re
import math
import copy


class ReadabilityAnalyzer:
    """Analyzes text readability of a webpage."""

    def __init__(self, soup):
        self.soup = soup
        self.issues = []
        self.recommendations = []

    def analyze(self):
        """Run readability analysis."""
        text = self._extract_text()
        
        if not text or len(text.split()) < 20:
            return {
                'score': 0,
                'flesch_reading_ease': 0,
                'flesch_grade_level': 0,
                'gunning_fog': 0,
                'avg_sentence_length': 0,
                'avg_word_length': 0,
                'total_sentences': 0,
                'total_words': 0,
                'difficulty': 'Insufficient Content',
                'issues': [{'severity': 'medium', 'message': 'Not enough text content to analyze readability'}],
                'recommendations': [{'category': 'Content', 'recommendation': 'Add more text content to the page'}]
            }

        sentences = self._split_sentences(text)
        words = self._get_words(text)
        syllable_counts = [self._count_syllables(w) for w in words]

        total_sentences = max(len(sentences), 1)
        total_words = len(words)
        total_syllables = sum(syllable_counts)
        complex_words = sum(1 for s in syllable_counts if s >= 3)

        avg_sentence_length = round(total_words / total_sentences, 1)
        avg_word_length = round(sum(len(w) for w in words) / max(total_words, 1), 1)

        flesch = self._flesch_reading_ease(total_sentences, total_words, total_syllables)
        grade = self._flesch_kincaid_grade(total_sentences, total_words, total_syllables)
        fog = self._gunning_fog(total_sentences, total_words, complex_words)

        difficulty = self._get_difficulty(flesch)

        if avg_sentence_length > 25:
            self.issues.append({'severity': 'medium', 'message': f'Average sentence length is {avg_sentence_length} words — aim for under 20'})
            self.recommendations.append({'category': 'Readability', 'recommendation': 'Break long sentences into shorter ones for better readability'})

        if flesch < 40:
            self.issues.append({'severity': 'high', 'message': 'Content is very difficult to read'})
            self.recommendations.append({'category': 'Readability', 'recommendation': 'Simplify language — use shorter words and sentences'})
        elif flesch < 60:
            self.issues.append({'severity': 'low', 'message': 'Content readability could be improved'})

        score = self._calculate_score(flesch, avg_sentence_length)

        return {
            'score': score,
            'flesch_reading_ease': round(flesch, 1),
            'flesch_grade_level': round(grade, 1),
            'gunning_fog': round(fog, 1),
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'total_sentences': total_sentences,
            'total_words': total_words,
            'complex_words': complex_words,
            'difficulty': difficulty,
            'issues': self.issues,
            'recommendations': self.recommendations
        }

    def _extract_text(self):
        """Extract readable text from the page."""
        soup_copy = copy.copy(self.soup)
        for tag in soup_copy.find_all(['script', 'style', 'nav', 'header', 'footer', 'noscript']):
            tag.decompose()
        
        text_elements = soup_copy.find_all(['p', 'article', 'section', 'main', 'div', 'li'])
        text_parts = []
        for el in text_elements:
            t = el.get_text(strip=True)
            if len(t) > 20:
                text_parts.append(t)
        
        return ' '.join(text_parts)

    def _split_sentences(self, text):
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip().split()) >= 3]

    def _get_words(self, text):
        """Extract words from text."""
        words = re.findall(r'[a-zA-Z]+', text.lower())
        return [w for w in words if len(w) > 1]

    def _count_syllables(self, word):
        """Estimate syllable count for a word."""
        word = word.lower()
        if len(word) <= 2:
            return 1
        
        vowels = 'aeiouy'
        count = 0
        prev_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        
        if word.endswith('e'):
            count -= 1
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            count += 1
        
        return max(count, 1)

    def _flesch_reading_ease(self, sentences, words, syllables):
        """Calculate Flesch Reading Ease score."""
        if sentences == 0 or words == 0:
            return 0
        return 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)

    def _flesch_kincaid_grade(self, sentences, words, syllables):
        """Calculate Flesch-Kincaid Grade Level."""
        if sentences == 0 or words == 0:
            return 0
        return 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59

    def _gunning_fog(self, sentences, words, complex_words):
        """Calculate Gunning Fog Index."""
        if sentences == 0 or words == 0:
            return 0
        return 0.4 * ((words / sentences) + 100 * (complex_words / words))

    def _get_difficulty(self, flesch):
        """Get difficulty label from Flesch score."""
        if flesch >= 80:
            return 'Very Easy'
        elif flesch >= 60:
            return 'Easy'
        elif flesch >= 40:
            return 'Moderate'
        elif flesch >= 20:
            return 'Difficult'
        else:
            return 'Very Difficult'

    def _calculate_score(self, flesch, avg_sentence):
        """Calculate readability score (0-100)."""
        # Map Flesch (0-100) to score with sweet spot around 60-70
        if flesch >= 60:
            score = min(100, int(flesch))
        elif flesch >= 40:
            score = int(flesch * 1.2)
        else:
            score = max(10, int(flesch))

        # Penalize very long sentences
        if avg_sentence > 30:
            score -= 15
        elif avg_sentence > 25:
            score -= 10

        return max(0, min(100, score))
