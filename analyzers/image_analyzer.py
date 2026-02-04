"""
Image SEO Analyzer Module
Analyzes images for alt text, naming, and optimization
"""

from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re


class ImageAnalyzer:
    """Analyzes images for SEO optimization"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.images = []
        self._extract_images()
    
    def _extract_images(self):
        """Extract all images from HTML"""
        img_tags = self.soup.find_all('img')
        
        for img in img_tags:
            image_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'loading': img.get('loading', ''),
                'has_alt': bool(img.get('alt')),
                'alt_is_empty': img.get('alt') == '',
            }
            
            # Extract filename from src
            if image_data['src']:
                parsed = urlparse(image_data['src'])
                image_data['filename'] = parsed.path.split('/')[-1] if parsed.path else ''
            else:
                image_data['filename'] = ''
            
            self.images.append(image_data)
    
    def analyze(self) -> dict:
        """Perform complete image analysis"""
        result = {
            'score': 0,
            'total_images': len(self.images),
            'issues': [],
            'recommendations': [],
            'details': {}
        }
        
        if len(self.images) == 0:
            result['score'] = 70  # Not critical if no images, but could be opportunity
            result['issues'].append({
                'type': 'info',
                'message': 'No images found on the page'
            })
            result['recommendations'].append('Consider adding relevant images to improve engagement')
            return result
        
        score = 100
        
        # Analyze alt text
        images_without_alt = [img for img in self.images if not img['has_alt']]
        images_with_empty_alt = [img for img in self.images if img['alt_is_empty'] and img['has_alt']]
        images_with_alt = [img for img in self.images if img['has_alt'] and img['alt']]
        
        result['details']['with_alt'] = len(images_with_alt)
        result['details']['without_alt'] = len(images_without_alt)
        result['details']['empty_alt'] = len(images_with_empty_alt)
        
        # Score deduction for missing alt text
        if images_without_alt:
            missing_percentage = (len(images_without_alt) / len(self.images)) * 100
            deduction = min(40, missing_percentage * 0.5)
            score -= deduction
            
            result['issues'].append({
                'type': 'warning',
                'message': f'{len(images_without_alt)} images missing alt text'
            })
            result['recommendations'].append('Add descriptive alt text to all images for accessibility and SEO')
        
        # Check for lazy loading
        lazy_loaded = [img for img in self.images if img['loading'] == 'lazy']
        result['details']['lazy_loaded'] = len(lazy_loaded)
        
        if len(lazy_loaded) < len(self.images) and len(self.images) > 3:
            result['recommendations'].append('Consider adding loading="lazy" to below-the-fold images')
        
        # Check for dimensions
        images_with_dimensions = [img for img in self.images if img['width'] and img['height']]
        result['details']['with_dimensions'] = len(images_with_dimensions)
        
        if len(images_with_dimensions) < len(self.images):
            score -= 10
            result['issues'].append({
                'type': 'info',
                'message': 'Some images missing width/height attributes'
            })
            result['recommendations'].append('Add width and height attributes to prevent layout shift')
        
        # Check filename quality
        poor_filenames = []
        for img in self.images:
            filename = img['filename'].lower()
            # Check for generic names
            if any(pattern in filename for pattern in ['img', 'image', 'photo', 'picture', 'untitled', 'dsc', 'screenshot']):
                if not any(c.isalpha() for c in filename.replace('.', '').replace('-', '').replace('_', '')):
                    continue
                poor_filenames.append(filename)
        
        if poor_filenames:
            score -= 5
            result['details']['poor_filenames'] = len(poor_filenames)
            result['issues'].append({
                'type': 'info',
                'message': f'{len(poor_filenames)} images have non-descriptive filenames'
            })
            result['recommendations'].append('Use descriptive, keyword-rich filenames for images')
        
        # Check for modern formats (webp, avif)
        modern_formats = [img for img in self.images if img['filename'].endswith(('.webp', '.avif'))]
        result['details']['modern_format_count'] = len(modern_formats)
        
        if len(modern_formats) == 0 and len(self.images) > 0:
            result['recommendations'].append('Consider using modern image formats (WebP, AVIF) for better compression')
        
        # Analyze alt text quality
        good_alts = []
        for img in images_with_alt:
            alt = img['alt']
            # Check alt text length
            if len(alt) > 10 and len(alt) < 125:
                good_alts.append(alt)
        
        result['details']['quality_alt_texts'] = len(good_alts)
        
        result['score'] = max(0, min(100, score))
        result['details']['images'] = self.images[:10]  # First 10 for detail view
        
        return result
