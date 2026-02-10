"""
Sitemap & Robots.txt Analyzer
Checks for sitemap.xml and robots.txt presence and validity.
"""

import requests
from urllib.parse import urlparse, urljoin


class SitemapAnalyzer:
    """Analyzes sitemap.xml and robots.txt of a website."""

    def __init__(self, url, timeout=10):
        self.url = url
        self.parsed = urlparse(url)
        self.base_url = f"{self.parsed.scheme}://{self.parsed.netloc}"
        self.timeout = timeout
        self.issues = []
        self.recommendations = []

    def analyze(self):
        """Run sitemap and robots.txt analysis."""
        robots = self._check_robots()
        sitemap = self._check_sitemap(robots.get('sitemap_urls', []))

        score = self._calculate_score(robots, sitemap)

        return {
            'score': score,
            'robots': robots,
            'sitemap': sitemap,
            'issues': self.issues,
            'recommendations': self.recommendations
        }

    def _check_robots(self):
        """Check robots.txt file."""
        robots_url = f"{self.base_url}/robots.txt"
        try:
            resp = requests.get(robots_url, timeout=self.timeout,
                                headers={'User-Agent': 'SEO-Audit-Tool/1.0'})
            if resp.status_code == 200:
                content = resp.text
                has_sitemap = 'sitemap' in content.lower()
                has_disallow = 'disallow' in content.lower()
                has_user_agent = 'user-agent' in content.lower()

                # Extract sitemap URLs
                sitemap_urls = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        sitemap_urls.append(sitemap_url)

                if not has_sitemap:
                    self.recommendations.append({
                        'category': 'Sitemap',
                        'recommendation': 'Add a Sitemap directive to robots.txt'
                    })

                return {
                    'exists': True,
                    'status_code': 200,
                    'has_sitemap_directive': has_sitemap,
                    'has_disallow_rules': has_disallow,
                    'has_user_agent': has_user_agent,
                    'sitemap_urls': sitemap_urls,
                    'content_preview': content[:500]
                }
            else:
                self.issues.append({
                    'severity': 'medium',
                    'message': 'robots.txt not found or inaccessible'
                })
                self.recommendations.append({
                    'category': 'Crawlability',
                    'recommendation': 'Create a robots.txt file to control search engine crawling'
                })
                return {
                    'exists': False,
                    'status_code': resp.status_code,
                    'has_sitemap_directive': False,
                    'has_disallow_rules': False,
                    'has_user_agent': False,
                    'sitemap_urls': []
                }
        except Exception:
            return {
                'exists': False,
                'status_code': 0,
                'has_sitemap_directive': False,
                'has_disallow_rules': False,
                'has_user_agent': False,
                'sitemap_urls': [],
                'error': 'Could not fetch robots.txt'
            }

    def _check_sitemap(self, robots_sitemap_urls=None):
        """Check sitemap.xml file."""
        # Try URLs from robots.txt first, then default location
        urls_to_try = []
        if robots_sitemap_urls:
            urls_to_try.extend(robots_sitemap_urls)
        urls_to_try.append(f"{self.base_url}/sitemap.xml")
        urls_to_try.append(f"{self.base_url}/sitemap_index.xml")

        for sitemap_url in urls_to_try:
            try:
                resp = requests.get(sitemap_url, timeout=self.timeout,
                                    headers={'User-Agent': 'SEO-Audit-Tool/1.0'})
                if resp.status_code == 200 and ('<?xml' in resp.text[:100] or '<urlset' in resp.text[:200] or '<sitemapindex' in resp.text[:200]):
                    is_index = '<sitemapindex' in resp.text[:500]
                    url_count = resp.text.count('<url>')
                    if is_index:
                        url_count = resp.text.count('<sitemap>')

                    return {
                        'exists': True,
                        'url': sitemap_url,
                        'status_code': 200,
                        'is_index': is_index,
                        'url_count': url_count,
                        'is_xml': True
                    }
            except Exception:
                continue

        self.issues.append({
            'severity': 'high',
            'message': 'No sitemap.xml found — search engines may not index all pages'
        })
        self.recommendations.append({
            'category': 'Sitemap',
            'recommendation': 'Create a sitemap.xml to help search engines discover and index your pages'
        })

        return {
            'exists': False,
            'url': None,
            'status_code': 0,
            'is_index': False,
            'url_count': 0,
            'is_xml': False
        }

    def _calculate_score(self, robots, sitemap):
        """Calculate sitemap/robots score."""
        score = 0
        if robots['exists']:
            score += 25
            if robots['has_user_agent']:
                score += 10
            if robots['has_sitemap_directive']:
                score += 15
        if sitemap['exists']:
            score += 30
            if sitemap['is_xml']:
                score += 10
            if sitemap['url_count'] > 0:
                score += 10
        return min(score, 100)
