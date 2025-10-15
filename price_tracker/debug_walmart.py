#!/usr/bin/env python3
"""
Debug Walmart specifically to understand the blocking
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
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_walmart():
    """Debug Walmart access specifically"""
    
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-browser-side-navigation')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1366,768')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Try Walmart search page directly
        search_term = "laptop"  # Use simple term
        url = f"https://www.walmart.com/search?q={search_term}"
        
        print(f"🔍 Testing Walmart URL: {url}")
        driver.get(url)
        
        # Wait and check what we get
        time.sleep(8)
        
        print(f"📄 Page title: '{driver.title}'")
        print(f"📄 Current URL: {driver.current_url}")
        
        page_source = driver.page_source
        print(f"📄 Page length: {len(page_source)} characters")
        
        # Check for specific blocking indicators
        if 'robot' in driver.title.lower():
            print("🚫 ROBOT DETECTION in title")
        
        if 'human' in driver.title.lower():
            print("🚫 HUMAN VERIFICATION in title")
        
        if 'captcha' in page_source.lower():
            print("🚫 CAPTCHA detected in content")
            
        if 'blocked' in page_source.lower():
            print("🚫 BLOCKED indicator in content")
            
        # Save content for inspection
        with open('walmart_debug.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        
        print("💾 Saved content to walmart_debug.html")
        
        # Try to find any product-like elements
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid]")
            print(f"🎯 Found {len(elements)} elements with data-testid")
            
            elements = driver.find_elements(By.CSS_SELECTOR, "[data-automation-id]")
            print(f"🎯 Found {len(elements)} elements with data-automation-id")
            
            elements = driver.find_elements(By.CSS_SELECTOR, "div")
            print(f"🎯 Found {len(elements)} div elements")
            
        except Exception as e:
            print(f"❌ Error finding elements: {e}")
        
        # Try a different approach - navigate to homepage first
        print("\n🏠 Trying homepage first approach...")
        driver.get("https://www.walmart.com")
        time.sleep(5)
        
        print(f"📄 Homepage title: '{driver.title}'")
        
        if 'robot' not in driver.title.lower() and 'human' not in driver.title.lower():
            print("✅ Homepage loaded successfully!")
            
            # Now try search
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-automation-id='search-bar-input'], #global-search-input, input[type='search']"))
                )
                print("✅ Found search box")
                
                search_box.clear()
                search_box.send_keys(search_term)
                time.sleep(2)
                search_box.submit()
                
                time.sleep(8)
                
                print(f"📄 Search results title: '{driver.title}'")
                print(f"📄 Search results URL: {driver.current_url}")
                
            except Exception as e:
                print(f"❌ Search box error: {e}")
        
    except Exception as e:
        print(f"❌ Main error: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_walmart()