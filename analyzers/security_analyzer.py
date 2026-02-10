"""
SSL/Security Analyzer
Checks HTTPS, security headers, and mixed content issues.
"""

from urllib.parse import urlparse


class SecurityAnalyzer:
    """Analyzes SSL and security aspects of a webpage."""

    SECURITY_HEADERS = {
        'Strict-Transport-Security': {
            'label': 'HSTS',
            'description': 'Enforces HTTPS connections'
        },
        'Content-Security-Policy': {
            'label': 'CSP',
            'description': 'Prevents XSS and injection attacks'
        },
        'X-Content-Type-Options': {
            'label': 'X-Content-Type-Options',
            'description': 'Prevents MIME type sniffing'
        },
        'X-Frame-Options': {
            'label': 'X-Frame-Options',
            'description': 'Prevents clickjacking'
        },
        'X-XSS-Protection': {
            'label': 'X-XSS-Protection',
            'description': 'XSS filter protection'
        },
        'Referrer-Policy': {
            'label': 'Referrer-Policy',
            'description': 'Controls referrer information'
        },
        'Permissions-Policy': {
            'label': 'Permissions-Policy',
            'description': 'Controls browser features'
        }
    }

    def __init__(self, soup, url, response_headers=None):
        self.soup = soup
        self.url = url
        self.parsed_url = urlparse(url)
        self.headers = response_headers or {}
        self.issues = []
        self.recommendations = []

    def analyze(self):
        """Run security analysis."""
        https_check = self._check_https()
        mixed_content = self._check_mixed_content()
        headers_check = self._check_security_headers()

        score = self._calculate_score(https_check, mixed_content, headers_check)

        return {
            'score': score,
            'is_https': https_check['is_https'],
            'ssl_status': 'Secure' if https_check['is_https'] else 'Not Secure',
            'mixed_content': mixed_content,
            'security_headers': headers_check,
            'headers_found': headers_check['found_count'],
            'headers_total': len(self.SECURITY_HEADERS),
            'issues': self.issues,
            'recommendations': self.recommendations
        }

    def _check_https(self):
        """Check if site uses HTTPS."""
        is_https = self.parsed_url.scheme == 'https'
        if not is_https:
            self.issues.append({
                'severity': 'high',
                'message': 'Site does not use HTTPS — data is transmitted insecurely'
            })
            self.recommendations.append({
                'category': 'Security',
                'recommendation': 'Migrate to HTTPS with an SSL certificate for secure connections'
            })
        return {'is_https': is_https}

    def _check_mixed_content(self):
        """Check for mixed content (HTTP resources on HTTPS page)."""
        if self.parsed_url.scheme != 'https':
            return {'has_mixed_content': False, 'mixed_items': [], 'count': 0}

        mixed_items = []
        # Check images, scripts, stylesheets, iframes
        for tag in self.soup.find_all(['img', 'script', 'link', 'iframe']):
            src = tag.get('src') or tag.get('href', '')
            if src and src.startswith('http://'):
                mixed_items.append({
                    'tag': tag.name,
                    'url': src[:80]
                })

        if mixed_items:
            self.issues.append({
                'severity': 'medium',
                'message': f'{len(mixed_items)} mixed content item(s) found — HTTP resources on HTTPS page'
            })

        return {
            'has_mixed_content': len(mixed_items) > 0,
            'mixed_items': mixed_items[:10],
            'count': len(mixed_items)
        }

    def _check_security_headers(self):
        """Check for security headers."""
        found = []
        missing = []

        for header, info in self.SECURITY_HEADERS.items():
            header_lower = header.lower()
            present = False
            for h in self.headers:
                if h.lower() == header_lower:
                    present = True
                    break
            
            if present:
                found.append({'header': header, 'label': info['label']})
            else:
                missing.append({'header': header, 'label': info['label'], 'description': info['description']})

        if missing:
            self.issues.append({
                'severity': 'medium',
                'message': f'{len(missing)} security header(s) missing'
            })
            if len(missing) > 3:
                self.recommendations.append({
                    'category': 'Security',
                    'recommendation': 'Add security headers (HSTS, CSP, X-Frame-Options) to improve protection'
                })

        return {
            'found': found,
            'missing': missing,
            'found_count': len(found),
            'missing_count': len(missing)
        }

    def _calculate_score(self, https, mixed, headers):
        """Calculate security score."""
        score = 0
        if https['is_https']:
            score += 40
        if not mixed['has_mixed_content']:
            score += 20
        # Header score: up to 40 points
        total_headers = len(self.SECURITY_HEADERS)
        if total_headers > 0:
            score += int((headers['found_count'] / total_headers) * 40)
        return min(score, 100)
