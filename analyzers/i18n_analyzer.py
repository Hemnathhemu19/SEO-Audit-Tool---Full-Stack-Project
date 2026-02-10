"""
Internationalization (i18n) Checker
Checks for hreflang tags, language declarations, and charset.
"""


class I18nAnalyzer:
    """Analyzes internationalization aspects of a webpage."""

    def __init__(self, soup):
        self.soup = soup
        self.issues = []
        self.recommendations = []

    def analyze(self):
        """Run i18n analysis."""
        lang_check = self._check_language()
        charset_check = self._check_charset()
        hreflang_check = self._check_hreflang()
        dir_check = self._check_direction()

        score = self._calculate_score(lang_check, charset_check, hreflang_check)

        return {
            'score': score,
            'language': lang_check,
            'charset': charset_check,
            'hreflang': hreflang_check,
            'direction': dir_check,
            'issues': self.issues,
            'recommendations': self.recommendations
        }

    def _check_language(self):
        """Check for language declaration."""
        html_tag = self.soup.find('html')
        lang = html_tag.get('lang', '') if html_tag else ''

        if not lang:
            self.issues.append({
                'severity': 'high',
                'message': 'No lang attribute on <html> tag'
            })
            self.recommendations.append({
                'category': 'i18n',
                'recommendation': 'Add lang attribute to <html> tag (e.g., lang="en")'
            })

        # Check content-language meta
        content_lang = ''
        meta_lang = self.soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'content-language'})
        if meta_lang:
            content_lang = meta_lang.get('content', '')

        return {
            'html_lang': lang,
            'content_language': content_lang,
            'has_lang': bool(lang),
            'language_name': self._get_language_name(lang)
        }

    def _check_charset(self):
        """Check charset declaration."""
        charset_meta = self.soup.find('meta', charset=True)
        charset = charset_meta.get('charset', '') if charset_meta else ''

        if not charset:
            # Check content-type meta
            ct_meta = self.soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'content-type'})
            if ct_meta:
                content = ct_meta.get('content', '')
                if 'charset=' in content:
                    charset = content.split('charset=')[-1].strip()

        is_utf8 = charset.lower().replace('-', '') == 'utf8' if charset else False

        if not charset:
            self.issues.append({
                'severity': 'medium',
                'message': 'No charset declaration found'
            })
            self.recommendations.append({
                'category': 'i18n',
                'recommendation': 'Add <meta charset="UTF-8"> as the first element in <head>'
            })
        elif not is_utf8:
            self.issues.append({
                'severity': 'low',
                'message': f'Charset is {charset} — consider using UTF-8 for wider compatibility'
            })

        return {
            'charset': charset,
            'is_utf8': is_utf8,
            'has_charset': bool(charset)
        }

    def _check_hreflang(self):
        """Check for hreflang tags."""
        hreflang_tags = self.soup.find_all('link', rel='alternate', hreflang=True)
        
        languages = []
        has_x_default = False
        for tag in hreflang_tags:
            lang = tag.get('hreflang', '')
            href = tag.get('href', '')
            if lang.lower() == 'x-default':
                has_x_default = True
            languages.append({
                'lang': lang,
                'url': href[:80]
            })

        is_multilingual = len(languages) > 1

        if is_multilingual and not has_x_default:
            self.recommendations.append({
                'category': 'i18n',
                'recommendation': 'Add hreflang="x-default" for the default language version'
            })

        return {
            'has_hreflang': len(languages) > 0,
            'languages': languages,
            'language_count': len(languages),
            'has_x_default': has_x_default,
            'is_multilingual': is_multilingual
        }

    def _check_direction(self):
        """Check text direction attribute."""
        html_tag = self.soup.find('html')
        direction = html_tag.get('dir', '') if html_tag else ''
        return {
            'has_dir': bool(direction),
            'direction': direction or 'ltr (default)'
        }

    def _get_language_name(self, code):
        """Get human-readable language name from code."""
        langs = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'ru': 'Russian',
            'zh': 'Chinese', 'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic',
            'hi': 'Hindi', 'tr': 'Turkish', 'pl': 'Polish', 'sv': 'Swedish',
            'da': 'Danish', 'fi': 'Finnish', 'no': 'Norwegian', 'th': 'Thai'
        }
        base = code.split('-')[0].lower() if code else ''
        return langs.get(base, code or 'Unknown')

    def _calculate_score(self, lang, charset, hreflang):
        """Calculate i18n score."""
        score = 0
        if lang['has_lang']:
            score += 40
        if charset['has_charset']:
            score += 30
            if charset['is_utf8']:
                score += 10
        if hreflang['has_hreflang']:
            score += 15
            if hreflang['has_x_default']:
                score += 5
        return min(score, 100)
