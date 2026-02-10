"""
Mobile-Friendly Analyzer
Checks mobile optimization of a webpage
"""

import re
from bs4 import BeautifulSoup


class MobileAnalyzer:
    """Analyzes mobile-friendliness of a webpage"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.issues = []
        self.recommendations = []
        
    def analyze(self) -> dict:
        """Run complete mobile-friendliness analysis"""
        viewport = self._check_viewport()
        text_size = self._check_text_size()
        tap_targets = self._check_tap_targets()
        responsive = self._check_responsive_design()
        media_queries = self._check_media_queries()
        touch_friendly = self._check_touch_elements()
        
        # Calculate overall score
        score = self._calculate_score(viewport, text_size, tap_targets, responsive)
        
        # Determine overall status
        if score >= 80:
            status = 'mobile_friendly'
            status_text = 'Mobile Friendly'
        elif score >= 60:
            status = 'partially_mobile'
            status_text = 'Partially Mobile Friendly'
        else:
            status = 'not_mobile'
            status_text = 'Not Mobile Friendly'
        
        return {
            'status': status,
            'status_text': status_text,
            'score': score,
            'viewport': viewport,
            'text_size': text_size,
            'tap_targets': tap_targets,
            'responsive_design': responsive,
            'media_queries': media_queries,
            'touch_elements': touch_friendly,
            'issues': self.issues,
            'recommendations': self.recommendations
        }
    
    def _check_viewport(self) -> dict:
        """Check viewport meta tag"""
        viewport_meta = self.soup.find('meta', attrs={'name': 'viewport'})
        
        result = {
            'has_viewport': False,
            'content': '',
            'has_width': False,
            'has_initial_scale': False,
            'is_valid': False
        }
        
        if viewport_meta:
            result['has_viewport'] = True
            content = viewport_meta.get('content', '')
            result['content'] = content
            
            # Check for essential properties
            result['has_width'] = 'width=' in content
            result['has_initial_scale'] = 'initial-scale=' in content
            result['is_valid'] = result['has_width'] and 'device-width' in content
            
            if not result['is_valid']:
                self.issues.append({
                    'type': 'warning',
                    'message': 'Viewport meta tag is incomplete'
                })
                self.recommendations.append('Use: <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        else:
            self.issues.append({
                'type': 'high',
                'message': 'Missing viewport meta tag - page will not scale on mobile'
            })
            self.recommendations.append('Add viewport meta tag for mobile responsiveness')
        
        return result
    
    def _check_text_size(self) -> dict:
        """Check text readability on mobile"""
        # Find all text elements
        text_elements = self.soup.find_all(['p', 'span', 'div', 'li', 'td'])
        
        small_text_count = 0
        readable_text_count = 0
        
        # Check inline styles for font sizes
        for elem in text_elements[:50]:  # Check first 50 elements
            style = elem.get('style', '')
            if style:
                # Look for font-size
                font_match = re.search(r'font-size:\s*(\d+)(px|pt|em|rem)', style)
                if font_match:
                    size = int(font_match.group(1))
                    unit = font_match.group(2)
                    
                    # Convert to approximate px for comparison
                    if unit in ['em', 'rem']:
                        size *= 16
                    elif unit == 'pt':
                        size *= 1.33
                    
                    if size < 14:
                        small_text_count += 1
                    else:
                        readable_text_count += 1
        
        # Estimate based on common patterns
        is_readable = small_text_count < readable_text_count
        
        if small_text_count > 5:
            self.issues.append({
                'type': 'warning',
                'message': f'Found {small_text_count} elements with potentially small text'
            })
            self.recommendations.append('Use at least 16px font size for body text on mobile')
        
        return {
            'is_readable': is_readable,
            'small_text_elements': small_text_count,
            'readable_text_elements': readable_text_count
        }
    
    def _check_tap_targets(self) -> dict:
        """Check tap target sizes"""
        # Find all interactive elements
        interactive = self.soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        
        total_targets = len(interactive)
        potential_issues = 0
        
        for elem in interactive:
            style = elem.get('style', '')
            
            # Check for very small inline dimensions
            if style:
                width_match = re.search(r'width:\s*(\d+)px', style)
                height_match = re.search(r'height:\s*(\d+)px', style)
                
                if width_match and int(width_match.group(1)) < 44:
                    potential_issues += 1
                elif height_match and int(height_match.group(1)) < 44:
                    potential_issues += 1
        
        # Also check for links that are too close together
        links = self.soup.find_all('a')
        close_links = 0
        for i, link in enumerate(links[:-1]):
            if link.parent == links[i + 1].parent:
                # Links are siblings - might be too close
                close_links += 1
        
        if potential_issues > 0:
            self.issues.append({
                'type': 'warning',
                'message': f'{potential_issues} tap targets may be too small (minimum 44x44px recommended)'
            })
            self.recommendations.append('Ensure buttons and links are at least 44x44 pixels')
        
        return {
            'total_targets': total_targets,
            'potential_small_targets': potential_issues,
            'close_together': close_links,
            'is_adequate': potential_issues == 0
        }
    
    def _check_responsive_design(self) -> dict:
        """Check for responsive design patterns"""
        # Check for responsive images
        responsive_images = len(self.soup.find_all('img', class_=re.compile(r'responsive|fluid')))
        images_with_max_width = 0
        
        for img in self.soup.find_all('img'):
            style = img.get('style', '')
            if 'max-width' in style or 'width: 100%' in style:
                images_with_max_width += 1
        
        # Check for responsive containers
        responsive_containers = len(self.soup.find_all(class_=re.compile(r'container|wrapper|responsive|fluid')))
        
        # Check for flexbox/grid usage in styles
        has_flexbox = bool(self.soup.find(style=re.compile(r'display:\s*flex')))
        has_grid = bool(self.soup.find(style=re.compile(r'display:\s*grid')))
        
        # Check for responsive meta tags
        has_manifest = bool(self.soup.find('link', rel='manifest'))
        has_apple_meta = bool(self.soup.find('meta', attrs={'name': 'apple-mobile-web-app-capable'}))
        
        return {
            'responsive_images': responsive_images + images_with_max_width,
            'responsive_containers': responsive_containers,
            'uses_flexbox': has_flexbox,
            'uses_grid': has_grid,
            'has_manifest': has_manifest,
            'has_apple_meta': has_apple_meta
        }
    
    def _check_media_queries(self) -> dict:
        """Check for CSS media queries"""
        # Find inline styles and style tags
        style_tags = self.soup.find_all('style')
        
        media_query_count = 0
        breakpoints = set()
        
        for style in style_tags:
            if style.string:
                # Find @media queries
                queries = re.findall(r'@media[^{]+', style.string)
                media_query_count += len(queries)
                
                # Extract breakpoints
                for query in queries:
                    bp_match = re.findall(r'(\d+)px', query)
                    breakpoints.update(bp_match)
        
        # Check for linked responsive stylesheets
        responsive_links = len(self.soup.find_all('link', media=re.compile(r'screen|max-width|min-width')))
        
        has_mobile_styles = media_query_count > 0 or responsive_links > 0
        
        if not has_mobile_styles:
            self.issues.append({
                'type': 'info',
                'message': 'No media queries detected in inline styles'
            })
            self.recommendations.append('Use CSS media queries for responsive layouts')
        
        return {
            'media_query_count': media_query_count,
            'breakpoints': list(breakpoints),
            'responsive_stylesheets': responsive_links,
            'has_mobile_styles': has_mobile_styles
        }
    
    def _check_touch_elements(self) -> dict:
        """Check for touch-friendly elements"""
        # Check for touch-action CSS
        has_touch_css = bool(self.soup.find(style=re.compile(r'touch-action')))
        
        # Check for touch event handlers (common patterns)
        touch_handlers = 0
        for elem in self.soup.find_all(True):
            attrs = ' '.join(str(v) for v in elem.attrs.values())
            if 'touch' in attrs.lower() or 'swipe' in attrs.lower():
                touch_handlers += 1
        
        # Check for horizontal scrolling containers
        horizontal_scroll = len(self.soup.find_all(style=re.compile(r'overflow-x:\s*(auto|scroll)')))
        
        return {
            'has_touch_css': has_touch_css,
            'touch_handlers': touch_handlers,
            'horizontal_scroll_areas': horizontal_scroll
        }
    
    def _calculate_score(self, viewport: dict, text_size: dict, 
                         tap_targets: dict, responsive: dict) -> int:
        """Calculate overall mobile-friendliness score"""
        score = 0
        
        # Viewport (30 points)
        if viewport['has_viewport']:
            score += 15
            if viewport['is_valid']:
                score += 15
        
        # Text readability (20 points)
        if text_size['is_readable']:
            score += 20
        elif text_size['small_text_elements'] < 3:
            score += 10
        
        # Tap targets (25 points)
        if tap_targets['is_adequate']:
            score += 25
        elif tap_targets['potential_small_targets'] < 3:
            score += 15
        
        # Responsive design (25 points)
        if responsive['responsive_images'] > 0 or responsive['responsive_containers'] > 0:
            score += 10
        if responsive['uses_flexbox'] or responsive['uses_grid']:
            score += 10
        if responsive['has_manifest'] or responsive['has_apple_meta']:
            score += 5
        
        return min(100, score)
