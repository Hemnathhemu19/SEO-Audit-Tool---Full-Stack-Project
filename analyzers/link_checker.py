"""
Broken Link Checker
Crawls all links on a page and verifies their HTTP status.
"""

import requests
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed


class LinkChecker:
    """Checks all links on a page for broken URLs."""

    def __init__(self, soup, base_url, timeout=5, max_links=50):
        self.soup = soup
        self.base_url = base_url
        self.timeout = timeout
        self.max_links = max_links
        self.issues = []
        self.recommendations = []

    def analyze(self):
        """Run broken link check."""
        raw_links = self._extract_links()
        unique_links = list(set(raw_links))[:self.max_links]

        results = self._check_links(unique_links)

        working = [r for r in results if r['status'] == 'working']
        redirected = [r for r in results if r['status'] == 'redirected']
        broken = [r for r in results if r['status'] == 'broken']
        unreachable = [r for r in results if r['status'] == 'unreachable']

        if broken:
            self.issues.append({
                'severity': 'high',
                'message': f'{len(broken)} broken link(s) found on this page'
            })
            self.recommendations.append({
                'category': 'Links',
                'recommendation': 'Fix or remove broken links to improve user experience and SEO'
            })

        if redirected and len(redirected) > 3:
            self.issues.append({
                'severity': 'low',
                'message': f'{len(redirected)} redirected link(s) — consider updating to direct URLs'
            })

        score = self._calculate_score(results)

        return {
            'score': score,
            'total_links': len(unique_links),
            'working': len(working),
            'redirected': len(redirected),
            'broken': len(broken),
            'unreachable': len(unreachable),
            'broken_links': [{'url': r['url'], 'status_code': r['status_code']} for r in broken],
            'redirected_links': [{'url': r['url'], 'status_code': r['status_code']} for r in redirected],
            'details': results,
            'issues': self.issues,
            'recommendations': self.recommendations
        }

    def _extract_links(self):
        """Extract all href links from the page."""
        links = []
        for a_tag in self.soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            # Skip anchors, javascript, mailto, tel
            if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            # Resolve relative URLs
            full_url = urljoin(self.base_url, href)
            # Only check HTTP(s) links
            parsed = urlparse(full_url)
            if parsed.scheme in ('http', 'https'):
                links.append(full_url)
        return links

    def _check_single_link(self, url):
        """Check a single URL and return its status."""
        try:
            response = requests.head(
                url,
                timeout=self.timeout,
                allow_redirects=False,
                headers={'User-Agent': 'SEO-Audit-Tool/1.0'}
            )
            code = response.status_code

            if 200 <= code < 300:
                return {'url': url, 'status': 'working', 'status_code': code}
            elif 300 <= code < 400:
                return {'url': url, 'status': 'redirected', 'status_code': code}
            else:
                return {'url': url, 'status': 'broken', 'status_code': code}
        except requests.exceptions.Timeout:
            return {'url': url, 'status': 'unreachable', 'status_code': 0}
        except requests.exceptions.RequestException:
            return {'url': url, 'status': 'unreachable', 'status_code': 0}

    def _check_links(self, links):
        """Check multiple links in parallel."""
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {
                executor.submit(self._check_single_link, url): url
                for url in links
            }
            for future in as_completed(future_to_url):
                try:
                    result = future.result()
                    results.append(result)
                except Exception:
                    url = future_to_url[future]
                    results.append({'url': url, 'status': 'unreachable', 'status_code': 0})
        return results

    def _calculate_score(self, results):
        """Calculate link health score."""
        if not results:
            return 100

        total = len(results)
        broken_count = sum(1 for r in results if r['status'] in ('broken', 'unreachable'))
        
        if broken_count == 0:
            return 100
        
        ratio = broken_count / total
        score = max(0, int((1 - ratio) * 100))
        return score
