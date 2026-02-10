"""
Social Media Preview Analyzer
Extracts and validates Open Graph and Twitter Card meta tags
"""

from bs4 import BeautifulSoup


class SocialAnalyzer:
    """Analyzes Open Graph and Twitter Card meta tags"""
    
    def __init__(self, soup: BeautifulSoup, url: str = ''):
        self.soup = soup
        self.url = url
        self.issues = []
        self.recommendations = []
        
    def analyze(self) -> dict:
        """Run complete social media analysis"""
        og_tags = self._extract_og_tags()
        twitter_tags = self._extract_twitter_tags()
        
        # Build previews
        facebook_preview = self._build_facebook_preview(og_tags)
        twitter_preview = self._build_twitter_preview(twitter_tags, og_tags)
        linkedin_preview = self._build_linkedin_preview(og_tags)
        
        # Calculate score
        score = self._calculate_score(og_tags, twitter_tags)
        
        return {
            'og_tags': og_tags,
            'twitter_tags': twitter_tags,
            'facebook_preview': facebook_preview,
            'twitter_preview': twitter_preview,
            'linkedin_preview': linkedin_preview,
            'score': score,
            'issues': self.issues,
            'recommendations': self.recommendations
        }
    
    def _extract_og_tags(self) -> dict:
        """Extract Open Graph meta tags"""
        og_tags = {}
        
        # Common OG properties
        og_properties = [
            'og:title', 'og:description', 'og:image', 'og:url',
            'og:type', 'og:site_name', 'og:locale', 'og:image:width',
            'og:image:height', 'og:image:alt'
        ]
        
        for prop in og_properties:
            meta = self.soup.find('meta', property=prop)
            if meta and meta.get('content'):
                key = prop.replace('og:', '').replace(':', '_')
                og_tags[key] = meta['content']
        
        return og_tags
    
    def _extract_twitter_tags(self) -> dict:
        """Extract Twitter Card meta tags"""
        twitter_tags = {}
        
        # Common Twitter properties
        twitter_properties = [
            'twitter:card', 'twitter:title', 'twitter:description',
            'twitter:image', 'twitter:site', 'twitter:creator',
            'twitter:image:alt'
        ]
        
        for prop in twitter_properties:
            meta = self.soup.find('meta', attrs={'name': prop})
            if meta and meta.get('content'):
                key = prop.replace('twitter:', '').replace(':', '_')
                twitter_tags[key] = meta['content']
        
        return twitter_tags
    
    def _build_facebook_preview(self, og_tags: dict) -> dict:
        """Build Facebook/Open Graph preview data"""
        # Get title from OG or fallback to page title
        title = og_tags.get('title')
        if not title:
            title_tag = self.soup.find('title')
            title = title_tag.string if title_tag else 'No title'
            self.issues.append({
                'type': 'warning',
                'message': 'Missing og:title meta tag'
            })
            self.recommendations.append('Add og:title meta tag for better Facebook sharing')
        
        # Get description
        description = og_tags.get('description')
        if not description:
            meta_desc = self.soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc and meta_desc.get('content') else 'No description'
            self.issues.append({
                'type': 'warning',
                'message': 'Missing og:description meta tag'
            })
            self.recommendations.append('Add og:description meta tag for better Facebook sharing')
        
        # Get image
        image = og_tags.get('image', '')
        if not image:
            self.issues.append({
                'type': 'high',
                'message': 'Missing og:image meta tag - posts will have no image preview'
            })
            self.recommendations.append('Add og:image meta tag (recommended: 1200x630 pixels)')
        
        return {
            'title': title[:60] + '...' if len(title) > 60 else title,
            'description': description[:155] + '...' if len(description) > 155 else description,
            'image': image,
            'url': og_tags.get('url', self.url),
            'site_name': og_tags.get('site_name', '')
        }
    
    def _build_twitter_preview(self, twitter_tags: dict, og_tags: dict) -> dict:
        """Build Twitter Card preview data"""
        # Card type
        card_type = twitter_tags.get('card', 'summary')
        
        # Title (Twitter > OG > page title)
        title = twitter_tags.get('title') or og_tags.get('title')
        if not title:
            title_tag = self.soup.find('title')
            title = title_tag.string if title_tag else 'No title'
        
        # Description
        description = twitter_tags.get('description') or og_tags.get('description', '')
        
        # Image
        image = twitter_tags.get('image') or og_tags.get('image', '')
        
        # Check for Twitter-specific issues
        if 'card' not in twitter_tags:
            self.issues.append({
                'type': 'info',
                'message': 'Missing twitter:card meta tag - defaults to summary'
            })
            self.recommendations.append('Add twitter:card meta tag (summary_large_image recommended)')
        
        return {
            'card_type': card_type,
            'title': title[:70] + '...' if len(title) > 70 else title,
            'description': description[:200] + '...' if len(description) > 200 else description,
            'image': image,
            'site': twitter_tags.get('site', ''),
            'creator': twitter_tags.get('creator', '')
        }
    
    def _build_linkedin_preview(self, og_tags: dict) -> dict:
        """Build LinkedIn preview data (uses OG tags)"""
        title = og_tags.get('title')
        if not title:
            title_tag = self.soup.find('title')
            title = title_tag.string if title_tag else 'No title'
        
        description = og_tags.get('description', '')
        image = og_tags.get('image', '')
        
        return {
            'title': title[:100] + '...' if len(title) > 100 else title,
            'description': description[:200] + '...' if len(description) > 200 else description,
            'image': image,
            'url': og_tags.get('url', self.url)
        }
    
    def _calculate_score(self, og_tags: dict, twitter_tags: dict) -> int:
        """Calculate social media optimization score"""
        score = 0
        
        # Essential OG tags (60 points max)
        if og_tags.get('title'):
            score += 15
        if og_tags.get('description'):
            score += 15
        if og_tags.get('image'):
            score += 20
        if og_tags.get('url'):
            score += 5
        if og_tags.get('type'):
            score += 5
        
        # Twitter tags (30 points max)
        if twitter_tags.get('card'):
            score += 10
        if twitter_tags.get('title') or og_tags.get('title'):
            score += 10
        if twitter_tags.get('image') or og_tags.get('image'):
            score += 10
        
        # Bonus points (10 points max)
        if og_tags.get('site_name'):
            score += 5
        if twitter_tags.get('site'):
            score += 5
        
        return min(100, score)
