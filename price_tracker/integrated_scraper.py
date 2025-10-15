#!/usr/bin/env python3
"""
Integrated Multi-Retailer Scraper
=================================

Combines HTTP scraping and browser automation for comprehensive coverage

Author: GitHub Copilot
Created: September 2025
"""

import requests
import json
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import re
import urllib.parse
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedMultiRetailerScraper:
    """Combined HTTP + Browser automation scraper"""
    
    def __init__(self):
        self.session = requests.Session()
        self.browser = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]
        self.setup_http_session()
        
    def setup_http_session(self):
        """Setup HTTP session for faster scraping"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def setup_browser(self):
        """Initialize browser automation when needed"""
        if self.browser:
            return True
            
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1366,768')
            chrome_options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.browser = webdriver.Chrome(service=service, options=chrome_options)
            self.browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Browser automation initialized")
            return True
            
        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            self.browser = None
            return False
    
    def human_delay(self, min_delay=1, max_delay=3):
        """Human-like delays"""
        time.sleep(random.uniform(min_delay, max_delay))
    
    def search_amazon_browser(self, search_term, max_results=10):
        """Search Amazon using browser automation"""
        if not self.setup_browser():
            return []
        
        try:
            # Navigate to Amazon with search
            url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(search_term)}"
            logger.info(f"Browser scraping Amazon: {search_term}")
            
            self.browser.get(url)
            self.human_delay(2, 4)
            
            # Scroll to load more content
            self.browser.execute_script("window.scrollBy(0, 800);")
            self.human_delay(1, 2)
            
            page_source = self.browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            products = []
            result_items = soup.select('[data-component-type="s-search-result"]')
            
            logger.info(f"Amazon browser: Found {len(result_items)} product containers")
            
            for item in result_items[:max_results]:
                try:
                    # Get title
                    title_elem = item.select_one('h2 a span, [data-cy="title-recipe"] span')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Skip sponsored items without proper titles
                    if not title or title.lower() in ['sponsored', 'sponsoredsponsored']:
                        continue
                    
                    # Get price
                    price_elem = item.select_one('.a-price .a-offscreen')
                    price_text = price_elem.get_text(strip=True) if price_elem else "Price not available"
                    
                    # Get URL
                    url_elem = item.select_one('h2 a')
                    url = "https://www.amazon.com" + url_elem.get('href') if url_elem and url_elem.get('href') else ""
                    
                    products.append({
                        'title': title,
                        'price': price_text,
                        'url': url,
                        'retailer': 'Amazon'
                    })
                
                except Exception as e:
                    logger.debug(f"Error parsing Amazon item: {e}")
                    continue
            
            logger.info(f"Amazon: Successfully parsed {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Amazon browser search error: {e}")
            return []
    
    def search_walmart_http(self, search_term, max_results=10):
        """Try HTTP scraping for Walmart first"""
        try:
            url = f"https://www.walmart.com/search?q={urllib.parse.quote_plus(search_term)}"
            logger.info(f"HTTP scraping Walmart: {search_term}")
            
            # Use fresh headers
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Check for blocking
            if 'robot' in response.text.lower() or response.status_code == 403:
                logger.warning("Walmart HTTP blocked, trying browser...")
                return self.search_walmart_browser(search_term, max_results)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Try multiple Walmart selectors
            selectors = [
                '[data-automation-id="product-title"]',
                '[data-testid="item-stack"]',
                '.mb1'
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    logger.info(f"Walmart HTTP: Found {len(items)} items with {selector}")
                    
                    for item in items[:max_results]:
                        try:
                            title_elem = item.select_one('[data-automation-id="product-title"], .normal.dark-gray')
                            if not title_elem:
                                continue
                                
                            title = title_elem.get_text(strip=True)
                            if not title:
                                continue
                            
                            # Get price
                            price_elem = item.select_one('.price, [data-automation-id="product-price"]')
                            price = price_elem.get_text(strip=True) if price_elem else "Price not available"
                            
                            # Get URL
                            url_elem = item.select_one('a[href*="/ip/"]')
                            url = "https://www.walmart.com" + url_elem.get('href') if url_elem else ""
                            
                            products.append({
                                'title': title,
                                'price': price,
                                'url': url,
                                'retailer': 'Walmart'
                            })
                            
                        except Exception as e:
                            logger.debug(f"Error parsing Walmart item: {e}")
                            continue
                    break
            
            logger.info(f"Walmart HTTP: Found {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Walmart HTTP error: {e}")
            return []
    
    def search_walmart_browser(self, search_term, max_results=10):
        """Fallback browser automation for Walmart"""
        if not self.setup_browser():
            return []
            
        try:
            # Go to homepage first
            logger.info("Walmart browser: Loading homepage first")
            self.browser.get("https://www.walmart.com")
            self.human_delay(3, 5)
            
            # Check if homepage loaded successfully
            if 'robot' in self.browser.title.lower():
                logger.warning("Walmart browser: Blocked at homepage")
                return []
            
            # Find search box
            try:
                search_box = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-automation-id='search-bar-input'], #global-search-input"))
                )
                
                search_box.clear()
                search_box.send_keys(search_term)
                self.human_delay(1, 2)
                search_box.submit()
                
                self.human_delay(5, 8)
                
                # Parse results
                page_source = self.browser.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                products = []
                # Add parsing logic similar to HTTP version
                # ... (product parsing code)
                
                logger.info(f"Walmart browser: Found {len(products)} products")
                return products
                
            except Exception as e:
                logger.error(f"Walmart browser search failed: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Walmart browser error: {e}")
            return []
    
    def search_all_retailers(self, search_term, max_results_per_retailer=5):
        """Search across all retailers with hybrid approach"""
        all_products = []
        
        logger.info(f"🔍 Comprehensive search for: {search_term}")
        
        # Amazon - Use browser automation (most reliable)
        try:
            amazon_products = self.search_amazon_browser(search_term, max_results_per_retailer)
            all_products.extend(amazon_products)
            logger.info(f"✅ Amazon: {len(amazon_products)} products")
        except Exception as e:
            logger.error(f"❌ Amazon failed: {e}")
        
        # Walmart - Try HTTP first, fallback to browser
        try:
            walmart_products = self.search_walmart_http(search_term, max_results_per_retailer)
            all_products.extend(walmart_products)
            logger.info(f"✅ Walmart: {len(walmart_products)} products")
        except Exception as e:
            logger.error(f"❌ Walmart failed: {e}")
        
        # Add other retailers here as needed...
        
        logger.info(f"📊 Total products found: {len(all_products)}")
        return all_products
    
    def close(self):
        """Clean up resources"""
        if self.browser:
            try:
                self.browser.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")

def search_products(search_term, max_results=5):
    """Main function to replace the old search_products function"""
    scraper = IntegratedMultiRetailerScraper()
    try:
        return scraper.search_all_retailers(search_term, max_results)
    finally:
        scraper.close()

# Test function
if __name__ == "__main__":
    test_term = "mini split air conditioner"
    print(f"🧪 Testing integrated scraper with: {test_term}")
    products = search_products(test_term)
    
    print(f"\n📊 Results: {len(products)} products found")
    for i, product in enumerate(products[:5], 1):
        print(f"{i}. [{product['retailer']}] {product['title'][:60]}...")
        print(f"   Price: {product['price']}")
        print()