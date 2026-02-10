"""
Core Web Vitals Estimator
Estimates LCP, CLS, and FID/INP based on page structure analysis.
"""

import re


class VitalsAnalyzer:
    """Estimates Core Web Vitals from page structure."""

    def __init__(self, soup, response_time=None):
        self.soup = soup
        self.response_time = response_time or 0
        self.issues = []
        self.recommendations = []

    def analyze(self):
        """Run Core Web Vitals estimation."""
        lcp = self._estimate_lcp()
        cls_data = self._estimate_cls()
        inp = self._estimate_inp()

        score = self._calculate_score(lcp, cls_data, inp)

        return {
            'score': score,
            'lcp': lcp,
            'cls': cls_data,
            'inp': inp,
            'issues': self.issues,
            'recommendations': self.recommendations
        }

    def _estimate_lcp(self):
        """Estimate Largest Contentful Paint."""
        # LCP is affected by: large images, render-blocking resources, server time
        risk_factors = []
        risk_level = 'good'

        # Check for large hero images without loading optimization
        images = self.soup.find_all('img')
        large_images = [img for img in images if not img.get('loading') == 'lazy']
        above_fold_images = large_images[:3]  # First 3 images likely above fold
        
        unoptimized = [img for img in above_fold_images if not img.get('width') or not img.get('height')]
        if unoptimized:
            risk_factors.append('Images without explicit dimensions')

        # Render-blocking resources
        blocking_css = self.soup.find_all('link', rel='stylesheet')
        blocking_js = [s for s in self.soup.find_all('script', src=True)
                       if not s.get('async') and not s.get('defer')]
        
        if len(blocking_css) > 3:
            risk_factors.append(f'{len(blocking_css)} render-blocking CSS files')
        if len(blocking_js) > 2:
            risk_factors.append(f'{len(blocking_js)} render-blocking JS files')

        # Estimate LCP time
        estimated_ms = self.response_time * 1000 if self.response_time else 500
        estimated_ms += len(blocking_css) * 100
        estimated_ms += len(blocking_js) * 150
        if unoptimized:
            estimated_ms += 300

        if estimated_ms > 4000:
            risk_level = 'poor'
            self.issues.append({'severity': 'high', 'message': 'High LCP risk — page may load slowly'})
        elif estimated_ms > 2500:
            risk_level = 'needs_improvement'
            self.issues.append({'severity': 'medium', 'message': 'LCP may need improvement'})

        return {
            'estimated_ms': round(estimated_ms),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'blocking_css': len(blocking_css),
            'blocking_js': len(blocking_js)
        }

    def _estimate_cls(self):
        """Estimate Cumulative Layout Shift."""
        risk_factors = []
        risk_level = 'good'

        # Images without dimensions cause layout shifts
        images = self.soup.find_all('img')
        no_dimensions = [img for img in images if not (img.get('width') and img.get('height'))]
        
        # Ads, iframes without dimensions
        iframes = self.soup.find_all('iframe')
        no_dim_iframes = [f for f in iframes if not (f.get('width') and f.get('height'))]

        # Dynamic content injection (ads, embeds)
        dynamic_elements = self.soup.find_all(['ins', 'amp-ad'])

        if no_dimensions:
            risk_factors.append(f'{len(no_dimensions)} images without width/height')
        if no_dim_iframes:
            risk_factors.append(f'{len(no_dim_iframes)} iframes without dimensions')
        if dynamic_elements:
            risk_factors.append(f'{len(dynamic_elements)} dynamic ad elements')

        # Web fonts without font-display
        font_links = [l for l in self.soup.find_all('link') if 'font' in (l.get('href', '') or '').lower()]
        styles = self.soup.find_all('style')
        has_font_display = any('font-display' in (s.string or '') for s in styles)
        if font_links and not has_font_display:
            risk_factors.append('Web fonts without font-display swap')

        shift_score = len(no_dimensions) * 0.02 + len(no_dim_iframes) * 0.05 + len(dynamic_elements) * 0.03
        if shift_score > 0.25:
            risk_level = 'poor'
            self.issues.append({'severity': 'high', 'message': 'High CLS risk — significant layout shifts expected'})
        elif shift_score > 0.1:
            risk_level = 'needs_improvement'

        return {
            'estimated_score': round(min(shift_score, 1.0), 3),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'images_no_dimensions': len(no_dimensions),
            'iframes_no_dimensions': len(no_dim_iframes)
        }

    def _estimate_inp(self):
        """Estimate Interaction to Next Paint (replaces FID)."""
        risk_factors = []
        risk_level = 'good'

        # Heavy JS blocks main thread
        scripts = self.soup.find_all('script')
        inline_scripts = [s for s in scripts if s.string and len(s.string) > 500]
        external_scripts = [s for s in scripts if s.get('src')]

        if len(external_scripts) > 10:
            risk_factors.append(f'{len(external_scripts)} external scripts loaded')
        if inline_scripts:
            total_inline = sum(len(s.string) for s in inline_scripts)
            if total_inline > 5000:
                risk_factors.append(f'{total_inline // 1000}KB inline JavaScript')

        # Event handlers in HTML (legacy pattern)
        event_attrs = ['onclick', 'onload', 'onscroll', 'onmouseover']
        inline_handlers = 0
        for attr in event_attrs:
            inline_handlers += len(self.soup.find_all(attrs={attr: True}))
        if inline_handlers > 5:
            risk_factors.append(f'{inline_handlers} inline event handlers')

        estimated_ms = len(external_scripts) * 20 + len(inline_scripts) * 30
        if estimated_ms > 500:
            risk_level = 'poor'
            self.issues.append({'severity': 'high', 'message': 'Heavy JavaScript may cause slow interactions'})
        elif estimated_ms > 200:
            risk_level = 'needs_improvement'

        return {
            'estimated_ms': round(estimated_ms),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'external_scripts': len(external_scripts),
            'inline_scripts': len(inline_scripts)
        }

    def _calculate_score(self, lcp, cls_data, inp):
        """Calculate overall Core Web Vitals score."""
        scores = {'good': 100, 'needs_improvement': 60, 'poor': 20}
        lcp_score = scores.get(lcp['risk_level'], 50)
        cls_score = scores.get(cls_data['risk_level'], 50)
        inp_score = scores.get(inp['risk_level'], 50)
        return round((lcp_score * 0.4 + cls_score * 0.3 + inp_score * 0.3))
