"""
Link Analyzer Module
Analyzes internal and external links for SEO
"""

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re


class LinkAnalyzer:
    """Analyzes internal and external links for SEO"""
    
    def __init__(self, soup: BeautifulSoup, base_url: str):
        self.soup = soup
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.links = []
        self._extract_links()
    
    def _extract_links(self):
        """Extract all links from HTML"""
        anchor_tags = self.soup.find_all('a', href=True)
        
        for anchor in anchor_tags:
            href = anchor.get('href', '')
            text = anchor.get_text().strip()
            rel = anchor.get('rel', [])
            target = anchor.get('target', '')
            
            # Skip empty, anchor-only, or javascript links
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Resolve relative URLs
            full_url = urljoin(self.base_url, href)
            parsed = urlparse(full_url)
            
            link_data = {
                'href': href,
                'full_url': full_url,
                'text': text,
                'is_internal': parsed.netloc == self.base_domain or not parsed.netloc,
                'is_external': parsed.netloc != self.base_domain and parsed.netloc,
                'has_nofollow': 'nofollow' in rel if isinstance(rel, list) else 'nofollow' in str(rel),
                'opens_new_tab': target == '_blank',
                'is_mailto': href.startswith('mailto:'),
                'is_tel': href.startswith('tel:'),
            }
            
            self.links.append(link_data)
    
    def analyze(self) -> dict:
        """Perform complete link analysis"""
        result = {
            'score': 0,
            'total_links': len(self.links),
            'issues': [],
            'recommendations': [],
            'details': {}
        }
        
        score = 100
        
        # Filter links by type
        internal_links = [l for l in self.links if l['is_internal'] and not l['is_mailto'] and not l['is_tel']]
        external_links = [l for l in self.links if l['is_external']]
        
        result['details']['internal_count'] = len(internal_links)
        result['details']['external_count'] = len(external_links)
        
        # Check internal linking
        if len(internal_links) == 0:
            score -= 30
            result['issues'].append({
                'type': 'warning',
                'message': 'No internal links found on the page'
            })
            result['recommendations'].append('Add internal links to other relevant pages on your site')
        elif len(internal_links) < 3:
            score -= 15
            result['issues'].append({
                'type': 'info',
                'message': f'Only {len(internal_links)} internal links found. Consider adding more'
            })
            result['recommendations'].append('Include 3-5 internal links for better site structure')
        
        # Check for external links
        if len(external_links) == 0:
            result['issues'].append({
                'type': 'info',
                'message': 'No external links found'
            })
            result['recommendations'].append('Consider linking to authoritative external sources')
        
        # Check external links for nofollow
        external_without_nofollow = [l for l in external_links if not l['has_nofollow']]
        result['details']['external_dofollow'] = len(external_without_nofollow)
        
        # Check for links with no text (accessibility issue)
        links_without_text = [l for l in self.links if not l['text'] and not l['is_mailto'] and not l['is_tel']]
        result['details']['empty_anchor_text'] = len(links_without_text)
        
        if links_without_text:
            score -= 10
            result['issues'].append({
                'type': 'warning',
                'message': f'{len(links_without_text)} links have no anchor text'
            })
            result['recommendations'].append('Add descriptive anchor text to all links')
        
        # Check anchor text quality
        generic_anchors = ['click here', 'read more', 'here', 'link', 'this', 'more']
        generic_links = [l for l in self.links if l['text'].lower() in generic_anchors]
        result['details']['generic_anchor_text'] = len(generic_links)
        
        if generic_links:
            score -= 5
            result['issues'].append({
                'type': 'info', 
                'message': f'{len(generic_links)} links use generic anchor text'
            })
            result['recommendations'].append('Use descriptive anchor text instead of "click here" or "read more"')
        
        # Check for broken link patterns (can't actually test, but flag suspicious ones)
        suspicious_links = []
        for link in self.links:
            href = link['href']
            # Check for obvious issues
            if '.html.html' in href or '404' in href or 'undefined' in href:
                suspicious_links.append(href)
        
        if suspicious_links:
            score -= 15
            result['details']['suspicious_links'] = suspicious_links
            result['issues'].append({
                'type': 'warning',
                'message': f'{len(suspicious_links)} potentially broken or malformed links detected'
            })
            result['recommendations'].append('Review and fix suspicious link URLs')
        
        # External links security check
        external_without_rel = [l for l in external_links if l['opens_new_tab'] and not l['has_nofollow']]
        if external_without_rel:
            result['issues'].append({
                'type': 'info',
                'message': 'External links opening in new tab should have rel="noopener"'
            })
        
        result['score'] = max(0, min(100, score))
        
        # Include sample links in details
        result['details']['internal_links'] = [l['full_url'] for l in internal_links[:10]]
        result['details']['external_links'] = [l['full_url'] for l in external_links[:10]]
        
        return result
