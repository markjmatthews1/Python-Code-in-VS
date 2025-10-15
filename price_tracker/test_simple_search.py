#!/usr/bin/env python3
"""
Test script for simple product search to debug scraping issues
"""
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_amazon_simple():
    """Test Amazon with a simple, common product"""
    search_term = "laptop"
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Initialize WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Navigate to Amazon search
            url = f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}"
            print(f"🔍 Testing Amazon search: {url}")
            
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source and check what we received
            page_source = driver.page_source
            
            print(f"📄 Page title: {driver.title}")
            print(f"📄 Page length: {len(page_source)} characters")
            
            # Save HTML for inspection
            with open('amazon_test.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("💾 Saved page source to amazon_test.html")
            
            # Look for product containers
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Try different selectors
            selectors_to_test = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '[data-asin]',
                '.sg-col-inner',
                '.a-section'
            ]
            
            for selector in selectors_to_test:
                elements = soup.select(selector)
                print(f"🎯 Selector '{selector}': found {len(elements)} elements")
                
                if elements and len(elements) > 0:
                    print(f"   First element preview: {str(elements[0])[:200]}...")
            
            # Check for anti-bot detection
            if 'captcha' in page_source.lower() or 'robot' in page_source.lower():
                print("🚫 Anti-bot detection detected!")
            
            if 'Service Unavailable' in page_source:
                print("🚫 Service unavailable error!")
                
        except Exception as e:
            print(f"❌ Browser error: {e}")
        
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Setup error: {e}")

def test_walmart_simple():
    """Test Walmart with a simple search"""
    search_term = "laptop"
    
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Initialize WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Navigate to Walmart search
            url = f"https://www.walmart.com/search?q={search_term.replace(' ', '+')}"
            print(f"🔍 Testing Walmart search: {url}")
            
            driver.get(url)
            
            # Wait for content to load
            time.sleep(5)
            
            # Get page source
            page_source = driver.page_source
            
            print(f"📄 Page title: {driver.title}")
            print(f"📄 Page length: {len(page_source)} characters")
            
            # Save HTML for inspection
            with open('walmart_test.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("💾 Saved page source to walmart_test.html")
            
            # Look for product containers
            soup = BeautifulSoup(page_source, 'html.parser')
            
            selectors_to_test = [
                '[data-automation-id="product-title"]',
                '[data-testid="list-view"]',
                '[data-testid="item-stack"]',
                '.mb1',
                '.w_V_DM'
            ]
            
            for selector in selectors_to_test:
                elements = soup.select(selector)
                print(f"🎯 Selector '{selector}': found {len(elements)} elements")
                
                if elements and len(elements) > 0:
                    print(f"   First element preview: {str(elements[0])[:200]}...")
            
        except Exception as e:
            print(f"❌ Browser error: {e}")
        
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    print("🧪 Testing simple product searches...")
    print("=" * 50)
    
    print("\n1. Testing Amazon...")
    test_amazon_simple()
    
    print("\n2. Testing Walmart...")
    test_walmart_simple()
    
    print("\n✅ Test complete! Check the HTML files to debug issues.")