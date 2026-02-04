"""
Web Crawler Module
Handles URL validation and HTML fetching for SEO analysis
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import validators


class WebCrawler:
    """Crawls web pages and extracts HTML content for analysis"""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    def validate_url(self, url: str) -> dict:
        """Validate if the URL is properly formatted"""
        result = {
            'is_valid': False,
            'url': url,
            'error': None
        }
        
        if not url:
            result['error'] = 'URL is empty'
            return result
        
        # Add https if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        if validators.url(url):
            result['is_valid'] = True
            result['url'] = url
        else:
            result['error'] = 'Invalid URL format'
        
        return result
    
    def fetch_page(self, url: str) -> dict:
        """Fetch HTML content from a URL"""
        result = {
            'success': False,
            'html': None,
            'soup': None,
            'status_code': None,
            'error': None,
            'response_time': None,
            'url': url
        }
        
        # Validate URL first
        validation = self.validate_url(url)
        if not validation['is_valid']:
            result['error'] = validation['error']
            return result
        
        url = validation['url']
        result['url'] = url
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            result['status_code'] = response.status_code
            result['response_time'] = response.elapsed.total_seconds()
            
            if response.status_code == 200:
                result['success'] = True
                result['html'] = response.text
                result['soup'] = BeautifulSoup(response.text, 'lxml')
            else:
                result['error'] = f'HTTP {response.status_code}: Failed to fetch page'
                
        except requests.exceptions.Timeout:
            result['error'] = 'Request timed out'
        except requests.exceptions.ConnectionError:
            result['error'] = 'Failed to connect to the server'
        except requests.exceptions.RequestException as e:
            result['error'] = f'Request failed: {str(e)}'
        
        return result
    
    def get_page_resources(self, soup: BeautifulSoup) -> dict:
        """Extract resource information from the page"""
        resources = {
            'scripts': len(soup.find_all('script', src=True)),
            'stylesheets': len(soup.find_all('link', rel='stylesheet')),
            'images': len(soup.find_all('img')),
            'iframes': len(soup.find_all('iframe')),
            'fonts': len(soup.find_all('link', rel='preload', as_='font'))
        }
        return resources
