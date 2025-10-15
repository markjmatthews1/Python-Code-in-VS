#!/usr/bin/env python3
"""
Enhanced browser automation with better anti-bot evasion techniques
"""
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StealthBrowserScraper:
    """Enhanced browser scraper with anti-bot evasion"""
    
    def __init__(self):
        self.driver = None
        self.setup_browser()
    
    def setup_browser(self):
        """Set up Chrome with stealth options"""
        try:
            chrome_options = Options()
            
            # Stealth options to avoid detection
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-browser-side-navigation')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--no-service-autorun')
            chrome_options.add_argument('--password-store=basic')
            
            # Realistic window size
            chrome_options.add_argument('--window-size=1366,768')
            
            # Realistic user agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
            
            # Disable automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Additional prefs to seem more human
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Initialize WebDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Stealth browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            self.driver = None
    
    def human_like_delay(self, min_delay=1, max_delay=3):
        """Add human-like delays"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def scroll_page(self, scrolls=3):
        """Simulate human scrolling"""
        try:
            for i in range(scrolls):
                scroll_height = random.randint(300, 800)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
                self.human_like_delay(0.5, 1.5)
        except Exception as e:
            logger.warning(f"Scrolling error: {e}")
    
    def search_amazon_enhanced(self, search_term):
        """Enhanced Amazon search with anti-bot evasion"""
        if not self.driver:
            return []
        
        try:
            # Navigate to Amazon homepage first
            logger.info("Loading Amazon homepage...")
            self.driver.get("https://www.amazon.com")
            self.human_like_delay(2, 4)
            
            # Check if we're blocked
            if 'captcha' in self.driver.page_source.lower() or 'robot' in self.driver.title.lower():
                logger.warning("Amazon CAPTCHA detected")
                return []
            
            # Find search box and enter search term
            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
                )
                
                # Type like a human
                search_box.clear()
                for char in search_term:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                self.human_like_delay(1, 2)
                
                # Click search button
                search_button = self.driver.find_element(By.ID, "nav-search-submit-button")
                search_button.click()
                
                logger.info(f"Searching Amazon for: {search_term}")
                
            except Exception as e:
                # Fallback to direct URL
                url = f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}"
                logger.info(f"Fallback to direct URL: {url}")
                self.driver.get(url)
            
            # Wait for results to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.human_like_delay(2, 4)
            self.scroll_page(2)
            
            # Parse results
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            products = []
            
            # Try main product selector
            result_items = soup.select('[data-component-type="s-search-result"]')
            
            logger.info(f"Amazon: Found {len(result_items)} product containers")
            
            for item in result_items[:10]:  # Limit to first 10
                try:
                    # Get product title
                    title_elem = item.select_one('h2 a span, [data-cy="title-recipe"] span, .a-link-normal span')
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"
                    
                    # Get price
                    price_elem = item.select_one('.a-price .a-offscreen, .a-price-whole, .sx-price')
                    price_text = price_elem.get_text(strip=True) if price_elem else "N/A"
                    
                    # Get URL
                    url_elem = item.select_one('h2 a, [data-cy="title-recipe"] a')
                    url = "https://www.amazon.com" + url_elem.get('href') if url_elem and url_elem.get('href') else "N/A"
                    
                    if title != "N/A" and title:
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
            logger.error(f"Amazon search error: {e}")
            return []
    
    def search_walmart_enhanced(self, search_term):
        """Enhanced Walmart search with anti-bot evasion"""
        if not self.driver:
            return []
        
        try:
            # Navigate to Walmart homepage first
            logger.info("Loading Walmart homepage...")
            self.driver.get("https://www.walmart.com")
            self.human_like_delay(3, 5)
            
            # Check for bot detection
            if 'robot' in self.driver.title.lower() or 'human' in self.driver.title.lower():
                logger.warning("Walmart bot detection triggered")
                return []
            
            # Try to find and use search box
            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-automation-id='search-bar-input'], #global-search-input"))
                )
                
                # Human-like typing
                search_box.clear()
                for char in search_term:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                self.human_like_delay(1, 2)
                
                # Submit search
                search_box.submit()
                logger.info(f"Searching Walmart for: {search_term}")
                
            except Exception as e:
                # Fallback to direct URL
                url = f"https://www.walmart.com/search?q={search_term.replace(' ', '+')}"
                logger.info(f"Fallback to direct URL: {url}")
                self.driver.get(url)
            
            # Wait longer for Walmart's JavaScript to load
            self.human_like_delay(5, 8)
            
            # Scroll to trigger content loading
            self.scroll_page(3)
            self.human_like_delay(2, 4)
            
            # Parse results
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            products = []
            
            # Try multiple selectors for Walmart products
            selectors = [
                '[data-testid="item-stack"]',
                '[data-automation-id="product-title"]',
                '.mb1.ph1.pa0-xl.bb.b--near-white.w-25',
                '[data-testid="list-view"] > div',
                '.w_V_DM'
            ]
            
            result_items = []
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    result_items = items
                    logger.info(f"Walmart: Using selector '{selector}', found {len(items)} items")
                    break
            
            for item in result_items[:10]:  # Limit to first 10
                try:
                    # Get product title
                    title_elem = item.select_one('[data-automation-id="product-title"], .normal.dark-gray, span[data-automation-id="product-title"]')
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"
                    
                    # Get price
                    price_elem = item.select_one('.price, [data-automation-id="product-price"], .lh-title.mr1.mr2-xl.b.black.f5.f4-l')
                    price_text = price_elem.get_text(strip=True) if price_elem else "N/A"
                    
                    # Get URL
                    url_elem = item.select_one('a[href*="/ip/"]')
                    url = "https://www.walmart.com" + url_elem.get('href') if url_elem and url_elem.get('href') else "N/A"
                    
                    if title != "N/A" and title:
                        products.append({
                            'title': title,
                            'price': price_text,
                            'url': url,
                            'retailer': 'Walmart'
                        })
                
                except Exception as e:
                    logger.debug(f"Error parsing Walmart item: {e}")
                    continue
            
            logger.info(f"Walmart: Successfully parsed {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Walmart search error: {e}")
            return []
    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")

def test_enhanced_scraping():
    """Test the enhanced scraping approach"""
    scraper = StealthBrowserScraper()
    
    try:
        search_term = "mini split air conditioner"
        print(f"🔍 Testing enhanced scraping for: {search_term}")
        print("=" * 60)
        
        # Test Amazon
        print("\n🛒 Testing Amazon...")
        amazon_products = scraper.search_amazon_enhanced(search_term)
        
        print(f"Found {len(amazon_products)} Amazon products:")
        for i, product in enumerate(amazon_products[:3], 1):  # Show first 3
            print(f"  {i}. {product['title'][:80]}...")
            print(f"     Price: {product['price']}")
            print()
        
        # Test Walmart
        print("\n🛒 Testing Walmart...")
        walmart_products = scraper.search_walmart_enhanced(search_term)
        
        print(f"Found {len(walmart_products)} Walmart products:")
        for i, product in enumerate(walmart_products[:3], 1):  # Show first 3
            print(f"  {i}. {product['title'][:80]}...")
            print(f"     Price: {product['price']}")
            print()
        
        total_products = len(amazon_products) + len(walmart_products)
        print(f"\n📊 TOTAL RESULTS: {total_products} products found across 2 retailers")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    test_enhanced_scraping()