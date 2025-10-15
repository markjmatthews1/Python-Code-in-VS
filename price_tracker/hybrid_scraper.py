#!/usr/bin/env python3
"""
Advanced web scraping with browser automation fallback for JavaScript-heavy sites
This will attempt to get prices from ALL retailers using multiple techniques
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from bs4 import BeautifulSoup
import random
import time
import urllib.parse
import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BrowserScraper:
    """Browser automation for JavaScript-heavy sites"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with stealth options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager to automatically handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Browser automation driver initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup browser driver: {e}")
            logger.info("Browser automation not available - will use HTTP-only scraping")
            self.driver = None
    
    def scrape_with_browser(self, url, retailer_name):
        """Scrape using browser automation"""
        if not self.driver:
            return []
        
        try:
            logger.info(f"Using browser automation for {retailer_name}")
            self.driver.get(url)
            
            # Wait for page to load and try different selectors
            time.sleep(3)
            
            products = []
            
            if retailer_name.lower() == 'target':
                products = self.scrape_target_browser()
            elif retailer_name.lower() == 'home depot':
                products = self.scrape_homedepot_browser()
            elif retailer_name.lower() == 'best buy':
                products = self.scrape_bestbuy_browser()
            elif retailer_name.lower() == "sam's club":
                products = self.scrape_samsclub_browser()
                
            return products
            
        except Exception as e:
            logger.error(f"Browser scraping error for {retailer_name}: {e}")
            return []
    
    def scrape_target_browser(self):
        """Target-specific browser scraping"""
        products = []
        try:
            # Wait for products to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='product-details'], .ProductCardImage, .h-display-flex"))
            )
            
            # Try multiple selectors for Target
            selectors = [
                "[data-test='product-details']",
                ".ProductCardImage",
                ".h-display-flex",
                "[data-test*='product']",
                ".styles__ProductCardContainer"
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Target: Found {len(elements)} elements with selector: {selector}")
                    for element in elements[:5]:  # Limit to 5 products
                        try:
                            # Extract title
                            title_elem = element.find_element(By.CSS_SELECTOR, "a, h3, h2, span")
                            title = title_elem.text.strip()
                            
                            # Extract price
                            price_text = element.text
                            price_match = re.search(r'\$(\d+\.?\d*)', price_text)
                            price = float(price_match.group(1)) if price_match else 0
                            
                            # Extract URL
                            try:
                                link = element.find_element(By.CSS_SELECTOR, "a")
                                url = link.get_attribute('href')
                                if not url.startswith('http'):
                                    url = "https://www.target.com" + url
                            except:
                                url = "https://www.target.com"
                            
                            if title and price > 0 and len(title) > 10:
                                products.append({
                                    "title": title,
                                    "price": price,
                                    "url": url,
                                    "source": "target_browser"
                                })
                        except Exception as e:
                            continue
                    
                    if products:  # If we found products, break
                        break
            
        except TimeoutException:
            logger.warning("Target: Page load timeout")
        except Exception as e:
            logger.error(f"Target browser scraping error: {e}")
        
        return products[:3]  # Return top 3
    
    def scrape_homedepot_browser(self):
        """Home Depot browser scraping"""
        products = []
        try:
            # Wait for products to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='product'], .product-pod, .browse-search__pod"))
            )
            
            selectors = [
                "[data-testid='product-pod']",
                ".product-pod",
                ".browse-search__pod",
                "[data-testid*='product']",
                ".product-card"
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Home Depot: Found {len(elements)} elements with selector: {selector}")
                    for element in elements[:5]:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, "a, h3, span").text.strip()
                            
                            price_text = element.text
                            price_match = re.search(r'\$(\d+\.?\d*)', price_text)
                            price = float(price_match.group(1)) if price_match else 0
                            
                            try:
                                link = element.find_element(By.CSS_SELECTOR, "a")
                                url = link.get_attribute('href')
                                if not url.startswith('http'):
                                    url = "https://www.homedepot.com" + url
                            except:
                                url = "https://www.homedepot.com"
                            
                            if title and price > 0 and len(title) > 10:
                                products.append({
                                    "title": title,
                                    "price": price,
                                    "url": url,
                                    "source": "homedepot_browser"
                                })
                        except Exception as e:
                            continue
                    
                    if products:
                        break
            
        except TimeoutException:
            logger.warning("Home Depot: Page load timeout")
        except Exception as e:
            logger.error(f"Home Depot browser scraping error: {e}")
        
        return products[:3]
    
    def scrape_bestbuy_browser(self):
        """Best Buy browser scraping"""
        products = []
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".sku-item, .product-item, [data-testid*='product']"))
            )
            
            selectors = [
                ".sku-item",
                ".product-item", 
                "[data-testid*='product']",
                ".list-item"
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Best Buy: Found {len(elements)} elements with selector: {selector}")
                    for element in elements[:5]:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, "a, h4, h3").text.strip()
                            
                            price_text = element.text
                            price_match = re.search(r'\$(\d+\.?\d*)', price_text)
                            price = float(price_match.group(1)) if price_match else 0
                            
                            try:
                                link = element.find_element(By.CSS_SELECTOR, "a")
                                url = link.get_attribute('href')
                                if not url.startswith('http'):
                                    url = "https://www.bestbuy.com" + url
                            except:
                                url = "https://www.bestbuy.com"
                            
                            if title and price > 0 and len(title) > 10:
                                products.append({
                                    "title": title,
                                    "price": price,
                                    "url": url,
                                    "source": "bestbuy_browser"
                                })
                        except Exception as e:
                            continue
                    
                    if products:
                        break
            
        except TimeoutException:
            logger.warning("Best Buy: Page load timeout")
        except Exception as e:
            logger.error(f"Best Buy browser scraping error: {e}")
        
        return products[:3]
    
    def scrape_samsclub_browser(self):
        """Sam's Club browser scraping"""
        products = []
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-automation-id*='product'], .ProductTile"))
            )
            
            selectors = [
                "[data-automation-id*='product']",
                ".ProductTile",
                ".product-tile",
                "[data-testid*='product']"
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Sam's Club: Found {len(elements)} elements with selector: {selector}")
                    for element in elements[:5]:
                        try:
                            title = element.find_element(By.CSS_SELECTOR, "a, h3, span").text.strip()
                            
                            price_text = element.text
                            price_match = re.search(r'\$(\d+\.?\d*)', price_text)
                            price = float(price_match.group(1)) if price_match else 0
                            
                            try:
                                link = element.find_element(By.CSS_SELECTOR, "a")
                                url = link.get_attribute('href')
                                if not url.startswith('http'):
                                    url = "https://www.samsclub.com" + url
                            except:
                                url = "https://www.samsclub.com"
                            
                            if title and price > 0 and len(title) > 10:
                                products.append({
                                    "title": title,
                                    "price": price,
                                    "url": url,
                                    "source": "samsclub_browser"
                                })
                        except Exception as e:
                            continue
                    
                    if products:
                        break
            
        except TimeoutException:
            logger.warning("Sam's Club: Page load timeout")
        except Exception as e:
            logger.error(f"Sam's Club browser scraping error: {e}")
        
        return products[:3]
    
    def close(self):
        """Clean up browser driver"""
        if self.driver:
            self.driver.quit()

class HybridRetailerScraper:
    """Hybrid scraper combining regular HTTP and browser automation"""
    
    def __init__(self):
        self.browser = None
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Setup HTTP session with enhanced headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_browser(self):
        """Lazy load browser automation"""
        if not self.browser:
            self.browser = BrowserScraper()
        return self.browser
    
    def search_all_retailers(self, search_term, max_results=3):
        """Search all retailers with fallback methods"""
        
        retailers = {
            'Amazon': {
                'url': f"https://www.amazon.com/s?k={urllib.parse.quote_plus(search_term)}",
                'method': 'http',  # Amazon works with HTTP
                'parser': self.parse_amazon
            },
            'Walmart': {
                'url': f"https://www.walmart.com/search/?query={urllib.parse.quote_plus(search_term)}",
                'method': 'http',  # Walmart works with HTTP
                'parser': self.parse_walmart
            },
            'Target': {
                'url': f"https://www.target.com/s?searchTerm={urllib.parse.quote_plus(search_term)}",
                'method': 'browser',  # Target needs browser
                'parser': None
            },
            'Best Buy': {
                'url': f"https://www.bestbuy.com/site/searchpage.jsp?st={urllib.parse.quote_plus(search_term)}",
                'method': 'browser',  # Best Buy needs browser  
                'parser': None
            },
            'Home Depot': {
                'url': f"https://www.homedepot.com/s/{urllib.parse.quote_plus(search_term)}",
                'method': 'browser',  # Home Depot needs browser
                'parser': None
            },
            'Lowes': {
                'url': f"https://www.lowes.com/search?searchTerm={urllib.parse.quote_plus(search_term)}",
                'method': 'http_aggressive',  # Try aggressive HTTP first, then browser
                'parser': self.parse_lowes
            },
            "Sam's Club": {
                'url': f"https://www.samsclub.com/search?searchTerm={urllib.parse.quote_plus(search_term)}",
                'method': 'browser',  # Sam's Club needs browser
                'parser': None
            }
        }
        
        all_results = {}
        
        for name, config in retailers.items():
            print(f"\n🛒 Scraping {name}...")
            
            try:
                if config['method'] == 'http':
                    products = self.scrape_http(config['url'], config['parser'], name)
                elif config['method'] == 'http_aggressive':
                    products = self.scrape_http_aggressive(config['url'], config['parser'], name)
                    if not products:  # Fallback to browser
                        products = self.get_browser().scrape_with_browser(config['url'], name)
                else:  # browser method
                    products = self.get_browser().scrape_with_browser(config['url'], name)
                
                all_results[name] = products
                
                if products:
                    print(f"✅ Found {len(products)} products on {name}")
                    for i, product in enumerate(products[:2], 1):
                        print(f"  {i}. {product['title'][:60]}... - ${product['price']}")
                else:
                    print(f"❌ No products found on {name}")
                
                time.sleep(1)  # Be respectful
                
            except Exception as e:
                print(f"❌ Error with {name}: {e}")
                all_results[name] = []
        
        return all_results
    
    def scrape_http(self, url, parser, retailer_name):
        """Standard HTTP scraping"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return parser(soup) if parser else []
            
        except Exception as e:
            logger.error(f"HTTP scraping error for {retailer_name}: {e}")
            return []
    
    def scrape_http_aggressive(self, url, parser, retailer_name):
        """Aggressive HTTP scraping with multiple attempts"""
        attempts = [
            # Attempt 1: Standard
            lambda: self.session.get(url, timeout=10),
            # Attempt 2: Different user agent
            lambda: self._request_with_headers(url, {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}),
            # Attempt 3: Minimal headers
            lambda: self._request_with_headers(url, {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        ]
        
        for i, attempt in enumerate(attempts, 1):
            try:
                logger.info(f"HTTP attempt {i} for {retailer_name}")
                response = attempt()
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    products = parser(soup) if parser else []
                    if products:
                        return products
                
                time.sleep(2)  # Wait between attempts
                
            except Exception as e:
                logger.debug(f"HTTP attempt {i} failed for {retailer_name}: {e}")
                continue
        
        return []
    
    def _request_with_headers(self, url, headers):
        """Make request with custom headers"""
        session = requests.Session()
        session.headers.update(headers)
        return session.get(url, timeout=10)
    
    def parse_amazon(self, soup):
        """Parse Amazon results (existing logic)"""
        products = []
        containers = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for container in containers[:3]:
            try:
                title_elem = container.find('h2', class_=lambda x: x and 's-title' in str(x))
                if title_elem:
                    title_link = title_elem.find('a')
                    if title_link:
                        title = title_link.get_text(strip=True)
                        
                        price_elem = container.find('span', class_='a-price-whole')
                        price = 0
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            price = float(re.sub(r'[^0-9.]', '', price_text))
                        
                        url = "https://www.amazon.com" + title_link['href']
                        
                        products.append({
                            'title': title,
                            'price': price,
                            'url': url,
                            'source': 'amazon_http'
                        })
            except Exception:
                continue
        
        return products
    
    def parse_walmart(self, soup):
        """Parse Walmart results (existing logic)"""
        products = []
        containers = soup.find_all('div', {'data-automation-id': re.compile(r'product', re.I)})
        
        if not containers:
            containers = soup.find_all('div', {'data-testid': re.compile(r'item|product', re.I)})
        
        for container in containers[:3]:
            try:
                title_elem = container.find('a', {'data-automation-id': 'product-title'})
                if not title_elem:
                    title_elem = container.find('span', attrs={'data-automation-id': re.compile(r'product-title', re.I)})
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    price_elem = container.find('div', class_=lambda x: x and 'price' in str(x).lower())
                    price = 0
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                        if price_match:
                            price = float(price_match.group(1).replace(',', ''))
                    
                    url = "https://www.walmart.com" + (title_elem.get('href', '') if title_elem.name == 'a' else '')
                    
                    products.append({
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'walmart_http'
                    })
            except Exception:
                continue
        
        return products
    
    def parse_lowes(self, soup):
        """Parse Lowes results (existing logic)"""
        products = []
        containers = soup.find_all('div', class_=lambda x: x and 'search-results-item' in str(x))
        
        for container in containers[:3]:
            try:
                title_elem = container.find('a', class_=lambda x: x and 'title' in str(x))
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    price_elem = container.find('span', class_=lambda x: x and 'price' in str(x))
                    price = 0
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                        if price_match:
                            price = float(price_match.group(1).replace(',', ''))
                    
                    url = "https://www.lowes.com" + title_elem.get('href', '')
                    
                    products.append({
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'lowes_http'
                    })
            except Exception:
                continue
        
        return products
    
    def find_best_price(self, all_results):
        """Find the cheapest price across all retailers"""
        all_products = []
        
        for retailer, products in all_results.items():
            for product in products:
                if product['price'] > 0:  # Only include products with valid prices
                    product['retailer'] = retailer
                    all_products.append(product)
        
        if not all_products:
            return None
        
        # Sort by price
        all_products.sort(key=lambda x: x['price'])
        
        return all_products[0]  # Return cheapest
    
    def close(self):
        """Cleanup resources"""
        if self.browser:
            self.browser.close()

def test_comprehensive_search():
    """Test the comprehensive retailer search"""
    search_term = "12000 BTU 115v mini split air conditioner"
    
    print(f"🔍 Comprehensive Multi-Retailer Search: '{search_term}'")
    print("=" * 80)
    print("Using HTTP scraping + Browser automation for maximum coverage")
    print("=" * 80)
    
    scraper = HybridRetailerScraper()
    
    try:
        # Search all retailers
        results = scraper.search_all_retailers(search_term)
        
        print(f"\n📊 COMPREHENSIVE RESULTS SUMMARY:")
        print("=" * 80)
        
        total_products = sum(len(products) for products in results.values())
        working_retailers = sum(1 for products in results.values() if products)
        
        print(f"Total products found: {total_products}")
        print(f"Working retailers: {working_retailers}/7")
        print()
        
        for retailer, products in results.items():
            status = "✅" if products else "❌"
            print(f"{status} {retailer}: {len(products)} products")
        
        # Find best price
        best_deal = scraper.find_best_price(results)
        
        if best_deal:
            print(f"\n🏆 BEST PRICE FOUND:")
            print("=" * 50)
            print(f"Retailer: {best_deal['retailer']}")
            print(f"Price: ${best_deal['price']}")
            print(f"Product: {best_deal['title'][:100]}...")
            print(f"URL: {best_deal['url']}")
        else:
            print(f"\n❌ No valid prices found across any retailer")
        
        return results, best_deal
        
    finally:
        scraper.close()

if __name__ == "__main__":
    test_comprehensive_search()